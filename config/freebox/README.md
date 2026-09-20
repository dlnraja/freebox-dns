# Freebox OS — DNS / DHCP (résolveur = VM, pas le PC)

1. VM Freebox (recommandé) ou Pi, IP LAN fixe = `HOST_IP` (ex. `192.168.1.71`).
2. **Ne pas** utiliser l’IP d’un PC Windows comme DNS DHCP du salon.
3. Après health-check : Freebox OS → DHCP.

| Champ | Valeur |
| --- | --- |
| DNS1 (SOS) | `9.9.9.10` (Quad9 Unsecured) |
| DNS2 (résolveur) | `HOST_IP` = IP de la **VM** dns-libre `:53` |

Wi‑Fi : [docs/wifi-lan.md](../../docs/wifi-lan.md) · Pages : [wifi-lan.html](https://dlnraja.github.io/freebox-dns/guides/wifi-lan.html)

Fallbacks max : `config/upstreams/uncensoring-catalog.json` → `plain_fallback_order`.

DoH (navigateur / téléphone, toujours vers la VM) :

- Libre : `https://HOST_IP:8453/dns-query`
- Secure : `https://HOST_IP:8444/dns-query`
- Blocky : `http://HOST_IP:3080`
