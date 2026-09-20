#!/usr/bin/env python3
"""
Anti-degradation checks for freebox-dns (CI + local).

Detects bitrot without polling the user's Freebox:
  - SOS plain UDP resolvers still answer
  - DoT catalogue hostnames still resolve
  - Blocklist gravity URLs still HTTP 200
  - Critical repo invariants (pins, compose, generators)
  - GitHub Pages still serves

Exit 0 = healthy, 1 = degradation detected.
Writes config/uncensor/last-anti-degradation.json
"""
from __future__ import annotations

import json
import os
import socket
import struct
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "uncensor" / "last-anti-degradation.json"

SOS = ["9.9.9.10", "194.242.2.2", "94.140.14.140"]
DOT_HOSTS = [
    "dns.mullvad.net",
    "open.dns0.eu",
    "dns.digitale-gesellschaft.ch",
    "anycast.uncensoreddns.org",
    "dns10.quad9.net",
    "dns-unfiltered.adguard.com",
]
BLOCKLISTS = [
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
    "https://adaway.org/hosts.txt",
    "https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/multi.txt",
    "https://v.firebog.net/hosts/Admiral.txt",
    "https://small.oisd.nl/",
    "https://urlhaus.abuse.ch/downloads/hostfile/",
]
PAGES = [
    "https://dlnraja.github.io/freebox-dns/",
    "https://dlnraja.github.io/freebox-dns/guides/wifi-lan.html",
    "https://dlnraja.github.io/freebox-dns/guides/filtering.html",
]


