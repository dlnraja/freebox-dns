# Local uncensor / anti–DNS menteur (OONI-inspired)

| Fichier | Rôle |
| --- | --- |
| `hosts.local` | Overrides manuels A/AAAA |
| `hosts.generated` | Rempli par `scripts/ooni-like-anti-lie.py` |
| `probe-targets.txt` | Domaines à tester |
| `sinkhole-signatures.json` | Signatures de mensonge (127.0.0.1, NXDOMAIN…) |
| `last-probe-report.json` | Dernier rapport |

Doc : [docs/anti-lie-dns.md](../../docs/anti-lie-dns.md) · OONI : https://ooni.org/
