# Anti-dégradation (bitrot / régression)

Automatisations qui détectent la **dégradation** du stack sans interroger votre Freebox.

## Suite principale

| Automatisation | Fréquence | Effet |
| --- | --- | --- |
| [`anti-degradation.yml`](../.github/workflows/anti-degradation.yml) | toutes les 8 h | SOS dig + DoT hosts + blocklists + Pages + invariants → **issue** si rouge |
| [`link-health.yml`](../.github/workflows/link-health.yml) | quotidien | URLs gravity / DoH / Pages |
| [`anti-lie-probe.yml`](../.github/workflows/anti-lie-probe.yml) | toutes les 6 h | Overrides locaux anti–DNS menteur → PR |
| [`validate-and-health.yml`](../.github/workflows/validate-and-health.yml) | 12 h + PR | Smoke Docker + probe listes + **invariants** |
| [`ci-regen.yml`](../.github/workflows/ci-regen.yml) | nightly | Drift générateurs Blocky/profils → PR |
| [`freebox-conf-sync.yml`](../.github/workflows/freebox-conf-sync.yml) | path + hebdo | Lint conf + drift Blocky |
| [`build-freebox-os-qcow2.yml`](../.github/workflows/build-freebox-os-qcow2.yml) | hebdo | Bitrot image Debian cloud |
| [`stale.yml`](../.github/workflows/stale.yml) | hebdo | Ferme issues/PR mortes (sauf `anti-degradation`) |
| Dependabot | hebdo | Actions / Docker |

## Script local

```bash
python3 scripts/anti-degradation-check.py
# Rapport : config/uncensor/last-anti-degradation.json

# CI rapide (sans réseau) :
ANTI_DEGRADATION_INVARIANTS_ONLY=1 python3 scripts/anti-degradation-check.py
```

## Ce qui est surveillé

1. **SOS UDP** `9.9.9.10` / Mullvad / AdGuard encore joignables  
2. **DoT catalogue** (DNS names résolvables)  
3. **Gravity URLs** HTTP 200  
4. **GitHub Pages** live  
5. **Invariants repo** : pins SOS, `sos_plain`, Unbound `forward-first`, queryLog Blocky, cache Unbound, ordre forward Quad9 avant UncensoredDNS  
6. **Générateur Blocky** encore exécutable  

Échecs **durs** (invariants) → exit 1 + issue.  
Échecs **soft** réseau (≤3) tolérés (flakes).

## Issue automatique

Label `anti-degradation` : ouverte/mise à jour quand le watchdog échoue, **fermée** quand il redevient vert.

Voir aussi [ci.md](ci.md).
