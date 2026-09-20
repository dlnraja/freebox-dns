# CI / GitHub Actions

Workflows live in `.github/workflows/`. None of them poll a live Freebox.

| Workflow | Trigger | Role |
| --- | --- | --- |
| **`anti-degradation.yml`** | every 8h / PR | Bitrot watchdog → issue if red |
| **`link-health.yml`** | daily / PR | Remote URL / gravity / Pages |
| **`stale.yml`** | weekly | Close inactive issues/PRs |
| `validate-and-health.yml` | push / PR / 12h | Compose, invariants, SOS digs, blocklist → PR, Docker smoke |
| `freebox-conf-sync.yml` | path / weekly | JSON/YAML lint + Blocky drift |
| `anti-lie-probe.yml` | every 6h / PR | OONI-like probe → artifact + PR |
| `ci-regen.yml` | nightly | Regenerate Blocky + profiles → PR |
| `github-pages.yml` | site / PR check | Link check + deploy + curl |
| `docs-ci.yml` | docs/site PR | Required docs + site links |
| `package-freebox-vm.yml` | packaging / release | VM tarball + kit |
| `build-freebox-os-qcow2.yml` | packaging / weekly / release | Kit on PR; qcow2 on main/schedule |
| `release.yml` | tag `v*.*.*` | Release notes from CHANGELOG |
| Dependabot | weekly | Bump Actions (+ Docker) |

Anti-dégradation détail : [anti-degradation.md](anti-degradation.md)

## Operator tips

```bash
python3 scripts/anti-degradation-check.py
gh workflow run anti-degradation.yml
gh workflow run validate-and-health.yml

# Cut a release (qcow2/package attach assets)
git tag v1.2.0 && git push origin v1.2.0
```

Scheduled fixes use **pull requests** or **issues** — no silent `git push || true`.
