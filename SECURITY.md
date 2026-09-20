# Security Policy

## Supported versions

The `main` branch of [dlnraja/freebox-dns](https://github.com/dlnraja/freebox-dns) is the only supported line.

## Threat model (intentional)

| In scope | Out of scope |
| --- | --- |
| LAN DNS on Freebox VM (`HOST_IP` bind only) | Exposing DNS/DoH on the public Internet |
| Self-signed DoH/DoT for LAN clients | Public CA / ACME (optional later) |
| Freebox app token in **local** `.freebox-token.json` (gitignored) | Committing Freebox UID / remote `fbxos` domains |
| Privacy-oriented Blocky logs (`privacy: true` by default) | Long cloud query analytics |

## Reporting a vulnerability

Open a **private** security advisory on GitHub if available, or email the maintainer via the GitHub profile.  
Do **not** open a public issue with exploit details for LAN exposure bugs.

## Hardening checklist for operators

1. Change default VM password (`debian` / cloud-init) after first boot.
2. Keep Freebox DHCP DNS1 = SOS `9.9.9.10`, DNS2 = VM only after health-check.
3. Never publish compose ports on `0.0.0.0`.
4. Trust DoH cert only on devices you control (`certs/server.crt`).
5. Rotate / delete `.freebox-token.json` if the Freebox app is revoked.
