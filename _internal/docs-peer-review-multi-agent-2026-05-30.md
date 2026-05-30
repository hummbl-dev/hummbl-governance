# Documentation Peer Review — Multi-Agent Synthesis

**Date**: 2026-05-30  
**Reviewers**: 3 sub-agents (governance docs, root-level docs, founder-mode + machine docs)  
**Mode**: Read-only  
**Overall Grade**: **C+**

---

## Executive Summary

30+ documents reviewed across 4 scopes. **15 cross-document inconsistencies** identified, including 4 CRITICAL severity. The biggest risk is **staleness** — numeric claims (module counts, test counts, versions) rot within weeks of being written. Multiple documents are 2+ versions behind reality.

---

## Grade Distribution

| Grade | Count | Files |
|---|---|---|
| **A** | 2 | ADR-001, coverage/README.md |
| **A-** | 3 | coverage/EVIDENCE_VALIDATION.md, UNVERIFIED-CLAIMS.md, session-review-big-pickle |
| **B+** | 3 | evidence-readiness-review-receipt.md, TECH-SPEC-legal-governance, AGENTS.md (machine) |
| **B** | 3 | GITEA_MIGRATION_PLAYBOOK.md, ADR-BACKLOG.md, SCHEMA-FREEZE-REGISTER.md |
| **B-** | 3 | REPO_HEALTH.md, gitea-runners-operations.md, founder_mode/AGENTS.md |
| **C+** | 3 | PRD.md, CLAUDE.md (machine), big-pickle-session-review |
| **C** | 3 | ecosystem/PLAN.md, AGENTS.md (founder-mode root), .claude/CLAUDE.md |
| **C-** | 1 | ROADMAP.md |
| **D+** | 1 | founder_mode/README.md |
| **D** | 1 | README.md (founder-mode root) |
| **C+** | 1 | hummbl-governance/README.md |
| **B-** | 1 | .gitea/workflows/ci.yml |
| **A-** | 1 | pyproject.toml |
| **D** | 1 | CLAUDE.md (hummbl-governance) |

---

## CRITICAL Issues (Must Fix)

| # | Issue | Files | Impact |
|---|-------|-------|--------|
| 1 | **CI badges point to dead GitHub repos** — canonical remote is Gitea | founder-mode/README.md, founder_mode/README.md, hummbl-governance/README.md | Public-facing docs show broken CI status |
| 2 | **hummbl-governance version discrepancy** — README says v0.8.0, ROADMAP says v0.3.0 | ROADMAP.md vs all other docs | Misrepresents package maturity |
| 3 | **PRD.md is 2+ versions behind** — claims 0.1.0/7 modules/157 tests; reality is 0.8.0/28 modules/979 tests | PRD.md | Most misleading document in the repo |
| 4 | **Agent rosters are 40-70% incomplete** — docs list 4-12 agents; actual roster has 17 | founder-mode/README.md (4), founder_mode/README.md (4), AGENTS.md root (11), CLAUDE.md (9) | Agents working in the repo won't find their instructions |
| 5 | **Anthropic evidence contradiction** — TECH-SPEC shows ✅ for 4 claims; UNVERIFIED-CLAIMS shows all 4 unverified | TECH-SPEC vs UNVERIFIED-CLAIMS.md | Credibility risk if both are read together |
| 6 | **CI documentation vs reality gap** — REPO_HEALTH.md claims multi-OS, multi-Python matrix; actual CI is Windows-only (Gitea) or ubuntu-latest-only (GitHub), Python 3.13 only | REPO_HEALTH.md vs ci.yml | Repo health contract describes CI that doesn't exist |
| 7 | **AppData\Python313 has no python.exe** — Big Pickle session committed a workflow pointing to a broken path | big-pickle-session-review.md, ci.yml commit a5e06d4 | CI will fail on this path |
| 8 | **guard-bash.sh referenced but missing** — AGENTS.md:27 references a file that doesn't exist | AGENTS.md (machine) | Operational confusion |

---

## HIGH Issues

