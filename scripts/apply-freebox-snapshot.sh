#!/usr/bin/env bash
# Apply pinned Freebox DNS from snapshot into a local .env (never commits secrets).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SNAP="${ROOT}/config/freebox-dns-snapshot.json"
ENV_FILE="${ROOT}/.env"

if [[ ! -f "${SNAP}" ]]; then
  echo "Missing ${SNAP}"
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${ROOT}/.env.example" "${ENV_FILE}"
  echo "Created ${ENV_FILE} from .env.example"
fi

python3 - <<'PY' "${SNAP}" "${ENV_FILE}"
import json, re, sys
snap_path, env_path = sys.argv[1], sys.argv[2]
data = json.load(open(snap_path, encoding="utf-8"))
pins = data.get("pinned_fallback") or {}
text = open(env_path, encoding="utf-8").read()
for k, v in pins.items():
    text, n = re.subn(rf"^{k}=.*$", f"{k}={v}", text, flags=re.M)
    if n == 0:
        text += f"\n{k}={v}\n"
open(env_path, "w", encoding="utf-8").write(text)
print("Pinned into", env_path, ":", pins)
PY
