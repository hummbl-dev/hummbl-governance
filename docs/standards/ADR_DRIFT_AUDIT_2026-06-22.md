# ADR Drift Audit — 2026-06-22

**Auditor:** devin (automated)
**Date:** 2026-06-22
**Scope:** All 68 non-fork repos on `hummbl-dev` GitHub + local repos
**Total ADRs found:** 60 repos with ADRs, 100+ individual ADR files

## Executive summary

**10 distinct drift issues found across the fleet.** The most severe are:
numbering scheme fragmentation (3+ schemes), path fragmentation (11+ ADR
directories in founder-mode alone), and phantom cross-references in the
founder-mode ADR index.

---

## Fleet ADR inventory

| Repo | ADR count | Notes |
|------|-----------|-------|
| 59 repos | 1 each | All `ADR-001-repo-governance-baseline.md` from fleet rollout |
| `hummbl-governance` | 5 | ADR-001 through ADR-005 (canonical standards) |
| `hummbl-iac` | 3 | 2 real ADRs + 1 baseline (numbering collision) |
| `swarm-test` | 7 | 6 real ADRs + 1 baseline (non-standard naming) |
| `founder-mode` | 30+ | Across 7+ directories, 4+ naming schemes |

---

## Drift findings

### D1: Numbering scheme fragmentation (SEVERE)

**3+ incompatible numbering schemes in production:**

| Scheme | Example | Where | Standard? |
|--------|---------|-------|-----------|
| `ADR-NNN-kebab-title.md` | `ADR-001-repo-governance-baseline.md` | Fleet rollout (59 repos), hummbl-governance | Yes (Init Standard v0.1) |
| `NNN-kebab-title.md` | `001-lazy-spawn.md` | swarm-test ADRs 001-006 | No |
| `ADR-{DOMAIN}-NNN-title.md` | `ADR-GOV-002-runtime-agnostic-agent-execution.md` | founder-mode governance/agent/kernel/mobile | No (domain-prefixed) |
| `ADR-NNNN-title.md` | `ADR-0001-monorepo.md` | founder-mode platform | No (4-digit) |
| `ADR-NNNN-kebab-title.md` | `ADR-0012-push-pull-loop-adr.md` | founder-mode design | No (4-digit, no domain) |

**Fix:** The Init Standard v0.1 mandates `ADR-NNN-kebab-title.md` (3-digit,
zero-padded, ADR prefix, no domain prefix). All non-standard ADRs should be
renamed. Domain prefixing is useful but should be in the title, not the
number: `ADR-006-gov-runtime-agnostic-agent-execution.md` not
`ADR-GOV-002-runtime-agnostic-agent-execution.md`.

### D2: Path fragmentation (SEVERE)

**11+ different ADR directory paths in founder-mode alone:**

| Path | Count | Standard? |
|------|-------|-----------|
| `docs/adr/` | 59 repos | Yes (Init Standard v0.1) |
| `DOCS/adr/` | founder-mode (uppercase, from rollout) | No — casing drift |
| `docs/governance/adr/` | founder-mode (7 ADRs) | No — extra nesting |
| `docs/agent-onboarding/surface-identity/adr/` | founder-mode (4 ADRs) | No — deep nesting |
| `docs/design/agent-kernel-v0/adr/` | founder-mode (5 ADRs) | No — deep nesting |
| `docs/mobile-ops/adr/` | founder-mode (5 ADRs) | No — domain subdir |
| `docs/audit/` | founder-mode (1 ADR, no adr/ subdir) | No |
| `docs/design/` | founder-mode (1 ADR, no adr/ subdir) | No |
| `docs/infrastructure/` | founder-mode (ADRs mixed with non-ADR docs) | No |
| `PROJECTS/platform/docs/ARCHITECTURE_DECISIONS/` | founder-mode (2 ADRs) | No |
| `founder_mode/docs/governance/adr/` | founder-mode (snake_case cruft) | No — untracked dir |

**Fix:** All ADRs should live at `docs/adr/`. Domain subdirectories
(`docs/adr/governance/`, `docs/adr/agent-kernel/`) are acceptable for repos
with 10+ ADRs. The `DOCS/` casing in founder-mode should be lowered to
`docs/`.

### D3: Status field format drift (MODERATE)

**5 different status field formats:**

| Format | Example | Where |
|--------|---------|-------|
| `- **Status:** accepted` | `- **Status:** accepted` | Fleet rollout, hummbl-governance ADR-003+ | 
| `**Status**: ACCEPTED` | `**Status**: ACCEPTED` | hummbl-governance ADR-001/002, founder-mode design |
| `**Status**: Accepted` | `**Status**: Accepted` | hummbl-iac |
| `## Status\n\nAccepted` | `## Status\n\nAccepted` | swarm-test, founder-mode platform |
| `- Status: Accepted` | `- Status: Accepted` | founder-mode audit |

**Fix:** Init Standard v0.1 mandates `- **Status:** accepted` (lowercase
value, bold key with colon, dash prefix). All ADRs should be normalized.

