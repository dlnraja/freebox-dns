# Boîte à outils OSINT / mesure (Korben)

Références :

- [OONI Probe — mesurer censure & surveillance](https://korben.info/ooni-probe-mesurer-niveau-de-manipulation-surveillance-censure-de-internet.html)
- [Web-Check — radiographie OSINT d’un site](https://korben.info/web-check-outil-osint-analyse-site-securite.html)
- Upstream : [ooni.org](https://ooni.org/) · [github.com/Lissy93/web-check](https://github.com/Lissy93/web-check)

## Mapping OONI Probe → freebox-dns

| Test OONI | Chez nous |
| --- | --- |
| **Web Connectivity** (DNS menteur / IP / HTTP) | `scripts/ooni-like-anti-lie.py` (DNS) + `scripts/web-connectivity-lite.py` (HTTP fingerprint ANJ/DGCCRF) |
| HTTP invalid request line (proxy manipulateur) | Hors scope DNS — VPN / observation manuelle |
| NDT (débit / bridging) | Hors scope |

Risques OONI : [ooni.org/about/risks](https://ooni.org/about/risks/) — nos scripts restent **locaux** (pas d’upload OONI).

```bash
python3 scripts/ooni-like-anti-lie.py
python3 scripts/web-connectivity-lite.py   # strip hosts si page de censure HTTP
```

Rapports : `config/uncensor/last-probe-report.json`, `config/uncensor/last-web-connectivity.json`.

## Web-Check (optionnel, profile Compose `osint`)

Scanner OSINT local (TLS, DNS records, headers, stack, SPF/DKIM…) — **sans** passer par web-check.xyz.

```bash
# Bind HOST_IP only (jamais 0.0.0.0)
docker compose --profile osint up -d web-check
# UI → http://$HOST_IP:3090
```

Utile pour radiographier un domaine *après* résolution via `dns-libre` (vérifier CDN, WAF, historique) — complémentaire, pas un bloqueur.
