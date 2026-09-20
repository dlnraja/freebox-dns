# DHCP Freebox (option) — filet SOS

Sans Freebox : même logique sur tout routeur — [wifi-lan.md](wifi-lan.md).

| Rôle | Valeur |
| --- | --- |
| **DNS1** | IP LAN du résolveur (`dns-libre` `:53`) |
| **DNS2** | `9.9.9.10` (Quad9 No Threat Blocking — SOS) |
| DNS3 (optionnel) | `194.242.2.2` (Mullvad) |

UncensoredDNS (`91.239.100.100`) et Digitale Gesellschaft : **DoT uniquement** sur certains FAI — ne pas les mettre en DHCP.

Transports chiffrés vers le résolveur (pas dans le DHCP) : DoH `:8453` / `:8444`, DoT `:853`, DoQ, DNSCrypt — [encrypted-dns.md](encrypted-dns.md).
