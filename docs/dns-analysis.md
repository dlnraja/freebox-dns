# Analyse des DNS épinglés + amonts complémentaires

Verdict court : **garder 1–2–3–5 comme filet de secours LAN** ; **ne plus s’appuyer sur NextDNS (4) comme amont principal** ; **le vrai « DNS du projet » = stack locale** (dns-libre + dns-secure).

Lexique fin de chaque pin et dérivation locale : **[dns-lexicon.md](dns-lexicon.md)**.

## Les 5 DNS capturés sur la Freebox

| # | IP | Identité | Avantages | Inconvénients | Rôle dans ce projet |
| --- | --- | --- | --- | --- | --- |
| 1 | `91.239.100.100` | **UncensoredDNS** | Anti-censure explicite, DoT/DoH, indépendant des opérateurs FR | Moins d’anycast mondial que Cloudflare/Google → latence variable | ✅ Amont DoT + fallback |
| 2 | `185.95.218.42` | **Digitale Gesellschaft** (CH) | Privacy suisse, pas de filtre politique, DoT solide | Serveurs EU/CH ; moins « proche » hors Europe | ✅ Amont DoT prioritaire |
| 3 | `9.9.9.10` | **Quad9 unblocked** (+ ECS) | Très rapide (anycast), **sans** blocklist Quad9 (contrairement à `9.9.9.9`) | ECS peut exposer un préfixe réseau ; pas « zéro log » absolu | ✅ Bootstrap + fallback rapide |
| 4 | `45.90.28.0` | **NextDNS** anycast | Souvent déjà poussé par Freebox/apps | Sans ID de profil : comportement flou ; avec profil : filtres possibles ≠ « libre » | ⚠️ **Fallback dernier recours seulement** |
| 5 | `192.168.1.254` | **Passerelle Freebox** | Toujours joignable sur le LAN si Internet amont tombe | Résolveur opérateur / politiques Free possibles (« DNS menteur ») | ⚠️ **Repli LAN ultime uniquement** |

### Référence opérateur (ne pas utiliser en primaire)

| Nom | IP | Pourquoi éviter en primaire |
| --- | --- | --- |
| ns0/ns1.free.fr | `212.27.32.5` / `213.228.0.168` | DNS FAI : risque censure / NXDOMAIN politiques |

## Amonts complémentaires retenus (meilleurs pour ce projet)

Objectif : **non censure + DoT + diversité géographique/juridique**, complémentaires aux pins Freebox.

| Amont | Endpoint DoT | Pourquoi |
| --- | --- | --- |
| **Mullvad DNS** | `dns.mullvad.net` | Zéro filtre, zéro log revendiqué, DoT/DoH mature |
| **dns0.eu** | `dns0.eu` | EU, orientation privacy / anti-malware optionnelle — on utilise la variante **plain** non « kids » |
| Digitale Gesellschaft | `dns.digitale-gesellschaft.ch` | Déjà excellent (pin #2) |
| UncensoredDNS | `anycast.uncensoreddns.org` | Déjà excellent (pin #1) |
| Quad9 unblocked | `dns.quad9.net` via `9.9.9.10` | Bootstrap rapide seulement |

**Exclus volontairement comme amonts primaires :** Google `8.8.8.8`, Cloudflare `1.1.1.1` (centralisation + politiques commerciales), DNS Free, NextDNS profilé, Quad9 `9.9.9.9` (filtre malware distant — on filtre **en local** sur dns-secure).

## Architecture « ton propre DNS local »

```text
Clients LAN (Freebox DHCP / Pi / VM)
        │
        ├──────────── dns-libre  (non filtré)  ──► Unbound ──► DoT complémentaires
        │                 │                         └── fallback pins Freebox 1–3 (pas NextDNS/gateway sauf dernier recours)
        │
        └──────────── dns-secure (ads + malware only) ──► DoT complémentaires
                          └── listes locales Blocky (Pi-hole-like)
```

- **Exposition : local-only** → bind sur `HOST_IP` (LAN), pas d’écoute Internet publique.
- **Deux personnalités** : libre vs secure (comme Pi-hole + « unfiltered » côte à côte).
- **CI GitHub** : valide compose, sonde amonts DoT, sondes blocklists — **jamais** de poll distant de ta Freebox.

## Cibles de déploiement

| Cible | Fichiers |
| --- | --- |
| Freebox Delta / Ultra VM | `config/freebox/`, `docs/freebox.md`, `docker-compose.prod.yml` |
| Raspberry Pi OS | `docs/deploy-pi.md`, `cloud-init/pi-user-data.yaml` |
| Windows / WSL lab | ports `5356`/`5354` (5353 souvent pris par mDNS) |
