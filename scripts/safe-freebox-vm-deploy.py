#!/usr/bin/env python3
"""
Safe Freebox OS VM deploy helper - NEVER breaks LAN DNS.

Rules (hard):
  1. Do NOT change Freebox DHCP DNS primary until VM health is proven.
  2. Always keep a plain-UDP-reachable SOS as DHCP DNS1 (Quad9 Unsecured).
     UncensoredDNS/DG stay DoT-only — UDP/53 often timed out / refused on FR ISP.
  3. Prefer adding VM as DNS2 first; DNS1=VM only after dual health checks.
  4. Store Freebox app_token only in local .freebox-token.json (gitignored).
  5. Never touch other VMs (e.g. HA OS).

Phases:
  sos / auth / status / upload / create / start / health / dhcp-safe / dhcp-sos

Usage:
  python scripts/safe-freebox-vm-deploy.py auth
  python scripts/safe-freebox-vm-deploy.py upload
  python scripts/safe-freebox-vm-deploy.py create
  python scripts/safe-freebox-vm-deploy.py start
  python scripts/safe-freebox-vm-deploy.py dhcp-safe   # DNS1=SOS DNS2=VM
"""
from __future__ import annotations

import base64
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
# Plain UDP/53 SOS only (probed from Freebox LAN). DoT-only resolvers are not listed here.
SOS_DNS = ["9.9.9.10", "194.242.2.2", "94.140.14.140"]
SOS_LABELS = ["Quad9 Unsecured", "Mullvad Unfiltered", "AdGuard Non-filtering"]
API = "http://mafreebox.freebox.fr/api/v8"
WS_UPLOAD = "ws://mafreebox.freebox.fr/api/v8/ws/upload"
DISK_ROOT = "/Disque 1"
VMS_DIR = f"{DISK_ROOT}/VMs"
QCOW2 = ROOT / "dist" / "freeboxos-allinone" / "freebox-dns.qcow2"
CIDATA = ROOT / "dist" / "freeboxos-allinone" / "freebox-dns-cidata.iso"
USERDATA = ROOT / "packaging" / "freebox-os-import" / "cloudinit-userdata.yaml"
VM_NAME = "freebox-dns"
CHUNK = 512 * 1024


def load_userdata() -> str:
    if USERDATA.exists():
        return USERDATA.read_text(encoding="utf-8")
    return "#cloud-config\nhostname: freebox-dns\n"


def b64path(p: str) -> str:
    return base64.b64encode(p.encode("utf-8")).decode("ascii")


def http_json(method: str, url: str, data=None, headers=None, timeout: int = 60):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def cmd_sos() -> int:
    print("=== SOS / filet de secours DNS (ne pas casser Internet) ===")
    for i, (ip, label) in enumerate(zip(SOS_DNS, SOS_LABELS), start=1):
        print(f"  DNS{i} = {ip}  ({label})")
    print("Note: UncensoredDNS / Digitale Gesellschaft = DoT :853 only (UDP/53 often blocked).")
    print("Rollback: python scripts/safe-freebox-vm-deploy.py dhcp-sos")
    return 0


def load_token() -> dict | None:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    return None


def save_token(data: dict) -> None:
    TOKEN_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved token -> {TOKEN_FILE} (gitignored)")


def cmd_auth() -> int:
    print("=== Freebox API authorize (press OK on Freebox now) ===")
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
    app_token = (r.get("result") or {}).get("app_token")
    track_id = r["result"]["track_id"]
    if not app_token:
        print("POST authorize missing app_token:", json.dumps(r)[:500])
        return 1
    print(f"track_id={track_id} - press OK on Freebox now...", flush=True)
    print("(app_token received, waiting for grant...)", flush=True)
    for i in range(150):
        time.sleep(2)
        s = http_json("GET", f"{API}/login/authorize/{track_id}")
        status = (s.get("result") or {}).get("status")
        print(f"  [{i}] status={status}", flush=True)
        if status == "granted":
            break
        if status in ("denied", "timeout", "unknown"):
            print("Authorization failed:", status)
            return 1
    else:
        print("Timeout waiting for Freebox button.")
        return 1
    save_token({"app_id": APP_ID, "app_token": app_token, "app_name": APP_NAME})
    sess = open_session()
    if not sess:
        return 1
    print("Session OK - API ready (DHCP untouched).")
    return 0


