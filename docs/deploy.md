# Déployer freebox-dns

Choisissez **où** tourne le résolveur. Le but est toujours le même :
quelqu’un met **l’IP de cette machine en DNS1** → ça résout.

## Quelle cible ?

| Cible | Docker ? | Stack | Guide |
| --- | --- | --- | --- |
| **Raspberry Pi** | Oui (recommandé) | Complet : Unbound + 4 modes Blocky/dnsproxy | [deploy-pi.md](deploy-pi.md) |
| **VM Freebox OS** (ou autre VM Linux) | Oui | Idem | [freebox-vm.md](freebox-vm.md) |
| **Windows** (PC / mini-PC) | **Non** | Lite : un `dnsproxy.exe` + hosts + DoT | [deploy-windows.md](deploy-windows.md) |
| Lab Docker sur PC | Oui | Ports `5356`… — **ne pas** mettre cette IP en DHCP salon | [deploy-wsl.md](deploy-wsl.md) |

Après démarrage → [wifi-lan.md](wifi-lan.md) (DNS1 = IP du résolveur).

## Checklist commune

1. Machine **joignable en permanence** sur le LAN (IP fixe ou bail DHCP réservé).
2. Service DNS écoute sur **`:53`** (prod) ou vous pointez explicitement le port lab.
3. Test depuis un autre appareil : `dig @IP_RESOLVEUR example.com`.
4. Routeur ou interface réseau : **DNS1 = IP_RESOLVEUR**, DNS2 = `9.9.9.10` (SOS).

## Freebox n’est pas obligatoire

Si vous n’avez pas de Freebox : Pi, NAS Linux, Proxmox, Windows — même idée.
Les docs `freebox*.md` sont des **recettes** pour cet environnement, pas une dépendance.

## Stack complète vs lite Windows

```text
Complet (Pi / VM)     hosts → Blocky|dnsproxy → Unbound (local-data + DoT + root)
Lite (Windows exe)    hosts → dnsproxy → DoT catalogue (+ SOS fallback)
```

Le lite Windows suffit pour « DNS1 = mon PC/mini-PC et ça marche ».  
Les 4 modes filtrés demandent la stack complète (Pi/VM).
