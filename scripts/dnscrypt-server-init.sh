#!/usr/bin/env bash
# One-shot init for LAN DNSCrypt server (jedisct1/dnscrypt-server).
# Safe: does not touch Freebox DHCP or host :53.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
if [[ -f .env ]]; then set -a; # shellcheck source=/dev/null
  source .env; set +a; fi

HOST_IP="${HOST_IP:?Set HOST_IP in .env (Freebox VM LAN IP)}"
PORT="${DNSCRYPT_LIBRE_PORT:-8443}"
PROVIDER="${DNSCRYPT_PROVIDER_NAME:-freebox-dns.local}"
KEYS_DIR="${ROOT}/config/dnscrypt/keys"
STAMP_OUT="${ROOT}/config/clients/generated/dnscrypt-stamp.txt"

mkdir -p "$KEYS_DIR" "$(dirname "$STAMP_OUT")"

if [[ -f "${KEYS_DIR}/.initialized" ]]; then
  echo "Already initialized. Stamp:"
  cat "${KEYS_DIR}/stamp.txt" 2>/dev/null || true
  exit 0
fi

echo "Initializing DNSCrypt server provider=${PROVIDER} external=${HOST_IP}:${PORT}"
docker compose run --rm --no-deps \
  -v "${KEYS_DIR}:/opt/encrypted-dns/etc/keys" \
  dnscrypt-libre \
  init -N "${PROVIDER}" -E "${HOST_IP}:${PORT}" | tee "${KEYS_DIR}/init.log"

# Point encrypted-dns at dns-libre (preserve hosts → Unbound chain)
TOML="${KEYS_DIR}/encrypted-dns.toml"
if [[ -f "$TOML" ]]; then
  # Replace upstream_* lines with dns-libre
  grep -v -E '^\s*upstream_addr' "$TOML" > "${TOML}.tmp" || true
  {
    cat "${TOML}.tmp"
    echo 'upstream_addrs = ["172.28.0.20:53"]'
  } > "$TOML"
  rm -f "${TOML}.tmp"
fi

# Capture stamp from init log
grep -Eo 'sdns://[A-Za-z0-9_-]+' "${KEYS_DIR}/init.log" | head -1 > "${KEYS_DIR}/stamp.txt" || true
cp -f "${KEYS_DIR}/stamp.txt" "$STAMP_OUT" 2>/dev/null || true
touch "${KEYS_DIR}/.initialized"

echo "OK — start with: docker compose up -d dnscrypt-libre"
echo "Stamp file: ${STAMP_OUT}"
cat "${KEYS_DIR}/stamp.txt" 2>/dev/null || true
