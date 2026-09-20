# Déploiement Windows / WSL2

Docker Desktop n’est pas obligatoire si vous utilisez **WSL2 + Docker Engine**.

## WSL2

```bash
# Dans Ubuntu WSL
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo service docker start
cd /mnt/c/Users/Dell/Documents/freebox-dns
cp .env.example .env
bash scripts/generate-certs.sh
docker compose up -d
```

Exposez les ports Windows : Docker Desktop / WSL mirroir réseau, ou `netsh interface portproxy`.

`HOST_IP` doit être l’IP **LAN Windows** visible par la Freebox (pas l’IP virtuelle WSL seule), sauf mirroir réseau activé.

## PowerShell (certs)

```powershell
cd C:\Users\Dell\Documents\freebox-dns
powershell -File .\scripts\generate-certs.ps1
```

## Sans Docker sur l’hôte Windows

Installez Docker Desktop, activez l’intégration WSL2, puis `docker compose up -d` depuis ce dossier (ou depuis WSL sur le même chemin monté).

---

## Sources & crédits

Projets, listes et méthodes cités : **[CREDITS.md](CREDITS.md)** · site guides : [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/).
