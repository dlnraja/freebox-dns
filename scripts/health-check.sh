#!/usr/bin/env bash
# Health-check plain DNS + DoH (+ optional DoT) for both personalities.
set -euo pipefail
LIBRE_DNS="${LIBRE_DNS:-127.0.0.1}"
SECURE_DNS="${SECURE_DNS:-127.0.0.1}"
LIBRE_PORT="${DNS_LIBRE_PORT:-5356}"
SECURE_PORT="${DNS_SECURE_PORT:-5354}"
DOH_LIBRE="${DOH_LIBRE_URL:-https://127.0.0.1:8453/dns-query}"
DOH_SECURE="${DOH_SECURE_URL:-https://127.0.0.1:8444/dns-query}"
DOT_LIBRE_PORT="${DOT_LIBRE_PORT:-8853}"
DOT_SECURE_PORT="${DOT_SECURE_PORT:-8854}"

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
  if curl -sk --max-time 5 "${DOH_LIBRE}?name=example.com&type=A" | grep -qiE 'Answer|example|Status|"Answer"|IN'; then
    echo OK
  else
    # RFC8484 wire format may be binary — accept HTTP 200
    code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 5 \
      -H 'accept: application/dns-message' \
      "${DOH_LIBRE}?dns=AAABAAABAAAAAAAAA3d3dwdleGFtcGxlA2NvbQAAAQAB" || true)
    if [[ "${code}" == "200" ]]; then echo OK; else echo FAIL; fail=1; fi
  fi
  echo "== DoH dns-secure =="
  code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 5 \
    -H 'accept: application/dns-json' \
    "${DOH_SECURE}?name=example.com&type=A" || true)
  if [[ "${code}" == "200" ]]; then echo OK; else echo FAIL; fail=1; fi
fi

# DoT: TCP connect to TLS port (full dig +tls optional)
if command -v bash >/dev/null; then
  echo "== DoT port libre :${DOT_LIBRE_PORT} =="
  if timeout 2 bash -c "echo >/dev/tcp/${LIBRE_DNS}/${DOT_LIBRE_PORT}" 2>/dev/null; then
    echo OK
  else
    echo SKIP_OR_FAIL
  fi
  echo "== DoT port secure :${DOT_SECURE_PORT} =="
  if timeout 2 bash -c "echo >/dev/tcp/${SECURE_DNS}/${DOT_SECURE_PORT}" 2>/dev/null; then
    echo OK
  else
    echo SKIP_OR_FAIL
  fi
fi

exit "${fail}"
