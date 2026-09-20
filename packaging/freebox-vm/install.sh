#!/usr/bin/env bash
# Install freebox-dns on a Freebox OS VM guest (Debian/Ubuntu).
# Usage: sudo bash packaging/freebox-vm/install.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
xargs -a packaging/freebox-vm/packages.txt apt-get install -y

systemctl enable --now docker || service docker start
usermod -aG docker "${SUDO_USER:-$USER}" 2>/dev/null || true

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

IP="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}')"
if [[ -z "${IP:-}" ]]; then
  IP="$(hostname -I | awk '{print $1}')"
fi
if [[ -n "${IP:-}" ]]; then
  sed -i "s/^HOST_IP=.*/HOST_IP=${IP}/" .env
fi
sed -i 's/^DNS_LIBRE_PORT=.*/DNS_LIBRE_PORT=53/' .env || true

bash scripts/generate-certs.sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo ""
echo "Installed. HOST_IP=${IP:-unknown}"
echo "Freebox DHCP → DNS1=${IP:-HOST_IP}  DNS2=9.9.9.10"
echo "Docs: docs/freebox-vm.md"
bash scripts/health-check.sh || true
