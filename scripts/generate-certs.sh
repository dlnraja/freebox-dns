#!/usr/bin/env bash
# Generate self-signed TLS certs for local DoH / DoT / DoQ (LAN only).
# Includes SAN: freebox-dns.local, localhost, 127.0.0.1, HOST_IP (from env/.env).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CERT_DIR="${ROOT}/certs"
mkdir -p "${CERT_DIR}"
CN="${DOH_CN:-freebox-dns.local}"

# Load HOST_IP from .env if present
if [[ -f "${ROOT}/.env" ]]; then
  # shellcheck disable=SC1091
  set -a
  # Only pull HOST_IP / DOH_CN lines
  eval "$(grep -E '^(HOST_IP|DOH_CN)=' "${ROOT}/.env" | sed 's/\r$//' || true)"
  set +a
fi
HOST_IP="${HOST_IP:-127.0.0.1}"

FORCE="${FORCE_REGEN_CERTS:-0}"
if [[ -f "${CERT_DIR}/server.crt" && -f "${CERT_DIR}/server.key" && "${FORCE}" != "1" ]]; then
  echo "Certs already exist in ${CERT_DIR} — skip (FORCE_REGEN_CERTS=1 to regenerate)."
  exit 0
fi

SAN="DNS:${CN},DNS:localhost,DNS:freebox-dns.local,IP:127.0.0.1,IP:${HOST_IP}"
# Optional IPv6
if [[ -n "${HOST_IP6:-}" ]]; then
  SAN="${SAN},IP:${HOST_IP6}"
fi

TMP_CFG="$(mktemp)"
cat > "${TMP_CFG}" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
CN = ${CN}
O = freebox-dns
OU = LAN

[v3_req]
subjectAltName = ${SAN}
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
EOF

openssl req -x509 -newkey rsa:2048 -sha256 -days 825 -nodes \
  -keyout "${CERT_DIR}/server.key" \
  -out "${CERT_DIR}/server.crt" \
  -config "${TMP_CFG}"

rm -f "${TMP_CFG}"
chmod 644 "${CERT_DIR}/server.crt"
chmod 600 "${CERT_DIR}/server.key"
echo "Wrote ${CERT_DIR}/server.crt and server.key (SAN includes ${HOST_IP})"
