# Wi‑Fi / LAN — le DNS vient de la Freebox, pas du PC

## Principe

```text
Téléphone / PC / TV  --Wi-Fi-->  Freebox (DHCP)
                                    │
                         DNS1 = 9.9.9.10   (SOS Quad9)
                         DNS2 = IP_VM      (freebox-dns sur la Freebox)
                                    │
                                    ▼
                         VM freebox-dns (Unbound local-first)
```

- **Résolveur métier** = la **VM** qui tourne **dans** Freebox OS.
- Votre **PC Windows** (`192.168.1.x`) est un **client** comme les autres.
- Ne lancez **pas** Docker Desktop comme DNS DHCP du salon.

## Configurer le DHCP Freebox (tous les clients Wi‑Fi)

1. Freebox OS → **Paramètres** → **Mode avancé** → **DHCP**
2. Serveurs DNS **personnalisés** :
   - DNS1 = `9.9.9.10`
   - DNS2 = IP LAN de la VM (ex. `192.168.1.71`)
3. Sur chaque appareil : oublier / reconnecter le Wi‑Fi, ou `ipconfig /renew` (Windows)

Vérifier depuis un PC :

```powershell
Get-DnsClientServerAddress -AddressFamily IPv4
# Attendu sur Wi-Fi : 9.9.9.10 puis 192.168.1.71 (ordre Freebox)

python -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.settimeout(2); ..."
# ou : dig @192.168.1.71 example.com +short
```

## Ce qu’il ne faut pas faire

| Erreur | Pourquoi |
| --- | --- |
| DHCP DNS = IP du PC Windows | Le PC éteint = plus de DNS pour tout le Wi‑Fi |
| DHCP DNS = seule IP VM sans SOS | VM down = Internet cassé |
| DHCP DNS = UncensoredDNS UDP | Souvent timeout sur Free — garder en DoT Unbound |
| Pointer le DNS Windows vers `127.0.0.1` | Ce n’est pas la Freebox |

## Lab sur le PC

Docker / WSL sur le PC = tests locaux (ports `5356`…).  
**Ne pas** enregistrer l’IP du PC dans le DHCP Freebox.

## Pages & docs liés

- [DHCP sûr](https://dlnraja.github.io/freebox-dns/guides/dhcp-safe.html)
- [Déployer Freebox VM](https://dlnraja.github.io/freebox-dns/guides/deploy-freebox.html)
- [Résilience local-first](resilience.md)
- [safe-freebox-deploy.md](safe-freebox-deploy.md)
