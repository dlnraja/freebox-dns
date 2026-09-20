#!/usr/bin/env python3
"""
OONI Web Connectivity — lite (DNS + HTTP blockpage fingerprint).

Inspired by OONI Probe Web Connectivity (see Korben / ooni.org):
  1) DNS layer   — already handled by ooni-like-anti-lie.py
  2) TCP/HTTP    — connect to consensus IPs with Host/SNI = domain
  3) Detect      — gov blockpages (ANJ / DGCCRF) via redirect / body / title

Does NOT implement HTTP invalid request line or NDT (out of DNS scope).
Risks: https://ooni.org/about/risks/ — local LAN use only.

Usage (after ooni-like-anti-lie.py):
  python3 scripts/web-connectivity-lite.py
"""
from __future__ import annotations

import json
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNC = ROOT / "config" / "uncensor"
SIG = json.loads((UNC / "sinkhole-signatures.json").read_text(encoding="utf-8"))
HOSTS = UNC / "hosts.generated"
OUT = UNC / "last-web-connectivity.json"
WORKERS = 16

BLOCKPAGE_IPS = set(SIG.get("government_blockpage_ips") or [])
BLOCKPAGE_NAMES = {n.lower().rstrip(".") for n in (SIG.get("government_blockpage_names") or [])}
HTTP_MARKERS = [m.lower() for m in (SIG.get("http_blockpage_markers") or [])]


def load_domain_ips() -> dict[str, list[str]]:
    """domain -> list of IPv4 from hosts.generated (skip IPv6 for HTTP Host checks)."""
    mapping: dict[str, list[str]] = {}
    if not HOSTS.exists():
        return mapping
    for line in HOSTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        ip, domain = parts[0], parts[1].lower()
        if ":" in ip:  # skip AAAA for simple HTTP probe
            continue
        if ip in BLOCKPAGE_IPS:
            continue
        mapping.setdefault(domain, [])
        if ip not in mapping[domain]:
            mapping[domain].append(ip)
    return mapping


def looks_like_blockpage(url: str, headers: dict[str, str], body: str) -> str | None:
    loc = (headers.get("Location") or headers.get("location") or "").lower()
    for name in BLOCKPAGE_NAMES:
        if name in loc or name in url.lower():
            return f"redirect_or_url:{name}"
    low = body.lower()[:8000]
    for m in HTTP_MARKERS:
        if m and m in low:
            return f"body:{m}"
    for name in BLOCKPAGE_NAMES:
        if name in low:
            return f"body_host:{name}"
    return None


def http_probe(domain: str, ip: str) -> dict:
    """GET http://ip/ with Host: domain — detect FR gov blockpage fingerprints."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    result = {
        "domain": domain,
        "ip": ip,
        "ok": False,
        "blockpage": None,
        "status": None,
        "final_url": None,
        "error": None,
    }
    # Prefer HTTPS then HTTP (many sites redirect)
    for scheme in ("https", "http"):
        url = f"{scheme}://{ip}/"
        req = urllib.request.Request(
            url,
            headers={
                "Host": domain,
                "User-Agent": "freebox-dns-web-connectivity-lite/1.0",
                "Accept": "text/html,*/*",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=6, context=ctx if scheme == "https" else None) as resp:
                body = resp.read(12000).decode("utf-8", errors="replace")
                headers = {k: v for k, v in resp.headers.items()}
                result["status"] = getattr(resp, "status", None) or resp.getcode()
                result["final_url"] = resp.geturl()
                result["ok"] = True
                bp = looks_like_blockpage(result["final_url"] or url, headers, body)
                if bp:
                    result["blockpage"] = bp
                return result
        except urllib.error.HTTPError as e:
            body = e.read(12000).decode("utf-8", errors="replace") if e.fp else ""
            headers = {k: v for k, v in (e.headers.items() if e.headers else [])}
            result["status"] = e.code
            result["final_url"] = e.url if hasattr(e, "url") else url
            result["ok"] = True
            bp = looks_like_blockpage(result["final_url"] or url, headers, body)
            if bp:
                result["blockpage"] = bp
                return result
            # non-blockpage HTTP error — still counted as reachable
            return result
        except Exception as e:
            result["error"] = f"{scheme}:{type(e).__name__}:{e}"
            continue
    return result


def main() -> int:
    mapping = load_domain_ips()
    if not mapping:
        print("WARN: no hosts.generated IPv4 — run ooni-like-anti-lie.py first", file=sys.stderr)
        OUT.write_text(json.dumps({"error": "no_hosts"}, indent=2), encoding="utf-8")
        return 1

    jobs = [(d, ip) for d, ips in mapping.items() for ip in ips[:2]]
    print(f"web-connectivity-lite domains={len(mapping)} probes={len(jobs)}", flush=True)

    report = {
        "inspired_by": [
            "https://ooni.org/nettest/web-connectivity/",
            "https://korben.info/ooni-probe-mesurer-niveau-de-manipulation-surveillance-censure-de-internet.html",
        ],
        "layers": ["dns(local hosts)", "tcp/http fingerprint"],
        "clean": [],
        "http_blockpage": [],
        "unreachable": [],
    }

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(http_probe, d, ip): (d, ip) for d, ip in jobs}
        done = 0
        for f in as_completed(futs):
            done += 1
            r = f.result()
            if r.get("blockpage"):
                report["http_blockpage"].append(r)
            elif r.get("ok"):
                report["clean"].append({"domain": r["domain"], "ip": r["ip"], "status": r["status"]})
            else:
                report["unreachable"].append(r)
            if done % 20 == 0 or done == len(jobs):
                print(
                    f"… {done}/{len(jobs)} "
                    f"blockpage={len(report['http_blockpage'])} "
                    f"clean={len(report['clean'])}",
                    flush=True,
                )

    # If HTTP shows gov blockpage on a stored IP → strip from hosts.generated
    bad_keys = {(x["domain"], x["ip"]) for x in report["http_blockpage"]}
    stripped = 0
    if bad_keys and HOSTS.exists():
        keep = []
        for line in HOSTS.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) >= 2 and not line.startswith("#"):
                if (parts[1].lower(), parts[0]) in bad_keys:
                    stripped += 1
                    continue
            keep.append(line)
        if stripped:
            HOSTS.write_text("\n".join(keep) + "\n", encoding="utf-8")

    report["stripped_from_hosts"] = stripped
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"http_blockpage={len(report['http_blockpage'])} "
        f"clean={len(report['clean'])} "
        f"unreachable={len(report['unreachable'])} "
        f"stripped={stripped}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
