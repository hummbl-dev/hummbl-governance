# ADR-007 — Coverage matrix ratchet gate

- **Status:** accepted
- **Date:** 2026-06-25
- **Decision owner:** Reuben Bowlby
- **Steward:** HUMMBL Research Institute
- **Supersedes:** none
- **Superseded by:** none
- **Related:** [ADR-001](ADR-001-coverage-matrix-not-self-grade.md), `hummbl-dev/hummbl-governance#128`

## Context

The `coverage-matrix-validate` CI job has been advisory since inception (`continue-on-error: true`). While the job runs evidence validation across all coverage matrices and generates `EVIDENCE_VALIDATION.{json,md}`, it exits successfully regardless of validation results. This means:

1. Unresolved evidence references can accumulate without any CI signal.
2. The aggregate `ci` job cannot distinguish a clean validation pass from a warning-only pass.
3. There is no mechanism to prevent regression — a PR that breaks a previously-validating evidence ref would not be caught.

As of 2026-06-25, 5 of 198 Fulfilled rows (2.5%) have validated evidence. The matrices remain DRAFT scaffolds per ADR-001, so blocking CI on full validation would be premature. However, preventing regression of the 5 validated rows is both feasible and valuable.

## Decision

Add a **ratchet gate** to the `coverage-matrix-validate` CI job. The ratchet:

1. **Baseline file**: `docs/coverage/ratchet-baseline.json` records the current validated row count (5 as of 2026-06-25).
2. **Regression check**: CI runs `scripts/coverage_ratchet.py` after evidence validation. If current validated count < baseline, the ratchet emits `::error::` and exits 1.
3. **Advisory state preserved**: The job remains `continue-on-error: true`, so ratchet failure does not block the aggregate `ci` job yet. The ratchet result is exposed as a job output (`ratchet-result`, `validated-count`, `validated-pct`, `clean-pass`).
4. **Baseline raising**: The baseline can only be raised by an explicit `--init-baseline` commit. It can never be lowered without operator approval.
5. **Promotion threshold**: When `validated_pct >= 50%`, the ratchet prints a promotion notice. At that point, `continue-on-error` should be flipped to `false`, making the ratchet a blocking gate.

## Ratchet policy

| Condition | Ratchet exit | CI job result | Aggregate `ci` |
|-----------|-------------|---------------|-----------------|
| current >= baseline | 0 (pass) | success | success |
| current < baseline | 1 (fail) | success (advisory) | success (advisory) |
| current >= baseline, pct >= 50% | 0 (pass) | success | success + promotion notice |
| Post-promotion: current < baseline | 1 (fail) | failure (blocking) | failure |

## Exit criteria for advisory state

The advisory state (`continue-on-error: true`) ends when ALL of:
1. `validated_pct >= 50%` (at least 99 of 198 rows validated)
2. A PR explicitly flips `continue-on-error` to `false`
3. The ratchet baseline has been raised to the current validated count
4. The PR references this ADR as the governing decision

## Consequences

- Regression of validated evidence rows is now visible in CI outputs even while advisory.
- The aggregate `ci` job prints ratchet status (result, count, pct, clean_pass) for every run.
- The baseline file is a committed artifact — changes to it are reviewable.
- No premature blocking of draft coverage work — the ratchet only prevents regression of already-validated rows.
- The promotion threshold (50%) provides a clear, measurable target for the team.

## Receipts

- Implementation: `scripts/coverage_ratchet.py`, `docs/coverage/ratchet-baseline.json`
- CI integration: `.github/workflows/ci.yml` — `coverage-matrix-validate` job, `Ratchet gate` step
- Tests: `tests/test_coverage_ratchet.py` — 7 tests covering pass, fail, init, missing baseline, promotion threshold
- Acceptance: `hummbl-dev/hummbl-governance#128`
