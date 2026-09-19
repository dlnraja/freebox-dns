# Importer freebox-dns dans Freebox OS (all-in-one)

Freebox OS n’importe **pas** d’OVA : il faut une image disque **`.qcow2`** (ou raw).

## Contenu du package all-in-one

| Fichier | Rôle |
| --- | --- |
| `freebox-dns.qcow2` | Disque VM Debian 12 préparé (à importer) |
| `freebox-os-vm.json` | Paramètres VM (vCPU, RAM, cloud-init…) |
| `cloudinit-userdata.yaml` | User-data Freebox (`enable_cloudinit`) |
| `SHA256SUMS` | Contrôle d’intégrité |
| `IMPORT-FREEBOX-OS.md` | Cette notice |

## Import en 5 étapes (UI Freebox OS)

1. Téléchargez le zip **`freebox-dns-freeboxos-allinone-*.zip`** (GitHub Actions / Releases).
2. Via **FTP / Partages** Freebox : créez un dossier `VMs` sur le disque interne et y copiez **`freebox-dns.qcow2`**.
3. Freebox OS → **VM** → **Ajouter une VM** → **Sélectionner une image de disque existante** → choisissez `freebox-dns.qcow2`.
4. Réglez : **2 vCPU**, **2048 Mo RAM**, réseau **LAN**, OS **debian**, écran virtuel si besoin.  
   Si proposé : activer **cloud-init**, hostname `freebox-dns`, coller `cloudinit-userdata.yaml`.
5. Démarrer la VM → noter son **IP LAN** → DHCP Freebox : DNS1 = cette IP, DNS2 = `91.239.100.100`.

## Vérification

Sur un PC du LAN :

```text
dig @IP_VM example.com
dig @IP_VM -p 5354 doubleclick.net   → NXDOMAIN (dns-secure)
```

DoH : `https://IP_VM:8453/dns-query` (libre) · `https://IP_VM:8444/dns-query` (secure).

## API (optionnel)

Champs alignés sur `fbxvm-ctrl` / API VM Freebox :

```text
name=freebox-dns
vcpus=2
memory=2048
disk_type=qcow2
disk_path=<disque>/VMs/freebox-dns.qcow2
os=debian
enable_cloudinit=true
cloudinit_hostname=freebox-dns
enable_screen=true
```

## Construire l’image soi-même

```bash
bash scripts/build-freebox-qcow2.sh
bash scripts/package-freebox-os-allinone.sh
```

Sortie : `dist/freebox-dns.qcow2` + `dist/freebox-dns-freeboxos-allinone-*.zip`.
