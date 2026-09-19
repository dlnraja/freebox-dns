# Freebox — configuration DHCP / DNS / DoH

Compatible **Freebox Delta**, **Freebox Ultra**, et **VM Freebox** (Debian/Ubuntu dans la Freebox ou hôte local).

Paramètres : [`config/freebox/dhcp-dns.json`](../config/freebox/dhcp-dns.json) · checklist [`config/freebox/README.md`](../config/freebox/README.md) · **rubrique VM entière** [`freebox-vm.md`](freebox-vm.md) · amonts max [`upstreams-uncensoring.md`](upstreams-uncensoring.md).

## Capturer les DNS une fois (déjà fait ici)

Snapshot : `config/freebox-dns-snapshot.json` (Freebox v9 r1, API 16). Aucun UID / `*.fbxos.fr` / adresse perso.

## VM Freebox OS — import image (all-in-one)

Freebox OS importe du **`.qcow2`** (pas OVA).

1. Télécharger l’artefact CI **`freebox-dns-freeboxos-allinone-*.zip`**.
2. Copier `freebox-dns.qcow2` + `freebox-dns-cidata.iso` dans **`VMs/`** (FTP).
3. Freebox OS → **VM** → **image de disque existante** → monter l’ISO en CD.
4. 2 vCPU · 2048 Mo · LAN · DHCP DNS1 = IP de la VM.

Kit + notice : [`packaging/freebox-os-import/`](../packaging/freebox-os-import/) · doc : [`freebox-vm.md`](freebox-vm.md).

## Pointer le DHCP vers la stack (local-only)

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

| Champ Freebox DHCP | Valeur |
| --- | --- |
| DNS 1 | `HOST_IP` (**dns-libre** :53) |
| DNS 2 | `91.239.100.100` (UncensoredDNS) |

Fallbacks étendus (si VM down) : voir catalogue — pins 1–3, puis amonts libres, puis gateway, NextDNS soft-last.

## DoH

- Libre : `https://HOST_IP:8453/dns-query`
- Secure : `https://HOST_IP:8444/dns-query`
- UI Blocky : `http://HOST_IP:3080`

## VM Freebox OS (rubrique complète)

→ **[freebox-vm.md](freebox-vm.md)** : création VM, RAM/CPU/disque, packages apt, images Docker, cloud-init, paquet CI `packaging/freebox-vm/`, `install.sh`.

Raccourci :

```bash
# Dans la guest Freebox OS
curl -fsSL https://raw.githubusercontent.com/dlnraja/freebox-dns/main/packaging/freebox-vm/install.sh | sudo bash
```

## Sécurité

- Bind `HOST_IP` only · pas de poll distant Freebox depuis le CI.
