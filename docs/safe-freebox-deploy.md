# Déploiement VM Freebox — mode sûr (ne pas casser Internet)

## État de sécurité constaté

- Le **PC Wi‑Fi** est un **client** : il doit recevoir via DHCP Freebox `9.9.9.10` + IP_VM — **pas** Docker Desktop comme DNS système.
- La stack Docker sur le PC = lab uniquement.
- Déployer une VM Freebox **ne doit pas** toucher au DHCP tant qu’elle n’est pas saine.
- **UncensoredDNS / Digitale Gesellschaft** : DoT `:853` OK depuis la Freebox, mais **UDP/53 souvent timeout / refused** → interdits en DHCP SOS.

Voir aussi [wifi-lan.md](wifi-lan.md).

## Filet SOS (si panne DNS)

Freebox OS → DHCP → DNS personnalisés :

| Priorité | IP | Nom |
| --- | --- | --- |
| 1 | `9.9.9.10` | Quad9 **No Threat Blocking** (pas ECS) — [quad9.md](quad9.md) |
| 2 | `194.242.2.2` | Mullvad Unfiltered |
| 3 | `94.140.14.140` | AdGuard Non-filtering |

```bash
python scripts/safe-freebox-vm-deploy.py sos
python scripts/safe-freebox-vm-deploy.py dhcp-sos   # après auth API
```

## Déploiement (phases)

1. **SOS** — connaître le filet (ci-dessus).
2. **auth** — `python scripts/safe-freebox-vm-deploy.py auth` puis **OK sur l’écran Freebox**.
3. **download** — artefact `freebox-dns.qcow2` + `freebox-dns-cidata.iso` dans `dist/freeboxos-allinone/`.
4. **FTP** — copier vers `/VMs/` sur le disque Freebox (mot de passe Freebox OS).
5. **VM** — Freebox OS → VM → image disque existante → monter ISO CD → démarrer.
6. **health** — `dig @IP_VM example.com` OK.
7. **DHCP (seulement après health)** — DNS1 = IP_VM, DNS2 = `9.9.9.10` (SOS).

## Interdit

- Remplacer le DHCP par la seule IP VM sans secondaire.
- Mettre UncensoredDNS / DG en DNS1 DHCP (plain UDP souvent mort sur Free).
- Couper la stack Docker locale pendant un dépannage DNS PC (elle n’est de toute façon pas le DNS système Wi‑Fi ici).
- Committer `.freebox-token.json` / UID Freebox.

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
