# Identité des 5 DNS épinglés (FREEBOX_DNS_1..5)

Pins **plain UDP** pour DHCP SOS / bootstrap (prouvés joignables depuis Freebox LAN FR).  
UncensoredDNS + Digitale Gesellschaft restent dans le **catalogue DoT** (UDP/53 souvent filtré).

| Pin | IP | Nom | Lexique | Rôle |
| --- | --- | --- | --- | --- |
| FREEBOX_DNS_1 | `9.9.9.10` | **Quad9 Unsecured** | Unsecured / unblocked (≠ Secured `9.9.9.9`) | DHCP SOS #1 + bootstrap rapide |
| FREEBOX_DNS_2 | `194.242.2.2` | **Mullvad Unfiltered** | unfiltered, privacy, DoT/DoH | DHCP SOS #2 + amont DoT |
| FREEBOX_DNS_3 | `94.140.14.140` | **AdGuard Non-filtering** | non-filtering (≠ dns.adguard.com) | DHCP SOS #3 |
| FREEBOX_DNS_4 | `45.90.28.0` | **NextDNS** | firewall DNS, denylist, profiles | Donneur du bit `threat-local` — **pas** amont primaire |
| FREEBOX_DNS_5 | `192.168.1.254` | **Passerelle Freebox** | gateway, LAN, last hop | Bit `lan-gateway` — bind local-only + repli ultime |

## Bits locaux

| Service | Bit | Pins inspirateurs |
| --- | --- | --- |
| **dns-libre** | `uncensored` | #1 + #2 + #3 (+ catalogue DoT UncensoredDNS/DG) |
| **dns-secure** | `threat-local` | #4 (lexique denylist, filtrage **local**) |
| **site** | `lan-gateway` | #5 |

**Amonts complémentaires** : Mullvad, dns0.eu, Digitale Gesellschaft, UncensoredDNS — dans `config/unbound/forward-records.conf` et `config/upstreams/uncensoring-catalog.json`.

## Ordre opérationnel

1. **dns-libre** : Unbound (DoT complémentaires) ; fallback pins **1 → 2 → 3 → 5**.
2. **dns-secure** : Blocky denylist locale ; amont Unbound (même DoT).
3. **DHCP Freebox** : DNS1 = `FREEBOX_DNS_1` (`9.9.9.10`) ; DNS2 = `HOST_IP` (VM).