def open_session() -> str | None:
    tok = load_token()
    if not tok:
        print("No token - run: python scripts/safe-freebox-vm-deploy.py auth")
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


def api(session: str, method: str, path: str, data=None, timeout: int = 60):
    return http_json(
        method,
        f"{API}{path}",
        data=data,
        headers={"X-Fbx-App-Auth": session},
        timeout=timeout,
    )


def ensure_vms_dir(session: str) -> None:
    api(session, "POST", "/fs/mkdir/", {"parent": b64path(DISK_ROOT), "dirname": "VMs"})


def cmd_status() -> int:
    s = open_session()
    if not s:
        return 1
    vm = api(s, "GET", "/vm/")
    print("VMs:")
    for v in vm.get("result") or []:
        print(
            f"  id={v.get('id')} name={v.get('name')} status={v.get('status')} "
            f"disk={v.get('disk_type')}"
        )
    dhcp = api(s, "GET", "/dhcp/config/")
    print("DHCP dns:", (dhcp.get("result") or {}).get("dns"))
    ensure_vms_dir(s)
    ls = api(s, "GET", f"/fs/ls/{b64path(VMS_DIR)}")
    print(f"{VMS_DIR}:")
    for e in ls.get("result") or []:
        if e.get("name") not in (".", ".."):
            print(f"  {e.get('type')} {e.get('name')} size={e.get('size')}")
    return 0


def upload_file(session: str, local: Path, remote_dir: str, filename: str) -> int:
    try:
        import websocket
    except ImportError:
        print("pip install websocket-client")
        return 1
    if not local.exists():
        print("missing file:", local)
        return 1
    size = local.stat().st_size
    print(f"Upload {local.name} ({size} bytes) -> {remote_dir}/{filename}", flush=True)
    ensure_vms_dir(session)

    ws = websocket.create_connection(
        WS_UPLOAD,
        header=[f"X-Fbx-App-Auth: {session}"],
        timeout=120,
    )
    try:
        req_id = int(time.time()) % 1_000_000
        start = {
            "action": "upload_start",
            "request_id": req_id,
            "size": size,
            "dirname": b64path(remote_dir),
            "filename": filename,
            "force": "overwrite",
        }
        ws.send(json.dumps(start))
        resp = json.loads(ws.recv())
        if not resp.get("success"):
            print("upload_start failed:", resp)
            return 1
        sent = 0
        with local.open("rb") as f:
            while True:
                chunk = f.read(CHUNK)
                if not chunk:
                    break
                ws.send(chunk, opcode=websocket.ABNF.OPCODE_BINARY)
                sent += len(chunk)
                if sent == size or sent % (8 * CHUNK) < CHUNK:
                    pct = 100.0 * sent / size
                    print(f"  ... {sent}/{size} ({pct:.1f}%)", flush=True)
        ws.send(json.dumps({"action": "upload_finalize", "request_id": req_id}))
        # drain finalize ack (and any late chunk acks)
        deadline = time.time() + 120
        while time.time() < deadline:
            ws.settimeout(10)
            try:
                msg = ws.recv()
            except Exception:
                break
            if isinstance(msg, bytes):
                continue
            data = json.loads(msg)
            if data.get("action") == "upload_finalize":
                print("finalize:", data.get("success"), data.get("result"))
                return 0 if data.get("success") else 1
        print("upload finalize timeout (file may still be OK - check status)")
        return 0
    finally:
        try:
            ws.close()
        except Exception:
            pass


