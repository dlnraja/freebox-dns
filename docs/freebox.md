# Freebox — configuration DHCP / DNS / DoH / DoT

## DHCP (après health VM uniquement)

Filet SOS recommandé :

| Priorité | Valeur |
| --- | --- |
| DNS1 | `91.239.100.100` (UncensoredDNS) |
| DNS2 | IP VM freebox-dns |

Ne jamais laisser la seule IP VM sans secondaire.

## DoH (navigateurs / Freebox app Web / mobiles)

- Libre : `https://HOST_IP:8453/dns-query`
- Secure : `https://HOST_IP:8444/dns-query`

Profils prêts à installer : `config/clients/generated/`  
(`python3 scripts/generate-client-profiles.py`)

## DoT / DoQ

| | Lab | Prod (compose.prod) |
| --- | --- | --- |
| DoT libre | `:8853` | `:853` |
| DoQ libre | `:8853/udp` | `:853/udp` |
| DoT secure | `:8854` | `:8854` |

Détail : [encrypted-dns.md](encrypted-dns.md).

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
