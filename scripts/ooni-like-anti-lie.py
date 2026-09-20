#!/usr/bin/env python3
"""
Smart local DNS list builder (anti–DNS menteur / anti–page de censure).

1) Query many uncensoring CONTROL resolvers (catalogue).
2) Reject sinkholes, private IPs, FR government blockpages (ANJ, DGCCRF…).
3) Keep multi-resolver consensus only (>=2 controls when possible).
4) Compare Free/gateway liars — if they lie or redirect to blockpage, flag it.
5) Write LOCAL hosts ALWAYS for verified consensus (local-first resilience),
   not only when a lie is detected.

Refs: OONI France report, censxres.fr, Citizen Lab fr.csv
"""
from __future__ import annotations

import ipaddress
import json
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
UNC = ROOT / "config" / "uncensor"
SIG = json.loads((UNC / "sinkhole-signatures.json").read_text(encoding="utf-8"))
TARGETS = UNC / "probe-targets.txt"
CRITICAL = UNC / "critical-targets.txt"
OUT_HOSTS = UNC / "hosts.generated"
OUT_UNBOUND = ROOT / "config" / "unbound" / "a-records.conf"
OUT_BLOCKY = UNC / "blocky-custom-dns.yml"
OUT_REPORT = UNC / "last-probe-report.json"
FR_CSV_URL = "https://raw.githubusercontent.com/citizenlab/test-lists/master/lists/fr.csv"
WORKERS = 32

BLOCKPAGE_IPS = set(SIG.get("government_blockpage_ips") or [])
BLOCKPAGE_NAMES = {n.lower().rstrip(".") for n in (SIG.get("government_blockpage_names") or [])}
LIE_IPS = set(SIG.get("lie_answers_ipv4") or []) | {"::1"}


