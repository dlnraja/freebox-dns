# Freebox OS — rubrique VM (entière) + import QCOW2

Deux façons d’avoir **freebox-dns** sur Freebox Delta / Ultra :

1. **All-in-one (recommandé)** — importer `freebox-dns.qcow2`  
2. **Création manuelle** — ISO/cloud-init + `packaging/freebox-vm/install.sh`

Kit import : [`packaging/freebox-os-import/`](../packaging/freebox-os-import/).

---

## A. Import all-in-one (image VM prête)

Freebox OS accepte une **image disque `.qcow2`** (pas d’OVA).

### Télécharger

- GitHub → Actions → workflow **`build-freebox-os-qcow2`** → artefact  
  **`freebox-dns-freeboxos-allinone-*.zip`**  
  (contient `freebox-dns.qcow2` + JSON + cloud-init + checksums)
- Ou kit léger sans disque : **`freebox-dns-freeboxos-kit-*.zip`**

### Importer dans Freebox OS

1. Extraire le zip all-in-one.
2. FTP → dossier **`VMs/`** → copier `freebox-dns.qcow2` **et** `freebox-dns-cidata.iso`.
3. Freebox OS → **VM** → **Ajouter** → **image de disque existante** → `freebox-dns.qcow2`.
4. **2 vCPU** · **2048 Mo** · **LAN** · OS **debian**.
5. Monter **`freebox-dns-cidata.iso`** en **CD-ROM virtuel** (cloud-init 1er boot).
6. Démarrer → IP LAN → DHCP DNS1 = IP · DNS2 = `91.239.100.100`.

Détail : [`packaging/freebox-os-import/IMPORT-FREEBOX-OS.md`](../packaging/freebox-os-import/IMPORT-FREEBOX-OS.md).

### Construire l’image localement

```bash
sudo apt-get install -y qemu-utils cloud-image-utils genisoimage zip curl
bash scripts/build-freebox-qcow2.sh
bash scripts/package-freebox-os-allinone.sh
# → dist/freebox-dns.qcow2 + dist/freebox-dns-cidata.iso
# → dist/freebox-dns-freeboxos-allinone-*.zip
```

---

## B. Création manuelle (ISO)

| Élément | Valeur |
| --- | --- |
| Modèles | Freebox **Delta**, **Ultra**, Server v9+ |
| RAM | **2048 Mo** (limite fréquente UI Freebox) |
| vCPU | **2** |
| Disque | **16 Go**+ |
| Réseau | Bridge **LAN** |
| OS guest | Debian 12 / Ubuntu 24.04 |

```bash
curl -fsSL https://raw.githubusercontent.com/dlnraja/freebox-dns/main/packaging/freebox-vm/install.sh | sudo bash
```

Cloud-init : [`cloud-init/freebox-vm-user-data.yaml`](../cloud-init/freebox-vm-user-data.yaml).

---

## Packages & images Docker

- Apt : [`packaging/freebox-vm/packages.txt`](../packaging/freebox-vm/packages.txt)
- Manifeste : [`packaging/freebox-vm/manifest.json`](../packaging/freebox-vm/manifest.json)
- Images : `mvance/unbound`, `adguard/dnsproxy`, `ghcr.io/0xerr0r/blocky`

## Ports (bind HOST_IP)

| Port | Service |
| --- | --- |
| 53 | dns-libre |
| 5354 | dns-secure |
| 8453 / 8444 | DoH libre / secure |
| 3080 | UI Blocky |

## Santé

```bash
cd /opt/freebox-dns
bash scripts/health-check.sh
docker compose ps
```

Voir [freebox.md](freebox.md), [upstreams-uncensoring.md](upstreams-uncensoring.md), [dns-lexicon.md](dns-lexicon.md).

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
