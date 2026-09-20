# Pointer le LAN vers le résolveur

**Objectif :** DNS1 = IP de la machine qui fait tourner freebox-dns
(Pi, VM, ou Windows). Ensuite téléphones / PC / TV résolvent via chez vous.

```text
Appareils  →  routeur (DHCP)  ou  DNS manuel sur l’appareil
                 │
                 DNS1 = IP_RESOLVEUR   ← Pi / VM / Windows (ce projet)
                 DNS2 = 9.9.9.10      ← SOS Quad9 (si la machine est down)
                 │
                 ▼
            freebox-dns (:53)
```

Aucune Freebox n’est requise : tout routeur qui laisse régler les DNS DHCP convient.

## Sur le routeur (tous les clients Wi‑Fi)

1. IP **fixe** ou bail réservé pour la machine résolveur.
2. DHCP → DNS personnalisés :
   - **DNS1** = IP du résolveur
   - **DNS2** = `9.9.9.10` (recommandé)
3. Reconnecter le Wi‑Fi / `ipconfig /renew`.

### Si vous avez une Freebox

Freebox OS → Mode avancé → DHCP → mêmes valeurs.  
Détail Freebox : [freebox.md](freebox.md) · déploiement sûr : [safe-freebox-deploy.md](safe-freebox-deploy.md).

## Sur un seul appareil (sans toucher au routeur)

| OS | Action |
| --- | --- |
| Windows | `scripts/set-windows-wifi-dns-to-vm.ps1 -ResolverDns IP` (Admin) |
| Android / iOS | Wi‑Fi → DNS manuel → IP du résolveur |
| Linux | NetworkManager / `resolvectl` |

Vérifier :

```bash
dig @IP_RESOLVEUR example.com +short
```

```powershell
Resolve-DnsName example.com -Server IP_RESOLVEUR
Get-DnsClientServerAddress -AddressFamily IPv4
```

## Erreurs fréquentes

| Erreur | Pourquoi |
| --- | --- |
| DNS1 = PC portable qui dort | Plus de DNS dès que le PC s’éteint |
| DNS1 = IP lab Docker (`5356`) sans `:53` | Les clients DHCP parlent au **port 53** |
| Oublier de tester `dig @IP` avant le DHCP | Un mauvais DNS casse tout le salon — testez d’abord |
| Uniquement DNS publics, jamais l’IP locale | Vous n’utilisez pas ce projet |
| Ouvrir le port 53/853 vers Internet (NAT Freebox) | Résolveur ouvert = **DDoS** — [lan-only.md](lan-only.md) |

## Lab vs salon

- **Salon** : Pi / VM / mini-PC Windows **prod** (`:53`) → DNS1 = cette IP.
- **Lab** : Docker sur le PC de dev (ports `5356`…) → ne pas mettre cette IP dans le DHCP familial.

Déploiement : [deploy.md](deploy.md).
