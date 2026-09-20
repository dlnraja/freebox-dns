## Summary

<!-- What changed and why (1–3 bullets). -->

-

## Checklist

- [ ] `python3 scripts/assert-lan-only.py` passes (no public DNS bind)
- [ ] Regenerated Blocky / client profiles if ports or lists changed (`generate-blocky-modes.py` / `generate-client-profiles.py`)
- [ ] No secrets (`.env`, tokens, private dumps)
- [ ] Docs updated if user-facing (`CHANGELOG.md` [Unreleased] if needed)
- [ ] Not claiming Pi-hole FTL features we don’t ship ([docs/pihole-parity.md](../docs/pihole-parity.md))

## Test plan

- [ ] `dig @HOST_IP …` (or lab ports) for affected modes
- [ ] If DHCP/docs touched: DNS1 = resolver, DNS2 = `9.9.9.10`
