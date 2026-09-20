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
  HOST_IP=192.168.1.15 python3 scripts/generate-client-profiles.py
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
    doh_libre = env_int("DOH_LIBRE_PORT", 8453)
    doh_secure = env_int("DOH_SECURE_PORT", 8444)
    dot_libre = env_int("DOT_LIBRE_PORT", 8853)
    dot_secure = env_int("DOT_SECURE_PORT", 8854)
    doq_libre = env_int("DOQ_LIBRE_PORT", 8853)
    dns_libre = env_int("DNS_LIBRE_PORT", 5356)
    dns_secure = env_int("DNS_SECURE_PORT", 5354)

    libre_doh = f"https://{host}:{doh_libre}/dns-query"
    secure_doh = f"https://{host}:{doh_secure}/dns-query"
    # Android Private DNS needs a hostname:port is NOT supported — document IP:port via apps
    # that support custom DoT (Intra, Nebulo) or use :853 in prod
    libre_dot = f"{host}:{dot_libre}"
    secure_dot = f"{host}:{dot_secure}"
    libre_doq = f"quic://{host}:{doq_libre}"

    OUT.mkdir(parents=True, exist_ok=True)

    catalog = {
        "host_ip": host,
        "personalities": {
            "libre": {
                "bit": "uncensored",
                "plain": f"{host}:{dns_libre}",
                "doh": libre_doh,
                "dot": f"tls://{libre_dot}",
                "doq": libre_doq,
                "note": "No ads filter — anti-censure + anti-lie hosts",
            },
            "secure": {
                "bit": "threat-local",
                "plain": f"{host}:{dns_secure}",
                "doh": secure_doh,
                "dot": f"tls://{secure_dot}",
                "doq": None,
                "note": "Pi-hole + uBlock + anti-adblock + malware",
            },
        },
        "sos_plain": ["91.239.100.100", "185.95.218.42", "9.9.9.10"],
        "cert": "certs/server.crt (self-signed — install/trust on clients for DoH/DoT)",
        "freebox_os": {
            "dhcp_dns1_sos": "91.239.100.100",
            "dhcp_dns2_vm": host,
            "app_doh_libre": libre_doh,
            "app_doh_secure": secure_doh,
        },
    }
    (OUT / "endpoints.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    # Firefox enterprise policies (about:policies)
    firefox = {
        "policies": {
            "DNSOverHTTPS": {
                "Enabled": True,
                "ProviderURL": libre_doh,
                "Locked": False,
                "Fallback": True,
            }
        }
    }
    (OUT / "firefox-policies-libre.json").write_text(json.dumps(firefox, indent=2) + "\n", encoding="utf-8")
    firefox_sec = {
        "policies": {
            "DNSOverHTTPS": {
                "Enabled": True,
                "ProviderURL": secure_doh,
                "Locked": False,
                "Fallback": True,
            }
        }
    }
    (OUT / "firefox-policies-secure.json").write_text(
        json.dumps(firefox_sec, indent=2) + "\n", encoding="utf-8"
    )

    (OUT / "apple-doh-libre.mobileconfig").write_bytes(
        apple_mobileconfig("libre", libre_doh, [host])
    )
    (OUT / "apple-doh-secure.mobileconfig").write_bytes(
        apple_mobileconfig("secure", secure_doh, [host])
    )

    android = f"""# Android Private DNS
# Stock Android Private DNS only accepts a hostname (no IP:port).
# Options:
#  1) Prod Freebox VM with DoT on :853 + local name freebox-dns.local (trust cert)
#  2) Use Nebulo / RethinkDNS / Intra with custom DoH:
#       Libre:  {libre_doh}
#       Secure: {secure_doh}
#  3) DoT custom apps:
#       Libre:  {libre_dot}
#       Secure: {secure_dot}
#
# Freebox mobile app: set DHCP DNS to VM; browsers use DoH URLs above.
"""
    (OUT / "android-private-dns.txt").write_text(android, encoding="utf-8")

    win = f"""# Windows 11 DoH (Admin PowerShell) — libre personality
# Requires trusting certs/server.crt in "Trusted Root" for the LAN IP.
$doh = '{libre_doh}'
Add-DnsClientDohServerAddress -ServerAddress '{host}' -DohTemplate $doh -AllowFallbackToUdp $true -AutoUpgrade $true
Set-DnsClientServerAddress -InterfaceAlias (Get-NetAdapter | ? Status -eq 'Up' | select -First 1 -ExpandProperty Name) -ServerAddresses '{host}'
# Secure personality template: {secure_doh}
"""
    (OUT / "windows-doh.ps1").write_text(win, encoding="utf-8")

    readme = f"""# Client encrypted DNS profiles (generated)

Host: `{host}`

| Personality | Plain | DoH | DoT | DoQ |
| --- | --- | --- | --- | --- |
| **libre** | `{host}:{dns_libre}` | `{libre_doh}` | `tls://{libre_dot}` | `{libre_doq}` |
| **secure** | `{host}:{dns_secure}` | `{secure_doh}` | `tls://{secure_dot}` | — |

## Freebox OS / app

1. DHCP (après health VM) : DNS1=`91.239.100.100`, DNS2=`{host}` (ou inverse seulement si double check OK).
2. Navigateurs / Freebox app Web : coller l’URL DoH **libre** ou **secure**.
3. iOS/macOS : installer `apple-doh-libre.mobileconfig` (Réglages → Profil).
4. Firefox : `about:policies` ← `firefox-policies-libre.json`.
5. Trust `certs/server.crt` (auto-signé LAN).

Regenerate: `python3 scripts/generate-client-profiles.py`
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print(f"wrote profiles -> {OUT}")
    print(f"  DoH libre  {libre_doh}")
    print(f"  DoH secure {secure_doh}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