| # | Issue | Files |
|---|-------|-------|
| 9 | **MCP server count mismatch** — README says 3 documented, changelog says 7 total, 4 new ones undocumented | hummbl-governance/README.md |
| 10 | **Dual-label strategy not implemented** — runbook documents it, CI workflow doesn't use it | gitea-runners-operations.md vs ci.yml |
| 11 | **Kimi listed as active** — retired 2026-04-05 but still appears in founder_mode/README.md | founder_mode/README.md |
| 12 | **Q2 2026 milestones all passed** — PLAN.md and SCHEMA-FREEZE-REGISTER.md show May 15 deadlines with no status update | ecosystem/PLAN.md, SCHEMA-FREEZE-REGISTER.md |
| 13 | **Test count history has 30-test gap** — v0.6.0 says 673→740, v0.7.0 says 700→784 | hummbl-governance/README.md |
| 14 | **Coverage count discrepancy** — coverage/README.md says 259 ✅, EVIDENCE_VALIDATION.md says 198 Fulfilled | coverage/README.md vs EVIDENCE_VALIDATION.md |
| 15 | **CI run numbering unreconciled** — session logs reference runs 552, 563, 564 without clear mapping to commits | _internal/ session logs |

---

## MEDIUM Issues

| # | Issue | Files |
|---|-------|-------|
| 16 | **CLAUDE.md (hummbl-governance) lists 7 of 28 primitives** | CLAUDE.md |
| 17 | **Migration playbook references 4 workflows that don't exist** | GITEA_MIGRATION_PLAYBOOK.md |
| 18 | **Python prerequisites say "macOS or Linux"** — primary host is Windows | founder-mode/README.md, founder_mode/README.md |
| 19 | **Duplicate Windows Host Policy section** in CLAUDE.md | founder_mode/CLAUDE.md |
| 20 | **cognition/ placement instruction is wrong** — founder_mode/cognition/ is NOT empty | founder_mode/CLAUDE.md |
| 21 | **Node version drifted** — AGENTS.md says 22.22.2, actual is 22.22.3 | AGENTS.md (machine) |
| 22 | **CI workflow hardcodes Python path** — fragile across toolcache updates | .gitea/workflows/ci.yml |
| 23 | **Runbook references non-existent ci-cd-architecture-plan.md** | gitea-runners-operations.md |
| 24 | **HANDOFF_SPEC_v2.md referenced but doesn't exist** | AGENTS.md (founder-mode root) |
| 25 | **Three session logs for same CI issue** — should be consolidated | _internal/ |

---

## Per-Scope Summary

### hummbl-governance/docs/ (Agent 1)
- **Best**: ADR-001 (A), coverage/README.md (A-)
- **Worst**: PRD.md (C+), ecosystem/PLAN.md (C)
- **Pattern**: Tracker docs are excellent; planning docs are stale

### Root-level files (Agent 2)
- **Best**: pyproject.toml (A-)
- **Worst**: CLAUDE.md (D)
- **Pattern**: Code-level files are accurate; human-facing docs are stale

### founder-mode (Agent 3)
- **Best**: founder_mode/AGENTS.md (B-)
- **Worst**: README.md root (D), founder_mode/README.md (D+)
- **Pattern**: Every numeric claim is stale. Agent rosters are 40-70% incomplete.

### Machine-level (Agent 3)
- **Best**: AGENTS.md machine-global (B+)
- **Worst**: .claude/CLAUDE.md (C)
- **Pattern**: Machine docs are the most current but have minor drift

---

## Top 5 Recommendations

1. **Replace hardcoded numbers with dynamic references** — module counts, test counts, schema counts rot within weeks. Use `pytest --collect-only | wc -l`, `ls founder_mode/services/ | wc -l`, or link to CI dashboards.

2. **Fix CI badges** — point to Gitea or remove them. Dead badges misrepresent repo health.

3. **Supersede or rewrite PRD.md** — it's the most misleading document. Either update to v0.8.0 or mark SUPERSEDED.

4. **Sync all agent rosters from `.claude/rules/agent-roster.md`** — 17 entries, not 4-12.

5. **Consolidate _internal/ session logs** — three logs for one CI issue should be one post-mortem with a clear timeline.

---

## What's Working Well

- **Tracker culture**: DOCS-CODE-PARITY, ADR-BACKLOG, SCHEMA-FREEZE-REGISTER, UNVERIFIED-CLAIMS — excellent practice
- **ADR discipline**: ADR-001 is a gold-standard decision record
- **Honest status labeling**: LIVE/DESIGNED/PROPOSED convention, probation transparency
- **Machine documentation**: AGENTS.md is thorough, current, and actionable
- **Coverage matrix**: Mechanically validated, clear disclaimers, ADR-compliant
