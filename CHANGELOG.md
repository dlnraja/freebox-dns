# Changelog

All notable changes to **freebox-dns** are documented here.  
Format inspired by [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [1.3.0] — 2026-09-20

### Added

- **Windows natif** (`scripts/windows-native/`) : `dnsproxy.exe` sans Docker — [docs/deploy-windows.md](docs/deploy-windows.md)
- Hub déploiement multi-cible [docs/deploy.md](docs/deploy.md) (Pi / VM / Windows)
- **LAN-only** : refuse bind public / `0.0.0.0` — [docs/lan-only.md](docs/lan-only.md) · `scripts/assert-lan-only.py`
- Shared CI gates: `ci-conf-lint.py` + reusable workflow; `changelog-check`, `labeler`, `docs-lint` (lychee)
- Hardened workflows: scoped write perms, qcow2 no mid-build cancel, link-health fail-closed criticals, Pages deploy timeout
- **Unbound resilience (full chain)**: custom mounted `unbound.conf` with **active** DoT
  `forward-records.conf` include; `local-zone: … static` for critical + anti-lie names;
  `serve-expired: yes` + `serve-expired-client-timeout: 0` in `a-records.conf`;
  `a-records.critical.conf` + `srv-records.conf` mounts; `scripts/verify-unbound-forwards.sh`;
  `blocky-custom-dns.yml` stub (hostsFile only); acceptance tests in `docs/resilience.md`

### Changed

- README / docs / site : parité Pi-hole **honnête** (Blocky, UI secure only, hors scope)
- Product DHCP : **DNS1 = HOST_IP**, **DNS2 = 9.9.9.10** (SOS)
- PR template + CONTRIBUTING (LAN-only, regen clients, pas de FTL)
- « smart spit » = marque volontaire (4 personnalités par port/DoH)
- Multi-host framing (Pi / Freebox VM / Windows) — Freebox optional

### Documentation

- GitHub Pages Wi‑Fi / LAN guide; deploy hub; lan-only; pihole-parity
- CI docs (`docs/ci.md`) — reusable conf-lint, changelog-check, labeler, docs-lint
- Quad9 matrix, public DNS landscape, CaptainDNS ops

### CI / Automation

- Harden all workflows: `permissions`, `concurrency`, timeouts, path filters
- Blocky generator **drift gate**; smoke artifacts on failure
- Anti-lie + blocklist stamp open **PRs** (no silent `git push || true`)
- Pages PR link-check + post-deploy curl verify
- Weekly qcow2 schedule + cloud image cache; kit on every packaging PR
- Nightly `ci-regen` (Blocky + client profiles → PR)
- `release.yml` from `v*.*.*` tags + CHANGELOG notes
- Dependabot for GitHub Actions
- `docs-ci.yml` / `docs-lint.yml` / `changelog-check.yml` / `labeler.yml`
- **Anti-degradation watchdog** → GitHub issue
- **Link-health** daily + **stale** bot

## [1.2.0] — 2026-09-20

### Added

- **Smart spit modes**: `uncensored` · `malware` · `antipub` · `secure`
- Unbound **local-first**: `a-records.critical.conf`, serve-expired cache volume, warm scripts
- Wi‑Fi / LAN docs — resolver = Freebox VM, not Windows PC
- Client profiles regenerated for VM `HOST_IP`
- `scripts/set-windows-wifi-dns-to-vm.ps1`
- Pi-hole-like **CSV query log** (7 days) on `dns-secure`
- `scripts/blocky-refresh-lists.sh` (gravity refresh)
- CHANGELOG, CONTRIBUTING, SECURITY, FEATURES, issue templates, `docs/pihole-parity.md`

### Changed

- DHCP SOS plain UDP → Quad9 `9.9.9.10` / Mullvad / AdGuard (UncensoredDNS/DG = DoT only on Free ISP)
- README / Pages: production = Freebox OS VM

### Fixed

- Malware mode port `5355` → `5357` (LLMNR conflict)
- Freebox DHCP API 403 when app lacks `settings`
- warm-unbound-runtime.sh CRLF / `.env` BOM on Debian

## [1.1.0] — 2026-09-19

### Added

- Full **CREDITS** + illustrated **GitHub Pages** (`site/`)
- Freebox OS **QCOW2 ARM64** all-in-one + cloud-init + deploy helper
- OONI-like **anti–DNS menteur** + web-connectivity lite
- Max uncensoring DoT catalogue
- Safe Freebox deploy (SOS before DHCP)
- DoH / DoT / DoQ on dns-libre; DoH/DoT on Blocky modes
- Pi-hole / uBlock / anti–anti-adblock lists via Blocky groups

### Changed

- Dual stack → four personalities sharing Unbound

## [1.0.0] — 2026-09-18

### Added

- Initial dual DNS: **dns-libre** (uncensoring) + **dns-secure** (Blocky)
- Pinned Freebox DNS identities (`FREEBOX_DNS_1..5`)
- Docker Compose local-only binds, CI validate/health
- Lexicon mapping Freebox pins → local personalities

[Unreleased]: https://github.com/dlnraja/freebox-dns/compare/main...HEAD
[1.2.0]: https://github.com/dlnraja/freebox-dns/commits/main
