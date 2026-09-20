# Filet SOS Freebox DHCP

| Rôle | Valeur |
| --- | --- |
| DNS1 | `9.9.9.10` (Quad9 No Threat Blocking) |
| DNS2 | IP LAN de la VM (`dns-libre` `:53`) |
| DNS3 (optionnel) | `194.242.2.2` (Mullvad) |

UncensoredDNS (`91.239.100.100`) et Digitale Gesellschaft : **DoT uniquement** depuis le LAN Free — ne pas les mettre en DHCP SOS.

Transports chiffrés vers la VM (pas dans le DHCP) : DoH `:8453` / `:8444`, DoT `:853`, DoQ, DNSCrypt `:5359` / `:8443` — [encrypted-dns.md](encrypted-dns.md).
