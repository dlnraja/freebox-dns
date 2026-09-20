#!/usr/bin/env bash
# Force Blocky denylist refresh (Pi-hole gravity update equivalent).
# Targets dns-secure UI/API on HOST_IP:BLOCKY_HTTP_PORT (default 3080).
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

HOST_IP="${HOST_IP:-}"
PORT="${BLOCKY_HTTP_PORT:-3080}"
if [[ -f .env ]]; then
  line="$(grep -E '^HOST_IP=' .env | tail -1 | tr -d '\r' || true)"
  [[ -n "$line" ]] && HOST_IP="${line#HOST_IP=}"
  HOST_IP="$(echo "$HOST_IP" | tr -d '[:space:]\"' )"
  pline="$(grep -E '^BLOCKY_HTTP_PORT=' .env | tail -1 | tr -d '\r' || true)"
  [[ -n "$pline" ]] && PORT="${pline#BLOCKY_HTTP_PORT=}"
  PORT="$(echo "$PORT" | tr -d '[:space:]\"' )"
fi
HOST_IP="${HOST_IP:-127.0.0.1}"

base="http://${HOST_IP}:${PORT}"
echo "Refreshing Blocky lists via ${base} ..."

# Blocky API: POST /api/blocking/refreshLists (versions vary — try common paths)
ok=0
for path in /api/blocking/refreshLists /api/lists/refresh /api/refresh; do
  code="$(curl -s -o /tmp/blocky-refresh.out -w '%{http_code}' -X POST "${base}${path}" || true)"
  if [[ "$code" == "200" || "$code" == "204" ]]; then
    echo "OK ${path} → HTTP ${code}"
    ok=1
    break
  fi
  echo "… ${path} → HTTP ${code}"
done

if [[ "$ok" -ne 1 ]]; then
  echo "API refresh failed — recreating dns-secure / antipub / malware containers"
  if [[ -f docker-compose.prod.yml ]]; then
    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --force-recreate dns-secure dns-antipub dns-malware
  else
    docker compose up -d --force-recreate dns-secure dns-antipub dns-malware
  fi
fi

echo "Done. UI: ${base}/"
