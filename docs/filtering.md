# Modèle de filtrage (lexique pins → local)

Voir : [dns-lexicon.md](dns-lexicon.md) · **modes (smart spit)** : [modes.md](modes.md) · **parité Pi-hole** : [pihole-parity.md](pihole-parity.md) · catalogue : [`config/blocky/lists/filter-intelligence.json`](../config/blocky/lists/filter-intelligence.json)

Chaîne commune : **hosts locaux → filtre du mode → Unbound (DoT) → monde**.

| Mode | Service | Port (lab) | Order |
| --- | --- | --- | --- |
| **uncensored** | `dns-libre` | `5356` (prod `:53`) | hosts → Unbound → (dnsproxy fallbacks) |
| **malware** | `dns-malware` | `5357` | hosts → malware denylist → Unbound |
| **antipub** | `dns-antipub` | `5358` | hosts → pihole + ublock + anti_adblock → Unbound |
| **secure** | `dns-secure` | `5354` | hosts → pihole + ublock + anti_adblock + malware → Unbound |

Détail modes / ports DoH : [modes.md](modes.md).

## uncensored — `dns-libre`

Inspiré de **UncensoredDNS** (#1), **Digitale Gesellschaft** (#2), **Quad9 No Threat Blocking** (#3).

- Pas de blocklists (*keine Sperrlisten*).
- Amonts DoT non censeurs via Unbound ; réponses *unblocked*.
- Objectif : éviter les « DNS menteurs » / pages ANJ·DGCCRF.

## malware — `dns-malware`

Menaces / phishing uniquement (groupe Blocky `malware`). Les pubs restent résolues.

## antipub — `dns-antipub`

Pare-feu pubs/trackers intelligent (**Pi-hole + uBlock Origin DNS + anti–anti-adblock**), sans listes malware.

## secure — `dns-secure` — bit `threat-local`

antipub **+** malware, sans cloud NextDNS ni contrôle parental.

Les benches publics ([Nexxwave 2025](https://techblog.nexxwave.eu/public-dns-malware-filters-to-be-tested-in-2025/), fil [r/dns](https://www.reddit.com/r/dns/comments/1fv5f9u/what_dns_do_you_recommend_1111_vs_9999_vs_opendns/)) placent ControlD / dns0 / Quad9 Secured en tête du **blocage distant** — ici on reproduit l’intention avec des **listes locales** (URLhaus, HaGeZi TIF…) pour garder le contrôle et un SOS uncensoring. Voir [public-dns-landscape.md](public-dns-landscape.md).

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
**UI Blocky = mode secure uniquement** → `http://HOST_IP:3080` (malware/antipub ont `http:4000` en interne, **non publiés** sur l’hôte).  
Query log CSV (7 j, VM locale) : `config/blocky/querylog/` · `log.privacy: true` (pas de log verbeux type Pi-hole).  
Prometheus : **désactivé** (pas de Grafana dans ce dépôt).

Parité détaillée / hors scope : [pihole-parity.md](pihole-parity.md).

### Blocky HTTP API (secure → `:3080`)

API native Blocky (même port que l’UI). Exemples LAN-only :

```bash
# Santé / status
curl -s "http://HOST_IP:3080/api/blocking/status"

# Forcer un refresh des listes (équivalent soft de gravity)
curl -s -X POST "http://HOST_IP:3080/api/lists/refresh"

# Ou script projet
bash scripts/blocky-refresh-lists.sh
```

Référence amont : [Blocky API docs](https://0xerr0r.github.io/blocky/latest/api/). Ne pas exposer `:3080` sur Internet — [lan-only.md](lan-only.md).

**Exclu volontairement** : parental, porn, SafeSearch, listes StevenBlack *gambling/social/porn*, censure nationale, logs cloud, regex UI, groupes par client/MAC, teleporter, DHCP intégré.

Les hosts anti-lie (`hosts.generated`) passent **avant** les denylists : on ne remplace jamais une vérité contrôle par une page de censure.

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
