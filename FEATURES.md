# Features

Checklist of product goals delivered since the start of the project.

## Core

- [x] Dual personality → **4 smart spit modes** (uncensored / malware / antipub / secure)
- [x] **Local-first**: hosts → Unbound local-data/cache → DoT → root
- [x] Max **uncensoring** DoT catalogue + plain SOS reachable on Free ISP
- [x] **Pi-hole-like** gravity via Blocky (+ uBlock DNS + anti–anti-adblock)
- [x] DoH / DoT / DoQ (libre) · DoH / DoT (Blocky modes)
- [x] Freebox OS **VM ARM64** QCOW2 + cloud-init all-in-one
- [x] Safe DHCP: SOS `9.9.9.10` + DNS2 = VM (never PC as LAN resolver)
- [x] Anti–DNS menteur (OONI-like) + web-connectivity lite
- [x] Credits + **GitHub Pages** illustrated guides
- [x] Wi‑Fi / LAN operator guide
- [x] Client profiles (Firefox / Apple / Android / Windows DoH)
- [x] CI validate + list health + anti-lie probe + Pages deploy

## Pi-hole-like (Blocky)

- [x] Multi-list gravity + 12h refresh
- [x] Whitelist / extra blacklists (files)
- [x] Groups pihole / ublock / anti_adblock / malware
- [x] NXDOMAIN blocking
- [x] Admin UI on secure `:3080`
- [x] Manual list refresh script
- [x] CSV query log (7 days) on secure — local VM disk only
- [ ] Pi-hole DHCP / teleporter / regex UI — **out of scope**
- [ ] Cloud analytics — **out of scope** (privacy)
## Operator docs

- [x] README (VM canon)
- [x] CHANGELOG / CONTRIBUTING / SECURITY
- [x] docs/pihole-parity.md · filtering · resilience · wifi-lan
- [x] GitHub Pages site/

See [CHANGELOG.md](CHANGELOG.md) for release notes.