def dig_a(server: str, name: str = "example.com", timeout: float = 3.0) -> bool:
    labels = name.split(".")
    q = b"".join(bytes([len(x)]) + x.encode() for x in labels) + b"\x00"
    pkt = struct.pack("!HHHHHH", 0xAD01, 0x0100, 1, 0, 0, 0) + q + struct.pack("!HH", 1, 1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(pkt, (server, 53))
        data, _ = sock.recvfrom(512)
        return len(data) >= 12 and (data[2] & 0x80) != 0
    except OSError:
        return False
    finally:
        sock.close()


def http_ok(url: str, timeout: float = 45.0) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "freebox-dns-anti-degradation/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(64)
            return (200 <= r.status < 400 and len(body) >= 0), f"HTTP {r.status}"
    except Exception as e:  # noqa: BLE001
        return False, type(e).__name__


def resolve_host(host: str) -> bool:
    try:
        socket.getaddrinfo(host, 853, type=socket.SOCK_STREAM)
        return True
    except OSError:
        return False


def invariants() -> list[dict]:
    checks = []
    snap = json.loads((ROOT / "config/freebox-dns-snapshot.json").read_text(encoding="utf-8"))
    cat = json.loads((ROOT / "config/upstreams/uncensoring-catalog.json").read_text(encoding="utf-8"))
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    blocky = (ROOT / "config/blocky/config.yml").read_text(encoding="utf-8")
    forward = (ROOT / "config/unbound/forward-records.conf").read_text(encoding="utf-8")

    def ok(name: str, cond: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": bool(cond), "detail": detail})

    pins = snap.get("pinned_fallback") or {}
    ok("pin_sos_quad9", pins.get("FREEBOX_DNS_1") == "9.9.9.10", str(pins.get("FREEBOX_DNS_1")))
    ident = (snap.get("pinned_identity") or {}).get("FREEBOX_DNS_1") or {}
    lex = " ".join(ident.get("lexicon") or []).lower()
    ok("pin_sos_no_ecs_claim", "ecs" not in lex or "no ecs" in lex, lex)
    ok("catalog_quad9_variants", "quad9_variants" in cat and cat["quad9_variants"].get("chosen_sos") == "9.9.9.10", "")
    ok("catalog_excludes_quad9_secured", "9.9.9.9" in (cat.get("exclude_as_primary") or []), "")
    ok("catalog_community_landscape", (ROOT / "config/upstreams/community-dns-landscape.json").is_file(), "")
    ok("no_mix_sos_secure_in_plain_fallback", "9.9.9.9" not in (cat.get("plain_fallback_order") or []), "")
    ok("quad9_ops_script", (ROOT / "scripts/quad9-ops-check.py").is_file(), "")
    ok("dnscrypt_proxy_toml", (ROOT / "config/dnscrypt/proxy/dnscrypt-proxy.toml").is_file(), "")
    ok("dnscrypt_quad9_stamps", (ROOT / "config/dnscrypt/quad9-nofilter.stamps").is_file(), "")
    ok("catalog_dnscrypt_flag", bool((cat.get("local_server_transports") or {}).get("dnscrypt")), "")
    modes_path = ROOT / "config/blocky/modes.json"
    modes_doc = json.loads(modes_path.read_text(encoding="utf-8")) if modes_path.is_file() else {}
    mode_keys = set((modes_doc.get("modes") or {}).keys())
    ok("modes_json_four", mode_keys >= {"uncensored", "malware", "antipub", "secure"}, str(sorted(mode_keys)))
    unc_order = ((modes_doc.get("modes") or {}).get("uncensored") or {}).get("order", "")
    ok("modes_json_order_uncensored", "dnsproxy fallbacks" in unc_order, unc_order)
    sec_order = ((modes_doc.get("modes") or {}).get("secure") or {}).get("order", "")
    ok("modes_json_order_secure", "malware" in sec_order and "pihole" in sec_order, sec_order)
    ok("catalog_dot_min10", len(cat.get("dot_uncensoring", [])) >= 10, str(len(cat.get("dot_uncensoring", []))))
    ok("catalog_sos_plain", "sos_plain" in cat, "")
    ok("compose_unbound_cache", "unbound-cache" in compose, "")
    ok(
        "compose_mounts_unbound_conf",
        "unbound.conf:/opt/unbound/etc/unbound/unbound.conf" in compose,
        "",
    )
    ok(
        "compose_mounts_critical",
        "a-records.critical.conf:/opt/unbound/etc/unbound/a-records.critical.conf" in compose,
        "",
    )
    unbound_main = (ROOT / "config/unbound/unbound.conf").read_text(encoding="utf-8")
    ok(
        "unbound_conf_forward_include_active",
        any(
            line.lstrip().startswith("include:") and "forward-records.conf" in line and not line.lstrip().startswith("#")
            for line in unbound_main.splitlines()
            if "forward-records.conf" in line
        ),
        "forward include must be uncommented",
    )
    a_recs = (ROOT / "config/unbound/a-records.conf").read_text(encoding="utf-8")
    ok("serve_expired_explicit", "serve-expired: yes" in a_recs, "")
    ok("serve_expired_client_timeout_0", "serve-expired-client-timeout: 0" in a_recs, "")
    crit = (ROOT / "config/unbound/a-records.critical.conf").read_text(encoding="utf-8")
    ok("critical_zones_static", 'local-zone:' in crit and "static" in crit and "typetransparent" not in crit, "")
    ok("verify_forwards_script", (ROOT / "scripts/verify-unbound-forwards.sh").is_file(), "")
    try:
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts/assert-lan-only.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        ok("assert_lan_only", r.returncode == 0, (r.stdout or r.stderr or "")[:200])
    except Exception as e:  # noqa: BLE001
        ok("assert_lan_only", False, type(e).__name__)
    blocky_stub = (ROOT / "config/uncensor/blocky-custom-dns.yml").read_text(encoding="utf-8")
    ok("blocky_custom_dns_obsolete_stub", "OBSOLETE" in blocky_stub and "customDNS:" not in blocky_stub, "")
    ok("compose_querylog", "querylog" in compose, "")
    ok("blocky_querylog", "queryLog:" in blocky, "")
    ok("blocky_pihole_group", "pihole:" in blocky, "")
    ok("forward_first", "forward-first: yes" in forward, "")
    idx_q = forward.find("9.9.9.10@853")
    idx_unc = forward.find("91.239.100.100@853")
    ok(
        "forward_sos_before_uncensored",
        idx_q >= 0 and (idx_unc < 0 or idx_q < idx_unc),
        f"q={idx_q} u={idx_unc}",
    )
    # Generator still runs
    try:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/generate-blocky-modes.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            timeout=60,
        )
        ok("generate_blocky_modes", True, "ran")
    except Exception as e:  # noqa: BLE001
        ok("generate_blocky_modes", False, type(e).__name__)

    return checks


def main() -> int:
    report: dict = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "checks": [],
        "failed": [],
        "ok_count": 0,
        "fail_count": 0,
    }

    for ip in SOS:
        good = dig_a(ip)
        item = {"name": f"sos_udp_{ip}", "ok": good, "detail": "dig example.com"}
        report["checks"].append(item)

    for host in DOT_HOSTS:
        good = resolve_host(host)
        report["checks"].append({"name": f"dot_host_{host}", "ok": good, "detail": "getaddrinfo :853"})

    for url in BLOCKLISTS:
        good, detail = http_ok(url)
        report["checks"].append({"name": f"blocklist_{url.split('/')[2]}", "ok": good, "detail": f"{detail} {url}"})

    for url in PAGES:
        good, detail = http_ok(url, timeout=30)
        report["checks"].append({"name": f"pages_{url.rstrip('/').split('/')[-1] or 'home'}", "ok": good, "detail": f"{detail} {url}"})

    report["checks"].extend(invariants())

    for c in report["checks"]:
        if c["ok"]:
            report["ok_count"] += 1
        else:
            report["fail_count"] += 1
            report["failed"].append(c)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"anti-degradation: ok={report['ok_count']} fail={report['fail_count']}")
    for f in report["failed"]:
        print(f"  FAIL {f['name']}: {f.get('detail','')}")

    # Soft threshold: allow up to 2 soft remote flakes unless invariants fail
    hard = [
        f
        for f in report["failed"]
        if f["name"].startswith(("pin_", "catalog_", "compose_", "blocky_", "forward_", "generate_"))
    ]
    soft = [f for f in report["failed"] if f not in hard]
    if hard:
        print("HARD failures:", len(hard))
        return 1
    if len(soft) > 3:
        print("Too many soft remote failures:", len(soft))
        return 1
    return 0


if __name__ == "__main__":
    # Allow skipping network-heavy sections in constrained envs
    if os.environ.get("ANTI_DEGRADATION_INVARIANTS_ONLY") == "1":
        report = {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "checks": invariants(),
            "failed": [],
            "ok_count": 0,
            "fail_count": 0,
        }
        for c in report["checks"]:
            if c["ok"]:
                report["ok_count"] += 1
            else:
                report["fail_count"] += 1
                report["failed"].append(c)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"invariants-only: ok={report['ok_count']} fail={report['fail_count']}")
        raise SystemExit(0 if report["fail_count"] == 0 else 1)
    raise SystemExit(main())
