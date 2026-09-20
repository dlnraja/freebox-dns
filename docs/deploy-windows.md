# Windows natif — résolveur DNS sans Docker

Hébergez le DNS sur Windows avec **un seul binaire** ([AdGuard dnsproxy](https://github.com/AdguardTeam/dnsproxy)) :
hosts locaux + DoT uncensoring. Aucune Freebox, aucun Docker requis.

Idéal : mini-PC / NUC **toujours allumé**. Un laptop qui dort ≠ DNS pour le salon.

## Démarrage rapide

PowerShell **en Administrateur** (port 53) :

```powershell
cd C:\chemin\vers\freebox-dns
powershell -ExecutionPolicy Bypass -File .\scripts\windows-native\Run-DnsResolver.ps1
```

Le script :

1. Télécharge `dnsproxy.exe` dans `scripts/windows-native/bin/` si besoin
2. Écrit une config runtime avec chemins absolus vers `config/uncensor/hosts.*`
3. Écoute sur l’**IP LAN privée** (jamais `0.0.0.0` / Internet — [lan-only.md](lan-only.md))

Test :

```powershell
Resolve-DnsName example.com -Server 127.0.0.1
# Depuis un autre appareil du LAN :
Resolve-DnsName example.com -Server 192.168.x.x
```

Puis pointez **DNS1** vers l’IP LAN de ce Windows — [wifi-lan.md](wifi-lan.md).

### Options

```powershell
# IP précise (recommandé si plusieurs interfaces)
.\scripts\windows-native\Run-DnsResolver.ps1 -ListenAddr 192.168.1.50

# Port lab si 53 est pris / sans admin
.\scripts\windows-native\Run-DnsResolver.ps1 -Port 5353
# → DNS client : 192.168.1.50#5353 (ou netsh portproxy 53→5353)
```

Arrêt : `Ctrl+C`. Pour un service permanent : [Install-DnsResolver.ps1](../scripts/windows-native/Install-DnsResolver.ps1) (tâche planifiée au logon).

## Ce que ça fait / ne fait pas

| Oui | Non (stack Pi/VM) |
| --- | --- |
| hosts.critical / local / generated | Unbound serve-expired + local-data |
| DoT Mullvad / Quad9 / AdGuard / … | Modes Blocky malware / antipub / secure |
| Cache dnsproxy + fallbacks SOS | UI Blocky `:3080` |

Pour peupler les hosts anti-lie (optionnel, Python) :

```powershell
python scripts\warm-local-cache.py
python scripts\ooni-like-anti-lie.py
# puis redémarrer Run-DnsResolver.ps1
```

## Pointer ce PC comme DNS (un appareil)

```powershell
# Admin — DNS1 = ce PC, DNS2 = SOS
.\scripts\set-windows-wifi-dns-to-vm.ps1 -ResolverDns 192.168.1.50
```

Pour **tout le Wi‑Fi** : configurez le DHCP du routeur (Freebox ou autre) avec la même paire — pas seulement ce script.

## Firewall

Autoriser UDP/TCP **53** entrant sur le profil Privé (le script propose une règle si admin).

---

## Sources

dnsproxy : AdGuardTeam · hosts / catalogue : ce dépôt · [CREDITS.md](CREDITS.md)
