# Paquet VM Freebox OS

Contenu livré pour Freebox OS → **VM** :

| Fichier | Rôle |
| --- | --- |
| `manifest.json` | Images Docker, packages apt, RAM/CPU/disque, ports |
| `packages.txt` | Paquets système Debian/Ubuntu |
| `install.sh` | Bootstrap complet sur la guest |
| `../cloud-init/freebox-vm-user-data.yaml` | Cloud-init alternatif |

Doc complète : [docs/freebox-vm.md](../../docs/freebox-vm.md).

```bash
sudo bash packaging/freebox-vm/install.sh
```

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
