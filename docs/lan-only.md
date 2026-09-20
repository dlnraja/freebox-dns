# LAN only — ne jamais exposer le résolveur sur Internet

## Oui, c’est risqué

Un DNS **récursif ouvert** sur Internet sert surtout à :

- **Amplification DDoS** (requêtes spoofées → grosses réponses vers une victime)
- Abus / scan / pollution de cache
- Exposition DoH/DoT/UI Blocky hors du salon

Ce projet est un **résolveur de salon (LAN)** — pas un DNS public.

## Ce que le dépôt impose

| Couche | Comportement |
| --- | --- |
| Docker Compose | Ports publiés uniquement sur `${HOST_IP}` (IP LAN), **jamais** `0.0.0.0` |
| Unbound | `access-control` = réseaux privés seulement (`10/8`, `172.16/12`, `192.168/16`, …) |
| Windows natif | Bind auto sur une IPv4 **privée** ; refuse `0.0.0.0` sauf `-ForcePublicBind` |
| Pare-feu Windows | Règle **Private** uniquement, adresse locale = IP LAN |
| CI | `scripts/assert-lan-only.py` échoue si bind public |

```bash
python3 scripts/assert-lan-only.py
```

## Ce que vous ne devez pas faire sur le routeur / Freebox

- **Pas** de redirection de ports (NAT) vers la VM/Pi pour `53`, `853`, `443`, `8443–8453`, `3080`
- **Pas** de « accès distant » / IPv6 firewall ouvert vers ces ports
- **Pas** de `HOST_IP=0.0.0.0` dans `.env`

Les clients du salon atteignent déjà le résolveur via l’IP LAN (DHCP DNS1). Aucun besoin d’Internet entrant.

## Vérifier

```bash
# Depuis le LAN — OK
dig @IP_LAN example.com +short

# Depuis Internet (ne doit PAS répondre) — ou scanner shodan/censys
# Si ça répond : fermer le NAT / le firewall immédiatement
```

Sur Freebox OS : Paramètres → **Gestion des ports** / **IPv6** → aucune ouverture vers la VM DNS.

Voir aussi [SECURITY.md](../SECURITY.md) · [wifi-lan.md](wifi-lan.md).
