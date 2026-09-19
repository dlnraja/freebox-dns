# Freebox OS — rubrique VM (entière)

Guide pour créer et faire tourner **freebox-dns** dans Freebox OS → **VM** (Delta / Ultra / Server v9+).

Pas d’adresse perso / UID / `*.fbxos.fr` dans ce dépôt. Paramètres : [`config/freebox/`](../config/freebox/) · paquet : [`packaging/freebox-vm/`](../packaging/freebox-vm/).

## 1. Prérequis Freebox OS

| Élément | Valeur recommandée |
| --- | --- |
| Modèles | Freebox **Delta**, **Ultra**, Server v9 (r1) API 16+ |
| Rubrique | Freebox OS → **VM** (ou Virtualisation) |
| RAM guest | **2 Go** min (4 Go confort) |
| vCPU | **2** |
| Disque | **16 Go** min (32 Go si images Docker en local) |
| Réseau | Pont / bridge **LAN** (même VLAN que les clients DHCP) |
| IP | Fixe LAN = `HOST_IP` (réserver le bail DHCP) |

## 2. Image OS guest

| Image | Notes |
| --- | --- |
| **Debian 12** (bookworm) cloud / netinst | Recommandée — cloud-init OK |
| **Ubuntu Server 24.04** | Alternative LTS |
| Raspberry Pi OS 64-bit | Si hôte = Pi (hors Freebox VM) — voir [deploy-pi.md](deploy-pi.md) |

Cloud-init : [`cloud-init/freebox-vm-user-data.yaml`](../cloud-init/freebox-vm-user-data.yaml).

## 3. Packages système (à installer dans la VM)

Liste canonique : [`packaging/freebox-vm/packages.txt`](../packaging/freebox-vm/packages.txt).

```text
docker.io
docker-compose-v2
git curl ca-certificates openssl
bind9-dnsutils jq
```

Optionnel monitoring : `htop`, `tmux`.

## 4. Images Docker tirées par Compose

| Image | Service | Rôle |
| --- | --- | --- |
| `mvance/unbound:latest` | unbound | Récursion DoT uncensoring |
| `adguard/dnsproxy:latest` | dns-libre | Front libre + DoH |
| `ghcr.io/0xerr0r/blocky:latest` | dns-secure | Front threat-local + DoH |

Manifeste : [`packaging/freebox-vm/manifest.json`](../packaging/freebox-vm/manifest.json).

## 5. Création VM (checklist Freebox OS)

1. Freebox OS → **VM** → **Ajouter** / Créer une machine virtuelle.
2. Choisir image Debian 12 / Ubuntu 24.04 (ISO ou cloud image).
3. RAM 2–4 Go, 2 vCPU, disque ≥ 16 Go.
4. Réseau = **LAN** (pas Guest-only).
5. Installer l’OS ; activer SSH ; utilisateur sudo.
6. Appliquer cloud-init **ou** lancer le paquet :

```bash
# Sur la VM, en root/sudo :
curl -fsSL https://raw.githubusercontent.com/dlnraja/freebox-dns/main/packaging/freebox-vm/install.sh | bash
# ou depuis un tarball CI :
#   tar xzf freebox-dns-vm-*.tar.gz && cd freebox-dns && sudo bash packaging/freebox-vm/install.sh
```

7. Noter l’IP LAN → `HOST_IP` dans `.env`.
8. Freebox OS → DHCP → DNS primaire = `HOST_IP`, secondaire = `91.239.100.100`.

## 6. Ports exposés (local-only sur HOST_IP)

| Port | Service |
| --- | --- |
| UDP/TCP **53** | dns-libre (prod overlay) |
| UDP/TCP **5354** | dns-secure (même hôte) |
| TCP **8453** | DoH libre |
| TCP **8444** | DoH secure |
| TCP **3080** | UI Blocky |

Bind **uniquement** `HOST_IP` — pas Internet public.

## 7. Paquet / artefact CI

Workflow GitHub `package-freebox-vm.yml` produit un tarball :

- sources + `packaging/freebox-vm/`
- `manifest.json` (images + packages + ports)
- script `install.sh`

Télécharger depuis Actions → Artifacts, copier sur la VM, extraire, `sudo bash packaging/freebox-vm/install.sh`.

## 8. Dual personnalité (idéal)

- **Option A** : 2 VM (ou 2 IP macvlan) → les deux sur `:53` (libre + secure).
- **Option B** : 1 VM → libre `:53`, secure `:5354` + DoH `:8444`.

## 9. Santé

```bash
cd /opt/freebox-dns   # ou chemin install
bash scripts/health-check.sh
docker compose ps
```

Voir aussi [freebox.md](freebox.md), [upstreams-uncensoring.md](upstreams-uncensoring.md), [dns-lexicon.md](dns-lexicon.md).
