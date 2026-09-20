# Client encrypted DNS profiles (generated)

Host: `192.168.1.15`  
Smart split: **local hosts → mode filter → Unbound → world** — see [docs/modes.md](../../../docs/modes.md)

| Mode | Plain | DoH | DoT |
| --- | --- | --- | --- |
| **uncensored** | `192.168.1.15:5356` | `https://192.168.1.15:8453/dns-query` | `tls://192.168.1.15:8853` |
| **malware** | `192.168.1.15:5357` | `https://192.168.1.15:8445/dns-query` | `tls://192.168.1.15:8855` |
| **antipub** | `192.168.1.15:5358` | `https://192.168.1.15:8446/dns-query` | `tls://192.168.1.15:8856` |
| **secure** | `192.168.1.15:5354` | `https://192.168.1.15:8444/dns-query` | `tls://192.168.1.15:8854` |

## Freebox OS / app

1. DHCP (après health VM) : DNS1=`91.239.100.100`, DNS2=`192.168.1.15` (uncensored `:53` en prod).
2. Choix de mode : coller l’URL DoH du tableau (navigateur / app).
3. iOS/macOS : `apple-doh-<mode>.mobileconfig`.
4. Firefox : `firefox-policies-<mode>.json`.
5. Trust `certs/server.crt` (auto-signé LAN).

Regenerate: `python3 scripts/generate-client-profiles.py`
