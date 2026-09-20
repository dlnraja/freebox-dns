# Catalogue amonts DNS libres / sans censure

Source de vérité machine : [`config/upstreams/uncensoring-catalog.json`](../config/upstreams/uncensoring-catalog.json).

Politique : **zéro censure politique**, **zéro parental amont**, **zéro filtre pub amont**. Ads/malware uniquement sur **dns-secure** local.

## DoT uncensoring (max)

| ID | TLS name | IPv4 | Notes |
| --- | --- | --- | --- |
| mullvad | `dns.mullvad.net` | `194.242.2.2` | FREEBOX_DNS_2 + SOS #2 |
| dns0_open | `open.dns0.eu` | `193.110.81.254`, `185.253.5.254` | Tier **open** non filtré |
| digitale_gesellschaft | `dns.digitale-gesellschaft.ch` | `185.95.218.42`, `.43` | DoT-only sur FR ISP |
| uncensoreddns_anycast | `anycast.uncensoreddns.org` | `91.239.100.100` | DoT-only sur FR ISP |
| uncensoreddns_unicast | `unicast.uncensoreddns.org` | `89.233.43.71` | Copenhague |
| quad9_unsecured | `dns10.quad9.net` | `9.9.9.10`, `149.112.112.10` | FREEBOX_DNS_1 — SOS UDP #1 |
| applied_privacy | `dot1.applied-privacy.net` | `146.255.56.98` | AT non-profit |
| libredns | `dot.libredns.gr` | `116.202.176.26` | Pas `noads` |
| lavadns | `eu1.dns.lavate.ch` | `95.217.25.217` | No log / no ECS / no filter |
| public_rdns_open | `open.public-rdns.com` | `37.27.125.213` | Tier Open |
| radeksprta | `dns.radeksprta.eu` | `80.211.208.74` | CZ |
| controld_uncensored | `uncensored.freedns.controld.com` | `76.76.2.5`, `.10.5` | Profil uncensored only |
| adguard_unfiltered | `dns-unfiltered.adguard.com` | `94.140.14.140`, `.141` | FREEBOX_DNS_3 — SOS #3 |

## Fallbacks plain (ordre)

1. SOS pins `9.9.9.10` → `194.242.2.2` → `94.140.14.140` (+ secondaries Quad9/AdGuard)
2. open.dns0 / Applied Privacy / LibreDNS / Lava / Public RDNS / CZ / Control D
3. Gateway `192.168.1.254`
4. Soft last : NextDNS `45.90.28.0`

UncensoredDNS / Digitale Gesellschaft : **pas** en plain fallback (DoT Unbound seulement).

## Exclus en primaire

Google, Cloudflare, Quad9 Secured `9.9.9.9`, DNS Free, NextDNS profilé, Mullvad adblock/family, AdGuard filtré, dns0.eu non-open.

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
