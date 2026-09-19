#!/usr/bin/env bash
# Assemble Freebox OS all-in-one zip (qcow2 + import JSON + cloud-init + checksums).
# Prereq: dist/freebox-dns.qcow2 (from scripts/build-freebox-qcow2.sh)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${ROOT}/dist"
VER="${1:-$(date -u +%Y%m%d%H%M)}"
IMG="${DIST}/freebox-dns.qcow2"
STAGE="${DIST}/allinone-stage"
ZIP="${DIST}/freebox-dns-freeboxos-allinone-${VER}.zip"

if [[ ! -f "${IMG}" ]]; then
  echo "Missing ${IMG} — run: bash scripts/build-freebox-qcow2.sh" >&2
  exit 1
fi

rm -rf "${STAGE}"
mkdir -p "${STAGE}"
cp -f "${IMG}" "${STAGE}/freebox-dns.qcow2"
cp -f "${ROOT}/packaging/freebox-os-import/freebox-os-vm.json" "${STAGE}/"
cp -f "${ROOT}/packaging/freebox-os-import/cloudinit-userdata.yaml" "${STAGE}/"
cp -f "${ROOT}/packaging/freebox-os-import/IMPORT-FREEBOX-OS.md" "${STAGE}/"
cp -f "${ROOT}/docs/freebox-vm.md" "${STAGE}/freebox-vm.md" 2>/dev/null || true

(
  cd "${STAGE}"
  if command -v sha256sum >/dev/null; then
    sha256sum freebox-dns.qcow2 freebox-os-vm.json cloudinit-userdata.yaml IMPORT-FREEBOX-OS.md > SHA256SUMS
  else
    shasum -a 256 freebox-dns.qcow2 freebox-os-vm.json cloudinit-userdata.yaml IMPORT-FREEBOX-OS.md > SHA256SUMS
  fi
)

rm -f "${ZIP}"
(
  cd "${STAGE}"
  if command -v zip >/dev/null; then
    zip -9 "${ZIP}" ./*
  else
    tar -czf "${ZIP%.zip}.tar.gz" ./*
    echo "zip not found — wrote ${ZIP%.zip}.tar.gz"
    ls -lh "${ZIP%.zip}.tar.gz"
    exit 0
  fi
)

echo "Wrote ${ZIP}"
ls -lh "${ZIP}"
