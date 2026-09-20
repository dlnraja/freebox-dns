# Analyse des DNS épinglés + amonts complémentaires

Verdict court : **garder 1–2–3–5 comme filet de secours LAN** ; **ne plus s’appuyer sur NextDNS (4) comme amont principal** ; **le vrai « DNS du projet » = stack locale** (dns-libre + dns-secure).

**Amonts max (libres / sans censure)** : catalogue [`config/upstreams/uncensoring-catalog.json`](../config/upstreams/uncensoring-catalog.json) — Mullvad, open.dns0.eu, DG, UncensoredDNS×2, Quad9 Unsecured, Applied Privacy, LibreDNS, LavaDNS, Public RDNS Open, RadekSprta, Control D Uncensored, AdGuard unfiltered. Doc : [upstreams-uncensoring.md](upstreams-uncensoring.md).

**VM Freebox OS** : [freebox-vm.md](freebox-vm.md) + [`packaging/freebox-vm/`](../packaging/freebox-vm/).

## Les 5 DNS capturés sur la Freebox

| # | IP | Identité | Avantages | Inconvénients | Rôle dans ce projet |
| --- | --- | --- | --- | --- | --- |
| 1 | `9.9.9.10` | **Quad9 No Threat Blocking** | Anycast, **sans** blocklist Quad9, **sans ECS** | DNSSEC strict depuis 2026-06 (SERVFAIL si zone cassée) | ✅ DHCP SOS #1 + bootstrap |
| 2 | `194.242.2.2` | **Mullvad Unfiltered** | Privacy, DoT/DoH, plain UDP OK sur Free | Moins d’anycast que Quad9 | ✅ DHCP SOS #2 + DoT |
| 3 | `94.140.14.140` | **AdGuard Non-filtering** | Plain UDP OK, unfiltered | Ne pas confondre avec AdGuard filtré | ✅ DHCP SOS #3 |
| 4 | `45.90.28.0` | **NextDNS** anycast | Souvent déjà poussé par Freebox/apps | Sans ID de profil : comportement flou | ⚠️ **Fallback dernier recours seulement** |
| 5 | `192.168.1.254` | **Passerelle Freebox** | Toujours joignable sur le LAN | Résolveur opérateur possible | ⚠️ **Repli LAN ultime uniquement** |

DoT-only (pas DHCP SOS) : UncensoredDNS `91.239.100.100`, Digitale Gesellschaft `185.95.218.42`.

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
| Digitale Gesellschaft | `dns.digitale-gesellschaft.ch` | DoT catalogue (UDP/53 souvent filtré sur Free) |
| UncensoredDNS | `anycast.uncensoreddns.org` | DoT catalogue (UDP/53 souvent filtré sur Free) |
| Quad9 unblocked | `dns10.quad9.net` via `9.9.9.10` | SOS #1 + bootstrap |

**Exclus volontairement comme amonts primaires :** Google `8.8.8.8`, Cloudflare `1.1.1.1`, DNS Free, NextDNS profilé, Quad9 `9.9.9.9` / `.11` (filtre distant) et `.12` (ECS) — on filtre **en local** sur dns-secure ; détail variantes : [quad9.md](quad9.md).

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

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
