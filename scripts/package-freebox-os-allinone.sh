#!/usr/bin/env bash
# Assemble Freebox OS all-in-one zip (qcow2 + cidata ISO + import JSON + docs).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${ROOT}/dist"
VER="${1:-$(date -u +%Y%m%d%H%M)}"
IMG="${DIST}/freebox-dns.qcow2"
ISO="${DIST}/freebox-dns-cidata.iso"
STAGE="${DIST}/allinone-stage"
ZIP="${DIST}/freebox-dns-freeboxos-allinone-${VER}.zip"

[[ -f "${IMG}" ]] || { echo "Missing ${IMG} — run scripts/build-freebox-qcow2.sh" >&2; exit 1; }
[[ -f "${ISO}" ]] || { echo "Missing ${ISO} — run scripts/build-freebox-qcow2.sh" >&2; exit 1; }

rm -rf "${STAGE}"
mkdir -p "${STAGE}"
cp -f "${IMG}" "${STAGE}/freebox-dns.qcow2"
cp -f "${ISO}" "${STAGE}/freebox-dns-cidata.iso"
cp -f "${ROOT}/packaging/freebox-os-import/freebox-os-vm.json" "${STAGE}/"
cp -f "${ROOT}/packaging/freebox-os-import/cloudinit-userdata.yaml" "${STAGE}/"
cp -f "${ROOT}/packaging/freebox-os-import/IMPORT-FREEBOX-OS.md" "${STAGE}/"
cp -f "${ROOT}/docs/freebox-vm.md" "${STAGE}/freebox-vm.md" 2>/dev/null || true

(
  cd "${STAGE}"
  sha256sum freebox-dns.qcow2 freebox-dns-cidata.iso freebox-os-vm.json cloudinit-userdata.yaml IMPORT-FREEBOX-OS.md > SHA256SUMS
)

rm -f "${ZIP}"
(cd "${STAGE}" && zip -9 "${ZIP}" ./*)
echo "Wrote ${ZIP}"
ls -lh "${ZIP}"
