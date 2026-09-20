# Pi-hole parity — done via Blocky

This project does **not** run Pi-hole FTL. The **Pi-hole-like** DNS firewall is **Blocky** on modes `antipub` / `secure` (and malware lists on `malware` / `secure`).

Canonical list map: [`config/blocky/lists/filter-intelligence.json`](../config/blocky/lists/filter-intelligence.json) · narrative: [filtering.md](filtering.md)

## Feature matrix

| Pi-hole feature | freebox-dns | How |
| --- | --- | --- |
| Gravity multi-list | **Yes** | Blocky groups `pihole` + `ublock` (+ `malware`) |
| List auto-update | **Yes** | `loading.refreshPeriod: 12h` |
| Exact blacklist | **Yes** | `lists/ads-extra.txt`, `anti-adblock.txt`, `malware-extra.txt` |
| Whitelist | **Yes** | `lists/allowlist.txt` (edit file, recreate container) |
| NXDOMAIN block | **Yes** | `blockType: nxDomain` |
| Groups | **Yes** | Groups above; modes select which subset applies |
| Query log (verbose) | **Yes (secure)** | CSV → `config/blocky/querylog/` (7 days, local VM only) |
| Force gravity refresh | **Yes** | `bash scripts/blocky-refresh-lists.sh` |
| Admin UI / light stats | **Yes** | Blocky UI on **secure** → `http://HOST_IP:3080` |
| DHCP | **Via Freebox** | DNS1 SOS + DNS2 = VM — not Pi-hole DHCP |
| Local DNS records | **Yes (files)** | `config/uncensor/hosts.*` + Unbound `a-records*.conf` |
| Conditional forwarding | **N/A** | LAN names via Freebox / hosts; Unbound local-data |
| Regex blacklist | **No** | Use HaGeZi wildcards / file lists; no Pi-hole regex UI |
| Teleporter backup | **No** | Git + compose volumes |
| Parental / porn / SafeSearch | **Excluded** | Never |

## Modes ↔ Pi-hole mental model

| Mode | Port prod | Like… |
| --- | --- | --- |
| `uncensored` | `:53` | Pi-hole with **all blocking off** + uncensoring Unbound |
| `malware` | `:5357` | Threat lists only |
| `antipub` | `:5358` | Classic Pi-hole ads/trackers + uBO DNS + anti-adblock |
| `secure` | `:5354` | Full Pi-hole-like + malware (+ UI `:3080`) |

## Whitelist / blacklist day-to-day

```bash
# Allow a domain (Pi-hole whitelist equivalent)
echo "example-cdn.good.com" >> config/blocky/lists/allowlist.txt

# Block an extra ad domain
echo "annoying-ads.example" >> config/blocky/lists/ads-extra.txt

python3 scripts/generate-blocky-modes.py   # if you changed generator inputs
docker compose up -d --force-recreate dns-secure dns-antipub dns-malware
bash scripts/blocky-refresh-lists.sh
```

## uBlock Origin

DNS cannot do cosmetic filters. Keep **uBlock Origin in the browser**; DNS covers EasyList/EasyPrivacy-class **domains** via HaGeZi / Firebog.

## Why not install Pi-hole itself?

Freebox DHCP + SOS, uncensoring Unbound DoT, and four personalities on one VM fit better than a single FTL box. Blocky is the intentional engine — see CREDITS.
