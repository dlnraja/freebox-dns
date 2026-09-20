#!/usr/bin/env python3
"""
Generate client encrypted-DNS profiles for Freebox OS / phones / browsers.

Outputs under config/clients/generated/:
  - endpoints.json          machine catalog
  - firefox-policies.json   enterprise DoH policies (libre + secure)
  - apple-doh-libre.mobileconfig / apple-doh-secure.mobileconfig
  - android-private-dns.txt
  - windows-doh.ps1
  - README.md

Usage:
  python3 scripts/generate-client-profiles.py
  HOST_IP=192.168.1.71 python3 scripts/generate-client-profiles.py
  # HOST_IP = Freebox VM LAN IP (never Windows PC for production profiles)
"""
from __future__ import annotations

import json
import os
import plistlib
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "clients" / "generated"


def load_host_ip() -> str:
    env_ip = os.environ.get("HOST_IP", "").strip()
    if env_ip:
        return env_ip
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("HOST_IP="):
                return line.split("=", 1)[1].strip() or "127.0.0.1"
    return "127.0.0.1"


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw and raw.isdigit():
        return int(raw)
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{name}="):
                v = line.split("=", 1)[1].strip()
                if v.isdigit():
                    return int(v)
    return default


def apple_mobileconfig(name: str, doh_url: str, server_addrs: list[str]) -> bytes:
    """DNS Settings payload (iOS 14+ / macOS Big Sur+) for DoH."""
    payload_uuid = str(uuid.uuid4()).upper()
    profile_uuid = str(uuid.uuid4()).upper()
    payload = {
        "PayloadContent": [
            {
                "DNSSettings": {
                    "DNSProtocol": "HTTPS",
                    "ServerURL": doh_url,
                    "ServerAddresses": server_addrs,
                },
                "PayloadDescription": f"freebox-dns {name} DoH",
                "PayloadDisplayName": f"freebox-dns {name}",
                "PayloadIdentifier": f"fr.freeboxdns.doh.{name}",
                "PayloadType": "com.apple.dnsSettings.managed",
                "PayloadUUID": payload_uuid,
                "PayloadVersion": 1,
                "ProhibitDisablement": False,
            }
        ],
        "PayloadDescription": f"Encrypted DNS (DoH) → freebox-dns {name}",
        "PayloadDisplayName": f"freebox-dns {name} DoH",
        "PayloadIdentifier": f"fr.freeboxdns.profile.{name}",
        "PayloadRemovalDisallowed": False,
        "PayloadType": "Configuration",
        "PayloadUUID": profile_uuid,
        "PayloadVersion": 1,
    }
    return plistlib.dumps(payload, fmt=plistlib.FMT_XML)


