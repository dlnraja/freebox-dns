# Lexique des 5 DNS Freebox → personnalités locales

Chaque pin DHCP porte un **vocabulaire métier** distinct. Les DNS locaux du projet (`dns-libre`, `dns-secure`) ne copient pas les marques : ils **réutilisent ces bits sémantiques** pour rester cohérents avec ce que la Freebox annonce déjà.

## Matrice lexicale (pins)

| Pin | IP | Nom | Lexique officiel / bits | Ce qu’on **prend** | Ce qu’on **refuse** |
| --- | --- | --- | --- | --- | --- |
| **FREEBOX_DNS_1** | `9.9.9.10` | **Quad9 No Threat Blocking** | **Unsecured** / unblocked ; **pas** de threat-intel Quad9 ; **pas d’ECS** ; DNSSEC (depuis 2026-06-15) ; anycast ; ≠ Secured `9.9.9.9` / ≠ ECS `.11`/`.12` | Chemin *unblocked* + **SOS UDP** joignable sur Free | **Secured** distant — malware filtré **chez nous** |
| **FREEBOX_DNS_2** | `194.242.2.2` | **Mullvad Unfiltered** | unfiltered, privacy, DoT/DoH (pas adblock/family) | Privacy + réponses intactes | Profils adblock/family Mullvad |
| **FREEBOX_DNS_3** | `94.140.14.140` | **AdGuard Non-filtering** | non-filtering / unfiltered (≠ dns.adguard.com) | SOS #3 plain UDP | AdGuard « default » filtré |
| **FREEBOX_DNS_4** | `45.90.28.0` | **NextDNS** | *firewall for the modern Internet*, threat model, denylist/allowlist, configs/profiles, ads & trackers, analytics, block page, « Pi-hole in the cloud » | Dual-profil, denylist ads/malware, UI/analytics locale, modèle *threat* | Parental / porn / SafeSearch / censure morale / cloud obligatoire / logs longs |
| **FREEBOX_DNS_5** | `192.168.1.254` | **Passerelle Freebox** | gateway, LAN, toujours joignable, dernier hop site | *local-only*, repli LAN, résilience site | DNS FAI comme vérité primaire (« DNS menteur ») |

> **DoT-only sur Free ISP** : UncensoredDNS `91.239.100.100` et Digitale Gesellschaft `185.95.218.42` restent dans le catalogue Unbound DoT (UDP/53 souvent timeout / refused).

### Glossaire croisé

| Terme pin | Sens | Équivalent local |
| --- | --- | --- |
| Uncensored / censurfri | Pas de filtre politique | **dns-libre** — bit `uncensored` |
| Keine Sperrlisten | Aucune liste de blocage amont | Amonts DoT libres (Mullvad, dns0.eu, DG, UncensoredDNS) |
| Quad9 **No Threat Blocking** (`9.9.9.10`) | Pas de threat-intel Quad9, **pas d’ECS** | dns-libre = réponses intactes |
| Quad9 **Secured** (`9.9.9.9`) | Block malware *chez* Quad9 | **Non** — remplacé par filtrage **local** dns-secure |
| Quad9 **+ ECS** (`.11` / `.12`) | Préfixe client vers les autoritaires | **Non** — privacy SOS |
| NextDNS *configuration* / *profile* | Plusieurs politiques DNS | Exactement 2 profils locaux fixes |
| NextDNS *denylist* | Listes de blocage | Blocky groupes `pihole` + `ublock` + `anti_adblock` + `malware` |
| NextDNS *firewall* | Contrôle au niveau DNS | dns-secure = pare-feu DNS **LAN**, pas cloud |
| Gateway | Dernier recours local | Bind `HOST_IP` + pin #5 en fallback ultime |

---

## Personnalités locales (lexique dérivé)

### `dns-libre` — bit **`uncensored`**

Inspiré de **#1 UncensoredDNS** + **#2 Digitale Gesellschaft** + **#3 Quad9 Unsecured**.

| Champ | Valeur |
| --- | --- |
| Service Compose | `dns-libre` |
| Display name | Libre / Uncensored |
| Bit | `uncensored` |
| Tagline FR | Résolution complète, sans Sperrliste ni censure politique |
| Tagline EN | Full answers — uncensoring path (Quad9-Unsecured spirit, DG privacy transport) |
| Transport | Plain DNS + DoH `/dns-query` (esprit DoT/DoH DG & UncensoredDNS) |
| Filtrage | **Aucun** (ni ads, ni malware distant, ni politique) |
| Amonts | DoT complémentaires → fallback pins **1 → 2 → 3** → gateway **5** |
| Ne pas confondre avec | Quad9 Secured, NextDNS profilé, ns0.free.fr |

### `dns-secure` — bit **`threat-local`**

Inspiré du **toolkit** NextDNS (#4) et du *concept* Quad9 Secured, mais **exécuté en local** (Pi-hole-like), sans le pan parental/censure de NextDNS.

| Champ | Valeur |
| --- | --- |
| Service Compose | `dns-secure` |
| Display name | Secure / Threat-local |
| Bit | `threat-local` |
| Tagline FR | Pare-feu DNS local : Pi-hole + uBlock + anti–anti-adblock |
| Tagline EN | Local DNS firewall — Pi-hole gravity + uBlock-equivalent + anti-adblock (not NextDNS cloud) |
| Transport | Plain DNS + DoH + UI Blocky (analytics light) |
| Filtrage | Groupes `pihole` + `ublock` + `anti_adblock` + `malware` (voir `docs/filtering.md`) |
| Amonts | Mêmes DoT uncensoring que libre (le filtre est **ici**, pas chez Quad9/NextDNS) |
| Explicitement hors scope | Parental, porn blocks, SafeSearch, TLD bans politiques, logs cloud |

### Couche site — bit **`lan-gateway`**

Inspiré de **#5**.

| Champ | Valeur |
| --- | --- |
| Bit | `lan-gateway` |
| Règle | Publier uniquement sur `HOST_IP` (local-only) |
| Fallback DHCP | `FREEBOX_DNS_1` si la VM tombe ; `FREEBOX_DNS_5` seulement en dernier recours stack |

---

## Mapping opérationnel

```text
FREEBOX_DNS_1 Quad9 Unsecured ──lexique──►  dns-libre.bit = uncensoring + SOS UDP
FREEBOX_DNS_2 Mullvad Unfilt. ──lexique──►  privacy / unfiltered DoT
FREEBOX_DNS_3 AdGuard NF      ──lexique──►  unfiltered SOS #3
FREEBOX_DNS_4 NextDNS         ──lexique──►  dns-secure = dual profile + denylist
                                           (sans cloud / parental)
FREEBOX_DNS_5 Freebox GW      ──lexique──►  local-only bind + ultimate LAN fallback
DoT-only: UncensoredDNS + Digitale Gesellschaft ──► Unbound catalogue
```

Fichiers liés : `config/freebox-dns-snapshot.json` → `local_lexicon`, `config/freebox/dhcp-dns.json`, Compose `dns-libre` / `dns-secure`.

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
