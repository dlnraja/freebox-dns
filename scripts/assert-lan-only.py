#!/usr/bin/env python3
"""Fail if freebox-dns would bind DNS on a public / all-interfaces address."""
from __future__ import annotations

import ipaddress
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def is_lan(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip.strip())
    except ValueError:
        return False
    return bool(
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_unique_local  # IPv6 ULA
    )


def main() -> int:
    errors: list[str] = []

    for name in (
        "docker-compose.yml",
        "docker-compose.prod.yml",
        "docker-compose.ipv6.yml",
        "docker-compose.arm64.yml",
    ):
        path = ROOT / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        # Host publish like "0.0.0.0:53:" or '":::53:'
        for m in re.finditer(r'["\']?(0\.0\.0\.0|::)(?::\d+)?:', text):
            # allow comments mentioning 0.0.0.0
            line = text[: m.start()].splitlines()[-1] if m.start() else ""
            if line.lstrip().startswith("#"):
                continue
            # real ports: lines contain HOST_IP or look like publish
            full_line = [ln for ln in text.splitlines() if m.group(0).rstrip(":") in ln or "0.0.0.0" in ln]
            for ln in text.splitlines():
                if re.search(r'["\']0\.0\.0\.0:', ln) or re.search(r'["\']::\d', ln):
                    if not ln.lstrip().startswith("#"):
                        errors.append(f"{name}: public bind publish → {ln.strip()}")

    # .env / .env.example HOST_IP must be LAN if set
    for env_name in (".env", ".env.example"):
        env = ROOT / env_name
        if not env.is_file():
            continue
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("HOST_IP=") and not line.strip().startswith("#"):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val and not is_lan(val):
                    errors.append(f"{env_name}: HOST_IP={val} is not a private/LAN address")
            if line.startswith("HOST_IP6=") and not line.strip().startswith("#"):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val and not is_lan(val):
                    errors.append(f"{env_name}: HOST_IP6={val} is not private/ULA")

    # Windows runner must not default to 0.0.0.0
    win = (ROOT / "scripts/windows-native/Run-DnsResolver.ps1").read_text(encoding="utf-8")
    if re.search(r'\$ListenAddr\s*=\s*"0\.0\.0\.0"', win):
        errors.append("Run-DnsResolver.ps1 defaults ListenAddr to 0.0.0.0 (all interfaces)")
    if "ForcePublicBind" not in win and "0.0.0.0" in win:
        # still allow documented opt-in later
        pass

    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    if "${HOST_IP}" not in compose:
        errors.append("docker-compose.yml missing ${HOST_IP} port binds")
    if re.search(r'ports:\s*\n\s*-\s*["\']?\d+:', compose):
        errors.append("docker-compose.yml has unbound host port (missing HOST_IP)")

    if errors:
        print("assert-lan-only FAIL:")
        for e in errors:
            print(" ", e)
        return 1

    print("assert-lan-only: OK (LAN bind only)")
    return 0


if __name__ == "__main__":
    # Allow CI override only for intentional lab on loopback
    if os.environ.get("ALLOW_PUBLIC_DNS_BIND") == "1":
        print("assert-lan-only: SKIP (ALLOW_PUBLIC_DNS_BIND=1)")
        sys.exit(0)
    sys.exit(main())
