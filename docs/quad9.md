# Quad9 — pourquoi `9.9.9.10` (SOS #1)

Références : [Services Quad9](https://docs.quad9.net/services/) · [CaptainDNS — DNS 9.9.9.9](https://www.captaindns.com/fr/blog/dns-9999-quad9) · [DoH HTTP/1.1 retirement](https://quad9.net/news/blog/doh-http-1-1-retirement/) · [comparatif publics](https://www.captaindns.com/fr/blog/public-dns-resolver-benchmark-comparison-guide).

## Choix du projet (≠ défaut PME CaptainDNS)

| Rôle | Adresse | Pourquoi |
| --- | --- | --- |
| **DHCP SOS #1** + bootstrap | **`9.9.9.10`** (`dns10.quad9.net`) | **No Threat Blocking** + **pas d’ECS** ; Internet intact si la VM tombe |
| Filtrage malware / pubs | **local** (`dns-secure` / Blocky) | Équivalent opérationnel de Quad9 Secure, mais contrôlé chez nous |
| Amont Unbound / dns-libre | DoT `dns10.quad9.net` | Même service *unfiltered* en chiffré |

CaptainDNS recommande `9.9.9.9` en prod PME et réserve `.10` au **debug**.  
Chez nous, le « Secure » est **Blocky** ; le filet DHCP doit rester **uncensored** → `.10` est volontairement le SOS de prod (pas un oubli).

**Ne jamais mélanger** `.9` et `.10` dans le même round-robin DHCP/forwarder (perte de couverture + diag impossible) — CaptainDNS + nous sommes d’accord.

## Matrice des variantes

| IPv4 | Nom | Threat | ECS | DoT / DoH | Repo |
| --- | --- | --- | --- | --- | --- |
| `9.9.9.9` | Secure | oui | non | `dns.quad9.net` | Exclu primaire |
| **`9.9.9.10`** | **No Threat Blocking** | non | non | `dns10.quad9.net` | **SOS #1** |
| `9.9.9.11` | Secure + ECS | oui | oui | `dns11.quad9.net` | Exclu |
| `9.9.9.12` | No Threat + ECS | non | oui | `dns12.quad9.net` | Exclu |

Secondaires IPv4 `.10` : `149.112.112.10`.  
IPv6 `.10` : `2620:fe::10`, `2620:fe::fe:10`.

### DNSSEC

CaptainDNS (déc. 2025) notait encore « pas de DNSSEC » sur `.10`.  
**Depuis le 15 juin 2026**, Quad9 valide DNSSEC sur **toutes** les adresses (y compris `.10`) → `SERVFAIL` si zone cassée.  
Pour un test *non-validating*, utiliser Mullvad / AdGuard NF (hors Quad9).

### ECS

Ne basculer vers `.11` / `.12` **que** si un vrai problème CDN/géoloc est prouvé. Nous restons sans ECS.

## Pattern forwarder (aligné CaptainDNS)

```text
Clients LAN  →  Freebox DHCP : DNS1=9.9.9.10  DNS2=IP_VM
IP_VM        →  dns-libre / Blocky  →  Unbound (cache)
Unbound      →  DoT 9.9.9.10@853#dns10.quad9.net (+ catalogue)
```

Bénéfices rappelés par CaptainDNS : chiffrement sortant, cache local, point de contrôle unique.

## DoH Quad9 : HTTP/2 obligatoire

Depuis le **15 décembre 2025**, Quad9 n’accepte plus DoH en **HTTP/1.1** ([annonce](https://quad9.net/news/blog/doh-http-1-1-retirement/)).

- Clients DoH → Quad9 : **HTTP/2+** (dnsproxy / navigateurs OK ; MikroTik DoH legacy = basculer DoT).
- Fallback sûr : **DoT** `tls://dns10.quad9.net` (déjà dans `dns-libre.yaml`).

```bash
curl --http2 -I https://dns10.quad9.net/dns-query
python3 scripts/quad9-ops-check.py
```

## Tests opérationnels (CaptainDNS)

| Test | Commande / outil | Attendu |
| --- | --- | --- |
| Suis-je sur Quad9 ? | <https://on.quad9.net> | Page confirme Quad9 |
| Protocole réel | `dig +short txt proto.on.quad9.net.` | `do53-udp` / `dot` / `doh` / … |
| Blocage Secure | `dig @9.9.9.9 isitblocked.org` | NXDOMAIN + `AUTHORITY: 0` = block Quad9 |
| SOS unfiltered | `dig @9.9.9.10 isitblocked.org` | Doit **résoudre** (pas de threat block) |
| Suite repo | `python3 scripts/quad9-ops-check.py` | Rapport JSON |

Windows : `Resolve-DnsName -Type txt proto.on.quad9.net.`

## Config projet (rappel)

```text
Freebox DHCP  →  DNS1 = 9.9.9.10 (+ optionnel 149.112.112.10 en 3ᵉ pin lab)
Unbound DoT   →  9.9.9.10@853#dns10.quad9.net
dns-libre FB  →  https://dns10.quad9.net/dns-query  puis  tls://dns10.quad9.net
```

Voir [public-dns-landscape.md](public-dns-landscape.md) · [encrypted-dns.md](encrypted-dns.md) · [dns-pins.md](dns-pins.md).
