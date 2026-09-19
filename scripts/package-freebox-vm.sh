#!/usr/bin/env bash
# Build a deployable tarball for Freebox OS VM guests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VER="${1:-$(date -u +%Y%m%d)}"
OUT="dist/freebox-dns-vm-${VER}.tar.gz"
mkdir -p dist
tar --exclude='.git' --exclude='dist' --exclude='certs/*.key' --exclude='.env' \
  -czf "$OUT" \
  docker-compose.yml docker-compose.prod.yml \
  .env.example config scripts packaging cloud-init docs LICENSE README.md
echo "Wrote $OUT"
ls -lh "$OUT"
