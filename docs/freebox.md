# Freebox — configuration DHCP / DNS / DoH

Compatible **Freebox Delta**, **Freebox Ultra**, et **VM Freebox** (Debian/Ubuntu dans la Freebox ou hôte local).

Paramètres structurés : [`config/freebox/dhcp-dns.json`](../config/freebox/dhcp-dns.json) · checklist [`config/freebox/README.md`](../config/freebox/README.md) · analyse [`dns-analysis.md`](dns-analysis.md).

## Capturer les DNS une fois (déjà fait ici)

Sur le LAN de développement, snapshot enregistré dans `config/freebox-dns-snapshot.json` :

- Modèle vu : Freebox v9 (r1) — API 16
- DNS DHCP annoncés → `FREEBOX_DNS_1..5` (identités : [dns-pins.md](dns-pins.md))
- **Aucun** UID Freebox, domaine distant `*.fbxos.fr`, ni adresse personnelle dans le dépôt

Pour un autre site : lisez les DNS du client DHCP, ou Freebox OS → réglages DNS/DHCP, puis éditez le snapshot **localement**.

## Pointer le DHCP vers la stack (local-only)

1. Notez l’IP LAN de la machine Docker (`HOST_IP` dans `.env`) — les ports Compose sont bindés **uniquement** sur cette IP.
2. Lab Windows (ports `5356`/`5354`) : Freebox DHCP ne pousse que le port 53 → utiliser un forwarder, ou l’overlay prod.
3. Prod recommandée (Freebox VM / Pi) :

```bash
cp .env.example .env
# HOST_IP=192.168.x.y
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

| Champ Freebox DHCP | Valeur |
| --- | --- |
| DNS 1 | `HOST_IP` (**dns-libre** sur UDP/TCP 53) |
| DNS 2 | `91.239.100.100` (UncensoredDNS — repli si VM down) |

Dual filtré + non filtré idéal : **deux IP LAN** (macvlan / 2 VM) toutes deux sur `:53`, ou DoH secure en parallèle.

Ne pas mettre `ns0.free.fr` / `ns1.free.fr` en primaire.

## DoH optionnel

Le DHCP Freebox ne pousse en général **pas** de DoH. Configurez navigateur / OS :

- Libre : `https://HOST_IP:8453/dns-query`
- Secure : `https://HOST_IP:8444/dns-query`

Acceptez le certificat auto-signé LAN, ou remplacez `certs/` par un cert interne.

UI Blocky : `http://HOST_IP:3080` (LAN only).

## VM Freebox / images

1. Créez une VM Debian 12 / Ubuntu 24.04 dans Freebox OS (Delta / Ultra).
2. Cloud-init prêt à l’emploi : [`cloud-init/freebox-vm-user-data.yaml`](../cloud-init/freebox-vm-user-data.yaml).
3. Images Docker tirées par Compose : `mvance/unbound`, `adguard/dnsproxy`, `ghcr.io/0xerr0r/blocky`.
4. IP fixe LAN → DHCP Freebox comme ci-dessus.

## Sécurité / vie privée

- Exposition **local-only** (`HOST_IP`), pas `0.0.0.0` public.
- Ne committez pas `.env` ni dumps Freebox (UID / token).
- CI GitHub = confs + smoke Docker — **aucun** poll distant de votre box.
