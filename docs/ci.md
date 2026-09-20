# CI / GitHub Actions

Workflows live in `.github/workflows/`. None of them poll a live Freebox.

| Workflow | Trigger | Role |
| --- | --- | --- |
| `validate-and-health.yml` | push / PR / every 12h | Compose validate, Freebox conf, SOS digs, blocklist probe → PR, Docker smoke |
| `freebox-conf-sync.yml` | path filters / weekly | JSON/YAML lint + Blocky generator drift gate |
| `anti-lie-probe.yml` | every 6h / PR paths | OONI-like probe → artifact + PR with hosts overrides |
| `ci-regen.yml` | nightly | Regenerate Blocky + client profiles → PR |
| `github-pages.yml` | site paths / PR check | Link check + deploy Pages + live curl |
| `docs-ci.yml` | docs/site PR | Required docs + site link check |
| `package-freebox-vm.yml` | packaging paths / release | VM tarball + kit zip artifacts |
| `build-freebox-os-qcow2.yml` | packaging / weekly / release | Kit on PR; full qcow2 on main/schedule/release |
| `release.yml` | tag `v*.*.*` | GitHub Release notes from CHANGELOG |
| Dependabot | weekly | Bump Actions (+ Docker ecosystem) |

## Operator tips

```bash
# Manual smoke
gh workflow run validate-and-health.yml

# Cut a release (then qcow2/package attach assets)
git tag v1.2.0 && git push origin v1.2.0
# or: gh workflow run release.yml -f tag=v1.2.0
```

Auto-commits use **pull requests** (`peter-evans/create-pull-request`) — no silent `git push || true`.
