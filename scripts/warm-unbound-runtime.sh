#!/usr/bin/env bash
# Warm Unbound runtime cache so serve-expired has answers when all DoT die.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

HOST_IP="${HOST_IP:-127.0.0.1}"
# Optional .env HOST_IP (ignore BOM / exotic chars — do not `source`)
if [[ -f .env ]]; then
  line="$(grep -E '^HOST_IP=' .env | tail -1 | tr -d '\r' || true)"
  if [[ -n "$line" ]]; then
    HOST_IP="${line#HOST_IP=}"
    HOST_IP="${HOST_IP%%#*}"
    HOST_IP="$(echo "$HOST_IP" | tr -d '[:space:]\"' )"
  fi
fi
HOST_IP="${HOST_IP:-127.0.0.1}"

TARGETS=(
  example.com github.com raw.githubusercontent.com api.github.com
  registry-1.docker.io auth.docker.io cloud.debian.org
  dns.mullvad.net dns10.quad9.net
  wikipedia.org fr.wikipedia.org proton.me signal.org
)

echo "=== warm local cache via dns-libre @${HOST_IP}:53 ==="
ok=0
for d in "${TARGETS[@]}"; do
  if command -v dig >/dev/null 2>&1; then
    if dig @"$HOST_IP" "$d" A +time=2 +tries=1 +short >/dev/null 2>&1; then
      echo "  OK $d"
      ok=$((ok + 1))
      continue
    fi
  fi
  if python3 -c "
import socket, struct, sys
name, server = '$d', '$HOST_IP'
q = b''.join(bytes([len(x)]) + x.encode() for x in name.split('.')) + b'\x00'
pkt = struct.pack('!HHHHHH', 0x99, 0x100, 1, 0, 0, 0) + q + struct.pack('!HH', 1, 1)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(2)
s.sendto(pkt, (server, 53))
data, _ = s.recvfrom(512)
s.close()
sys.exit(0 if len(data) >= 12 and (data[2] & 0x80) else 1)
" 2>/dev/null; then
    echo "  OK $d"
    ok=$((ok + 1))
  else
    echo "  FAIL $d"
  fi
done
echo "warmed ${ok}/${#TARGETS[@]} names into local Unbound/edge cache"