def main() -> int:
    host = load_host_ip()
    modes = {
        "uncensored": {
            "bit": "uncensored",
            "dns": env_int("DNS_LIBRE_PORT", 5356),
            "doh": env_int("DOH_LIBRE_PORT", 8453),
            "dot": env_int("DOT_LIBRE_PORT", 8853),
            "doq": env_int("DOQ_LIBRE_PORT", 8853),
            "note": "No denylist — local hosts then Unbound (anti-censure)",
        },
        "malware": {
            "bit": "malware-free",
            "dns": env_int("DNS_MALWARE_PORT", 5357),
            "doh": env_int("DOH_MALWARE_PORT", 8445),
            "dot": env_int("DOT_MALWARE_PORT", 8855),
            "doq": None,
            "note": "Malware/phishing only — ads still resolve",
        },
        "antipub": {
            "bit": "ads-free",
            "dns": env_int("DNS_ANTIPUB_PORT", 5358),
            "doh": env_int("DOH_ANTIPUB_PORT", 8446),
            "dot": env_int("DOT_ANTIPUB_PORT", 8856),
            "doq": None,
            "note": "Pi-hole + uBlock DNS + anti–anti-adblock (intelligent)",
        },
        "secure": {
            "bit": "threat-local",
            "dns": env_int("DNS_SECURE_PORT", 5354),
            "doh": env_int("DOH_SECURE_PORT", 8444),
            "dot": env_int("DOT_SECURE_PORT", 8854),
            "doq": None,
            "note": "Full: antipub + malware",
        },
    }

    OUT.mkdir(parents=True, exist_ok=True)

    personalities = {}
    for name, m in modes.items():
        doh = f"https://{host}:{m['doh']}/dns-query"
        entry = {
            "bit": m["bit"],
            "plain": f"{host}:{m['dns']}",
            "doh": doh,
            "dot": f"tls://{host}:{m['dot']}",
            "note": m["note"],
        }
        if m.get("doq"):
            entry["doq"] = f"quic://{host}:{m['doq']}"
        else:
            entry["doq"] = None
        personalities[name] = entry

    catalog = {
        "host_ip": host,
        "smart_split": "local_hosts → mode_filter → unbound_forward → world",
        "personalities": personalities,
        "transports": {
            "do53": True,
            "doh": True,
            "dot": True,
            "doq": "uncensored only",
            "dnscrypt_proxy": f"{host}:{env_int('DNSCRYPT_PROXY_PORT', 5359)}",
            "dnscrypt_server": f"{host}:{env_int('DNSCRYPT_LIBRE_PORT', 8443)} (profile dnscrypt-server)",
        },
        "sos_plain": ["9.9.9.10", "194.242.2.2", "94.140.14.140"],
        "cert": "certs/server.crt (self-signed — install/trust on clients for DoH/DoT)",
        "dnscrypt": {
            "proxy": f"{host}:{env_int('DNSCRYPT_PROXY_PORT', 5359)}",
            "quad9_nofilter_stamps": "config/dnscrypt/quad9-nofilter.stamps",
            "local_stamp_file": "config/clients/generated/dnscrypt-stamp.txt",
            "init": "bash scripts/dnscrypt-server-init.sh",
        },
        "freebox_os": {
            "dhcp_dns1_resolver": host,
            "dhcp_dns2_sos": "9.9.9.10",
            "modes_doc": "docs/modes.md",
        },
    }
    (OUT / "endpoints.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    for name, m in modes.items():
        doh = f"https://{host}:{m['doh']}/dns-query"
        firefox = {
            "policies": {
                "DNSOverHTTPS": {
                    "Enabled": True,
                    "ProviderURL": doh,
                    "Locked": False,
                    "Fallback": True,
                }
            }
        }
        (OUT / f"firefox-policies-{name}.json").write_text(
            json.dumps(firefox, indent=2) + "\n", encoding="utf-8"
        )
        (OUT / f"apple-doh-{name}.mobileconfig").write_bytes(
            apple_mobileconfig(name, doh, [host])
        )

    lines = [
        "# Android / custom DoH apps (Nebulo, Intra, RethinkDNS)",
        f"# Host VM: {host}",
        "",
    ]
    for name, m in modes.items():
        lines.append(f"# {name} ({m['bit']}): https://{host}:{m['doh']}/dns-query")
        lines.append(f"#   plain {host}:{m['dns']}  DoT {host}:{m['dot']}")
    lines.append("")
    lines.append("# Stock Android Private DNS needs a hostname — prefer custom DoH apps on LAN.")
    (OUT / "android-private-dns.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    unc = personalities["uncensored"]
    win = f"""# Windows 11 DoH (Admin PowerShell) — uncensored by default
$doh = '{unc["doh"]}'
Add-DnsClientDohServerAddress -ServerAddress '{host}' -DohTemplate $doh -AllowFallbackToUdp $true -AutoUpgrade $true
# Other modes: malware={personalities['malware']['doh']} antipub={personalities['antipub']['doh']} secure={personalities['secure']['doh']}
"""
    (OUT / "windows-doh.ps1").write_text(win, encoding="utf-8")

    rows = ["| Mode | Plain (Do53) | DoH | DoT |", "| --- | --- | --- | --- |"]
    for name, p in personalities.items():
        rows.append(f"| **{name}** | `{p['plain']}` | `{p['doh']}` | `{p['dot']}` |")
    dnscrypt_port = env_int("DNSCRYPT_PROXY_PORT", 5359)
    server_port = env_int("DNSCRYPT_LIBRE_PORT", 8443)
    readme = f"""# Client encrypted DNS profiles (generated)

Host: `{host}`  
Transports: **Do53 · DoH · DoT · DoQ · DNSCrypt** — [docs/encrypted-dns.md](../../../docs/encrypted-dns.md)

{chr(10).join(rows)}

| Extra | Endpoint |
| --- | --- |
| **DoQ** (uncensored) | `quic://{host}:{personalities['uncensored'].get('doq','').split(':')[-1] if personalities['uncensored'].get('doq') else '8853'}` |
| **DNSCrypt proxy** | `{host}:{dnscrypt_port}` (Do53→DNSCrypt→Quad9 nofilter) |
| **DNSCrypt server** | `{host}:{server_port}` / `dnscrypt-stamp.txt` (after `scripts/dnscrypt-server-init.sh`) |

## Freebox OS / Wi-Fi

1. DHCP (après health VM) : DNS1=`9.9.9.10` (SOS), DNS2=`{host}` (**VM Freebox** uncensored `:53` — pas le PC).
2. Choix de mode : coller l’URL DoH du tableau (navigateur / app).
3. iOS/macOS : `apple-doh-<mode>.mobileconfig`.
4. Firefox : `firefox-policies-<mode>.json`.
5. Trust `certs/server.crt` (auto-signé LAN).
6. DNSCrypt : voir [config/dnscrypt/README.md](../../dnscrypt/README.md).

Host `{host}` = IP de la **VM freebox-dns** sur Freebox OS.  
Wi‑Fi : voir docs/wifi-lan.md

Regenerate: `HOST_IP=<vm> python3 scripts/generate-client-profiles.py`
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    # Copy Quad9 nofilter stamps next to generated profiles for clients
    stamps_src = ROOT / "config" / "dnscrypt" / "quad9-nofilter.stamps"
    if stamps_src.is_file():
        (OUT / "quad9-dnscrypt-nofilter.stamps").write_text(
            stamps_src.read_text(encoding="utf-8"), encoding="utf-8"
        )
    print(f"wrote profiles -> {OUT}")
    for name, p in personalities.items():
        print(f"  {name:12} {p['doh']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

