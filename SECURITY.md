# Security Policy

## Supported versions

The `main` branch of [dlnraja/freebox-dns](https://github.com/dlnraja/freebox-dns) is the only supported line.

## Threat model (intentional)

| In scope | Out of scope / forbidden |
| --- | --- |
| LAN DNS on Pi / VM / Windows (`HOST_IP` bind only) | **Open recursive DNS on the public Internet** |
| Self-signed DoH/DoT for LAN clients | Public CA / ACME (optional later) |
| Freebox app token in **local** `.freebox-token.json` (gitignored) | Committing Freebox UID / remote `fbxos` domains |
| Privacy-oriented Blocky logs (`privacy: true` by default) | Long cloud query analytics |

Exposing this resolver on the Internet enables **DNS amplification DDoS** and abuse.  
Policy: **LAN only** — [docs/lan-only.md](docs/lan-only.md).

## Reporting a vulnerability

Open a **private** security advisory on GitHub if available, or email the maintainer via the GitHub profile.  
Do **not** open a public issue with exploit details for LAN exposure bugs.

## Hardening checklist for operators

1. Change default VM password (`debian` / cloud-init) after first boot.
2. DHCP: DNS1 = resolver `HOST_IP`, DNS2 = SOS `9.9.9.10` — only after `dig @HOST_IP` works.
3. Never publish compose ports on `0.0.0.0` — run `python3 scripts/assert-lan-only.py`.
4. **Never** create router/Freebox port-forwards for `53` / `853` / DoH / Blocky UI.
5. Trust DoH cert only on devices you control (`certs/server.crt`).
6. Rotate / delete `.freebox-token.json` if the Freebox app is revoked.