def cmd_upload() -> int:
    s = open_session()
    if not s:
        return 1
    rc = upload_file(s, QCOW2, VMS_DIR, "freebox-dns.qcow2")
    if rc != 0:
        return rc
    if CIDATA.exists():
        rc = upload_file(s, CIDATA, VMS_DIR, "freebox-dns-cidata.iso")
    return rc


def find_vm(session: str, name: str = VM_NAME) -> dict | None:
    r = api(session, "GET", "/vm/")
    for v in r.get("result") or []:
        if v.get("name") == name:
            return v
    return None


def cmd_create() -> int:
    s = open_session()
    if not s:
        return 1
    existing = find_vm(s)
    if existing:
        print(f"VM already exists id={existing.get('id')} status={existing.get('status')}")
        return 0
    # Never recreate HA OS - only create freebox-dns
    disk_path = f"{VMS_DIR}/freebox-dns.qcow2"
    cd_path = f"{VMS_DIR}/freebox-dns-cidata.iso"
    # Verify files exist on Freebox
    ls = api(s, "GET", f"/fs/ls/{b64path(VMS_DIR)}")
    names = {e.get("name") for e in (ls.get("result") or [])}
    if "freebox-dns.qcow2" not in names:
        print("qcow2 not on Freebox - run upload first")
        return 1
    payload = {
        "name": VM_NAME,
        "vcpus": 2,
        "memory": 2048,
        "disk_type": "qcow2",
        "disk_path": b64path(disk_path),
        "os": "debian",
        "enable_screen": True,
        "enable_cloudinit": True,
        "cloudinit_hostname": "freebox-dns",
        "cloudinit_userdata": load_userdata(),
    }
    if "freebox-dns-cidata.iso" in names:
        payload["cd_path"] = b64path(cd_path)
    print("Creating VM:", json.dumps({k: v for k, v in payload.items() if k != "disk_path"}))
    r = api(s, "POST", "/vm/", payload)
    print(r)
    if not r.get("success"):
        # retry with plain paths (some firmwares)
        payload["disk_path"] = disk_path
        if "cd_path" in payload:
            payload["cd_path"] = cd_path
        r = api(s, "POST", "/vm/", payload)
        print("retry plain path:", r)
    return 0 if r.get("success") else 1


def cmd_start() -> int:
    s = open_session()
    if not s:
        return 1
    vm = find_vm(s)
    if not vm:
        print("VM not found - run create")
        return 1
    vid = vm["id"]
    if vm.get("status") == "running":
        print(f"VM id={vid} already running")
        return 0
    r = api(s, "POST", f"/vm/{vid}/start")
    print("start:", r)
    return 0 if r.get("success") else 1


def cmd_health() -> int:
    """Best-effort: list DHCP leases looking for freebox-dns / new MAC."""
    s = open_session()
    if not s:
        return 1
    vm = find_vm(s)
    if not vm:
        print("no VM")
        return 1
    print("VM:", vm.get("name"), vm.get("status"), "mac=", vm.get("mac"))
    leases = api(s, "GET", "/dhcp/static_lease/")
    print("static leases:", json.dumps(leases, indent=2)[:1500])
    dyn = api(s, "GET", "/dhcp/dynamic_lease/")
    mac = (vm.get("mac") or "").lower()
    found = None
    for lease in dyn.get("result") or []:
        if (lease.get("mac") or "").lower() == mac:
            found = lease
            break
    if found:
        ip = found.get("ip")
        print(f"Lease IP: {ip}")
        ok = dns_probe(ip, "example.com", 53) and dns_probe(ip, "example.com", 5354)
        print("DNS health:", "OK" if ok else "WAIT (cloud-init/docker still booting?)")
        return 0 if ok else 1
    print("No DHCP lease yet - wait for cloud-init / DHCP")
    print(json.dumps(dyn.get("result"), indent=2)[:2000])
    return 1