def dig(server: str, name: str, qtype: str) -> list[str]:
    try:
        p = subprocess.run(
            ["dig", f"@{server}", name, qtype, "+time=2", "+tries=1", "+short"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    out: list[str] = []
    for line in (p.stdout or "").splitlines():
        line = line.strip().rstrip(".")
        if not line or line.startswith(";"):
            continue
        low = line.lower()
        if low in BLOCKPAGE_NAMES:
            out.append(f"BLOCKPAGE_NAME:{low}")
            continue
        try:
            ipaddress.ip_address(line)
            out.append(line)
        except ValueError:
            continue
    return out


def is_blockpage_or_sinkhole(addr: str) -> bool:
    if addr.startswith("BLOCKPAGE_NAME:"):
        return True
    if addr in LIE_IPS or addr in BLOCKPAGE_IPS:
        return True
    for pfx in SIG.get("lie_private_prefixes") or []:
        if addr.startswith(pfx):
            return True
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return addr.lower() in BLOCKPAGE_NAMES
    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_unspecified or ip.is_multicast:
        return True
    if ip in ipaddress.ip_network("192.0.2.0/24") or ip in ipaddress.ip_network("198.51.100.0/24"):
        return True
    if ip in ipaddress.ip_network("203.0.113.0/24"):
        return True
    return False


def is_clean_public(addr: str) -> bool:
    if is_blockpage_or_sinkhole(addr):
        return False
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return False
    return not (
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_unspecified
        or ip.is_reserved
    )


def is_lie_answer(addrs: list[str], nx: bool) -> bool:
    if nx or not addrs:
        return True
    return any(is_blockpage_or_sinkhole(a) for a in addrs)


def dig_many(jobs: list[tuple[str, str, str]], pool: ThreadPoolExecutor) -> dict[tuple[str, str, str], list[str]]:
    """Parallel dig; jobs are (server, name, qtype)."""
    fut = {pool.submit(dig, s, n, t): (s, n, t) for s, n, t in jobs}
    out: dict[tuple[str, str, str], list[str]] = {}
    for f in as_completed(fut):
        key = fut[f]
        try:
            out[key] = f.result()
        except Exception:
            out[key] = []
    return out


def consensus_from_answers(answers: list[list[str]]) -> list[str]:
    """Multi-control consensus; never returns blockpage/sinkhole IPs."""
    bag: Counter[str] = Counter()
    for addrs in answers:
        for a in addrs:
            if is_clean_public(a):
                bag[a] += 1
    if not bag:
        return []
    best = bag.most_common()
    chosen = [a for a, n in best if n >= 2]
    if not chosen:
        chosen = [best[0][0]]
    return chosen[:4]


def load_targets() -> list[str]:
    domains: list[str] = []
    seen: set[str] = set()

    def add(d: str) -> None:
        d = d.lower().rstrip(".").strip()
        if not d or d.startswith("#") or d in seen:
            return
        if d in BLOCKPAGE_NAMES:
            return
        seen.add(d)
        domains.append(d)

    for path in (TARGETS, CRITICAL):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            add(line)

    try:
        import urllib.request

        with urllib.request.urlopen(FR_CSV_URL, timeout=30) as r:
            text = r.read().decode("utf-8", errors="replace")
        allow_cat = {
            "NEWS",
            "CULTR",
            "PUBH",
            "LGBT",
            "XED",
            "REL",
            "HACK",
            "IGO",
            "ECON",
            "COMM",
            "HUMR",
            "POLR",
        }
        for line in text.splitlines()[1:]:
            parts = line.split(",")
            if len(parts) < 2:
                continue
            url, cat = parts[0].strip(), parts[1].strip()
            if cat not in allow_cat:
                continue
            host = urlparse(url).hostname
            if host:
                add(host)
    except Exception as e:
        print("WARN: could not fetch fr.csv:", e, file=sys.stderr)

    return domains


def probe_domain(
    domain: str,
    liars: list[str],
    controls: list[str],
    pool: ThreadPoolExecutor,
) -> dict:
    jobs: list[tuple[str, str, str]] = []
    for liar in liars:
        jobs.append((liar, domain, "A"))
    for c in controls:
        jobs.append((c, domain, "A"))
        jobs.append((c, domain, "AAAA"))

    results = dig_many(jobs, pool)

    liar_a: list[str] = []
    liar_nx = True
    for liar in liars:
        ans = results.get((liar, domain, "A"), [])
        if ans:
            liar_a = ans
            liar_nx = False
            break
    lied = is_lie_answer(liar_a, liar_nx)

    ctrl_a = consensus_from_answers([results.get((c, domain, "A"), []) for c in controls])
    ctrl_aaaa = consensus_from_answers([results.get((c, domain, "AAAA"), []) for c in controls])

    sample = results.get((controls[0], domain, "A"), [])
    return {
        "domain": domain,
        "liar_a": liar_a,
        "liar_nx": liar_nx,
        "lied": lied,
        "ctrl_a": ctrl_a,
        "ctrl_aaaa": ctrl_aaaa,
        "sample": sample,
    }


def main() -> int:
    liars = SIG["liar_resolvers"]
    controls = SIG["control_resolvers"]
    report = {
        "lies_corrected": [],
        "verified_stored": [],
        "rejected_blockpage": [],
        "unknown": [],
        "policy": "store clean multi-control consensus; never store sinkhole/blockpage",
    }

    host_lines = [
        "# Smart local DNS — verified vs uncensoring controls",
        "# NEVER contains 127.0.0.1 / ANJ / DGCCRF blockpage IPs",
        "# Generated by scripts/ooni-like-anti-lie.py",
        "",
    ]

    unbound_header = OUT_UNBOUND.read_text(encoding="utf-8") if OUT_UNBOUND.exists() else ""
    keep = []
    for line in unbound_header.splitlines():
        if line.strip().startswith("local-data:"):
            break
        keep.append(line)
    if not any("serve-expired-ttl:" in x for x in keep):
        keep = [
            "# Included INSIDE mvance unbound server: block",
            "serve-expired-ttl: 259200",
            "serve-expired-client-timeout: 1800",
            "serve-expired-reply-ttl: 30",
            "serve-expired-ttl-reset: yes",
            "",
        ]
    unbound_lines = list(keep)
    crit = ROOT / "config" / "unbound" / "a-records.critical.conf"
    if crit.exists():
        for line in crit.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("local-data:"):
                unbound_lines.append(line)

    blocky_map: dict[str, str] = {}
    stored_domains: set[str] = set()

    targets = load_targets()
    print(f"targets={len(targets)} controls={len(controls)} workers={WORKERS}", flush=True)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for i, domain in enumerate(targets, 1):
            r = probe_domain(domain, liars, controls, pool)
            ctrl_a, ctrl_aaaa = r["ctrl_a"], r["ctrl_aaaa"]
            lied = r["lied"]

            if not ctrl_a and not ctrl_aaaa:
                sample = r["sample"]
                if sample and any(is_blockpage_or_sinkhole(a) for a in sample):
                    report["rejected_blockpage"].append(
                        {"domain": domain, "sample": sample, "note": "only blockpage/sinkhole"}
                    )
                else:
                    report["unknown"].append({"domain": domain, "reason": "no_clean_control_answer"})
                if i % 10 == 0 or i == len(targets):
                    print(f"… {i}/{len(targets)} stored={len(stored_domains)}", flush=True)
                continue

            # Final safety: never write blockpage/sinkhole
            ctrl_a = [a for a in ctrl_a if is_clean_public(a)]
            ctrl_aaaa = [a for a in ctrl_aaaa if is_clean_public(a)]
            if not ctrl_a and not ctrl_aaaa:
                report["rejected_blockpage"].append(
                    {"domain": domain, "note": "filtered_all_as_sinkhole"}
                )
                continue

            if domain not in stored_domains:
                for ip in ctrl_a:
                    host_lines.append(f"{ip} {domain}")
                    unbound_lines.append(f'local-data: "{domain}. IN A {ip}"')
                for ip in ctrl_aaaa:
                    host_lines.append(f"{ip} {domain}")
                    unbound_lines.append(f'local-data: "{domain}. IN AAAA {ip}"')
                if ctrl_a:
                    blocky_map[domain] = ctrl_a[0]
                stored_domains.add(domain)
                report["verified_stored"].append(
                    {"domain": domain, "a": ctrl_a, "aaaa": ctrl_aaaa, "liar_lied": lied}
                )

            if lied:
                report["lies_corrected"].append(
                    {
                        "domain": domain,
                        "liar_a": r["liar_a"],
                        "liar_nx": r["liar_nx"],
                        "control_a": ctrl_a,
                        "control_aaaa": ctrl_aaaa,
                        "liar_looks_like": "sinkhole_or_gov_blockpage"
                        if any(is_blockpage_or_sinkhole(a) for a in r["liar_a"])
                        else "nxdomain_or_empty",
                    }
                )

            if i % 10 == 0 or i == len(targets):
                print(f"… {i}/{len(targets)} stored={len(stored_domains)}", flush=True)

    # Never persist known blockpage IPs even if somehow present
    safe_hosts = []
    for line in host_lines:
        parts = line.split()
        if parts and not line.startswith("#"):
            if is_blockpage_or_sinkhole(parts[0]):
                continue
        safe_hosts.append(line)

    OUT_HOSTS.write_text("\n".join(safe_hosts) + "\n", encoding="utf-8")
    OUT_UNBOUND.write_text("\n".join(unbound_lines) + "\n", encoding="utf-8")
    yml = ["# Generated smart local mapping (clean IPs only)", "customDNS:", "  mapping:"]
    for d, ip in sorted(blocky_map.items()):
        if is_clean_public(ip):
            yml.append(f"    {d}: {ip}")
    if len(yml) == 3:
        yml.append("    # empty")
    OUT_BLOCKY.write_text("\n".join(yml) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"verified_stored={len(report['verified_stored'])} "
        f"lies_corrected={len(report['lies_corrected'])} "
        f"rejected_blockpage={len(report['rejected_blockpage'])} "
        f"unknown={len(report['unknown'])}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
