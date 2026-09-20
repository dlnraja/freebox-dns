# Déploiement Raspberry Pi

Cible recommandée pour un salon : Pi **toujours allumé**, IP en **DNS1** sur le routeur.

Image : **Raspberry Pi OS 64-bit** (Pi 4/5) ou Debian. Docker sert à lancer Unbound + les 4 modes — ce n’est pas lié à Freebox.

## Option A — cloud-init

[`cloud-init/pi-user-data.yaml`](../cloud-init/pi-user-data.yaml) : clone, `HOST_IP`, certs, `docker-compose.prod.yml`.

## Option B — manuel

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # puis re-login
git clone https://github.com/dlnraja/freebox-dns.git
cd freebox-dns
cp .env.example .env
# HOST_IP = IP LAN du Pi (eth0/wlan0) — celle que vous mettrez en DNS1
bash scripts/generate-certs.sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.arm64.yml up -d
bash scripts/health-check.sh
dig @HOST_IP example.com +short
```

## DNS du salon

Sur **n’importe quel** routeur (Freebox ou autre) :

| | |
| --- | --- |
| **DNS1** | IP du Pi |
| **DNS2** | `9.9.9.10` (SOS) |

Guide : [wifi-lan.md](wifi-lan.md) · hub : [deploy.md](deploy.md).

DoH : `https://IP_PI:8453/dns-query` (libre) · `https://IP_PI:8444/dns-query` (secure).

---

[CREDITS.md](CREDITS.md) · [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/)
