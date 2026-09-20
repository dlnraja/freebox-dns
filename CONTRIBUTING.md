# Contributing

Thanks for improving **freebox-dns**. Production target = **Freebox OS VM** DNS for the whole LAN Wi‑Fi.

## Ground rules

1. **Do not** put a Windows PC IP in Freebox DHCP as the LAN resolver.
2. **Do not** commit secrets: `.env`, `.freebox-token.json`, private LAN dumps with UID/address.
3. Prefer regenerating generated files over hand-edits.

## Generated files (regen, don’t hand-edit)

| File | Command |
| --- | --- |
| `config/blocky/config*.yml` | `python3 scripts/generate-blocky-modes.py` |
| `config/clients/generated/*` | `HOST_IP=<vm> python3 scripts/generate-client-profiles.py` |
| `config/uncensor/hosts.critical` + Unbound critical | `python3 scripts/warm-local-cache.py` |
| `hosts.generated` + `a-records.conf` body | `python3 scripts/ooni-like-anti-lie.py` |

## Local lab vs Freebox VM

| | Lab (PC/WSL) | Prod (Freebox VM) |
| --- | --- | --- |
| `HOST_IP` | Your PC LAN IP | VM LAN IP (e.g. `192.168.1.71`) |
| Compose | `docker compose up -d` | `+ docker-compose.prod.yml` (+ `arm64.yml` on Freebox) |
| DHCP Freebox | **Never** point at lab PC | DNS1=`9.9.9.10` DNS2=VM |

## Docs / Pages

- Markdown: `docs/`
- GitHub Pages HTML: `site/` (workflow `github-pages.yml`)
- Keep Pages and `docs/` in sync for DHCP / Wi‑Fi / modes

## PR checklist

- [ ] `bash scripts/health-check.sh` (or CI green)
- [ ] No secrets committed
- [ ] Regenerated Blocky/client artifacts if lists or ports changed
- [ ] Update `CHANGELOG.md` [Unreleased] if user-facing

## Code of conduct

Be respectful. This project fights DNS censorship and ads at the DNS layer — no parental/porn/SafeSearch “moral” filters in PRs.
