#!/usr/bin/env python3
"""Pull latest, recreate Unbound with local-first mounts, warm cache, verify."""
from __future__ import annotations

import socket
import struct
import time

import paramiko

HOST = "192.168.1.71"
USER = "debian"
PASS = "freeboxdns"


def dig(server: str, name: str, timeout: float = 3.0) -> bool:
    labels = name.split(".")
    q = b"".join(bytes([len(x)]) + x.encode() for x in labels) + b"\x00"
    pkt = struct.pack("!HHHHHH", 0x42, 0x100, 1, 0, 0, 0) + q + struct.pack("!HH", 1, 1)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(pkt, (server, 53))
        data, _ = s.recvfrom(512)
        return len(data) >= 12 and (data[2] & 0x80) != 0
    except OSError as e:
        print(f"  FAIL @{server} {name}: {e}")
        return False
    finally:
        s.close()


def main() -> int:
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PASS, timeout=20, allow_agent=False, look_for_keys=False)
    base = "/opt/freebox-dns"
    cmds = [
        f"cd {base} && sudo git fetch origin && sudo git reset --hard origin/main",
        f"cd {base} && COMPOSE='sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.arm64.yml' "
        f"&& $COMPOSE up -d --force-recreate unbound "
        f"&& sleep 5 && $COMPOSE up -d dns-libre dns-malware dns-antipub dns-secure",
        f"cd {base} && sudo python3 scripts/warm-local-cache.py || true",
        f"cd {base} && sudo bash scripts/warm-unbound-runtime.sh || true",
        f"sudo docker exec dns-unbound sh -c 'grep -E \"serve-expired:|include:.*critical|forward-first\" "
        f"/opt/unbound/etc/unbound/a-records.conf /opt/unbound/etc/unbound/forward-records.conf | head -20'",
        f"sudo docker exec dns-unbound sh -c 'wc -l /opt/unbound/etc/unbound/a-records.critical.conf; "
        f"head -8 /opt/unbound/etc/unbound/a-records.critical.conf'",
        f"sudo docker exec dns-unbound sh -c 'ls -la /opt/unbound/etc/unbound/var | head -10'",
    ]
    for cmd in cmds:
        print("===", cmd[:90])
        _, o, e = c.exec_command(cmd, timeout=300)
        code = o.channel.recv_exit_status()
        print(o.read().decode()[-2000:])
        err = e.read().decode()
        if err.strip():
            print("ERR", err[-800:])
        print("exit", code)
    c.close()
    print("=== PC verify local names via VM ===")
    for name in ("github.com", "example.com", "dns.mullvad.net", "mafreebox.freebox.fr"):
        print(f"  {'OK' if dig(HOST, name) else 'FAIL'} {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
