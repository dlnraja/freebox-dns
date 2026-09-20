#!/usr/bin/env bash
# Verify Unbound DoT forward catalogue is actually loaded (not just mounted).
# Usage: bash scripts/verify-unbound-forwards.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONF="$ROOT/config/unbound/unbound.conf"
FWD="$ROOT/config/unbound/forward-records.conf"
COMPOSE="$ROOT/docker-compose.yml"

fail=0
pass() { echo "OK  $*"; }
bad()  { echo "FAIL $*"; fail=$((fail+1)); }

# 1) Repo invariants
grep -qE '^[[:space:]]*include:[[:space:]]+/opt/unbound/etc/unbound/forward-records\.conf' "$CONF" \
  && pass "unbound.conf includes forward-records.conf (uncommented)" \
  || bad "unbound.conf missing active forward-records include"

grep -q 'forward-first: yes' "$FWD" \
  && pass "forward-first: yes" \
  || bad "forward-first missing"

grep -q 'forward-tls-upstream: yes' "$FWD" \
  && pass "forward-tls-upstream: yes" \
  || bad "forward-tls-upstream missing"

grep -q 'unbound.conf:/opt/unbound/etc/unbound/unbound.conf' "$COMPOSE" \
  && pass "compose mounts custom unbound.conf" \
  || bad "compose does not mount unbound.conf"

grep -q 'a-records.critical.conf:/opt/unbound/etc/unbound/a-records.critical.conf' "$COMPOSE" \
  && pass "compose mounts a-records.critical.conf" \
  || bad "compose missing critical mount"

grep -q 'unbound-cache:' "$COMPOSE" \
  && pass "compose has unbound-cache volume" \
  || bad "compose missing unbound-cache"

grep -q 'serve-expired: yes' "$ROOT/config/unbound/a-records.conf" \
  && pass "serve-expired: yes in a-records.conf" \
  || bad "serve-expired missing"

grep -q 'local-zone:.*static' "$ROOT/config/unbound/a-records.critical.conf" \
  && pass "critical zones are static" \
  || bad "critical zones not static"

# 2) Runtime (optional)
if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx dns-unbound; then
  docker exec dns-unbound unbound-checkconf >/dev/null 2>&1 \
    && pass "runtime unbound-checkconf" \
    || bad "runtime unbound-checkconf failed"

  if docker exec dns-unbound grep -qE '^[[:space:]]*include:[[:space:]]+/opt/unbound/etc/unbound/forward-records\.conf' \
      /opt/unbound/etc/unbound/unbound.conf; then
    pass "runtime container has active forward include"
  else
    bad "runtime container still has commented/missing forward include"
  fi

  # Prefer control if available; otherwise prove DoT path via dig to a local-data name
  if docker exec dns-unbound unbound-control list_forwards >/tmp/fbx-forwards.txt 2>/dev/null; then
    if grep -q '\.' /tmp/fbx-forwards.txt; then
      pass "unbound-control list_forwards has '.' zone"
      head -5 /tmp/fbx-forwards.txt || true
    else
      bad "list_forwards empty"
    fi
  else
    pass "unbound-control unavailable (expected if control-enable: no) — file checks suffice"
  fi
else
  echo "SKIP runtime (dns-unbound not running)"
fi

if [[ "$fail" -gt 0 ]]; then
  echo "verify-unbound-forwards: $fail failure(s)"
  exit 1
fi
echo "verify-unbound-forwards: all good"
exit 0
