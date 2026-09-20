# Smart local DNS lists (anti lie / blockpage / gov redirect)
# See docs/anti-lie-dns.md — never stores ANJ/DGCCRF/127.0.0.1

| Fichier | Rôle |
| --- | --- |
| `hosts.critical` | Seeds projet (warm-local-cache) |
| `hosts.local` | Overrides manuels |
| `hosts.generated` | Consensus multi-contrôles **propres** uniquement |
| `sinkhole-signatures.json` | 127.0.0.1, ANJ `145.239.225.117`, DGCCRF `146.59.230.139`… |
| `probe-targets.txt` | Cibles + import Citizen Lab FR (catégories non-gambling) |

```bash
python3 scripts/warm-local-cache.py
python3 scripts/ooni-like-anti-lie.py
python3 scripts/web-connectivity-lite.py   # OONI Web Connectivity lite (HTTP ANJ/DGCCRF)
docker compose up -d --force-recreate dns-libre unbound dns-secure
# Optionnel OSINT : docker compose --profile osint up -d web-check
```

Voir aussi [docs/osint-toolkit.md](../../docs/osint-toolkit.md) (Korben OONI + Web-Check).

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
