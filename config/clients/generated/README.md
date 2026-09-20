# Client encrypted DNS profiles (generated)

Host: `192.168.1.71`  
Smart split: **local hosts → mode filter → Unbound → world** — see [docs/modes.md](../../../docs/modes.md)

| Mode | Plain | DoH | DoT |
| --- | --- | --- | --- |
| **uncensored** | `192.168.1.71:5356` | `https://192.168.1.71:8453/dns-query` | `tls://192.168.1.71:8853` |
| **malware** | `192.168.1.71:5357` | `https://192.168.1.71:8445/dns-query` | `tls://192.168.1.71:8855` |
| **antipub** | `192.168.1.71:5358` | `https://192.168.1.71:8446/dns-query` | `tls://192.168.1.71:8856` |
| **secure** | `192.168.1.71:5354` | `https://192.168.1.71:8444/dns-query` | `tls://192.168.1.71:8854` |

## Freebox OS / Wi-Fi

1. DHCP (après health VM) : DNS1=`9.9.9.10` (SOS), DNS2=`192.168.1.71` (**VM Freebox** uncensored `:53` — pas le PC).
2. Choix de mode : coller l’URL DoH du tableau (navigateur / app).
3. iOS/macOS : `apple-doh-<mode>.mobileconfig`.
4. Firefox : `firefox-policies-<mode>.json`.
5. Trust `certs/server.crt` (auto-signé LAN).

Host `192.168.1.71` = IP de la **VM freebox-dns** sur Freebox OS.  
Wi‑Fi : voir docs/wifi-lan.md

Regenerate: `HOST_IP=<vm> python3 scripts/generate-client-profiles.py`
