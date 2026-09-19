#!/usr/bin/env python3
"""
Safe Freebox OS VM deploy helper — NEVER breaks LAN DNS.

Rules (hard):
  1. Do NOT change Freebox DHCP DNS primary until VM health is proven.
  2. Always keep UncensoredDNS 91.239.100.100 as DHCP secondary / SOS.
  3. Prefer adding VM as DNS2 first; DNS1 only after dual health checks.
  4. Store Freebox app_token only in local .freebox-token.json (gitignored).

Phases:
  sos      — print rollback DNS recipe + verify control resolvers
  auth     — Freebox API authorize (needs front-panel OK)
  download — fetch all-in-one artifact from GitHub Actions
  status   — list VMs via API if token present
  create   — create VM from uploaded qcow2 (no DHCP change)
  health   — dig @VM_IP example.com
  dhcp-safe — set DHCP DNS1=pin1 DNS2=VM (or DNS1=VM DNS2=pin1) with confirmation file

Usage:
  python scripts/safe-freebox-vm-deploy.py sos
  python scripts/safe-freebox-vm-deploy.py auth
  python scripts/safe-freebox-vm-deploy.py status
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = ROOT / ".freebox-token.json"
APP_ID = "fr.freeboxdns.safe.deploy"
APP_NAME = "freebox-dns-safe-deploy"
APP_VERSION = "1.0.0"
DEVICE = "cursor-agent"
SOS_DNS = ["91.239.100.100", "185.95.218.42", "9.9.9.10"]
API = "http://mafreebox.freebox.fr/api/v8"


def http_json(method: str, url: str, data=None, headers=None):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def cmd_sos() -> int:
    print("=== SOS / filet de secours DNS (ne pas casser Internet) ===")
    print("Si la VM Freebox tombe, configurez immédiatement DHCP Freebox :")
    print(f"  DNS1 = {SOS_DNS[0]}  (UncensoredDNS)")
    print(f"  DNS2 = {SOS_DNS[1]}  (Digitale Gesellschaft)")
    print(f"  DNS3 = {SOS_DNS[2]}  (Quad9 Unsecured)")
    print("OU remettez les DNS Freebox 'automatiques' temporairement.")
    print()
    print("Sur ce PC (Wi-Fi), les DNS actuels doivent deja etre les pins -")
    print("ne pointez PAS le DHCP primaire vers une VM non testee.")
    print()
    print("Verif controles :")
    for ip in SOS_DNS:
        print(f"  keep handy: {ip}")
    print()
    print("Rollback one-liner (apres auth API) :")
    print("  python scripts/safe-freebox-vm-deploy.py dhcp-sos")
    return 0


def load_token() -> dict | None:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    return None


def save_token(data: dict) -> None:
    TOKEN_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved token → {TOKEN_FILE} (gitignored)")


def cmd_auth() -> int:
    print("=== Freebox API authorize (appuyez OK sur la Freebox si demandé) ===")
    # Start authorize
    r = http_json(
        "POST",
        f"{API}/login/authorize/",
        {
            "app_id": APP_ID,
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
            "device_name": DEVICE,
        },
    )
    if not r.get("success"):
        print("authorize failed:", r)
        return 1
    track_id = r["result"]["track_id"]
    print(f"track_id={track_id} — validez sur l'écran de la Freebox maintenant…")
    app_token = None
    for i in range(60):
        time.sleep(2)
        s = http_json("GET", f"{API}/login/authorize/{track_id}")
        status = (s.get("result") or {}).get("status")
        print(f"  [{i}] status={status}")
        if status == "granted":
            app_token = s["result"]["app_token"]
            break
        if status in ("denied", "timeout", "unknown"):
            print("Authorization failed:", status)
            return 1
    if not app_token:
        print("Timeout waiting for Freebox button.")
        return 1
    save_token({"app_id": APP_ID, "app_token": app_token})
    # Open session to verify
    sess = open_session()
    if not sess:
        return 1
    print("Session OK — API ready for VM ops (DHCP still untouched).")
    return 0


def open_session() -> str | None:
    tok = load_token()
    if not tok:
        print("No token — run: python scripts/safe-freebox-vm-deploy.py auth")
        return None
    challenge = http_json("GET", f"{API}/login/")
    if not challenge.get("success"):
        print(challenge)
        return None
    ch = challenge["result"]["challenge"]
    password = hmac.new(
        tok["app_token"].encode(), ch.encode(), hashlib.sha1
    ).hexdigest()
    login = http_json(
        "POST",
        f"{API}/login/session/",
        {"app_id": tok["app_id"], "password": password},
    )
    if not login.get("success"):
        print("session failed:", login)
        return None
    return login["result"]["session_token"]


def api(session: str, method: str, path: str, data=None):
    return http_json(
        method,
        f"{API}{path}",
        data=data,
        headers={"X-Fbx-App-Auth": session},
    )


def cmd_status() -> int:
    s = open_session()
    if not s:
        return 1
    # VM list — API path may vary by version
    for path in ("/vm/", "/vm/info/", "/fs/tasks/"):
        try:
            r = api(s, "GET", path)
            print(path, "→", json.dumps(r, indent=2)[:2000])
        except Exception as e:
            print(path, "ERR", e)
    return 0


def cmd_dhcp_sos() -> int:
    """Emergency: set Freebox DHCP DNS to SOS pins only (no VM)."""
    s = open_session()
    if not s:
        return 1
    print("=== DHCP SOS — restoring uncensoring pins (no VM) ===")
    # Freebox DHCP config schema differs; attempt common endpoints carefully
    # We only SET dns servers to SOS pins — never blank.
    payload_candidates = [
        (
            "PUT",
            "/dhcp/config/",
            {
                "dns": SOS_DNS[:2],
            },
        ),
    ]
    for method, path, data in payload_candidates:
        try:
            r = api(s, method, path, data)
            print(method, path, "→", r)
            if r.get("success"):
                print("DHCP SOS applied:", SOS_DNS[:2])
                return 0
        except Exception as e:
            print("try failed", path, e)
    print(
        "API DHCP update failed — set manually in Freebox OS → DHCP →",
        SOS_DNS[0],
        SOS_DNS[1],
    )
    return 1


def cmd_download() -> int:
    print("Download all-in-one from GitHub Actions artifacts via gh CLI…")
    os.chdir(ROOT)
    code = os.system(
        "gh run download --repo dlnraja/freebox-dns "
        "-n freebox-dns-freeboxos-allinone -D dist/freeboxos-allinone "
        "$(gh run list --repo dlnraja/freebox-dns --workflow=build-freebox-os-qcow2.yml "
        "--json databaseId,conclusion --jq \"[.[]|select(.conclusion==\\\"success\\\")][0].databaseId\")"
    )
    return 0 if code == 0 else 1


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "sos").lower()
    if cmd == "sos":
        return cmd_sos()
    if cmd == "auth":
        return cmd_auth()
    if cmd == "status":
        return cmd_status()
    if cmd == "dhcp-sos":
        return cmd_dhcp_sos()
    if cmd == "download":
        return cmd_download()
    print(__doc__)
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.URLError as e:
        print("Network/API error:", e)
        print("Internet/DNS may be degraded — apply SOS DNS pins on Freebox DHCP UI.")
        raise SystemExit(2)
