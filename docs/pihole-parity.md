# Pi-hole parity — done via Blocky (not a Pi-hole clone)

This project does **not** run Pi-hole FTL. The Pi-hole-like DNS firewall is **Blocky**
on modes `malware` / `antipub` / `secure`. Uncensored mode is **dnsproxy** (no Blocky).

Canonical list map: [`config/blocky/lists/filter-intelligence.json`](../config/blocky/lists/filter-intelligence.json) · how-to: [filtering.md](filtering.md)

**Product choice:** keep Blocky + Freebox/router DHCP + SOS. Do **not** replace with Pi-hole
unless you explicitly want FTL DHCP / regex UI / teleporter.

## Feature matrix

| Capability | freebox-dns | Real Pi-hole | Status |
| --- | --- | --- | --- |
| Multi-list “gravity” | Blocky `denylists` (StevenBlack, HaGeZi, OISD, URLhaus…) | Gravity | **Done via Blocky** |
| List auto-update | `loading.refreshPeriod: 12h` | Gravity cron | **Done via Blocky** |
| Whitelist | `lists/allowlist.txt` (file) | Admin UI | **Done via files** (no UI edit) |
| Exact blacklist extras | `ads-extra.txt`, `anti-adblock.txt`, `malware-extra.txt` | Exact blacklist | **Done via files** |
| Block mode | `blockType: nxDomain` | NXDOMAIN / NULL / IP | **Done via Blocky** |
| List groups | `pihole` / `ublock` / `anti_adblock` / `malware` | Adlist groups | **Done via Blocky** |
| Per-client groups | All clients → `default` | Client → group | **Out of scope** — use **ports / DoH** (4 modes) instead |
| Admin UI | **secure only** → `http://HOST_IP:3080` | Full admin | **Partial by design** (malware/antipub HTTP not published) |
| Query log | CSV 7d on **secure** (`config/blocky/querylog/`) · `log.privacy: true` | Full dashboard log | **Partial** — local CSV, not Pi-hole charts |
| Prometheus / Grafana | `prometheus.enable: false` | Optional | **Off on purpose** |
| Regex denylists | None | Regex UI | **Out of scope** — use HaGeZi wildcards / file lists |
| Local DNS records | `hosts.*` + Unbound `a-records*.conf` | Local DNS UI | **Done via files** |
| Gravity teleporter | — | Backup/restore | **Out of scope** — Git + volumes |
| DHCP | Router / Freebox DHCP | Pi-hole DHCP | **Router** — DNS1=resolver, DNS2=`9.9.9.10` |
| Conditional forwarding | hosts / Unbound local-data | CF to router | **Out of scope as UI** — LAN = router / hosts pins |
| HTTP API | Blocky API on secure `:3080` | Pi-hole API | **Documented** in [filtering.md](filtering.md#blocky-http-api-secure--3080) |
| DoH / DoT / DoQ | dnsproxy + Blocky | Usually add-on | **Stronger than stock Pi-hole** |

## Modes ↔ mental model

| Mode | Port (prod lab) | Like… |
| --- | --- | --- |
| `uncensored` | `:53` | Pi-hole with **blocking off** + uncensoring Unbound |
| `malware` | `:5357` | Threat lists only |
| `antipub` | `:5358` | Classic ads/trackers + uBO DNS + anti-adblock |
| `secure` | `:5354` + UI `:3080` | Full filter + malware + thin UI + CSV log |

“**Smart spit**” = four personalities spit/split by port & DoH (not one FTL + client groups).

## Day-to-day lists

```bash
echo "cdn.example.com" >> config/blocky/lists/allowlist.txt
echo "bad-ads.example" >> config/blocky/lists/ads-extra.txt
python3 scripts/generate-blocky-modes.py   # if generator inputs changed
docker compose up -d --force-recreate dns-secure dns-antipub dns-malware
bash scripts/blocky-refresh-lists.sh
```

## Why not install Pi-hole itself?

Router DHCP + SOS, uncensoring Unbound DoT, four personalities on one host, and LAN-only binds fit this project better than a single FTL box. Blocky is the intentional engine — [CREDITS.md](CREDITS.md).
