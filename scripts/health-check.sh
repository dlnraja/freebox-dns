#!/usr/bin/env bash
# Health-check plain DNS + DoH for both personalities.
set -euo pipefail
LIBRE_DNS="${LIBRE_DNS:-127.0.0.1}"
SECURE_DNS="${SECURE_DNS:-127.0.0.1}"
LIBRE_PORT="${DNS_LIBRE_PORT:-5353}"
SECURE_PORT="${DNS_SECURE_PORT:-5354}"
DOH_LIBRE="${DOH_LIBRE_URL:-https://127.0.0.1:8443/dns-query}"
DOH_SECURE="${DOH_SECURE_URL:-https://127.0.0.1:8444/dns-query}"

fail=0
echo "== plain dns-libre :${LIBRE_PORT} =="
if dig @"${LIBRE_DNS}" -p "${LIBRE_PORT}" example.com +time=2 +tries=1 +short | grep -qE '^[0-9.]+'; then
  echo OK
else
  echo FAIL; fail=1
fi

echo "== plain dns-secure :${SECURE_PORT} =="
if dig @"${SECURE_DNS}" -p "${SECURE_PORT}" example.com +time=2 +tries=1 +short | grep -qE '^[0-9.]+'; then
  echo OK
else
  echo FAIL; fail=1
fi

if command -v curl >/dev/null; then
  echo "== DoH dns-libre =="
  if curl -sk --max-time 5 "${DOH_LIBRE}?name=example.com&type=A" | grep -qi 'Answer\|example\|Status'; then
    echo OK
  else
    echo FAIL; fail=1
  fi
  echo "== DoH dns-secure =="
  if curl -sk --max-time 5 "${DOH_SECURE}?name=example.com&type=A" | grep -qi 'Answer\|example\|Status'; then
    echo OK
  else
    echo FAIL; fail=1
  fi
fi

exit "${fail}"
