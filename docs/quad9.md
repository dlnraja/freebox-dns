# Quad9 — pourquoi `9.9.9.10` (SOS #1)

Référence officielle : [Services](https://docs.quad9.net/services/) · [adresses & features](https://www.quad9.net/service/service-addresses-and-features/).

## Choix du projet

| Rôle | Adresse | Pourquoi |
| --- | --- | --- |
| **DHCP SOS #1** + bootstrap Unbound / dns-libre | **`9.9.9.10`** (`dns10.quad9.net`) | **No Threat Blocking** — réponses intactes ; **pas d’ECS** (meilleure privacy) ; anycast UDP/53 joignable sur Free FR |
| Filtrage malware | **local** (`dns-secure` / Blocky) | Pas chez Quad9 Secured |

Ce n’est **pas** un DNS « debug only » pour nous : c’est le filet LAN quand la VM est down, aligné avec le bit **uncensored** de `dns-libre`.

## Matrice des variantes Quad9

| IPv4 | Nom officiel | Threat blocking | ECS | DoT / DoH | Dans ce repo |
| --- | --- | --- | --- | --- | --- |
| `9.9.9.9` | Secure | **oui** | non | `dns.quad9.net` | **Exclu** en primaire (filtre distant) |
| **`9.9.9.10`** | **No Threat Blocking** | **non** | **non** | `dns10.quad9.net` | **SOS #1** + DoT catalogue |
| `9.9.9.11` | Secure + ECS | oui | **oui** | `dns11.quad9.net` | Exclu (filtre + ECS) |
| `9.9.9.12` | No Threat Blocking + ECS | non | **oui** | `dns12.quad9.net` | Exclu (ECS = préfixe client aux auth) |

Secondaries IPv4 utiles avec `.10` : `149.112.112.10` (déjà dans Unbound / fallbacks).

### DNSSEC (état 2026)

Historiquement, `.10` / `.12` pouvaient servir de référence **sans** validation DNSSEC (dépannage).  
**Depuis le 15 juin 2026**, Quad9 active la validation DNSSEC sur **toutes** les adresses (y compris `.10`) — un échec DNSSEC renvoie `SERVFAIL`.  
Pour un test *non-validating*, il faut un résolveur **hors** Quad9 (ex. Mullvad / AdGuard NF du filet SOS).

### ECS en un mot

ECS envoie un préfixe de l’IP client aux serveurs autoritaires (meilleur géo-CDN, moins de privacy).  
Nous gardons **`.10` (sans ECS)** ; pas `.12`.

## Ce que `9.9.9.10` n’est pas

- Pas `9.9.9.9` (malware/phishing bloqués **chez** Quad9 — chez nous c’est `dns-secure`)
- Pas UncensoredDNS (`91.239.100.100`) — autre opérateur, DoT-only sur Free
- Pas le résolveur LAN : la **VM** (`HOST_IP`) reste DNS2 après health-check

## Config projet (rappel)

```text
Freebox DHCP  →  DNS1 = 9.9.9.10   DNS2 = IP_VM
Unbound DoT   →  9.9.9.10@853#dns10.quad9.net  (avant UncensoredDNS)
dns-libre     →  plain + DoH/DoT vers dns10.quad9.net
```

Voir aussi [dns-pins.md](dns-pins.md) · [dns-lexicon.md](dns-lexicon.md) · [safe-freebox-deploy.md](safe-freebox-deploy.md).
