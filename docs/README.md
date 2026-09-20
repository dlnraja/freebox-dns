# Documentation freebox-dns

**But produit :** héberger un DNS local → mettre son IP en **DNS1** → ça marche.
Freebox / Docker / votre salon précis ne sont **pas** des prérequis.

## Démarrer ici

| | |
| --- | --- |
| **Choisir où déployer** | [deploy.md](deploy.md) |
| **Pi** | [deploy-pi.md](deploy-pi.md) |
| **Windows (exe, sans Docker)** | [deploy-windows.md](deploy-windows.md) |
| **VM Freebox (option)** | [freebox-vm.md](freebox-vm.md) |
| **Pointer DNS1 / Wi‑Fi** | [wifi-lan.md](wifi-lan.md) |
| **LAN only (pas Internet)** | [lan-only.md](lan-only.md) |
| **Guides web** | [dlnraja.github.io/freebox-dns](https://dlnraja.github.io/freebox-dns/) |

## Produit

| Doc | Sujet |
| --- | --- |
| [modes.md](modes.md) | 4 modes « smart spit » |
| [filtering.md](filtering.md) · [pihole-parity.md](pihole-parity.md) | Listes Blocky (pas un clone Pi-hole) |
| [resilience.md](resilience.md) | Local-first Unbound / hosts |
| [encrypted-dns.md](encrypted-dns.md) | Do53 / DoH / DoT / DoQ / DNSCrypt |
| [anti-lie-dns.md](anti-lie-dns.md) | Anti–DNS menteur |
| [quad9.md](quad9.md) | SOS `9.9.9.10` |
| [dns-analysis.md](dns-analysis.md) | Analyse des pins |
| [CREDITS.md](CREDITS.md) | Sources & crédits |

## Freebox seulement (optionnel)

| Doc | Sujet |
| --- | --- |
| [freebox.md](freebox.md) | DHCP Freebox |
| [safe-freebox-deploy.md](safe-freebox-deploy.md) | Ne pas casser Internet |
| [dns-pins.md](dns-pins.md) · [dns-lexicon.md](dns-lexicon.md) | Pins historiques du projet |

## Lab / CI

| Doc | Sujet |
| --- | --- |
| [deploy-wsl.md](deploy-wsl.md) | Lab Docker / WSL (pas le DNS salon) |
| [ci.md](ci.md) · [anti-degradation.md](anti-degradation.md) | Automatisation GitHub |
| [CREDITS.md](CREDITS.md) | Sources |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) · [../SECURITY.md](../SECURITY.md) | Contrib / sécu |

Site HTML : [`../site/`](../site/).
