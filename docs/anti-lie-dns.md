# Anti–DNS menteur (couche locale avant forward)
# Inspiré d’**OONI** (Open Observatory of Network Interference) — la « pieuvre »
# des mesures de censure réseau : https://ooni.org/
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

Listes de cibles : `config/uncensor/probe-targets.txt`  
(Citizen Lab / OONI FR : https://github.com/citizenlab/test-lists/blob/master/lists/fr.csv)

## Lancer le probe

```bash
# dig requis
python3 scripts/ooni-like-anti-lie.py
docker compose up -d --force-recreate dns-libre unbound dns-secure
```

CI : workflow `anti-lie-probe.yml` (schedule).

## IPv6

Les overrides AAAA sont écrits dans le même hosts file.  
Exposition LAN IPv6 : `docker-compose.ipv6.yml` + `HOST_IP6` dans `.env`.

## Périmètre

- Corrige les **mensonges DNS** (résolutions fausses) détectés vs contrôles.
- Ne remplace pas un VPN contre le DPI/SNI.
- `dns-secure` continue de filtrer ads/malware **après** résolution vraie.
