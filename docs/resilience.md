# Résilience DNS — local d'abord, puis le reste du monde

Quand « tous les DNS publics » tombent, la VM Freebox doit encore répondre
avec ce qu'elle connaît déjà (hosts + Unbound local-data + cache serve-expired).

## Chaîne (ordre strict)

```text
Client LAN
  │
  ▼
1. EDGE (dns-libre / Blocky) — LOCAL FIRST
   hosts.critical   → seeds infra (github, docker, debian, Freebox LAN)
   hosts.local      → overrides manuels
   hosts.generated  → anti–DNS menteur (OONI-like)
   cache edge
  │
  ▼
2. UNBOUND (172.28.0.10) — peuplé localement, puis forward intelligent
   a) a-records.critical.conf  → local-zone + local-data (warm-local-cache)
   b) a-records.conf           → local-data anti-lie (OONI)
   c) cache + serve-expired    → jusqu'à 3 jours (volume unbound-cache)
   d) forward-records.conf     → DoT catalogue (Quad9/Mullvad/AdGuard d'abord)
      forward-first: yes
   e) si amonts DoT morts      → récursion ROOT HINTS
  │
  ▼
3. FALLBACK dns-libre seulement si Unbound est DOWN
   DoH/DoT puis plain SOS (9.9.9.10 / Mullvad / AdGuard)
```

## Ce que ça garantit

| Situation | Comportement |
| --- | --- |
| Domaine dans hosts / local-data | Réponse **locale**, sans Internet |
| Domaine déjà vu (cache chaud) | **serve-expired** même si DoT morts |
| DoT joignables | Forward intelligent (catalogue) |
| Unbound process down | dns-libre fallbacks SOS |
| Fibre coupée + jamais vu le domaine | Impossible — limite honnête |

## Commandes

```bash
# Peupler seeds critiques → hosts + Unbound local-data
python3 scripts/warm-local-cache.py

# Anti–DNS menteur → hosts.generated + a-records.conf
python3 scripts/ooni-like-anti-lie.py

docker compose up -d --force-recreate unbound

# Remplir le cache runtime (serve-expired)
bash scripts/warm-unbound-runtime.sh
```

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `config/uncensor/hosts.*` | LOCAL FIRST edge |
| `config/unbound/a-records.critical.conf` | Seeds Unbound (toujours monté) |
| `config/unbound/a-records.conf` | serve-expired + anti-lie + include critical |
| `config/unbound/forward-records.conf` | DoT après le local |
| `docker volume unbound-cache` | Cache persistant entre recreates |

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
