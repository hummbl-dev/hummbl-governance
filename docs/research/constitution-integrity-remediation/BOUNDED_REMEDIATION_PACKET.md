# Constitution Bounded Remediation Packet v0.1

**Status: P1 BOUNDED REMEDIATION — RE-VERIFY BEFORE MUTATION — NON-CANONICAL**

Parent: hummbl-dev/hummbl-governance#220
Issue: hummbl-dev/hummbl-governance#221

## Objective

Repair current constitutional truth and incorporation defects without
broad constitutional redesign.

## Finding 1: founder-mode schema-count claim

### Pre-state

`founder-mode/CONSTITUTION.md` line 27:

> **Contracts are canonical.** The 78 governance schemas are the
> source of truth.

### Source-of-truth command

```bash
cd /Users/others/PROJECTS/founder-mode
find . -name "*.schema.json" -not -path "*/.git/*" 2>/dev/null | wc -l
# Result: 120
```

### Classification

**C1 — FALSE_CONSTITUTIONAL_CLAIM**

The hard-coded count "78" does not match the actual 120 schema files.
Furthermore, the `contracts/` symlink is broken (points to
`/Users/others/PROJECTS/platform/agent-os/contracts` which does not
exist).

### Proposed correction

Replace the hard-coded count with an authoritative-source reference:

> **Contracts are canonical.** Governance schemas in the tracked
> schema directories are the source of truth. Code conforms to
> schemas; schemas are never silently mutated to satisfy code. The
> current schema count is governed by `docs/SCHEMA_COUNT_AUTHORITY.md`
> (to be created) or verified via
> `find . -name "*.schema.json" -not -path "*/.git/*" | wc -l`.

### Amendment authority

`founder-mode/CONSTITUTION.md` requires: a PR, an ADR under
`docs/adr/`, a KRINEIA receipt, and human approval (Reuben Bowlby).

### Post-state (target)

Constitution no longer contains a hard-coded schema count. Schema
count is derived from the authoritative source.

### Execution receipt

**NOT YET EXECUTED** — This packet proposes the correction. Execution
requires a repo-specific PR in `founder-mode` with ADR and KRINEIA
receipt.

## Finding 2: founder-mode broken normative references

### Pre-state

`founder-mode/CONSTITUTION.md` lines 43-45:

```
- `founder_mode/contracts/`
- `founder_mode/schemas/`
- `founder_mode/services/kill_switch_core.py`
```

### Source-of-truth commands

```bash
cd /Users/others/PROJECTS/founder-mode
ls -la founder_mode/contracts/
# Result: No such file or directory

ls founder_mode/schemas/
# Result: Exists (5 files)

ls founder_mode/services/kill_switch_core.py
# Result: No such file or directory

ls founder-mode/founder_mode/services/kill_switch_core.py
# Result: Exists (canonical path)

readlink contracts
# Result: /Users/others/PROJECTS/platform/agent-os/contracts (broken symlink)

ls /Users/others/PROJECTS/platform/agent-os/contracts/
# Result: No such file or directory
```

### Classification

**C2 — BROKEN_INCORPORATION_REFERENCE**

- `founder_mode/contracts/` — does not exist (broken symlink at root `contracts/`)
- `founder_mode/schemas/` — exists but is the stale root directory
- `founder_mode/services/kill_switch_core.py` — does not exist at this path
- Canonical kill_switch path: `founder-mode/founder_mode/services/kill_switch_core.py`

### Proposed correction

Update normative references to canonical paths:

```
- `founder-mode/founder_mode/schemas/`
- `founder-mode/founder_mode/services/kill_switch_core.py`
```

Remove reference to `founder_mode/contracts/` (the directory does not
exist and the symlink is broken). If contracts are canonical, identify
the actual canonical contract location or remove the claim.

### Amendment authority

Same as Finding 1: PR + ADR + KRINEIA receipt + Reuben approval.

### Post-state (target)

All normative references resolve from the declared repository root.

### Execution receipt

**NOT YET EXECUTED** — requires repo-specific PR in `founder-mode`.

## Finding 3: founder-mode amendment path reference

### Pre-state

`founder-mode/CONSTITUTION.md` line 70:

> Changes to this constitution require: a PR, an ADR under `docs/adr/`,
> a KRINEIA receipt, and human approval (Reuben Bowlby).

### Source-of-truth command

```bash
cd /Users/others/PROJECTS/founder-mode
ls docs/adr/
# Result: Exists (multiple ADR subdirectories)
```

### Classification

**No defect found.** `docs/adr/` exists and contains ADRs.

### Proposed correction

None needed.

## Finding 4: hummbl-research dependency invariant

### Pre-state

The 2026-07-10 audit reported that `hummbl-research/CONSTITUTION.md`
contained a "Stdlib-only runtime" invariant inconsistent with actual
runtime dependencies.

### Source-of-truth commands

