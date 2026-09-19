# Freebox — configuration DHCP / DNS / DoH

Compatible **Freebox Delta**, **Freebox Ultra**, et **VM Freebox** (Debian/Ubuntu dans la Freebox ou hôte local).

## Capturer les DNS une fois (déjà fait ici)

Sur le LAN de développement, snapshot enregistré dans `config/freebox-dns-snapshot.json` :

- Modèle vu : Freebox v9 (r1) — API 16
- DNS DHCP annoncés (Wi‑Fi) → `FREEBOX_DNS_1..5`
- **Aucun** UID Freebox, domaine distant `*.fbxos.fr`, ni adresse personnelle dans le dépôt

Pour un autre site : lisez les DNS du client DHCP, ou Freebox OS → réglages DNS/DHCP, puis éditez le snapshot **localement**.

## Pointer le DHCP vers la stack

1. Notez l’IP LAN de la machine Docker (`HOST_IP` dans `.env`).
2. En lab (ports 5353/5354) : les clients doivent utiliser un forwarder local ou mapper `53:53`.
3. En prod recommandée :

```env
DNS_LIBRE_PORT=53
DNS_SECURE_PORT=53
```

Utilisez **deux IP** (macvlan / second conteneur IP) ou un seul service DHCP primaire (libre) + secondaire (secure) si vous exposez secure sur une autre IP.

Exemple simple (un hôte, libre sur 53) :

| Champ Freebox DHCP | Valeur |
| --- | --- |
| DNS 1 | `HOST_IP` (dns-libre) |
| DNS 2 | `FREEBOX_DNS_1` (repli épinglé) |

## DoH optionnel

Le DHCP Freebox ne pousse en général **pas** de DoH. Configurez navigateur / OS :

- Libre : `https://HOST_IP:8443/dns-query`
- Secure : `https://HOST_IP:8444/dns-query`

Acceptez le certificat auto-signé LAN, ou remplacez `certs/` par un cert interne.

## VM Freebox

1. Créez une VM Debian/Ubuntu dans Freebox OS (ou utilisez un NAS/Pi).
2. Installez Docker Compose.
3. Clonez ce dépôt, `cp .env.example .env`, générez les certs, `docker compose up -d`.
4. Donnez une IP fixe LAN à la VM ; renseignez-la dans le DHCP Freebox.

## Sécurité / vie privée

- Ne committez pas `.env` ni de dumps Freebox contenant UID / token session.
- Ce projet n’implémente **aucun** polling distant périodique de votre box.
