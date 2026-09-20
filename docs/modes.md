# Modes DNS intelligents (« smart spit »)

« **Smart spit** » = quatre personnalités DNS séparées par port / DoH
(équivalent pratique d’un *smart split* — pas un seul Pi-hole FTL + groupes clients).

La **machine** héberge son propre DNS. Chaque mode applique la même chaîne :

```text
1. Listes / hosts LOCAUX   (anti-lie, seeds critiques)
2. Filtre du MODE         (aucun | malware | antipub | full)
3. Forward Unbound        (DoT uncensoring, puis root / serve-expired)
4. Jamais de censure FR   (pas de page ANJ/DGCCRF en vérité locale)
```

## Matrice canonique

| Mode | Service | Port (lab) | Order |
| --- | --- | --- | --- |
| **uncensored** | `dns-libre` | `5356` (prod `:53`) | `hosts → Unbound → (dnsproxy fallbacks)` |
| **malware** | `dns-malware` | `5357` | `hosts → malware denylist → Unbound` |
| **antipub** | `dns-antipub` | `5358` | `hosts → pihole + ublock + anti_adblock → Unbound` |
| **secure** | `dns-secure` | `5354` | `hosts → pihole + ublock + anti_adblock + malware → Unbound` |

Source machine : [`config/blocky/modes.json`](../config/blocky/modes.json) (régénéré par `scripts/generate-blocky-modes.py`).

### Ports chiffrés (lab)

| Mode | DoH | DoT | DoQ | UI |
| --- | --- | --- | --- | --- |
| uncensored | `:8453` | `:8853` (prod `:853`) | `:8853/udp` (prod `:853/udp`) | — |
| malware | `:8445` | `:8855` | — | — |
| antipub | `:8446` | `:8856` | — | — |
| secure | `:8444` | `:8854` | — | `:3080` + query log CSV |

## Détail par mode

### uncensored — `dns-libre` (dnsproxy)

- **Order** : hosts locaux → Unbound `172.28.0.10` → si Unbound down, fallbacks DoH/DoT/plain SOS (`dns-libre.yaml`)
- **Filtre** : aucun denylist
- **DHCP** : c’est le mode poussé en **DNS1** (`:53` prod)

### malware — `dns-malware` (Blocky)

- **Order** : hosts → groupe `malware` → Unbound
- **Filtre** : URLhaus, Spam404, KADhosts, HaGeZi TIF, … — **pubs encore résolues**

### antipub — `dns-antipub` (Blocky)

- **Order** : hosts → `pihole` + `ublock` + `anti_adblock` → Unbound
- **Filtre** : gravity Pi-hole + HaGeZi/Firebog/OISD + Admiral / anti-adblock
- **Sans** listes malware

### secure — `dns-secure` (Blocky)

- **Order** : hosts → `pihole` + `ublock` + `anti_adblock` + `malware` → Unbound
- **Filtre** : antipub **+** malware
- **Extras** : UI Blocky `:3080`, query log CSV 7 j (`config/blocky/querylog/`)

## DHCP (tout routeur)

| DNS1 | DNS2 |
| --- | --- |
| IP du résolveur = **uncensored** `:53` | SOS `9.9.9.10` (Quad9) |

Les modes `malware` / `antipub` / `secure` se choisissent par **port Do53**, **DoH** ou profil généré — **ne jamais** mettre un mode filtré seul en DNS1 sans filet SOS.

Chaîne Unbound : [resilience.md](resilience.md) · listes : [filtering.md](filtering.md) · transports : [encrypted-dns.md](encrypted-dns.md).

## Config / génération

```bash
python3 scripts/generate-blocky-modes.py   # YAML Blocky + modes.json
python3 scripts/generate-client-profiles.py
bash scripts/blocky-refresh-lists.sh       # gravity refresh
```

| Fichier | Rôle |
| --- | --- |
| `config/blocky/modes.json` | Catalogue modes + ports + order |
| `config/blocky/config-malware.yml` | Mode malware |
| `config/blocky/config-antipub.yml` | Mode antipub |
| `config/blocky/config.yml` | Mode secure |
| `config/dnsproxy/dns-libre.yaml` | Mode uncensored |

Amont filtré : **toujours** Unbound `172.28.0.10` (pas de DoT direct depuis Blocky).

## Tests rapides

```bash
# Uncensored (lab :5356 / prod :53)
dig @$HOST_IP -p 5356 example.com +short

# Malware — ads encore résolus en général
dig @$HOST_IP -p 5357 doubleclick.net +short

# Antipub — ads → NXDOMAIN
dig @$HOST_IP -p 5358 doubleclick.net +short

# Secure = antipub + malware
dig @$HOST_IP -p 5354 doubleclick.net +short
dig @$HOST_IP -p 5354 example.com +short

bash scripts/health-check.sh
```

Profils clients : `config/clients/generated/`.

---

## Sources & crédits

**[CREDITS.md](CREDITS.md)** · Pages : [modes.html](https://dlnraja.github.io/freebox-dns/guides/modes.html)
