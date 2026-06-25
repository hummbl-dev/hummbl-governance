# Phase 7 Repo-Standard Rollout Tracking

**Source audit:** `docs/standards/AUDIT_2026-06-25.md`
**Tracking issue:** #124
**Created:** 2026-06-25

## Disposition categories

| Disposition | Meaning |
|-------------|---------|
| **scaffold** | Create missing artifacts — repo is active and needs governance stack |
| **defer** | Intentionally deferred with reason |
| **archive** | Recommend archiving — repo is inactive or experimental |
| **reclassify** | Change repo class (e.g., from code/library to docs/research) |

## Phase 7 repo list with dispositions

### Tier 7a — Score 12/15 (8 repos, add DOCTRINE.md only)

| Repo | Disposition | Missing | Notes |
|------|-------------|---------|-------|
| arbiter | scaffold | DOCTRINE.md | Public, active — high priority |
| base120 | scaffold | DOCTRINE.md | Public, active — high priority |
| founder-mode | scaffold | DOCTRINE.md | Private, active — high priority |
| hummbl-agent | scaffold | DOCTRINE.md | Public, active |
| hummbl-bibliography | scaffold | DOCTRINE.md | Public, active |
| hummbl-governance | scaffold | DOCTRINE.md | Public, active — self-compliance |
| lejepa | scaffold | DOCTRINE.md | Private |
| meeting-archive | scaffold | DOCTRINE.md | Private |

### Tier 7b — Score 11/15 (18 repos, add DOCTRINE.md + CODEOWNERS)

| Repo | Disposition | Missing | Notes |
|------|-------------|---------|-------|
| arcana | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| autoresearch-pipeline | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| crab | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| general-claim-validator | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl-brainstorm | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl-iac | scaffold | CHANGELOG.md, DOCTRINE.md | Private — has CODEOWNERS |
| hummbl-kernel-factory | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl-medical | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl-models | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl-production | scaffold | CHANGELOG.md, DOCTRINE.md | Private — has CODEOWNERS |
| hummbl-research | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl-skills | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl-spacetime | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl-transparency | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| hummbl-tuples | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| idp-spec | scaffold | DOCTRINE.md, CODEOWNERS | Private |
| krineia | scaffold | DOCTRINE.md, CODEOWNERS | Private — reference repo |

### Tier 7c — Score 10/15 (27 repos, add CHANGELOG + DOCTRINE + CODEOWNERS)

| Repo | Disposition | Missing | Notes |
|------|-------------|---------|-------|
| agent-tools | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private, active |
| apex-nexus | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| baseN | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| claude-config | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| coaching | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| corpus | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| fleet-standard | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| fractional-bench | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| huaomp | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| hummbl-brand | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| hummbl-cca-f | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| hummbl-dev | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Public — high priority |
| hummbl-doctrine | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| hummbl-gameboard | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| hummbl-graphs | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| hummbl-music | defer | CHANGELOG, DOCTRINE, CODEOWNERS | Private — experimental, low activity |
| hummbl-papers | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Public |
| hummbl-system-prompts | defer | CHANGELOG, DOCTRINE, CODEOWNERS | Private — reference only |
| hummbl-theory | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| hummingbird | defer | CHANGELOG, DOCTRINE, CODEOWNERS | Private — assess if active |
| job-search-2026 | defer | CHANGELOG, DOCTRINE, CODEOWNERS | Private — time-bound, may archive |
| lsat-prep | defer | CHANGELOG, DOCTRINE, CODEOWNERS | Private — personal, low priority |
| mcp-server | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Public — high priority |
| psychedelic-claim-validator | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| unified-frameworks | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |
| whether-book | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS | Private |

### Tier 7d — Score 9/15 (2 repos)

| Repo | Disposition | Missing | Notes |
|------|-------------|---------|-------|
| .github | defer | LICENSE, CHANGELOG, DOCTRINE, CODEOWNERS | Org profile repo — special case, may not need full stack |
| mintlify-docs | scaffold | CHANGELOG, DOCTRINE, CODEOWNERS, _receipts | Public docs repo |

### Tier 7e — Score 1-6/15 (5 repos, partial stack)

| Repo | Disposition | Missing | Notes |
|------|-------------|---------|-------|
| hummbl-toolkit | scaffold | AGENTS, CONTRIB, SECURITY, LICENSE, CHANGELOG, DOCTRINE, CODEOWNERS | Public — needs most of the stack |
| docs | scaffold | CONTRIB, SECURITY, CHANGELOG, KRINEIA, CONSTITUTION, DOCTRINE, hummbl.repo.yaml, CODEOWNERS, _receipts, docs/adr | Public docs repo |
| hummbl-security-auditor | scaffold | CONTRIB, SECURITY, CHANGELOG, KRINEIA, CONSTITUTION, DOCTRINE, hummbl.repo.yaml, CODEOWNERS, _receipts, docs/adr | Private — active |
| hummbl-cyber-workbench | scaffold | CONTRIB, SECURITY, LICENSE, CHANGELOG, KRINEIA, CONSTITUTION, DOCTRINE, hummbl.repo.yaml, CODEOWNERS, _receipts, docs/adr | Private — governed cyber workbench |
| mtsmu | scaffold | AGENTS, CONTRIB, SECURITY, LICENSE, CHANGELOG, KRINEIA, CONSTITUTION, DOCTRINE, hummbl.repo.yaml, CODEOWNERS, docs/adr | Private |
| swarm-test | archive | README, AGENTS, CONTRIB, SECURITY, LICENSE, CHANGELOG, KRINEIA, CONSTITUTION, DOCTRINE, hummbl.repo.yaml, CODEOWNERS, docs/adr | Private — test repo, recommend archiving |

### Tier 7f — Score 0/15 (9 repos, empty — full governance stack needed)

| Repo | Disposition | Missing | Notes |
|------|-------------|---------|-------|
| anvil-fleet | scaffold | All | Private — active fleet surface |
| hummbl-bus | scaffold | All | Private — active bus module |
| hummbl-cli | scaffold | All | Private — active CLI |
| hummbl-cognition | scaffold | All | Private — active cognition module |
| hummbl-dashboard | scaffold | All | Private — active dashboard |
| hummbl-eval | scaffold | All | Private — assess if active |
| hummbl-foundry | scaffold | All | Private — assess if active |
| hummbl-quality | scaffold | All | Private — assess if active |
| research-and-development | scaffold | All | Private — assess if active |

## Summary

| Disposition | Count | Work estimate |
|-------------|-------|---------------|
| scaffold | 58 | Create missing artifacts |
| defer | 6 | Intentionally deferred |
| archive | 1 | Recommend archiving (swarm-test) |
| reclassify | 0 | — |

## Execution plan

1. **Batch 1 (Tier 7a)**: Add DOCTRINE.md to 8 repos — lowest effort, highest score
2. **Batch 2 (Tier 7b)**: Add DOCTRINE.md + CODEOWNERS to 18 repos
3. **Batch 3 (Tier 7c)**: Add CHANGELOG + DOCTRINE + CODEOWNERS to 21 repos (excluding 6 deferred)
4. **Batch 4 (Tier 7d-7e)**: Add partial/full stack to 6 repos
5. **Batch 5 (Tier 7f)**: Add full governance stack to 9 empty repos
6. **Assessment**: Review 6 deferred repos and 1 archive candidate with operator

## References

- Audit: `docs/standards/AUDIT_2026-06-25.md`
- Standard: `docs/standards/HUMMBL_REPO_STANDARD.md`
- Issue: #124
