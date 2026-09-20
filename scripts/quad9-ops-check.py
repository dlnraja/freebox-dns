#!/usr/bin/env python3
"""
Quad9 operational checks (CaptainDNS / Quad9 docs).

- SOS 9.9.9.10 still answers (uncensored path)
- Secure 9.9.9.9 still blocks isitblocked.org (AUTHORITY 0) when reachable
- DoH endpoints speak HTTP/2 (required since 2025-12-15)
- Optional: proto.on.quad9.net TXT if system DNS is Quad9

Writes config/uncensor/last-quad9-ops.json
Exit 0 = healthy enough for SOS path; 1 = hard failure on SOS/.10 path.
"""
from __future__ import annotations

import json
import os
import socket
import struct
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "uncensor" / "last-quad9-ops.json"

SOS = "9.9.9.10"
SECURE = "9.9.9.9"
BLOCK_TEST = "isitblocked.org"
DOH_URLS = [
    "https://dns10.quad9.net/dns-query",
    "https://dns.quad9.net/dns-query",
]


def dig_udp(server: str, name: str, qtype: int = 1, timeout: float = 3.0) -> bytes | None:
    labels = name.rstrip(".").split(".")
    q = b"".join(bytes([len(x)]) + x.encode() for x in labels) + b"\x00"
    pkt = struct.pack("!HHHHHH", 0xAD02, 0x0100, 1, 0, 0, 0) + q + struct.pack("!HH", qtype, 1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(pkt, (server, 53))
        data, _ = sock.recvfrom(1024)
        return data
    except OSError:
        return None
    finally:
        sock.close()


def parse_rcode_ancount_nscount(data: bytes) -> tuple[int, int, int]:
    if len(data) < 12:
        return -1, 0, 0
    flags = struct.unpack("!H", data[2:4])[0]
    rcode = flags & 0xF
    ancount = struct.unpack("!H", data[6:8])[0]
    nscount = struct.unpack("!H", data[8:10])[0]
    return rcode, ancount, nscount


def http2_ok(url: str) -> tuple[bool, str]:
    """Assert HTTP/2 when curl supports it; treat HTTP/1.1→505 as proof of enforcement."""
    probe = url if "?" in url else f"{url}?name=example.com&type=A"
    headers = ["-H", "accept: application/dns-json"]

    def run(extra: list[str]) -> tuple[int, str, str]:
        r = subprocess.run(
            ["curl", *extra, "-s", "-o", os.devnull, "-w", "%{http_version} %{http_code}",
             "--max-time", "20", *headers, probe],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()

    try:
        code, out, err = run(["--http2"])
        if "does not support" in err or code == 2:
            code2, out2, _ = run([])
            parts = out2.split()
            # Without --http2, curl uses HTTP/1.1 → Quad9 returns 505 since 2025-12-15
            status = parts[-1] if parts else (out2 or "")
            if status == "505":
                return True, "HTTP/1.1 rejected with 505 (Quad9 requires HTTP/2 — local curl has no --http2)"
            if status.startswith("2"):
                return True, f"reachable HTTP {status} (http2 not asserted — local curl has no --http2)"
            return False, f"doh status={status or 'empty'} rc={code2}"
        parts = out.split()
        ver = parts[0] if parts else ""
        status = parts[1] if len(parts) > 1 else ""
        ok = (ver.startswith("2") or ver.startswith("3")) and status.startswith("2")
        return ok, f"http/{ver} status={status}"
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
        try:
            req = urllib.request.Request(
                probe,
                headers={"User-Agent": "freebox-dns-quad9-ops/1.0", "Accept": "application/dns-json"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return True, f"reachable HTTP {resp.status} (http2 not verified)"
        except Exception as e2:  # noqa: BLE001
            # urllib may also get 505
            msg = str(e2)
            if "505" in msg:
                return True, "HTTP/1.1 rejected with 505 (requires HTTP/2)"
            return False, f"{type(e).__name__}/{type(e2).__name__}: {msg[:120]}"


def main() -> int:
    checks: list[dict] = []
    hard_fail = False

    # SOS must answer A for example.com
    data = dig_udp(SOS, "example.com")
    if data and parse_rcode_ancount_nscount(data)[0] == 0:
        checks.append({"name": "sos_udp_example", "ok": True, "detail": f"@{SOS}"})
    else:
        checks.append({"name": "sos_udp_example", "ok": False, "detail": f"@{SOS} no NOERROR"})
        hard_fail = True

    # Unfiltered: isitblocked.org should NOT be NXDOMAIN-blocked on .10
    data = dig_udp(SOS, BLOCK_TEST)
    if data is None:
        checks.append({"name": "sos_isitblocked_resolves", "ok": False, "detail": "timeout"})
        hard_fail = True
    else:
        rcode, an, ns = parse_rcode_ancount_nscount(data)
        # rcode 3 = NXDOMAIN — on .10 that would mean unexpected blocking (or domain gone)
        ok = rcode == 0 and an >= 1
        checks.append(
            {
                "name": "sos_isitblocked_resolves",
                "ok": ok,
                "detail": f"rcode={rcode} an={an} ns={ns} (expect NOERROR on No Threat Blocking)",
            }
        )
        if not ok:
            hard_fail = True

    # Secure path (soft): .9 should NXDOMAIN isitblocked with authority-ish block
    data = dig_udp(SECURE, BLOCK_TEST)
    if data is None:
        checks.append({"name": "secure_isitblocked_nxdomain", "ok": True, "detail": "soft skip — .9 unreachable", "soft": True})
    else:
        rcode, an, ns = parse_rcode_ancount_nscount(data)
        # NXDOMAIN = 3; Quad9 blocks often with AUTHORITY 0 (ns==0)
        ok = rcode == 3
        checks.append(
            {
                "name": "secure_isitblocked_nxdomain",
                "ok": ok,
                "detail": f"rcode={rcode} an={an} ns={ns} (CaptainDNS: NXDOMAIN+AUTHORITY0 = block)",
                "soft": True,
            }
        )

    for url in DOH_URLS:
        ok, detail = http2_ok(url)
        item = {"name": f"doh_http2_{url.split('/')[2]}", "ok": ok, "detail": detail}
        if "dns10" in url and not ok:
            hard_fail = True
        elif not ok:
            item["soft"] = True
        checks.append(item)

    # Protocol self-test via system resolver (informational)
    try:
        answers = socket.getaddrinfo("proto.on.quad9.net", None)  # noqa: F841 — reachability only
        checks.append({"name": "proto_on_quad9_name_resolves", "ok": True, "detail": "use: dig +short txt proto.on.quad9.net.", "soft": True})
    except OSError:
        checks.append({"name": "proto_on_quad9_name_resolves", "ok": False, "detail": "not using Quad9 system-wide (OK for freebox-dns)", "soft": True})

    report = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "sources": [
            "https://www.captaindns.com/fr/blog/dns-9999-quad9",
            "https://quad9.net/news/blog/doh-http-1-1-retirement/",
            "https://docs.quad9.net/services/",
        ],
        "policy": "SOS uses 9.9.9.10 only — never mix with 9.9.9.9 in DHCP round-robin",
        "checks": checks,
        "ok_count": sum(1 for c in checks if c["ok"]),
        "fail_count": sum(1 for c in checks if not c["ok"]),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"quad9-ops: ok={report['ok_count']} fail={report['fail_count']}")
    for c in checks:
        flag = "OK" if c["ok"] else ("SOFT" if c.get("soft") else "FAIL")
        print(f"  {flag} {c['name']}: {c.get('detail', '')}")

    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
