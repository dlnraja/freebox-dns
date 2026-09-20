#!/usr/bin/env python3
"""Shared Freebox/Blocky/Unbound config lint for CI (no live Freebox)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        import yaml  # type: ignore
    except ImportError:
        print("PyYAML required: pip install pyyaml", file=sys.stderr)
        return 2

    errors: list[str] = []

    def fail(msg: str) -> None:
        errors.append(msg)

    try:
        json.loads((ROOT / "config/freebox/dhcp-dns.json").read_text(encoding="utf-8"))
        json.loads((ROOT / "config/freebox-dns-snapshot.json").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        fail(f"JSON parse: {e}")

    for y in (
        "config/blocky/config.yml",
        "config/blocky/config-malware.yml",
        "config/blocky/config-antipub.yml",
        "config/dnsproxy/dns-libre.yaml",
        "cloud-init/pi-user-data.yaml",
        "cloud-init/freebox-vm-user-data.yaml",
    ):
        try:
            yaml.safe_load((ROOT / y).read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            fail(f"YAML {y}: {e}")

    fr = (ROOT / "config/unbound/forward-records.conf").read_text(encoding="utf-8")
    for must in (
        "dns.mullvad.net",
        "open.dns0.eu",
        "digitale-gesellschaft",
        "uncensoreddns",
        "applied-privacy",
        "libredns",
        "lavate",
        "public-rdns",
        "radeksprta",
        "controld",
        "adguard",
        "9.9.9.10",
        "forward-first: yes",
    ):
        if must not in fr:
            fail(f"forward-records missing {must}")

    by = (ROOT / "config/blocky/config.yml").read_text(encoding="utf-8")
    for must in ("denylists", "queryLog:", "pihole:", "ublock:", "anti_adblock:"):
        if must not in by:
            fail(f"blocky config.yml missing {must}")

    for f in (
        "config/blocky/lists/anti-adblock.txt",
        "config/blocky/lists/allowlist.txt",
        "docs/lan-only.md",
        "config/dnscrypt/proxy/dnscrypt-proxy.toml",
        "config/dnscrypt/quad9-nofilter.stamps",
    ):
        if not (ROOT / f).is_file():
            fail(f"missing {f}")

    snap = json.loads((ROOT / "config/freebox-dns-snapshot.json").read_text(encoding="utf-8"))
    if snap.get("local_lexicon", {}).get("dns_libre", {}).get("bit") != "uncensored":
        fail("snapshot dns_libre bit")
    if snap.get("local_lexicon", {}).get("dns_secure", {}).get("bit") != "threat-local":
        fail("snapshot dns_secure bit")

    cat = json.loads((ROOT / "config/upstreams/uncensoring-catalog.json").read_text(encoding="utf-8"))
    if len(cat.get("dot_uncensoring", [])) < 10:
        fail("catalog dot_uncensoring < 10")
    if "sos_plain" not in cat:
        fail("catalog missing sos_plain")
    if not (cat.get("local_server_transports") or {}).get("dnscrypt"):
        fail("catalog dnscrypt flag")

    man = json.loads((ROOT / "packaging/freebox-vm/manifest.json").read_text(encoding="utf-8"))
    if man.get("dhcp_recommended", {}).get("dns1") != "HOST_IP":
        fail("manifest dns1")
    if man.get("dhcp_recommended", {}).get("dns2") != "9.9.9.10":
        fail("manifest dns2")

    dhcp = json.loads((ROOT / "config/freebox/dhcp-dns.json").read_text(encoding="utf-8"))
    prod = dhcp.get("prod_recommended") or {}
    if prod.get("dhcp_dns_primary") != "${HOST_IP}":
        fail("dhcp-dns primary")
    if prod.get("dhcp_dns_secondary") != "9.9.9.10":
        fail("dhcp-dns secondary")

    env = (ROOT / ".env.example").read_text(encoding="utf-8")
    for must in ("DOH_LIBRE_PORT=8453", "DOH_SECURE_PORT=8444", "DNSCRYPT_PROXY_PORT=5359"):
        if must not in env:
            fail(f".env.example missing {must}")

    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    for must in ("HOST_IP", "dnscrypt-proxy", "querylog", "unbound-cache"):
        if must not in compose:
            fail(f"compose missing {must}")

    # Blocky generator drift
    subprocess.check_call([sys.executable, str(ROOT / "scripts/generate-blocky-modes.py")], cwd=ROOT)
    diff = subprocess.run(
        [
            "git",
            "diff",
            "--exit-code",
            "--",
            "config/blocky/config.yml",
            "config/blocky/config-malware.yml",
            "config/blocky/config-antipub.yml",
            "config/blocky/modes.json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if diff.returncode != 0:
        fail("Blocky YAML drifted — run: python3 scripts/generate-blocky-modes.py && commit")
        if diff.stdout:
            print(diff.stdout[:2000])

    # Product + lan-only
    for script in ("scripts/ci-assert-product.py", "scripts/assert-lan-only.py"):
        r = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            fail(f"{script}: {(r.stdout or r.stderr or '')[:400]}")

    if errors:
        print("ci-conf-lint FAIL:")
        for e in errors:
            print(" ", e)
        return 1
    print("ci-conf-lint: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
