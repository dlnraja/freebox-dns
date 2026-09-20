# Client encrypted DNS profiles (generated)

Host: `192.168.1.15`  
Transports: **Do53 · DoH · DoT · DoQ · DNSCrypt** — [docs/encrypted-dns.md](../../../docs/encrypted-dns.md)

| Mode | Plain (Do53) | DoH | DoT |
| --- | --- | --- | --- |
| **uncensored** | `192.168.1.15:5356` | `https://192.168.1.15:8453/dns-query` | `tls://192.168.1.15:8853` |
| **malware** | `192.168.1.15:5357` | `https://192.168.1.15:8445/dns-query` | `tls://192.168.1.15:8855` |
| **antipub** | `192.168.1.15:5358` | `https://192.168.1.15:8446/dns-query` | `tls://192.168.1.15:8856` |
| **secure** | `192.168.1.15:5354` | `https://192.168.1.15:8444/dns-query` | `tls://192.168.1.15:8854` |

| Extra | Endpoint |
| --- | --- |
| **DoQ** (uncensored) | `quic://192.168.1.15:8853` |
| **DNSCrypt proxy** | `192.168.1.15:5359` (Do53→DNSCrypt→Quad9 nofilter) |
| **DNSCrypt server** | `192.168.1.15:8443` / `dnscrypt-stamp.txt` (after `scripts/dnscrypt-server-init.sh`) |

## Freebox OS / Wi-Fi

1. DHCP (après health VM) : DNS1=`9.9.9.10` (SOS), DNS2=`192.168.1.15` (**VM Freebox** uncensored `:53` — pas le PC).
2. Choix de mode : coller l’URL DoH du tableau (navigateur / app).
3. iOS/macOS : `apple-doh-<mode>.mobileconfig`.
4. Firefox : `firefox-policies-<mode>.json`.
5. Trust `certs/server.crt` (auto-signé LAN).
6. DNSCrypt : voir [config/dnscrypt/README.md](../../dnscrypt/README.md).

Host `192.168.1.15` = IP de la **VM freebox-dns** sur Freebox OS.  
Wi‑Fi : voir docs/wifi-lan.md

Regenerate: `HOST_IP=<vm> python3 scripts/generate-client-profiles.py`
