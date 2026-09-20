# Importer freebox-dns dans Freebox OS (all-in-one)

Freebox OS n’importe **pas** d’OVA : il faut une image disque **`.qcow2`**.  
Le package all-in-one ajoute aussi un **CD cloud-init** (`.iso`) que Freebox OS peut monter.

## Contenu du zip all-in-one

| Fichier | Rôle |
| --- | --- |
| `freebox-dns.qcow2` | Disque Debian 12 cloud **arm64** (16 Go) — **à importer** |
| `freebox-dns-cidata.iso` | Cloud-init NoCloud — **monter en CD-ROM virtuel** |
| `freebox-os-vm.json` | Paramètres VM (2 vCPU, 2048 Mo, debian…) |
| `cloudinit-userdata.yaml` | User-data (référence / API) |
| `SHA256SUMS` | Intégrité |
| `IMPORT-FREEBOX-OS.md` | Cette notice |

> **Arch :** Freebox OS (Delta / Pop / Ultra) = **ARM64**. Une image amd64 ne boote pas (boucle PXE).

## Import en 6 étapes

1. Télécharger **`freebox-dns-freeboxos-allinone-*.zip`** (Actions → `build-freebox-os-qcow2`).
2. Extraire ; via **FTP** Freebox créer `VMs/` et y copier :
   - `freebox-dns.qcow2`
   - `freebox-dns-cidata.iso`
3. Freebox OS → **VM** → **Ajouter une VM** → **Sélectionner une image de disque existante** → `freebox-dns.qcow2`.
4. Régler : **2 vCPU**, **2048 Mo RAM**, réseau **LAN**, OS **debian**, écran virtuel OK.
5. **CD-ROM virtuel** → monter `freebox-dns-cidata.iso` (cloud-init au 1er boot).
6. Démarrer → attendre 2–5 min (Docker + stack) → noter l’**IP LAN** → DHCP : **DNS1 = IP_VM**, DNS2 = `9.9.9.10` (SOS).

## Vérification

```text
dig @IP_VM example.com
dig @IP_VM -p 5354 doubleclick.net
```

## API (optionnel)

```text
name=freebox-dns
vcpus=2
memory=2048
disk_type=qcow2
disk_path=<disque>/VMs/freebox-dns.qcow2
cd_path=<disque>/VMs/freebox-dns-cidata.iso
os=debian
enable_cloudinit=true
cloudinit_hostname=freebox-dns
enable_screen=true
```

## Rebuild local

```bash
sudo apt-get install -y qemu-utils cloud-image-utils genisoimage zip curl
bash scripts/build-freebox-qcow2.sh
bash scripts/package-freebox-os-allinone.sh
```

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
