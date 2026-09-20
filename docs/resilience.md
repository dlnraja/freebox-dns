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
   a) a-records.critical.conf  → local-zone: … static + local-data (warm)
   b) a-records.conf           → local-zone static + local-data anti-lie (OONI)
   c) cache + serve-expired    → jusqu'à 3 jours (volume unbound-cache)
   d) forward-records.conf     → DoT catalogue (chargé via unbound.conf monté)
      forward-first: yes
   e) si amonts DoT morts      → récursion ROOT HINTS (image auto-trust-anchor)
  │
  ▼
3. FALLBACK dns-libre seulement si Unbound est DOWN
   DoH/DoT puis plain SOS (9.9.9.10 / Mullvad / AdGuard)
```

Les fallbacks dns-libre **ne** sauvent **pas** le cas « Unbound up, tous les DoT morts » —
là, seuls local-data / static / serve-expired / root comptent.

## Ce que ça garantit

| Situation | Comportement |
| --- | --- |
| Domaine dans hosts / local-data (static) | Réponse **locale**, sans Internet |
| Domaine déjà vu (cache chaud) | **serve-expired** même si DoT morts |
| DoT joignables | Forward intelligent (catalogue) |
| Unbound process down | dns-libre fallbacks SOS |
| Fibre coupée + jamais vu le domaine | Impossible — limite honnête |

## DoT catalogue vraiment chargé

L'image `mvance/unbound` commente souvent :

```text
# include: /opt/unbound/etc/unbound/forward-records.conf
```

Ce dépôt **monte** `config/unbound/unbound.conf` avec l'include **actif**, plus
`forward-records.conf`, `a-records.conf`, `a-records.critical.conf`, `srv-records.conf`,
et le volume `unbound-cache`.

Vérification :

```bash
bash scripts/verify-unbound-forwards.sh
# Avec conteneur up : unbound-checkconf + include actif dans le container
```

## Tests d'acceptation (amonts bloqués)

Sur un réseau de test avec :853 / :53 sortants filtrés :

| Attendu | Résultat |
| --- | --- |
| Nom dans hosts / local-data | Réponse immédiate |
| Nom déjà résolu (cache) | serve-expired |
| Nom jamais vu | Échec fermé (limite honnête) |

## Commandes

```bash
# Peupler seeds critiques → hosts + Unbound local-data (static)
python3 scripts/warm-local-cache.py

# Anti–DNS menteur → hosts.generated + a-records.conf (static zones)
python3 scripts/ooni-like-anti-lie.py

docker compose up -d --force-recreate unbound

# Remplir le cache runtime (serve-expired)
bash scripts/warm-unbound-runtime.sh

# Preuve DoT include + mounts
bash scripts/verify-unbound-forwards.sh
```

Après chaque warm / OONI : recreator Unbound pour aligner `a-records*` sur les hosts edge.

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `config/uncensor/hosts.*` | LOCAL FIRST edge |
| `config/unbound/unbound.conf` | Conf montée — **include DoT actif** |
| `config/unbound/a-records.critical.conf` | Seeds Unbound static (toujours monté) |
| `config/unbound/a-records.conf` | serve-expired + anti-lie static + include critical |
| `config/unbound/forward-records.conf` | DoT après le local (`forward-first`) |
| `config/unbound/srv-records.conf` | Placeholder SRV (include requis) |
| `docker volume unbound-cache` | Cache persistant entre recreates |
| `config/uncensor/blocky-custom-dns.yml` | **Stub obsolète** — Blocky = hostsFile |

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
