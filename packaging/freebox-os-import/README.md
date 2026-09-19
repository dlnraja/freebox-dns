# Paquet d’import Freebox OS (QCOW2)

Freebox OS → **VM** → **Ajouter** → **image de disque existante** = fichier **`.qcow2`**.

| Fichier | Description |
| --- | --- |
| [`IMPORT-FREEBOX-OS.md`](IMPORT-FREEBOX-OS.md) | Procédure d’import UI |
| [`freebox-os-vm.json`](freebox-os-vm.json) | Paramètres VM (2 vCPU, 2048 Mo, debian, cloud-init) |
| [`cloudinit-userdata.yaml`](cloudinit-userdata.yaml) | Bootstrap dns-libre + dns-secure |

## Artefacts CI

Workflow **`build-freebox-os-qcow2`** :

1. **`freebox-dns-freeboxos-kit-*.zip`** — kit léger (sans image) immédiat  
2. **`freebox-dns-freeboxos-allinone-*.zip`** — **all-in-one** avec `freebox-dns.qcow2` prêt à copier dans `/VMs/`

```bash
# Local (Linux / WSL)
sudo apt-get install -y qemu-utils libguestfs-tools zip
bash scripts/build-freebox-qcow2.sh
bash scripts/package-freebox-os-allinone.sh
```
