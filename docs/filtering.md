# Modèle de filtrage (lexique pins → local)

Voir le glossaire : [dns-lexicon.md](dns-lexicon.md) · **modes smart spit** : [modes.md](modes.md) · catalogue : [`config/blocky/lists/filter-intelligence.json`](../config/blocky/lists/filter-intelligence.json)

Chaîne commune : **hosts locaux → filtre du mode → Unbound (DoT) → monde**.

## uncensored — `dns-libre`

Inspiré de **UncensoredDNS** (#1), **Digitale Gesellschaft** (#2), **Quad9 Unsecured** (#3).

- Pas de blocklists (*keine Sperrlisten*).
- Amonts DoT non censeurs via Unbound ; réponses *unblocked*.
- Objectif : éviter les « DNS menteurs » / pages ANJ·DGCCRF.

## malware — `dns-malware`

Menaces / phishing uniquement (groupe Blocky `malware`). Les pubs restent résolues.

## antipub — `dns-antipub`

Pare-feu pubs/trackers intelligent (**Pi-hole + uBlock Origin DNS + anti–anti-adblock**), sans listes malware.

## secure — `dns-secure` — bit `threat-local`

antipub **+** malware, sans cloud NextDNS ni contrôle parental.

### Features mappées intelligemment

| Source | Au DNS (Blocky) | Hors scope DNS |
| --- | --- | --- |
| **Pi-hole** | Gravity multi-listes, blacklist exacte, whitelist, groupes, NXDOMAIN, refresh 12h, UI `:3080`, query log CSV local (`secure`) | DHCP Freebox, teleporter, regex UI |
| **uBlock Origin** | HaGeZi `wildcard/multi` + `popupads`, EasyPrivacy/AdGuardDNS (Firebog), OISD small, malware | Filtres cosmétiques, scriptlets navigateur |
| **Anti–anti-adblock** | Firebog **Admiral** + `anti-adblock.txt` (Funding Choices, AdSafe…) | Masquage DOM — garder uBO dans le navigateur |

### Groupes Blocky

1. **`pihole`** — StevenBlack, AdAway, anudeepND, yoyo, Prigent-Ads, `ads-extra.txt`
2. **`ublock`** — HaGeZi multi + popupads (format *wildcard asterisk*, Blocky ≥0.23), EasyPrivacy, AdguardDNS, OISD small
3. **`anti_adblock`** — Admiral + `lists/anti-adblock.txt`
4. **`malware`** — URLhaus, Spam404, KADhosts, DandelionSprout, HaGeZi TIF medium

Allowlist commune : `config/blocky/lists/allowlist.txt` (GitHub, Freebox, mirrors…).  
Refresh forcé : `bash scripts/blocky-refresh-lists.sh`.  
UI + query log CSV (7 j) : mode **secure** → `http://HOST_IP:3080` · fichiers dans `config/blocky/querylog/`.

Parité détaillée : [pihole-parity.md](pihole-parity.md).

**Exclu volontairement** : parental, porn, SafeSearch, listes StevenBlack *gambling/social/porn*, censure nationale, logs cloud.

Les hosts anti-lie (`hosts.generated`) passent **avant** les denylists : on ne remplace jamais une vérité contrôle par une page de censure.

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
