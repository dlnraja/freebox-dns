#!/usr/bin/env python3
"""CI product invariants: DHCP DNS1=HOST_IP, DNS2=SOS, lan-only, modes dhcp note."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []

    dhcp = json.loads((ROOT / "config/freebox/dhcp-dns.json").read_text(encoding="utf-8"))
    prod = dhcp.get("prod_recommended") or {}
    if prod.get("dhcp_dns_primary") != "${HOST_IP}":
        errors.append(f"dhcp-dns.json primary={prod.get('dhcp_dns_primary')!r} want ${{HOST_IP}}")
    if prod.get("dhcp_dns_secondary") != "9.9.9.10":
        errors.append(f"dhcp-dns.json secondary={prod.get('dhcp_dns_secondary')!r} want 9.9.9.10")

    man = json.loads((ROOT / "packaging/freebox-vm/manifest.json").read_text(encoding="utf-8"))
    rec = man.get("dhcp_recommended") or {}
    if rec.get("dns1") != "HOST_IP":
        errors.append(f"manifest dns1={rec.get('dns1')!r} want HOST_IP")
    if rec.get("dns2") != "9.9.9.10":
        errors.append(f"manifest dns2={rec.get('dns2')!r} want 9.9.9.10")

    modes = json.loads((ROOT / "config/blocky/modes.json").read_text(encoding="utf-8"))
    mdh = modes.get("dhcp") or {}
    if "HOST_IP" not in str(mdh.get("dns1", "")):
        errors.append("modes.json dhcp.dns1 must mention HOST_IP")
    if mdh.get("dns2_sos") != "9.9.9.10" and "9.9.9.10" not in str(mdh.get("dns2", "")):
        errors.append("modes.json dhcp must list SOS 9.9.9.10 as dns2")

    # Docs / site: steady-state must not recommend DNS1=9.9.9.10 alone
    bad_patterns = [
        (ROOT / "docs/wifi-lan.md", r"DNS1\s*=\s*`?9\.9\.9\.10"),
        (ROOT / "docs/modes.md", r"DNS1\s*\|\s*SOS"),
        (ROOT / "site/guides/wifi-lan.html", r"DNS1\s*=\s*9\.9\.9\.10"),
        (ROOT / "site/guides/usage.html", r"<td>DNS1</td><td><code>9\.9\.9\.10</code>"),
    ]
    for path, pat in bad_patterns:
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if re.search(pat, text):
                errors.append(f"stale DNS1=SOS recommendation in {path.relative_to(ROOT)}")

    # Positive markers
    wifi = (ROOT / "docs/wifi-lan.md").read_text(encoding="utf-8")
    if "DNS1" in wifi and "9.9.9.10" in wifi and "IP_RESOLVEUR" not in wifi and "résolveur" not in wifi.lower():
        # soft: just ensure DNS2 SOS mentioned near 9.9.9.10
        if "DNS2" not in wifi:
            errors.append("docs/wifi-lan.md missing DNS2")

    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/assert-lan-only.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        errors.append("assert-lan-only failed: " + (r.stdout or r.stderr or "")[:300])

    if errors:
        print("ci-assert-product FAIL:")
        for e in errors:
            print(" ", e)
        return 1
    print("ci-assert-product: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
