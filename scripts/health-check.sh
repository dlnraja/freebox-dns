#!/usr/bin/env bash
# Health-check all smart DNS modes (uncensored / malware / antipub / secure).
set -euo pipefail
HOST="${DNS_HOST:-127.0.0.1}"
LIBRE_PORT="${DNS_LIBRE_PORT:-5356}"
MALWARE_PORT="${DNS_MALWARE_PORT:-5357}"
ANTIPUB_PORT="${DNS_ANTIPUB_PORT:-5358}"
SECURE_PORT="${DNS_SECURE_PORT:-5354}"

fail=0
check_plain() {
  local name="$1" port="$2"
  echo "== plain ${name} :${port} =="
  if dig @"${HOST}" -p "${port}" example.com +time=2 +tries=1 +short | grep -qE '^[0-9.]+'; then
    echo OK
  else
    echo FAIL; fail=1
  fi
}

check_plain "uncensored(dns-libre)" "${LIBRE_PORT}"
check_plain "malware" "${MALWARE_PORT}"
check_plain "antipub" "${ANTIPUB_PORT}"
check_plain "secure" "${SECURE_PORT}"

echo "== antipub should NXDOMAIN ads =="
if dig @"${HOST}" -p "${ANTIPUB_PORT}" doubleclick.net +time=2 +tries=1 2>/dev/null | grep -q NXDOMAIN; then
  echo OK
else
  echo WARN_OR_FAIL
fi

echo "== malware should still resolve ads (not blocked) =="
if dig @"${HOST}" -p "${MALWARE_PORT}" example.com +time=2 +tries=1 +short | grep -qE '^[0-9.]+'; then
  echo OK
else
  echo FAIL; fail=1
fi

if command -v curl >/dev/null; then
  for pair in \
    "uncensored|https://${HOST}:${DOH_LIBRE_PORT:-8453}/dns-query" \
    "malware|https://${HOST}:${DOH_MALWARE_PORT:-8445}/dns-query" \
    "antipub|https://${HOST}:${DOH_ANTIPUB_PORT:-8446}/dns-query" \
    "secure|https://${HOST}:${DOH_SECURE_PORT:-8444}/dns-query"
  do
    name="${pair%%|*}"
    url="${pair#*|}"
    echo "== DoH ${name} =="
    code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 5 \
      -H 'accept: application/dns-json' \
      "${url}?name=example.com&type=A" || true)
    if [[ "${code}" == "200" ]]; then echo OK; else echo FAIL; fail=1; fi
  done
fi

DNSCRYPT_PORT="${DNSCRYPT_PROXY_PORT:-5359}"
echo "== DNSCrypt proxy :${DNSCRYPT_PORT} (Do53→DNSCrypt→Quad9) =="
if dig @"${HOST}" -p "${DNSCRYPT_PORT}" example.com +time=3 +tries=1 +short 2>/dev/null | grep -qE '^[0-9.]+'; then
  echo OK
else
  echo WARN_OR_FAIL
fi

# Quad9 SOS / DoH HTTP/2 (CaptainDNS + Quad9 retirement notice)
if command -v python3 >/dev/null; then
  echo "== Quad9 ops (SOS .10 + DoH HTTP/2) =="
  if python3 "$(dirname "$0")/quad9-ops-check.py"; then
    echo OK
  else
    echo FAIL; fail=1
  fi
fi

exit "${fail}"

