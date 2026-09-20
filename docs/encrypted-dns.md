# DNS chiffré local — Do53 / DoT / DoH / DoQ / DNSCrypt

Voir aussi : [filtering.md](filtering.md) · [quad9.md](quad9.md) · [`config/dnscrypt/`](../config/dnscrypt/) · profils : [`config/clients/generated/`](../config/clients/generated/).

## Matrice des transports (LAN, bind `HOST_IP`)

| Transport | Libre (uncensor) | Secure | Client typique |
| --- | --- | --- | --- |
| **Do53** (classique) | `:5356` lab / `:53` prod | `:5354` | DHCP Freebox, IoT |
| **DoH** (HTTPS) | `:8453` `/dns-query` | `:8444` | Firefox, Chrome, iOS |
| **DoT** (TLS :853) | `:8853` lab / `:853` prod | `:8854` | Android apps, Stuby |
| **DoQ** (QUIC) | `:8853/udp` lab / `:853/udp` prod | — | AdGuard / dnsproxy |
| **DNSCrypt** proxy | `:5359` → Quad9 nofilter | — | Tests / fallback chiffré |
| **DNSCrypt** server | `:8443` `sdns://` (profile) | — | Nebulo, dnscrypt-proxy |

DHCP reste **Do53 only** : DNS1=`HOST_IP`, DNS2=`9.9.9.10` (SOS) — le chiffrement se fait vers le résolveur (DoH/DoT/DoQ/DNSCrypt), pas dans le DHCP.

```bash
bash scripts/generate-certs.sh
python3 scripts/generate-client-profiles.py
docker compose up -d
# DNSCrypt proxy (Quad9 via DNSCrypt) inclus dans `up -d`
# DNSCrypt server LAN (optionnel) :
bash scripts/dnscrypt-server-init.sh
docker compose --profile dnscrypt-server up -d dnscrypt-libre
```

## Routeur / clients

1. **DHCP** (après health) — Do53 :
   - DNS1 = IP du résolveur (Pi / VM / Windows)
   - DNS2 = `9.9.9.10` (Quad9 No Threat Blocking, SOS)
2. **DoH** : `https://HOST_IP:8453/dns-query` (libre) · `:8444` (secure)
3. **DoT** : `tls://HOST_IP:853` (prod) / `:8853` (lab)
4. **DoQ** : `quic://HOST_IP:853` (prod, libre only)
5. **DNSCrypt** :
   - Proxy : `dig @HOST_IP -p 5359 example.com` (trafic sortant en DNSCrypt vers Quad9)
   - Server : stamp dans `config/clients/generated/dnscrypt-stamp.txt` après init
6. iOS / Firefox / Windows : profils générés (DoH)

## Architecture

```text
Do53 / DoH / DoT / DoQ  →  dns-libre / Blocky  →  Unbound (DoT catalogue)
DNSCrypt :5359          →  dnscrypt-proxy      →  Quad9 DNSCrypt nofilter
DNSCrypt :8443 (opt.)   →  dnscrypt-libre      →  dns-libre → Unbound
```

## Fallbacks chiffrés (amont dns-libre)

Si Unbound est down : DoH/DoT Mullvad, `dns10.quad9.net`, AdGuard NF, etc. — `config/dnsproxy/dns-libre.yaml`.

### Quad9 DoH = HTTP/2 minimum

Depuis 2025-12-15 ([annonce](https://quad9.net/news/blog/doh-http-1-1-retirement/)).  
Fallback : DoT ou **DNSCrypt** Quad9 nofilter (`config/dnscrypt/quad9-nofilter.stamps`).

## Tests

```bash
# Do53
dig @$HOST_IP -p 5356 example.com +short

# DoH
curl -sk "https://$HOST_IP:8453/dns-query?name=example.com&type=A"

# DNSCrypt proxy (→ Quad9 via DNSCrypt)
dig @$HOST_IP -p 5359 example.com +short

# Suite health (inclut DNSCrypt proxy si up)
bash scripts/health-check.sh
python3 scripts/quad9-ops-check.py
```

## Sources

[CREDITS.md](CREDITS.md) · [CaptainDNS Quad9](https://www.captaindns.com/fr/blog/dns-9999-quad9) · [Quad9 DNSCrypt](https://quad9.net/dnscrypt/) · [dnscrypt-server](https://github.com/DNSCrypt/dnscrypt-server-docker)
