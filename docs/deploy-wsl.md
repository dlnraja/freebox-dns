# Lab Windows / WSL — tests seulement

Pour **héberger** le DNS du salon sur Windows **sans Docker** → [deploy-windows.md](deploy-windows.md).

Cette page = **lab** (Docker Desktop / WSL) pour développer. Ne mettez **pas** l’IP de ce PC de lab dans le DHCP familial, sauf mini-PC dédié toujours allumé.

## WSL2 + Docker (lab)

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo service docker start
cd /mnt/c/Users/VOUS/Documents/freebox-dns   # adaptez le chemin
cp .env.example .env
# HOST_IP = IP LAN Windows visible sur le réseau (pas seulement l’IP WSL)
bash scripts/generate-certs.sh
docker compose up -d
```

Ports lab : `5356` (libre), `5357`… — pas `:53` tant que vous n’ajoutez pas `docker-compose.prod.yml`.

## Certs PowerShell

```powershell
powershell -File .\scripts\generate-certs.ps1
```

## Salon Windows

| Besoin | Guide |
| --- | --- |
| DNS Windows natif (exe) | [deploy-windows.md](deploy-windows.md) |
| DNS1 sur routeur / PC | [wifi-lan.md](wifi-lan.md) |
| Choisir une cible | [deploy.md](deploy.md) |

---

[CREDITS.md](CREDITS.md)
