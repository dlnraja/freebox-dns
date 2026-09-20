# Freebox OS — DNS / DHCP (option Freebox)

Le résolveur = la **VM / Pi** (`HOST_IP`), pas un PC qui s’éteint.
Sans Freebox : même paire DNS sur n’importe quel routeur — [docs/wifi-lan.md](../../docs/wifi-lan.md).

1. Machine toujours allumée, IP LAN fixe = `HOST_IP`.
2. Health-check OK (`dig @HOST_IP example.com`).
3. Freebox OS → DHCP :

| Champ | Valeur |
| --- | --- |
| **DNS1** (résolveur) | `HOST_IP` — dns-libre `:53` |
| **DNS2** (SOS) | `9.9.9.10` (Quad9 — [quad9.md](../../docs/quad9.md)) |

DoH (vers la même machine) :

- Libre : `https://HOST_IP:8453/dns-query`
- Secure : `https://HOST_IP:8444/dns-query`
- Blocky UI : `http://HOST_IP:3080`
