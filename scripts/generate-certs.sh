#!/usr/bin/env bash
# Generate self-signed TLS certs for local DoH (LAN only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CERT_DIR="${ROOT}/certs"
mkdir -p "${CERT_DIR}"
CN="${DOH_CN:-freebox-dns.local}"

if [[ -f "${CERT_DIR}/server.crt" && -f "${CERT_DIR}/server.key" ]]; then
  echo "Certs already exist in ${CERT_DIR} — skip (delete to regenerate)."
  exit 0
fi

openssl req -x509 -newkey rsa:2048 -sha256 -days 825 -nodes \
  -keyout "${CERT_DIR}/server.key" \
  -out "${CERT_DIR}/server.crt" \
  -subj "/CN=${CN}/O=freebox-dns/OU=LAN" \
  -addext "subjectAltName=DNS:${CN},DNS:localhost,IP:127.0.0.1"

chmod 644 "${CERT_DIR}/server.crt"
chmod 600 "${CERT_DIR}/server.key"
echo "Wrote ${CERT_DIR}/server.crt and server.key"
