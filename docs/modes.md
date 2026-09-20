# Modes DNS intelligents (smart spit)

La VM **héberge son propre DNS**. Chaque mode applique le même **smart split** :

```text
1. Listes / hosts LOCAUX   (anti-lie, seeds critiques)
2. Filtre du MODE         (aucun | malware | antipub | full)
3. Forward Unbound        (DoT uncensoring, puis root / serve-expired)
4. Jamais de censure FR   (pas de page ANJ/DGCCRF en vérité locale)
```

| Mode | Service | Port DNS (lab) | DoH | Filtre |
| --- | --- | --- | --- | --- |
| **uncensored** | `dns-libre` | `5356` (prod `:53`) | `:8453` | Aucun denylist |
| **malware** | `dns-malware` | `5357` | `:8445` | Menaces / phishing uniquement |
| **antipub** | `dns-antipub` | `5358` | `:8446` | Pubs + trackers + anti–anti-adblock |
| **secure** | `dns-secure` | `5354` | `:8444` | antipub **+** malware |

DHCP Freebox recommandé : DNS1 = SOS `91.239.100.100`, DNS2 = IP VM (**uncensored** `:53`).  
Les autres modes se choisissent par **port** ou URL **DoH** (téléphone / navigateur / profil généré).

## Antipub intelligent

Groupes Blocky `pihole` + `ublock` + `anti_adblock` :

- Gravity type Pi-hole (StevenBlack, AdAway, …)
- Intelligence type uBlock via HaGeZi wildcard + Firebog + OISD
- Cassage des murs anti-adblock (Admiral, Funding Choices, …)

Sans listes malware (réservé au mode `malware` / `secure`).

## Malware-free

Uniquement le groupe `malware` (URLhaus, Spam404, KADhosts, HaGeZi TIF, …).  
Les pubs **passent** — utile pour un NAS / TV où l’on veut la sécurité sans casser les pubs « utiles ».

## Config

- Générateur : `python3 scripts/generate-blocky-modes.py`
- Catalogue : `config/blocky/modes.json`
- YAML : `config-malware.yml`, `config-antipub.yml`, `config.yml` (secure)
- Amont filtré : **toujours** Unbound `172.28.0.10` (plus de DoT direct depuis Blocky)

## Tests rapides

```bash
# Uncensored
dig @$HOST_IP -p 53 example.com +short
# Malware (ads encore résolus en général)
dig @$HOST_IP -p 5357 doubleclick.net +short
# Antipub (ads → NXDOMAIN)
dig @$HOST_IP -p 5358 doubleclick.net +short
# Secure = antipub + malware
dig @$HOST_IP -p 5354 doubleclick.net +short
```

Profils clients : `python3 scripts/generate-client-profiles.py` → `config/clients/generated/`.

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).

