# Anti–DNS menteur (couche locale avant forward)
# Inspiré d’**OONI** (Open Observatory of Network Interference) — la « pieuvre »
# des mesures de censure réseau : https://ooni.org/
# Intro FR : https://korben.info/ooni-probe-mesurer-niveau-de-manipulation-surveillance-censure-de-internet.html
# Rapport FR 2025 : la censure FAI est surtout du **DNS menteur**
# (NXDOMAIN / 127.0.0.1), pas un blocage IP/DPI généralisé.
# https://ooni.org/post/2025-france-report/

## Principe

```text
Client
  → dns-libre / dns-secure
      → 1) hosts.local + hosts.generated   ← vérité locale (A + AAAA)
      → 2) Unbound DoT uncensoring
      → 3) fallbacks catalogue
```

1. Le probe `scripts/ooni-like-anti-lie.py` interroge des **résolveurs menteurs**
   (gateway Freebox, ns0/ns1.free.fr) et des **contrôles** (UncensoredDNS, DG, Quad9 Unsecured, Mullvad, open.dns0).
2. Si le menteur renvoie sinkhole / NXDOMAIN / IP privée **alors que** les contrôles
   s’accordent sur des IP publiques → écriture dans `config/uncensor/hosts.generated`
   (+ `config/unbound/a-records.conf`).
3. Ces réponses sont servies **en local avant** tout forward amont.
4. `scripts/web-connectivity-lite.py` (couche OONI **Web Connectivity**) vérifie en HTTP
   que l’IP consensus ne sert pas une page ANJ/DGCCRF — sinon strip du hosts.

Listes de cibles : `config/uncensor/probe-targets.txt`  
(Citizen Lab / OONI FR : https://github.com/citizenlab/test-lists/blob/master/lists/fr.csv)

Boîte OSINT complémentaire (Web-Check) : [osint-toolkit.md](osint-toolkit.md).

## Smart local lists (anti-page de censure)

Le builder `scripts/ooni-like-anti-lie.py` :

1. Interroge **tous** les résolveurs contrôle du catalogue (pas Free/gateway).
2. **Rejette** : `127.0.0.1`, IP privées, pages ANJ (`145.239.225.117` / `offre-illegale.anj.fr`), DGCCRF (`146.59.230.139` / `blocage.conso.gouv.fr`).
3. Garde un **consensus ≥2 contrôles** d’IP publiques propres.
4. Écrit `hosts.generated` pour **chaque** domaine vérifié (liste locale intelligente), pas seulement les mensonges détectés.
5. Importe aussi les hôtes Citizen Lab FR (catégories NEWS/CULTR/PUBH/LGBT/… — pas les listes jeu comme source de vérité locale forcée).

Réf. techniques : [OONI FR](https://ooni.org/post/2025-france-report/), [censxres.fr](https://censxres.fr/technique/), [Korben OONI](https://korben.info/ooni-probe-mesurer-niveau-de-manipulation-surveillance-censure-de-internet.html).


## IPv6

Les overrides AAAA sont écrits dans le même hosts file.  
Exposition LAN IPv6 : `docker-compose.ipv6.yml` + `HOST_IP6` dans `.env`.

## Périmètre

- Corrige les **mensonges DNS** (résolutions fausses) détectés vs contrôles.
- Détecte les **pages de censure HTTP** sur IP stockées (Web Connectivity lite).
- Ne remplace pas un VPN contre le DPI/SNI.
- `dns-secure` continue de filtrer ads/trackers/malware **et** anti–anti-adblock **après** résolution vraie.

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
