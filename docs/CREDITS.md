# Crédits, citations et sources

Ce projet **freebox-dns** assemble des logiciels libres, des listes de blocage et des méthodes de mesure publiées par d’autres.  
**Rien ici ne prétend remplacer ni s’approprier ces projets** : on les cite, on les configure, et on les orchestre en local.

Licence de *ce* dépôt : [MIT](../LICENSE).  
Les composants tiers conservent **leurs propres licences** — vérifiez-les avant redistribution commerciale.

---

## Moteur DNS (conteneurs)

| Projet | Rôle dans freebox-dns | Auteur / org | Lien | Licence typique |
| --- | --- | --- | --- | --- |
| **Unbound** | Résolveur validant + forward DoT | NLnet Labs | [nlnetlabs.nl/projects/unbound](https://www.nlnetlabs.nl/projects/unbound/) | BSD |
| **mvance/unbound** | Image Docker Unbound (amd64) | Matthew Vance | [hub.docker.com/r/mvance/unbound](https://hub.docker.com/r/mvance/unbound) | voir image |
| **knfrmity/unbound-rpi64** | Image Unbound ARM64 (Freebox / Pi) | knfrmity (fork mvance) | [hub.docker.com/r/knfrmity/unbound-rpi64](https://hub.docker.com/r/knfrmity/unbound-rpi64) | voir image |
| **dnsproxy** | dns-libre (DoH / DoT / DoQ) | AdGuard | [github.com/AdguardTeam/dnsproxy](https://github.com/AdguardTeam/dnsproxy) | Apache-2.0 |
| **Blocky** | dns-secure (filtrage + UI) | 0xERR0R | [github.com/0xERR0R/blocky](https://github.com/0xERR0R/blocky) | Apache-2.0 |
| **Docker / Compose** | Orchestration | Docker Inc. / Moby | [docs.docker.com/compose](https://docs.docker.com/compose/) | Apache-2.0 |
| **Debian cloud** | Base QCOW2 Freebox VM | Debian Project | [cloud.debian.org](https://cloud.debian.org/) | DFSG |

---

## Inspiration produits (features mappées, pas de code copié)

| Projet | Ce qu’on reprend | Ce qu’on n’embarque pas | Lien |
| --- | --- | --- | --- |
| **Pi-hole** | Gravity multi-listes, whitelist, NXDOMAIN, UI stats | DHCP Pi-hole, teleporter cloud | [pi-hole.net](https://pi-hole.net/) · [github.com/pi-hole](https://github.com/pi-hole) |
| **uBlock Origin** | Intelligence EasyList/EasyPrivacy / annoyances via listes DNS | Filtres cosmétiques, scriptlets navigateur | [github.com/gorhill/uBlock](https://github.com/gorhill/uBlock) |
| **NextDNS** | Bit sémantique *threat-local* (pin Freebox #4) | Cloud, profils parentaux, SafeSearch | [nextdns.io](https://nextdns.io/) |

---

## Listes de blocage (dns-secure / Blocky)

| Liste / projet | Groupe Blocky | URL | Auteur |
| --- | --- | --- | --- |
| StevenBlack hosts | `pihole` | [github.com/StevenBlack/hosts](https://github.com/StevenBlack/hosts) | Steven Black |
| AdAway | `pihole` | [adaway.org](https://adaway.org/) | AdAway |
| anudeepND adservers | `pihole` | [github.com/anudeepND/blacklist](https://github.com/anudeepND/blacklist) | anudeepND |
| Peter Lowe / yoyo | `pihole` | [pgl.yoyo.org/adservers](https://pgl.yoyo.org/adservers/) | Peter Lowe |
| Prigent-Ads (Firebog) | `pihole` | [v.firebog.net](https://v.firebog.net/) | Firebog / Prigent |
| HaGeZi multi / popupads / tif.medium | `ublock` / `malware` | [github.com/hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists) | HaGeZi |
| EasyPrivacy / AdguardDNS / Admiral (Firebog) | `ublock` / `anti_adblock` | [v.firebog.net](https://v.firebog.net/) | Firebog mirrors |
| OISD small | `ublock` | [oisd.nl](https://oisd.nl/) | sjhgvr |
| URLhaus | `malware` | [urlhaus.abuse.ch](https://urlhaus.abuse.ch/) | abuse.ch |
| Spam404 | `malware` | [github.com/Spam404/lists](https://github.com/Spam404/lists) | Spam404 |
| KADhosts | `malware` | [github.com/PolishFiltersTeam/KADhosts](https://github.com/PolishFiltersTeam/KADhosts) | Polish Filters Team |
| DandelionSprout Anti-Malware | `malware` | [github.com/DandelionSprout/adfilt](https://github.com/DandelionSprout/adfilt) | Dandelion Sprout |

Manifeste machine : [`config/blocky/lists/filter-intelligence.json`](../config/blocky/lists/filter-intelligence.json).

---

## Résolveurs amont (uncensoring / bootstrap)

| Service | Usage | Lien |
| --- | --- | --- |
| **UncensoredDNS** | Pin #1, DoT/DoH uncensoring | [uncensoreddns.org](https://blog.uncensoreddns.org/) |
| **Digitale Gesellschaft** | Pin #2, DoT/DoH privacy CH | [digitale-gesellschaft.ch](https://www.digitale-gesellschaft.ch/dns/) |
| **Quad9 No Threat Blocking** (`9.9.9.10`) | SOS #1 / bootstrap *unblocked*, **sans ECS** (≠ Secured `.9`, ≠ ECS `.11`/`.12`) — [docs/quad9.md](quad9.md) | [docs.quad9.net/services](https://docs.quad9.net/services/) |
| **Mullvad DNS** | DoT/DoH unfiltered | [mullvad.net/en/help/dns-over-https-and-dns-over-tls](https://mullvad.net/en/help/dns-over-https-and-dns-over-tls) |
| **dns0.eu OPEN** | DoT/DoH open | [dns0.eu](https://www.dns0.eu/) |
| **Applied Privacy** | DoT | [appliedprivacy.net](https://appliedprivacy.net/) |
| **LibreDNS** | DoT unfiltered | [libredns.gr](https://libredns.gr/) |
| **LavaDNS** | DoT EU | [lavate.ch](https://www.lavate.ch/) |
| **Public RDNS Open** | DoT | [public-rdns.com](https://public-rdns.com/) |
| **Control D Uncensored** | DoT | [controld.com](https://controld.com/) |
| **AdGuard Non-filtering** | DoT/DoH | [adguard-dns.io](https://adguard-dns.io/) |

Catalogue : [`config/upstreams/uncensoring-catalog.json`](../config/upstreams/uncensoring-catalog.json).

---

## Mesure de censure / OSINT

| Projet / article | Rôle | Lien |
| --- | --- | --- |
| **OONI Probe** | Méthodologie anti–DNS menteur (inspiré, scripts locaux) | [ooni.org](https://ooni.org/) · risques : [ooni.org/about/risks](https://ooni.org/about/risks/) |
| **OONI France report** | Contexte censure DNS FR | [ooni.org/post/2025-france-report](https://ooni.org/post/2025-france-report/) |
| **Citizen Lab** (test lists FR) | Cibles de sonde | [github.com/citizenlab/test-lists](https://github.com/citizenlab/test-lists) |
| **censxres.fr** | Technique pages de blocage FR | [censxres.fr/technique](https://censxres.fr/technique/) |
| **Korben — OONI Probe** | Vulgarisation mesure censure | [korben.info/ooni-probe-…](https://korben.info/ooni-probe-mesurer-niveau-de-manipulation-surveillance-censure-de-internet.html) |
| **Korben — Web-Check** | OSINT radiographie site | [korben.info/web-check-…](https://korben.info/web-check-outil-osint-analyse-site-securite.html) |
| **Web-Check** (Lissy93) | Conteneur optionnel `profile: osint` | [github.com/Lissy93/web-check](https://github.com/Lissy93/web-Check) |

Scripts locaux (pas d’upload OONI) : `scripts/ooni-like-anti-lie.py`, `scripts/web-connectivity-lite.py`.

---

## Plateforme Freebox / cloud-init

| Source | Usage | Lien |
| --- | --- | --- |
| **Freebox OS API v8** | Auth, FS, VM, DHCP (local) | [dev.freebox.fr](https://dev.freebox.fr/) |
| **cloud-init** | Bootstrap VM | [cloud-init.io](https://cloud-init.io/) |
| **Debian** | Guest Freebox VM | [debian.org](https://www.debian.org/) |

---

## Standards

| RFC / spec | Transport |
| --- | --- |
| RFC 1035 | DNS classique |
| RFC 7858 | DNS over TLS (DoT) |
| RFC 8484 | DNS over HTTPS (DoH) |
| RFC 9250 | DNS over QUIC (DoQ) |
| RFC 8767 | Serve-stale (résilience Unbound) |
| RFC 7816 | QNAME minimization (récursion) |

---

## Benchmarks & discussions publiques

| Source | Usage | Lien |
| --- | --- | --- |
| **CaptainDNS — Quad9** | Guide ops FR (tests, DoH HTTP/2, pièges) → [quad9.md](quad9.md) | [captaindns.com/fr/blog/dns-9999-quad9](https://www.captaindns.com/fr/blog/dns-9999-quad9) |
| **CaptainDNS — comparatif** | Cas d’usage publics | [captaindns.com/…/public-dns-resolver…](https://www.captaindns.com/fr/blog/public-dns-resolver-benchmark-comparison-guide) |
| **Quad9 DoH HTTP/1.1 retirement** | HTTP/2 obligatoire depuis 2025-12-15 | [quad9.net/news/…](https://quad9.net/news/blog/doh-http-1-1-retirement/) |
| **r/dns** (1.1.1.1 vs 9.9.9.9 vs OpenDNS) | Synthèse communauté → [public-dns-landscape.md](public-dns-landscape.md) | [reddit.com/r/dns/…](https://www.reddit.com/r/dns/comments/1fv5f9u/what_dns_do_you_recommend_1111_vs_9999_vs_opendns/) |
| **Nexxwave** malware DNS tests | Justification du filtrage **local** vs resolveurs « Secure » | [2025](https://techblog.nexxwave.eu/public-dns-malware-filters-to-be-tested-in-2025/) · [2024](https://techblog.nexxwave.eu/public-dns-malware-filters-tested-in-2024/) |
| **Quad9 forwarder best practices** | Cache / dual-IP côté forwarder | [docs.quad9.net](https://docs.quad9.net/Quad9_For_Organizations/DNS_Forwarder_Best_Practices/) |
| **Pi-hole + Unbound guide** | Schéma voisin Blocky→Unbound | [docs.pi-hole.net](https://docs.pi-hole.net/guides/dns/unbound/) |
| **Control D free DNS** | Profils (uncensored déjà catalogue ; malware = réf. bench) | [controld.com/free-dns](https://controld.com/free-dns) |

---

## Comment citer freebox-dns

```text
freebox-dns — dual local DNS (dns-libre + dns-secure) for Freebox / Pi / WSL
https://github.com/dlnraja/freebox-dns
Licence MIT. See docs/CREDITS.md for third-party attribution.
```

Guides illustrés : [GitHub Pages](https://dlnraja.github.io/freebox-dns/).

---

## Remerciements

Merci aux mainteneurs des listes, résolveurs non censeurs, OONI / Citizen Lab, Korben pour la vulgarisation, et aux auteurs Unbound / dnsproxy / Blocky / Pi-hole / uBlock Origin — sans lesquels ce stack n’existerait pas.