### D4: Date field format drift (MODERATE)

**4 different date field formats:**

| Format | Where |
|--------|-------|
| `- **Date:** 2026-06-22` | Fleet rollout, hummbl-governance ADR-003+ |
| `**Decided**: 2026-05-14` | hummbl-governance ADR-001 |
| `**Date**: 2026-06-16` | hummbl-governance ADR-002, hummbl-iac |
| No date in header | swarm-test 001-004, founder-mode many |

**Fix:** Init Standard v0.1 mandates `- **Date:** YYYY-MM-DD`.

### D5: hummbl-iac ADR-001 numbering collision (MODERATE)

`hummbl-iac` has two ADRs both numbered 001:
- `ADR-001-chezmoi-for-dotfiles.md` (real decision, 2026-03-26)
- `ADR-001-repo-governance-baseline.md` (fleet rollout, 2026-06-22)

**Fix:** Renumber the chezmoi ADR to `ADR-001` and the baseline to
`ADR-003` (after the per-machine-keys ADR which is already 002). Or
renumber the baseline to `ADR-003` and leave the originals as-is.

### D6: swarm-test ADR naming non-standard (MODERATE)

swarm-test ADRs 001-006 use `NNN-kebab-title.md` (no `ADR-` prefix).
ADR-007 uses the standard `ADR-007-repo-governance-baseline.md`.

**Fix:** Rename `001-lazy-spawn.md` → `ADR-001-lazy-spawn.md`, etc.

### D7: founder-mode DOCS/ casing drift (LOW)

The fleet rollout placed the governance baseline ADR at `DOCS/adr/` in
founder-mode (uppercase) due to the `.gitignore` deny-by-default issue.
The repo's other ADRs use `docs/` (lowercase).

**Fix:** Rename `DOCS/adr/` → `docs/adr/` and update `.gitignore` to
allow `docs/`.

### D8: ADR_INDEX.md drift (MODERATE)

The `founder-mode/docs/ADR_INDEX.md` claims "90+ across 7 directories"
but:
- Only lists ~30 ADRs (60+ are missing from the index)
- Many entries have "—" for all metadata (status, date, owner, disposition)
- Infrastructure section says 8 ADRs but lists 7 (ADR-007 FastAPI is in
  `docs/audit/` not `docs/infrastructure/`)
- Research section says "50+" but lists only 8
- ADR-GOV-005 appears with two different titles:
  - "Bus Token Encryption" (in index table)
  - "AI Factory Simulation Mesh" (actual file at `founder_mode/docs/...`)

**Fix:** Rebuild the ADR index from a filesystem scan. Add a CI check
that validates the index against actual files.

### D9: Phantom cross-references (MODERATE)

Several ADRs reference files that don't exist at the expected path:

| Reference | Expected path | Actual path | Issue |
|-----------|--------------|-------------|-------|
| `ADR-GOV-001` | `docs/governance/adr/` | `founder-mode/docs/governance/adr/` | Path prefix drift |
| `ADR-006-tricloud` | `docs/infrastructure/` | `founder-mode/docs/infrastructure/` | Not in an `adr/` subdir |
| `ADR-007-fastapi` | `docs/adr/` | `founder-mode/docs/audit/` | Not in an `adr/` subdir |

**Fix:** Consolidate all ADRs to `docs/adr/` and update cross-references.

### D10: Missing fields in baseline ADRs (LOW)

Some fleet rollout baseline ADRs are missing standard fields:

| Repo | Missing |
|------|---------|
| `hummbl-production` | `**Steward:**` |
| `swarm-test` ADR-007 | Most fields (truncated content) |
| Many repos | `**Supersedes:**` and `**Superseded by:**` |

**Fix:** The generator script (`tools/init_repo.py`, not yet built) should
always include all standard fields with `none` as the default value.

---

## Recommended remediation

### Priority order

1. **D7 (DOCS/ casing)** — Quick fix, unblocks founder-mode consistency
2. **D5 (hummbl-iac collision)** — Renumber one ADR
3. **D6 (swarm-test naming)** — Rename 6 files
4. **D3 + D4 (status/date format)** — Batch normalize across fleet
5. **D2 (path consolidation)** — Move founder-mode ADRs to `docs/adr/`
6. **D1 (numbering scheme)** — Rename all non-standard ADR numbers
7. **D8 (ADR_INDEX.md)** — Rebuild from filesystem scan
8. **D9 (phantom refs)** — Fix after D2 consolidates paths
9. **D10 (missing fields)** — Fix in next rollout generator

### What NOT to do

- Do not mass-rename ADRs in repos that have active CI checking ADR paths
- Do not renumber hummbl-governance ADRs 001-005 (they are the canonical
  standards and referenced by other repos)
- Do not delete the `founder_mode/` (snake_case) ADRs until confirming
  they are truly untracked cruft (the path drift note in AGENTS.md says so,
  but verify before deleting)
