# Déploiement Raspberry Pi

1. Raspberry Pi OS 64-bit recommandé (Pi 4/5).
2. Installer Docker :

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

3. Cloner et lancer :

```bash
git clone https://github.com/dlnraja/freebox-dns.git
cd freebox-dns
cp .env.example .env
# HOST_IP = IP eth0/wlan0 du Pi
bash scripts/generate-certs.sh
docker compose up -d
```

4. Freebox DHCP → DNS = IP du Pi.

Astuce : fixe l’IP du Pi via bail DHCP Freebox (adresse réservée).
