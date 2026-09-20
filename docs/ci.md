# CI / GitHub Actions

Workflows live in `.github/workflows/`. None of them poll a live Freebox.

| Workflow | Trigger | Role |
| --- | --- | --- |
| **`validate-and-health.yml`** | push / PR* / 12h | Compose + reusable conf-lint + inventory + SOS digs + blocklist PR + Docker smoke |
| **`reusable-conf-lint.yml`** | `workflow_call` | Shared JSON/YAML/Blocky/product/lan-only (`scripts/ci-conf-lint.py`) |
| **`freebox-conf-sync.yml`** | path / weekly | Thin wrapper → reusable conf-lint |
| **`anti-degradation.yml`** | every 8h / PR | Bitrot watchdog → issue if red |
| **`link-health.yml`** | daily / PR | Critical URLs fail-closed; soft budget for mirrors |
| **`docs-ci.yml`** | docs/site | Required files + local site hrefs + product DHCP |
| **`docs-lint.yml`** | docs/site / Mon | Lychee links (soft on PR, hard on schedule) |
| **`github-pages.yml`** | site / main | Check + deploy (write scoped to deploy) |
| **`changelog-check.yml`** | PR product paths | Require `CHANGELOG.md` touch |
| **`labeler.yml`** | PR | Auto-labels via `.github/labeler.yml` |
| **`anti-lie-probe.yml`** | every 6h / PR | OONI probe → artifact + PR (write only on schedule) |
| **`ci-regen.yml`** | nightly | Blocky + client profiles → PR |
| **`package-freebox-vm.yml`** | packaging / release | Kit/tarball + shellcheck (write only on release) |
| **`build-freebox-os-qcow2.yml`** | packaging / weekly / release | Kit on PR; qcow2 without cancel mid-build |
| **`release.yml`** | tag `v*.*.*` | Notes from CHANGELOG |
| **`stale.yml`** | weekly | Close inactive issues/PRs |
| Dependabot | weekly | Actions + Docker |

\* PR skips pure markdown/site-only changes (`paths-ignore`).

## Shared gates (local)

```bash
pip install pyyaml   # for conf-lint
python3 scripts/ci-conf-lint.py
python3 scripts/ci-assert-product.py    # DNS1=HOST_IP, DNS2=9.9.9.10
python3 scripts/assert-lan-only.py
bash scripts/verify-unbound-forwards.sh
ANTI_DEGRADATION_INVARIANTS_ONLY=1 python3 scripts/anti-degradation-check.py
```

Product DHCP: **DNS1 = `HOST_IP`**, **DNS2 = `9.9.9.10`**.  
Pin `FREEBOX_DNS_1` = SOS inventory label — not DHCP DNS1.

No silent `git push || true` — scheduled fixes open **PRs** or **issues**.

## Operator tips

```bash
gh workflow run validate-and-health.yml
gh workflow run anti-degradation.yml
gh workflow run docs-lint.yml

git tag v1.2.0 && git push origin v1.2.0   # release + asset attach
```

Détail anti-dégradation : [anti-degradation.md](anti-degradation.md) · LAN : [lan-only.md](lan-only.md)
