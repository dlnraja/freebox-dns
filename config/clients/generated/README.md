# Client encrypted DNS profiles (generated)

Host: `192.168.1.15`

| Personality | Plain | DoH | DoT | DoQ |
| --- | --- | --- | --- | --- |
| **libre** | `192.168.1.15:5356` | `https://192.168.1.15:8453/dns-query` | `tls://192.168.1.15:8853` | `quic://192.168.1.15:8853` |
| **secure** | `192.168.1.15:5354` | `https://192.168.1.15:8444/dns-query` | `tls://192.168.1.15:8854` | — |

## Freebox OS / app

1. DHCP (après health VM) : DNS1=`91.239.100.100`, DNS2=`192.168.1.15` (ou inverse seulement si double check OK).
2. Navigateurs / Freebox app Web : coller l’URL DoH **libre** ou **secure**.
3. iOS/macOS : installer `apple-doh-libre.mobileconfig` (Réglages → Profil).
4. Firefox : `about:policies` ← `firefox-policies-libre.json`.
5. Trust `certs/server.crt` (auto-signé LAN).

Regenerate: `python3 scripts/generate-client-profiles.py`
