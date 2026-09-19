# Identité des 5 DNS épinglés (FREEBOX_DNS_1..5)

Snapshot capturé une fois depuis le LAN Freebox (DHCP Wi‑Fi). **Aucun** polling distant ultérieur.

Lexique fin + dérivation des DNS locaux : **[dns-lexicon.md](dns-lexicon.md)**.

| Pin | IP | Nom officiel | Bits lexicaux | Notes |
| --- | --- | --- | --- | --- |
| FREEBOX_DNS_1 | `91.239.100.100` | **UncensoredDNS** | uncensored, *censurfri*, anycast | Anti-censure DK — donneur principal du bit `uncensored` local |
| FREEBOX_DNS_2 | `185.95.218.42` | **Digitale Gesellschaft** | Privatsphäre, kein Logging, keine Sperrlisten, freier Zugang | Privacy CH — transport DoT/DoH + no-log spirit |
| FREEBOX_DNS_3 | `9.9.9.10` | **Quad9 Unsecured** (+ ECS) | Unsecured / unblocked (≠ Secured `9.9.9.9`) | Chemin réponses intactes — bootstrap rapide |
| FREEBOX_DNS_4 | `45.90.28.0` | **NextDNS** | firewall DNS, denylist, profiles, ads/trackers | Donneur du bit `threat-local` — **pas** amont primaire |
| FREEBOX_DNS_5 | `192.168.1.254` | **Passerelle Freebox** | gateway, LAN, last hop | Bit `lan-gateway` — bind local-only + repli ultime |

## Verdict

| Pin | Verdict |
| --- | --- |
| 1–3 | ✅ Fallback / bootstrap + lexique de **dns-libre** |
| 4 NextDNS | ⚠️ Lexique pour **dns-secure** seulement (pas amont principal) |
| 5 Gateway | ⚠️ Repli LAN ultime + inspiration exposition locale |

## Personnalités locales dérivées

| Local | Bit | Inspiré de |
| --- | --- | --- |
| **dns-libre** | `uncensored` | #1 + #2 + #3 Unsecured |
| **dns-secure** | `threat-local` | #4 toolkit (sans parental/cloud) |
| Site bind | `lan-gateway` | #5 |

**Amonts complémentaires** : Mullvad, dns0.eu, Digitale Gesellschaft, UncensoredDNS — dans `config/unbound/forward-records.conf` et `config/blocky/config.yml`.

## Comment la stack les utilise

1. **dns-libre** : Unbound (DoT complémentaires) ; fallback pins **1 → 2 → 3 → 5**.
2. **dns-secure** : Blocky + denylists ads/malware ; mêmes DoT uncensoring (filtre local, pas Quad9 Secured).
3. **DHCP Freebox** : DNS1 = `HOST_IP` ; DNS2 = `FREEBOX_DNS_1`.

## Référence opérateur Free (non utilisée en primaire)

| Nom | IP |
| --- | --- |
| ns0.free.fr | `212.27.32.5` |
| ns1.free.fr | `213.228.0.168` |

## Mettre à jour localement

Éditez `config/freebox-dns-snapshot.json` + `.env`, puis `bash scripts/apply-freebox-snapshot.sh` si disponible. Ne jamais automatiser une relecture distante de votre Freebox depuis le CI.