```bash
cd /Users/others/PROJECTS/hummbl-research
grep "Stdlib-only\|stdlib-only\|standard library" CONSTITUTION.md
# Result: (no matches)

sed -n '29p' CONSTITUTION.md
# Result: 4. **Declared runtime dependencies.** Production code uses
# the dependencies declared in `pyproject.toml [project.dependencies]`.
# Adding an undeclared runtime dependency is a constitutional violation.

python3 -c "
import tomllib
with open('pyproject.toml','rb') as f:
    d = tomllib.load(f)
print(d['project']['dependencies'])
"
# Result: ['networkx>=3.2,<4.0', 'numpy>=1.24.0,<2.0', 'scipy>=1.10.0,<2.0',
#          'google-cloud-aiplatform>=1.38.0,<2.0', 'vertexai>=1.38.0,<2.0',
#          'google-generativeai>=0.3.0,<1.0']
```

### Classification

**No defect found (already remediated).**

The constitution correctly states "Declared runtime dependencies"
rather than "Stdlib-only runtime." The pyproject.toml declares 6
runtime dependencies (networkx, numpy, scipy, google-cloud-aiplatform,
vertexai, google-generativeai). The constitution is consistent with
the actual dependency posture.

### Proposed correction

None needed. The audit finding appears to have been already remediated.

## Summary of findings

| # | Repo | Finding | Classification | Status |
|---|------|---------|---------------|--------|
| 1 | founder-mode | "78 governance schemas" hard-coded count | C1 — FALSE_CONSTITUTIONAL_CLAIM | Proposed correction ready |
| 2 | founder-mode | Broken normative paths (contracts/, services/) | C2 — BROKEN_INCORPORATION_REFERENCE | Proposed correction ready |
| 3 | founder-mode | docs/adr/ amendment path | No defect | No action needed |
| 4 | hummbl-research | "Stdlib-only runtime" invariant | No defect (already remediated) | No action needed |

## Proposed repo-specific amendment PRs

### PR 1: founder-mode constitution amendment

**Scope**: Fix findings 1 and 2 in `founder-mode/CONSTITUTION.md`

**Changes**:
1. Replace "The 78 governance schemas" with authoritative-source reference
2. Update normative file paths to canonical locations
3. Remove or fix broken `contracts/` reference

**Requirements**:
- PR in `founder-mode` repo
- ADR under `docs/adr/`
- KRINEIA receipt
- Reuben approval

**NOT YET EXECUTED** — This packet proposes the correction. The
actual PR must be created in the `founder-mode` repo following its
amendment requirements.

## Prohibited shortcuts (verified not taken)

- [x] No empty `contracts/`, `schemas/`, `services/`, or `docs/adr/` paths created
- [x] No unverified count substituted for "78"
- [x] No valid dependency invariant weakened
- [x] No unrelated fleet constitution edits combined into one PR

## Verification expectations

For each finding:

| Finding | Pre-state | Source command | Classification | Correction | Authority | Post-state | Receipt |
|---------|-----------|---------------|---------------|-----------|-----------|-----------|---------|
| 1 | "78 schemas" | `find ... *.schema.json` → 120 | C1 | Replace with authoritative source | founder-mode PR+ADR+KRINEIA+Reuben | Pending | Pending |
| 2 | Broken paths | `ls` commands | C2 | Update to canonical paths | founder-mode PR+ADR+KRINEIA+Reuben | Pending | Pending |
| 3 | docs/adr/ | `ls docs/adr/` | No defect | None | N/A | N/A | N/A |
| 4 | Stdlib-only | `grep` + `tomllib` | No defect | None | N/A | N/A | N/A |

## Residual ambiguity escalated to Reuben

1. **Broken `contracts/` symlink**: The `contracts/` symlink at
   founder-mode root points to `/Users/others/PROJECTS/platform/agent-os/contracts`
   which does not exist. Should this symlink be removed, or should
   the target be restored? This requires Reuben's decision.

2. **Canonical contract location**: If contracts are canonical (per
   the constitution), where is the actual canonical contract
   directory? The constitution references `founder_mode/contracts/`
   which does not exist. Reuben must identify the actual source of
   truth or confirm that contracts are no longer canonical.

3. **Schema count authority**: Should `founder-mode` create a
   `docs/SCHEMA_COUNT_AUTHORITY.md` file (similar to
   `docs/TEST_COUNT_AUTHORITY.md` in hummbl-governance) to govern
   the schema count? Reuben must decide.

## Acceptance criteria

- [x] Every scoped claim/path is re-verified and classified
- [ ] Founder-mode no longer contains false hard-coded schema authority/count claims — **PROPOSED, NOT YET EXECUTED**
- [ ] Founder-mode normative references resolve from declared repository root — **PROPOSED, NOT YET EXECUTED**
- [x] hummbl-research dependency invariant matches verified current runtime state
- [x] No empty placeholder paths are created
- [ ] Repo-specific amendment and receipt rules are satisfied — **PENDING EXECUTION**
- [x] Residual ambiguity is escalated to Reuben rather than guessed
- [ ] Parent #220 receives links to all PRs and post-merge verification receipts — **PENDING EXECUTION**

## References

- Parent: hummbl-dev/hummbl-governance#220
- Issue: hummbl-dev/hummbl-governance#221
- Authority packet: hummbl-dev/hummbl-governance#222
- Archetype packet: hummbl-dev/hummbl-governance#223
