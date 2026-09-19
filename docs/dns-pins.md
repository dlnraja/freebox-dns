# Identité des 5 DNS épinglés (FREEBOX_DNS_1..5)

Snapshot capturé une fois depuis le LAN Freebox (DHCP Wi‑Fi). **Aucun** polling distant ultérieur.

| Pin | IP | Rôle / « bit » | Notes |
| --- | --- | --- | --- |
| FREEBOX_DNS_1 | `91.239.100.100` | **UncensoredDNS** (anycast) | Résolveur anti-censure (DK). Pas de filtre politique. |
| FREEBOX_DNS_2 | `185.95.218.42` | **Digitale Gesellschaft** (CH) | DNS privé suisse, DoT/DoH disponibles côté amont. |
| FREEBOX_DNS_3 | `9.9.9.10` | **Quad9 unblocked** (+ ECS) | Quad9 **sans** blocklist malware (contrairement à `9.9.9.9`). |
| FREEBOX_DNS_4 | `45.90.28.0` | **NextDNS** anycast | Entrée DHCP Freebox ; comportement selon config NextDNS si ID client. |
| FREEBOX_DNS_5 | `192.168.1.254` | **Passerelle Freebox** | Résolveur / gateway LAN local (repli ultime sur le site). |

## Comment la stack les utilise

1. **dns-libre** : Unbound (amonts DoT non censeurs) en premier ; pins en fallback dnsproxy.
2. **dns-secure** : Blocky vers DoT non censeurs + listes ads/malware ; groupe `freebox_fallback` = mêmes pins.
3. **DHCP Freebox** (prod) : DNS1 = IP de la VM/hôte Docker ; DNS2 = `FREEBOX_DNS_1` (ou autre pin) si la VM tombe.

## Référence opérateur Free (non utilisée en primaire)

| Nom | IP |
| --- | --- |
| ns0.free.fr | `212.27.32.5` |
| ns1.free.fr | `213.228.0.168` |

Conservés dans `config/freebox-dns-snapshot.json` pour comparaison — **pas** comme amonts principaux (risque DNS menteur / politique opérateur).

## Mettre à jour localement

Éditez `config/freebox-dns-snapshot.json` + `.env`, puis `bash scripts/apply-freebox-snapshot.sh` si disponible. Ne jamais automatiser une relecture distante de votre Freebox depuis le CI.
