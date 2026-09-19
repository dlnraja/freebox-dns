# Déploiement Raspberry Pi

Image complète recommandée : **Raspberry Pi OS 64-bit** (Pi 4/5), ou Debian.

## Option A — cloud-init

Utilisez [`cloud-init/pi-user-data.yaml`](../cloud-init/pi-user-data.yaml) (rpi-imager / image cloud-init) : clone le dépôt, fixe `HOST_IP`, génère les certs, lance `docker-compose.prod.yml`.

## Option B — manuel

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# re-login
git clone https://github.com/dlnraja/freebox-dns.git
cd freebox-dns
cp .env.example .env
# HOST_IP = IP eth0/wlan0 du Pi
bash scripts/generate-certs.sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
bash scripts/health-check.sh
```

## Freebox

DHCP → DNS primaire = IP du Pi (`dns-libre` :53). Réservez le bail dans Freebox OS.

DoH : `https://IP_PI:8453/dns-query` (libre) · `https://IP_PI:8444/dns-query` (secure).

Voir aussi [freebox.md](freebox.md) et [dns-analysis.md](dns-analysis.md).
