# DNS chiffré local — DoH / DoT / DoQ (+ fallbacks)

Voir aussi : [filtering.md](filtering.md) · [anti-lie-dns.md](anti-lie-dns.md) · profils clients générés : [`config/clients/generated/`](../config/clients/generated/).

## Transports exposés (LAN only, `HOST_IP`)

| Transport | Libre (uncensor) | Secure (Pi-hole/uBO) | Client typique |
| --- | --- | --- | --- |
| Plain DNS | `:5356` lab / `:53` prod | `:5354` | DHCP Freebox, IoT |
| **DoH** (HTTPS) | `:8453` → `/dns-query` | `:8444` → `/dns-query` | Firefox, Chrome, iOS profile, apps |
| **DoT** (TLS) | `:8853` lab / `:853` prod | `:8854` | Android apps, Stuby, dig +tls |
| **DoQ** (QUIC) | `:8853/udp` lab / `:853/udp` prod | — | AdGuard, dnsproxy clients |

Certificats : `scripts/generate-certs.sh` (SAN = `freebox-dns.local` + `HOST_IP`).

```bash
bash scripts/generate-certs.sh          # FORCE_REGEN_CERTS=1 si IP change
python3 scripts/generate-client-profiles.py
docker compose up -d --force-recreate dns-libre dns-secure
```

## Freebox OS / app mobile

1. **DHCP** (après health VM) — filet SOS :
   - DNS1 = `9.9.9.10` (Quad9 No Threat Blocking, sans ECS)
   - DNS2 = IP de la VM freebox-dns
2. **Navigateurs / apps** qui parlent DoH : URL générée
   - Libre : `https://HOST_IP:8453/dns-query`
   - Secure : `https://HOST_IP:8444/dns-query`
3. **iOS / macOS** : installer `apple-doh-*.mobileconfig`
4. **Firefox** : policies JSON dans `config/clients/generated/`
5. **Android** : stock Private DNS = hostname seulement → utiliser Nebulo/Intra avec DoH, ou DoT `:853` en prod + nom local

La Freebox app elle-même suit le DNS DHCP ; le DoH est pour navigateurs / apps OS qui l’exposent.

## Fallbacks chiffrés (amont)

Si Unbound est down, dns-libre tente d’abord des amonts **DoH/DoT** (Mullvad, DG, Quad9 Unsecured, UncensoredDNS…) avant le plain — voir `config/dnsproxy/dns-libre.yaml`.

## Test rapide

```bash
# DoH
curl -sk "https://$HOST_IP:8453/dns-query?name=example.com&type=A"
curl -sk "https://$HOST_IP:8444/dns-query?name=example.com&type=A"
# DoT (si dig + openssl dispo)
# dig @HOST_IP -p 8853 +tls example.com
```

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
