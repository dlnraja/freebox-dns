# Paysage DNS public — synthèse communauté & benchmarks

Sources : fil [r/dns — 1.1.1.1 vs 9.9.9.9 vs OpenDNS](https://www.reddit.com/r/dns/comments/1fv5f9u/what_dns_do_you_recommend_1111_vs_9999_vs_opendns/) (oct. 2024) + liens cités + benchmarks Nexxwave 2024/2025.

Machine-readable : [`config/upstreams/community-dns-landscape.json`](../config/upstreams/community-dns-landscape.json).

## Verdict pour freebox-dns

Le consensus du fil **ne change pas** notre architecture — il la **valide** :

| Conseil communauté | Mapping freebox-dns |
| --- | --- |
| Filtrer **en local** (Pi-hole / Blocky / AdGuard Home) | `dns-secure` + Blocky gravity |
| Unbound en amont / cache | Unbound + `forward-first` DoT |
| Filet si le résolveur tombe | DHCP **DNS2** = **`9.9.9.10`** (No Threat Blocking) |
| Résolveur du salon | DHCP **DNS1** = IP Pi / VM / Windows |
| Malware **distant** (`.9`, `1.1.1.2`, ControlD malware…) | **Non** en primaire — on filtre **ici** |
| Cloudflare / OpenDNS / parental | **Exclus** en primaire |

Pourquoi pas `9.9.9.9` en SOS ? Le fil le recommande pour le **blocage malware distant**. Nous voulons un SOS **uncensored** (Internet intact si la VM est down) ; le malware reste sur `dns-secure`. Détail : [quad9.md](quad9.md).

## CaptainDNS (déc. 2025 / janv. 2026)

Articles : [DNS Quad9 9.9.9.9](https://www.captaindns.com/fr/blog/dns-9999-quad9) · [comparatif publics](https://www.captaindns.com/fr/blog/public-dns-resolver-benchmark-comparison-guide).

| Conseil CaptainDNS | Mapping freebox-dns |
| --- | --- |
| Forwarder local + DoT vers Quad9 | Unbound / dns-libre → `dns10.quad9.net` |
| Ne pas mélanger `.9` et `.10` | DHCP SOS = **uniquement** `.10` |
| `.10` = debug pour PME Secure | Chez nous `.10` = **SOS uncensor** (Secure = Blocky) |
| Tests `proto.on.quad9.net` / `isitblocked.org` | `scripts/quad9-ops-check.py` |
| DoH HTTP/2 depuis 2025-12-15 | Vérifié dans le script + fallback DoT |
| Cas « geek sans filtrage » → Quad9 unfiltered | Exactement notre SOS + `dns-libre` |

## Mentions dominantes du fil (ordre approx.)

Quad9 → AdGuard / NextDNS → Cloudflare `1.1.1.x` → Unbound / Pi-hole → Control D → OpenDNS (souvent dernier).

## Matrice « ce que les gens comparent »

| Produit | IPs typiques | Threat / parental | Verdict projet |
| --- | --- | --- | --- |
| Quad9 Secure | `9.9.9.9` | malware distant | Exclu primaire ; listes locales à la place |
| Quad9 No Threat | **`9.9.9.10`** | aucun filtre | **SOS #1** |
| Cloudflare | `1.1.1.1` | aucun | Exclu (centralisation, ECS signalé, incidents) |
| CF Families malware | `1.1.1.2` | malware | Exclu (filtre distant + US) |
| CF Families adult | `1.1.1.3` | malware + adult | Exclu (parental) |
| OpenDNS (Cisco) | `208.67.222.222` | catégories / FamilyShield | Exclu (parental / Cisco) |
| Control D Malware | `76.76.2.1` | malware (bench top) | Réf. perf listes — pas amont libre |
| Control D Uncensored | `76.76.2.5` | aucun | Déjà dans catalogue DoT |
| dns0.eu (filtré) | `193.110.81.0` | malware | Exclu ; on utilise **open.dns0.eu** |
| dns0.eu ZERO | zero.dns0.eu | malware agressif | Exclu |
| DNS4EU Protective | `86.54.11.1` | malware UE | Exclu primaire (filtre) |
| CleanBrowsing Security | `185.228.169.9` | security/family | Exclu |
| NextDNS | `45.90.28.0` | profil cloud | Lexique only — soft last resort |

## Benchmarks malware (Nexxwave)

| Année | Top blockers (domaine malveillant) | Lien |
| --- | --- | --- |
| 2025 | ControlD ≈100 %, dns0.eu ≈99 %, Quad9 ≈97 %, CF Families ≈96 %, DNS4EU ≈95 % | [nexxwave 2025](https://techblog.nexxwave.eu/public-dns-malware-filters-to-be-tested-in-2025/) |
| 2024 | ControlD, dns0, Quad9 en tête ; CF Families variable | [2024](https://techblog.nexxwave.eu/public-dns-malware-filters-tested-in-2024/) · [sept 2024](https://techblog.nexxwave.eu/public-dns-malware-filters-tested-in-september-2024/) |

**Lecture pour nous :** ces scores motivent des **listes locales solides** (URLhaus, HaGeZi TIF, etc. dans Blocky), pas de basculer le DHCP vers ControlD/Quad9 Secured.

## Liens utiles sortis du fil

| Lien | Intérêt |
| --- | --- |
| [CaptainDNS — Quad9](https://www.captaindns.com/fr/blog/dns-9999-quad9) | Opérations, tests, DoH HTTP/2, pièges mélange `.9`/`.10` |
| [CaptainDNS — comparatif](https://www.captaindns.com/fr/blog/public-dns-resolver-benchmark-comparison-guide) | Cas d’usage (geek / sécurité / famille / PME) |
| [Quad9 DoH HTTP/1.1 retirement](https://quad9.net/news/blog/doh-http-1-1-retirement/) | HTTP/2 obligatoire pour DoH Quad9 |
| [Quad9 forwarder best practices](https://docs.quad9.net/Quad9_For_Organizations/DNS_Forwarder_Best_Practices/) | Cache, dual IP, IPv6 ; DNSSEC/QNAME si *uniquement* Quad9 en forward |
| [Pi-hole + Unbound](https://docs.pi-hole.net/guides/dns/unbound/) | Même schéma que Blocky → Unbound |
| [Blocky](https://github.com/0xERR0R/blocky) | Notre filtre |
| [Control D free DNS](https://controld.com/free-dns) | Profils dont uncensored / malware |
| [dns0.eu ZERO](https://www.dns0.eu/de/zero) | Variante filtrée (≠ open) |
| [RFC 7816](https://datatracker.ietf.org/doc/html/rfc7816) | QNAME minimization (récursion) |
| [Phishing DNS filters (Medium)](https://medium.com/@nykolas.z/phishing-protection-comparing-dns-security-filters-9d5a09849b91) | Comparatif historique Quad9 vs CF vs OpenDNS |
| [trinib AdGuard+Unbound+DNScrypt](https://github.com/trinib/AdGuard-WireGuard-Unbound-DNScrypt) | Recette homelab voisine |

## Pratiques opérationnelles retenues

1. **Toujours deux DNS DHCP** (SOS + VM) — jamais la seule IP locale.
2. **Mesurer chez soi** (latence FR ≠ US) : [GRC DNS Benchmark](https://www.grc.com/dns/benchmark.htm) cité dans le fil.
3. **Ne pas mélanger** filtre distant + filtre local sans le savoir (double NXDOMAIN / faux positifs).
4. Cloudflare `1.1.1.1` envoie de l’**ECS** (signalé dans le fil) → mauvais fit privacy pour un SOS uncensoring.

Voir aussi [dns-analysis.md](dns-analysis.md) · [upstreams-uncensoring.md](upstreams-uncensoring.md) · [quad9.md](quad9.md) · [filtering.md](filtering.md).
