# Contributing

Thanks for improving **freebox-dns** — a **LAN-only** DNS resolver (Pi / Freebox VM / Windows).

## Ground rules

1. **DNS1** = resolver host IP · **DNS2** = SOS `9.9.9.10` — never put a sleeping laptop in router DHCP.
2. **LAN only** — never publish DNS/DoH on `0.0.0.0` or open router NAT for `:53` / `:853` / DoH ([docs/lan-only.md](docs/lan-only.md)).
3. **Do not** commit secrets: `.env`, `.freebox-token.json`, private dumps with UID/address.
4. Prefer regenerating generated files over hand-edits.
5. **Do not** turn this into Pi-hole FTL unless the issue explicitly asks — Blocky is intentional ([docs/pihole-parity.md](docs/pihole-parity.md)).

## Generated files (regen, don’t hand-edit)

| File | Command |
| --- | --- |
| `config/blocky/config*.yml` + `modes.json` | `python3 scripts/generate-blocky-modes.py` |
| `config/clients/generated/*` | `HOST_IP=<resolver-lan-ip> python3 scripts/generate-client-profiles.py` |
| `config/uncensor/hosts.critical` + Unbound critical | `python3 scripts/warm-local-cache.py` |
| `hosts.generated` + `a-records.conf` body | `python3 scripts/ooni-like-anti-lie.py` |

After changing `HOST_IP` in `.env`, **regen client profiles** so DoH URLs match the VM/Pi (not a stale lab PC IP).

## Lab vs production host

| | Lab (PC/WSL Docker) | Prod (Pi / Freebox VM / always-on) |
| --- | --- | --- |
| `HOST_IP` | PC LAN IP (tests only) | Machine that will be **DNS1** |
| Compose | `docker compose up -d` | `+ docker-compose.prod.yml` (+ `arm64.yml` if ARM) |
| Router DHCP | **Never** point at lab PC | DNS1=`HOST_IP` DNS2=`9.9.9.10` |
| Windows salon | — | [docs/deploy-windows.md](docs/deploy-windows.md) (no Docker) |

`.env.example` uses a **placeholder** `192.168.1.50` — replace on the real host.

## Docs / Pages

- Markdown: `docs/`
- GitHub Pages: `site/` (`github-pages.yml`)
- Keep DHCP / Wi‑Fi / modes aligned between `docs/` and `site/`

## PR checklist

- [ ] `python3 scripts/assert-lan-only.py` + CI green
- [ ] No secrets committed
- [ ] Regenerated Blocky/client artifacts if lists or ports changed
- [ ] Update `CHANGELOG.md` [Unreleased] if user-facing
- [ ] Honest about Pi-hole gaps (don’t claim FTL features)

## Code of conduct

Be respectful. This project fights DNS censorship and ads at the DNS layer — no parental/porn/SafeSearch “moral” filters in PRs.
