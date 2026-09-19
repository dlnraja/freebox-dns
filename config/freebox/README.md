# Freebox OS — checklist DHCP / DNS + VM

## Prérequis

1. VM Freebox / Pi / PC avec Docker, IP LAN fixe = `HOST_IP`.
2. Rubrique VM complète : [docs/freebox-vm.md](../../docs/freebox-vm.md).
3. Paquet : `packaging/freebox-vm/install.sh` ou cloud-init.
4. Certs DoH + `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`.

## DHCP Freebox

| Champ | Valeur |
| --- | --- |
| DNS primaire | `HOST_IP` (dns-libre :53) |
| DNS secondaire | `91.239.100.100` (UncensoredDNS) |

Fallbacks max : `config/upstreams/uncensoring-catalog.json` → `plain_fallback_order`.

## DoH / UI

- Libre : `https://HOST_IP:8453/dns-query`
- Secure : `https://HOST_IP:8444/dns-query`
- Blocky : `http://HOST_IP:3080`

## Fichiers

- `config/freebox/dhcp-dns.json`
- `packaging/freebox-vm/manifest.json` (images + packages)
- `docs/upstreams-uncensoring.md`
