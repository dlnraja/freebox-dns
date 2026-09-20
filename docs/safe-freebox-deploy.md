# Déploiement VM Freebox — mode sûr (ne pas casser Internet)

## État de sécurité constaté

- Le **PC Wi‑Fi** utilise déjà les pins UncensoredDNS / DG / Quad9 / NextDNS — **pas** la stack Docker locale en DNS système.
- Donc déployer une VM Freebox **ne doit pas** toucher au DHCP tant qu’elle n’est pas saine.
- **DHCP Freebox n’a pas été modifié** par les scripts (règle dure).

## Filet SOS (si panne DNS)

Freebox OS → DHCP → DNS personnalisés :

| Priorité | IP | Nom |
| --- | --- | --- |
| 1 | `91.239.100.100` | UncensoredDNS |
| 2 | `185.95.218.42` | Digitale Gesellschaft |
| 3 | `9.9.9.10` | Quad9 Unsecured |

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
7. **DHCP (seulement après health)** — DNS1 = pin UncensoredDNS, DNS2 = IP_VM **ou** l’inverse seulement si double check OK.

## Interdit

- Remplacer le DHCP par la seule IP VM sans secondaire.
- Couper la stack Docker locale pendant un dépannage DNS PC (elle n’est de toute façon pas le DNS système Wi‑Fi ici).
- Committer `.freebox-token.json` / UID Freebox.

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
