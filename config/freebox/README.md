# Freebox OS — checklist DHCP / DNS (à appliquer manuellement dans l’UI)

## Prérequis

1. VM Freebox / Pi / PC avec Docker, IP LAN **fixe** = `HOST_IP` (ex. `192.168.1.50`).
2. Certs DoH générés (`scripts/generate-certs.sh` ou `.ps1`).
3. `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

## DHCP Freebox

| Champ | Valeur recommandée |
| --- | --- |
| DNS primaire | `HOST_IP` (dns-libre, port 53) |
| DNS secondaire | `91.239.100.100` (UncensoredDNS — repli si VM down) |
| Passerelle | laissée à Freebox (`192.168.1.254` typique) |

Ne pas mettre `ns0.free.fr` / `ns1.free.fr` en primaire.

## DoH (navigateurs / apps)

- Libre : `https://HOST_IP:8453/dns-query`
- Secure (ads/malware) : `https://HOST_IP:8444/dns-query`

## UI Blocky

`http://HOST_IP:3080` — LAN only (bind `HOST_IP`).

## Fichier machine

Voir aussi `config/freebox/dhcp-dns.json` (paramètres structurés pour forks / automatisation locale).