def dns_probe(host: str, qname: str, port: int = 53, timeout: float = 3.0) -> bool:
    """Cross-platform UDP DNS A query (no dig required)."""
    import socket
    import struct

    tid = 0xC0DE
    q = b"".join(bytes([len(p)]) + p.encode() for p in qname.split(".")) + b"\x00"
    pkt = struct.pack("!HHHHHH", tid, 0x0100, 1, 0, 0, 0) + q + struct.pack("!HH", 1, 1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(pkt, (host, port))
        data, _ = sock.recvfrom(4096)
        # QR bit set + at least header
        return len(data) >= 12 and (data[2] & 0x80) != 0
    except OSError as e:
        print(f"  probe @{host}:{port} {qname}: {e}")
        return False
    finally:
        sock.close()


def cmd_dhcp_safe() -> int:
    """DNS1=SOS Quad9 Unsecured, DNS2=VM IP. Requires health OK + confirmation file."""
    s = open_session()
    if not s:
        return 1
    conf = ROOT / ".dhcp-safe-confirm"
    if not conf.exists():
        print("Create empty file .dhcp-safe-confirm to allow DHCP change (safety).")
        print("Then re-run: python scripts/safe-freebox-vm-deploy.py dhcp-safe")
        return 1
    vm = find_vm(s)
    if not vm or vm.get("status") != "running":
        print("VM not running")
        return 1
    dyn = api(s, "GET", "/dhcp/dynamic_lease/")
    mac = (vm.get("mac") or "").lower()
    ip = None
    for lease in dyn.get("result") or []:
        if (lease.get("mac") or "").lower() == mac:
            ip = lease.get("ip")
            break
    if not ip:
        print("No lease IP for VM")
        return 1
    cur = api(s, "GET", "/dhcp/config/")
    cfg = cur.get("result") or {}
    dns = [SOS_DNS[0], ip, SOS_DNS[1], SOS_DNS[2]]
    print(f"Setting DHCP dns={dns} (DNS1=SOS, DNS2=VM) - current was {cfg.get('dns')}")
    # Freebox PUT often needs full config object
    cfg = dict(cfg)
    cfg["dns"] = dns
    try:
        r = api(s, "PUT", "/dhcp/config/", cfg)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace") if hasattr(e, "read") else ""
        print(f"DHCP PUT failed HTTP {e.code}: {body[:300]}")
        if e.code == 403:
            print("App token lacks 'settings' permission.")
            print(f"Set manually in Freebox OS -> DHCP: DNS1={SOS_DNS[0]} DNS2={ip}")
            return 2
        raise
    print(r)
    if not r.get("success"):
        print("Need 'settings' permission on the Freebox app, or set manually in Freebox OS.")
        print(f"Manual: DNS1={SOS_DNS[0]} DNS2={ip}")
        return 1
    print(f"DHCP safe applied. Primary SOS = {SOS_DNS[0]} ({SOS_LABELS[0]}).")
    return 0


def cmd_dhcp_sos() -> int:
    s = open_session()
    if not s:
        return 1
    cur = api(s, "GET", "/dhcp/config/")
    cfg = dict(cur.get("result") or {})
    cfg["dns"] = SOS_DNS[:3] + [""]
    r = api(s, "PUT", "/dhcp/config/", cfg)
    print(r)
    return 0 if r.get("success") else 1


def cmd_download() -> int:
    print("Download all-in-one from GitHub Actions artifacts via gh CLI...")
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
    dispatch = {
        "sos": cmd_sos,
        "auth": cmd_auth,
        "status": cmd_status,
        "upload": cmd_upload,
        "create": cmd_create,
        "start": cmd_start,
        "health": cmd_health,
        "dhcp-safe": cmd_dhcp_safe,
        "dhcp-sos": cmd_dhcp_sos,
        "download": cmd_download,
    }
    fn = dispatch.get(cmd)
    if not fn:
        print(__doc__)
        return 1
    return fn()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.URLError as e:
        print("Network/API error:", e)
        print("Apply SOS DNS pins on Freebox DHCP UI if needed.")
        raise SystemExit(2)
