# Résilience DNS — local d’abord, puis le reste du monde

Quand « tous les DNS publics » tombent, ce projet doit encore répondre
avec ce qu’il connaît déjà, puis tenter les racines Internet, puis les amonts.

## Chaîne (ordre strict)

```text
1. LOCAL projet
   hosts.critical  →  seeds infra (github, docker, debian, Freebox LAN)
   hosts.local     →  overrides manuels
   hosts.generated →  anti–DNS menteur (OONI-like)

2. CACHE
   dnsproxy / blocky cache longue durée
   Unbound serve-expired (RFC 8767) jusqu’à 3 jours

3. UNBOUND
   a) forward DoT uncensoring (catalogue)     forward-first: yes
   b) si amonts morts → récursion ROOT HINTS  (pas besoin d’un « DNS tiers »)

4. FALLBACK en ligne (dns-libre)
   pins Freebox + catalogue plain DNS
   gateway Freebox / NextDNS soft-last
```

## Limite honnête

Si **plus aucune connectivité IP** (câble / fibre coupée) **et** aucun enregistrement
local/cache : aucun résolveur au monde ne peut inventer Internet.
La résilience ici = **ne pas dépendre d’un seul DNS public** + **garder la mémoire locale**.

## Commandes

```bash
# Remplir seeds critiques (github, registries…)
python3 scripts/warm-local-cache.py

# Corriger DNS menteurs FAI → hosts.generated
python3 scripts/ooni-like-anti-lie.py

docker compose up -d --force-recreate
```

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `config/uncensor/hosts.critical` | Seeds projet |
| `config/unbound/forward-records.conf` | `forward-first: yes` |
| `config/unbound/a-records.conf` | serve-expired + local-data |
| `config/dnsproxy/dns-libre.yaml` | local → unbound → fallbacks |
| `docs/anti-lie-dns.md` | couche anti-censure |
