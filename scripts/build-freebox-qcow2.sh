#!/usr/bin/env bash
# Build Freebox OS importables WITHOUT libguestfs:
#   1) freebox-dns.qcow2  — Debian 12 cloud disk (resized)
#   2) freebox-dns-cidata.iso — NoCloud cloud-init (mount as Freebox VM CD-ROM)
# Freebox OS: import qcow2 + attach the ISO as virtual CD.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${ROOT}/dist"
WORK="${DIST}/qcow-build"
DEBIAN_URL="${DEBIAN_CLOUD_URL:-https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2}"
DISK_GB="${DISK_GB:-16}"
USERDATA="${ROOT}/packaging/freebox-os-import/cloudinit-userdata.yaml"
OUT_QCOW="${DIST}/freebox-dns.qcow2"
OUT_ISO="${DIST}/freebox-dns-cidata.iso"

mkdir -p "${WORK}" "${DIST}"
cd "${WORK}"

echo "==> Download Debian 12 cloud qcow2"
if [[ ! -f base.qcow2 ]]; then
  curl -fL --retry 3 -o base.qcow2 "${DEBIAN_URL}"
fi

echo "==> Resize → ${OUT_QCOW} (${DISK_GB}G)"
cp -f base.qcow2 "${OUT_QCOW}"
qemu-img resize "${OUT_QCOW}" "${DISK_GB}G"
qemu-img info "${OUT_QCOW}"

META="${WORK}/meta-data"
NETWORK="${WORK}/network-config"
printf 'instance-id: freebox-dns-%s\nlocal-hostname: freebox-dns\n' "$(date -u +%Y%m%d)" >"${META}"
# DHCP on primary NIC (Freebox LAN bridge)
cat >"${NETWORK}" <<'EOF'
version: 2
ethernets:
  id0:
    match:
      name: "en*"
    dhcp4: true
    dhcp6: false
  id1:
    match:
      name: "eth*"
    dhcp4: true
    dhcp6: false
EOF

echo "==> Build NoCloud CIDATA ISO"
if command -v cloud-localds >/dev/null 2>&1; then
  cloud-localds --network-config="${NETWORK}" "${OUT_ISO}" "${USERDATA}" "${META}"
elif command -v genisoimage >/dev/null 2>&1 || command -v mkisofs >/dev/null 2>&1; then
  STAGE="${WORK}/cidata"
  rm -rf "${STAGE}" && mkdir -p "${STAGE}"
  cp -f "${USERDATA}" "${STAGE}/user-data"
  cp -f "${META}" "${STAGE}/meta-data"
  cp -f "${NETWORK}" "${STAGE}/network-config"
  MKISO=$(command -v genisoimage || command -v mkisofs)
  "${MKISO}" -output "${OUT_ISO}" -volid cidata -joliet -rock "${STAGE}"
else
  echo "ERROR: need cloud-image-utils (cloud-localds) or genisoimage" >&2
  exit 1
fi

ls -lh "${OUT_QCOW}" "${OUT_ISO}"
echo "==> Done. Import ${OUT_QCOW} into Freebox OS VM and attach ${OUT_ISO} as CD-ROM."
