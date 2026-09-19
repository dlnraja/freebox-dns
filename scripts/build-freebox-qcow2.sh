#!/usr/bin/env bash
# Build freebox-dns.qcow2 — Debian 12 cloud image ready for Freebox OS VM import.
# Requires: qemu-utils, curl, libguestfs-tools (virt-customize).
# Usage: bash scripts/build-freebox-qcow2.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${ROOT}/dist"
OUT="${DIST}/freebox-dns.qcow2"
WORK="${DIST}/qcow-build"
DEBIAN_URL="${DEBIAN_CLOUD_URL:-https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2}"
DISK_GB="${DISK_GB:-16}"
USERDATA="${ROOT}/packaging/freebox-os-import/cloudinit-userdata.yaml"

mkdir -p "${WORK}" "${DIST}"
cd "${WORK}"

echo "==> Download Debian 12 cloud qcow2"
if [[ ! -f base.qcow2 ]]; then
  curl -fL --retry 3 -o base.qcow2 "${DEBIAN_URL}"
fi

echo "==> Copy + resize to ${DISK_GB}G"
cp -f base.qcow2 "${OUT}.tmp"
qemu-img resize "${OUT}.tmp" "${DISK_GB}G"

command -v virt-customize >/dev/null 2>&1 || {
  echo "ERROR: install libguestfs-tools (virt-customize) and qemu-utils" >&2
  exit 1
}

export LIBGUESTFS_BACKEND="${LIBGUESTFS_BACKEND:-direct}"

META="${WORK}/meta-data"
printf 'instance-id: freebox-dns\nlocal-hostname: freebox-dns\n' >"${META}"

echo "==> Seed repo snapshot"
SEED_DIR="${WORK}/freebox-dns-seed"
rm -rf "${SEED_DIR}"
mkdir -p "${SEED_DIR}"
tar -C "${ROOT}" \
  --exclude='.git' --exclude='dist' --exclude='certs' --exclude='.env' \
  -cf - \
  docker-compose.yml docker-compose.prod.yml .env.example \
  config scripts packaging cloud-init docs LICENSE README.md \
  | tar -C "${SEED_DIR}" -xf -

FB="${WORK}/fb-firstboot.sh"
cat >"${FB}" <<'EOS'
#!/bin/bash
set -euo pipefail
systemctl enable --now docker || true
if [ ! -d /opt/freebox-dns ]; then
  cp -a /opt/freebox-dns-seed /opt/freebox-dns
fi
chmod +x /opt/freebox-dns/packaging/freebox-vm/install.sh || true
if [ -x /opt/freebox-dns/packaging/freebox-vm/install.sh ]; then
  bash /opt/freebox-dns/packaging/freebox-vm/install.sh || true
else
  cd /opt/freebox-dns
  cp -n .env.example .env || true
  IP=$(hostname -I | awk '{print $1}')
  sed -i "s/^HOST_IP=.*/HOST_IP=${IP}/" .env
  sed -i 's/^DNS_LIBRE_PORT=.*/DNS_LIBRE_PORT=53/' .env
  bash scripts/generate-certs.sh
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d || true
fi
EOS
chmod +x "${FB}"

echo "==> virt-customize"
virt-customize -a "${OUT}.tmp" \
  --smp 2 \
  --memsize 2048 \
  --update \
  --install docker.io,docker-compose-v2,git,curl,ca-certificates,openssl,bind9-dnsutils,jq \
  --mkdir /var/lib/cloud/seed/nocloud \
  --upload "${USERDATA}:/var/lib/cloud/seed/nocloud/user-data" \
  --upload "${META}:/var/lib/cloud/seed/nocloud/meta-data" \
  --copy-in "${SEED_DIR}:/opt" \
  --upload "${FB}:/usr/local/sbin/freebox-dns-firstboot.sh" \
  --run-command 'chmod 0755 /usr/local/sbin/freebox-dns-firstboot.sh' \
  --run-command 'chmod -R a+rX /opt/freebox-dns-seed' \
  --run-command 'cloud-init clean --logs || true' \
  --firstboot /usr/local/sbin/freebox-dns-firstboot.sh \
  --selinux-relabel || true

mv -f "${OUT}.tmp" "${OUT}"
qemu-img info "${OUT}"
ls -lh "${OUT}"
echo "==> Built ${OUT}"
