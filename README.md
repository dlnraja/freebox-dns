# freebox-dns — résolveur DNS local pour votre LAN

**But :** une machine toujours allumée répond au DNS. Vous mettez **son IP en DNS1**
sur le routeur (ou sur un PC / téléphone) → la résolution passe par chez vous
(hosts locaux, anti–DNS menteur, filtres optionnels, DoT uncensoring).

Ce dépôt **n’exige pas** votre Freebox ni Docker. Freebox / Pi / Windows sont
trois façons d’héberger le même rôle : *le serveur DNS du salon*.

| Vous avez… | Vous faites… |
| --- | --- |
| **Raspberry Pi** (recommandé) | [docs/deploy-pi.md](docs/deploy-pi.md) — stack complète |
| **VM sur Freebox OS** (ou autre hyperviseur) | [docs/freebox-vm.md](docs/freebox-vm.md) — option Freebox |
| **PC Windows** (sans Docker) | [docs/deploy-windows.md](docs/deploy-windows.md) — `dnsproxy.exe` |
| Juste tester | [docs/deploy.md](docs/deploy.md) — choisir une cible |

Guides web : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/) · [docs/](docs/README.md)

---

## En 30 secondes

1. Démarrez le résolveur sur une machine **toujours allumée** (Pi / VM / Windows).
2. Notez son IP LAN, ex. `192.168.1.71`.
3. Sur le routeur **ou** l’appareil final :

| | |
| --- | --- |
| **DNS1** | `192.168.1.71` ← **ce projet** |
| **DNS2** | `9.9.9.10` (SOS Quad9, optionnel si la machine tombe) |

4. Vérifiez : `dig @192.168.1.71 example.com` (ou `Resolve-DnsName example.com -Server 192.168.1.71`).

**LAN only** — ne pas exposer le DNS sur Internet ([docs/lan-only.md](docs/lan-only.md)).

```text
Client / Wi‑Fi
    → DNS1 = IP du résolveur (Pi · VM · Windows)
    → hosts locaux → cache → DoT uncensoring → (SOS si besoin)
```

---

## Quatre modes « smart spit » (Pi / VM + Docker)

Personnalités séparées par **port / DoH** (pas un clone Pi-hole FTL) :

| Mode | Rôle | Port prod | Transports |
| --- | --- | --- | --- |
| **uncensored** | Anti-censure, pas de filtre pub | `:53` | Do53 · DoH `:8453` · DoT/DoQ `:853` |
| **malware** | Denylist menaces | `5357` | Do53 · DoH · DoT |
| **antipub** | Pubs / trackers | `5358` | Do53 · DoH · DoT |
| **secure** | antipub + malware | `5354` | Do53 · DoH · DoT · **UI** `:3080` |

- **Pi-hole / uBlock au DNS** → Blocky ([docs/filtering.md](docs/filtering.md) · [docs/pihole-parity.md](docs/pihole-parity.md)) — UI **secure only** `http://HOST_IP:3080`
- Modes : [docs/modes.md](docs/modes.md) · transports : [docs/encrypted-dns.md](docs/encrypted-dns.md)
- Windows natif = lite uncensoring (hosts + DoT) — [deploy-windows](docs/deploy-windows.md)

---

## Ce que ce projet n’est pas

- Pas un **clone Pi-hole** (pas de DHCP FTL, pas de regex UI, pas de teleporter) — volontaire
- Pas « seulement pour Freebox » — Freebox est un **hôte possible**, comme un Pi
- Pas le DNS d’un laptop qui dort — machine toujours allumée
- Docker = moyen pour la stack complète, pas le produit

---

## Docs utiles

| Doc | Pour qui |
| --- | --- |
| [docs/deploy.md](docs/deploy.md) | Démarrer — Pi / VM / Windows |
| [docs/lan-only.md](docs/lan-only.md) | LAN only |
| [docs/wifi-lan.md](docs/wifi-lan.md) | DNS1 / Wi‑Fi |
| [docs/filtering.md](docs/filtering.md) · [pihole-parity.md](docs/pihole-parity.md) | Listes Blocky |
| [docs/resilience.md](docs/resilience.md) | Local-first Unbound |
| [docs/modes.md](docs/modes.md) | 4 modes |
| [CHANGELOG.md](CHANGELOG.md) · [FEATURES.md](FEATURES.md) · [CONTRIBUTING.md](CONTRIBUTING.md) | Suivi / contrib |

## Licence

MIT — [LICENSE](LICENSE).
