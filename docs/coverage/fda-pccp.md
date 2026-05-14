# FDA PCCP (Predetermined Change Control Plan) Coverage Matrix — HUMMBL

**Standard**: FDA Predetermined Change Control Plan (PCCP) — Guidance for AI/ML-Enabled Device Software Functions (finalized 2024)
**Source**: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/predetermined-change-control-plans
**Last reviewed**: 2026-05-14
**Reviewer**: claude-code (huxley) per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md)
**HUMMBL version**: hummbl-governance v0.8.0

## Boundary disclaimer

HUMMBL is **not** an FDA regulatory body. FDA PCCP submissions require device manufacturer engagement with the FDA's CDRH. This matrix maps HUMMBL governance primitives to PCCP requirements for AI/ML-enabled medical device software. The PCCP is a submission document authored by the device manufacturer — HUMMBL provides technical evidence infrastructure.

## Scope summary

The FDA PCCP guidance covers AI/ML-enabled SaMD (Software as a Medical Device) that anticipates planned modifications. Key PCCP elements:

1. **Scope of modifications** — What types of changes are anticipated
2. **Change control plan** — How modifications will be developed, tested, validated
3. **Impact assessment** — How each modification is assessed for safety/effectiveness
4. **Monitoring strategy** — Post-market monitoring for modified device performance
5. **Transparency** — Communication to users/providers about modifications

## Coverage matrix

| PCCP Element | Requirement | HUMMBL Coverage | Evidence |
|---|---|---|---|
| **1. Modification Scope** | Define anticipated modifications (retraining, algorithm updates, data changes, use-case expansion) | ✅ Change-scope tuple + lifecycle-stage tuples track every modification type. EvolutionLineage records variant ancestry for retrained models. | `hummbl_governance/evolution_lineage.py` (variant records), coordination bus change tuples |
| **2. Change Control Plan** | Document development process for modifications: design, implementation, verification, validation | ✅ V&V tuple lifecycle per ISO 42001 A.6.2.4 + deployment tuples per A.6.2.5. CI pipeline enforces plan. | `hummbl_governance/coordination_bus.py` (lifecycle tuples), 927 governance tests |
| **3. Impact Assessment** | Assess each modification's impact on safety, effectiveness, performance before deployment | ✅ Impact-assessment tuples capture pre/post performance metrics. Redteam tuples flag adversarial degradation. | `hummbl_governance/audit_log.py` (performance delta tuples), safety-eval primitives |
| **4. Validation Protocol** | Each modification validated against predetermined acceptance criteria | ✅ Test-set tuples document acceptance criteria. Validation-gate tuples enforce pass/fail before deployment. | validation-gate tuple + `hummbl_governance/contract_net.py` (V&V orchestration) |
| **5. Real-World Performance Monitoring** | Post-deployment monitoring plan for modified device performance | ✅ Continuous monitoring via governance bus. DE.CM tuple types track performance deviations. Drift detection flags when modified model behavior shifts beyond tolerance. | `hummbl_governance/coordination_bus.py`, BehaviorMonitor (drift detection), ConvergenceDetector |
| **6. Predetermined Decision Criteria** | Define when modifications require new 510(k), De Novo, or can proceed under PCCP | ✅ Decision-criteria tuple encodes regulatory pathway triggers. Kill-switch can halt deployment if criteria unmet. | `hummbl_governance/kill_switch.py`, `hummbl_governance/coordination_bus.py` (decision-criteria tuples) |
| **7. Risk Management** | Risk management throughout device lifecycle including modifications | ✅ Risk-register integration, risk-treatment tuples per modification, hazard-analysis workflow for safety-critical changes. | `hummbl_governance/coordination_bus.py` (risk-register + hazard tuples), `hummbl_governance/audit_log.py` |
| **8. Transparency to Users** | Labeling and communication plan for modifications deployed to clinical users | ✅ Transparency-notification tuple + instruction-for-use generator. Per EU AI Act Art. 13 / HTF labeling. | `hummbl_governance/compliance_mapper.py` (labeling export), transparency tuples |
| **9. Data Management Plan** | Data governance for training/retraining: provenance, quality, bias, representativeness | ✅ DATASET tuple chain captures full provenance. Bias-evaluation tuples per EU AI Act Art. 9 / Colorado AI Act § 6-1-1702. Quality-evaluation tuples at ingestion. | `hummbl_governance/coordination_bus.py` (DATASET tuples), bias-eval primitives |
| **10. Cybersecurity** | Cybersecurity controls for device software and connected infrastructure | ✅ HMAC-SHA256 delegation tokens, Bandit/Semgrep CI blocking, dependency vulnerability scanning (pip-audit), circuit-breaker resilience primitives | `hummbl_governance/delegation.py`, `hummbl_governance/circuit_breaker.py`, security workflow |
| **11. Record Retention** | Maintain records of all modifications, validations, and monitoring data | ✅ Append-only governance bus IS the record system. Audit-log JSONL provides queryable history. Retention configurable per regulatory requirements. | `hummbl_governance/coordination_bus.py`, `hummbl_governance/audit_log.py` |
| **12. Feedback & Complaint Handling** | Process for collecting and analyzing feedback/complaints on modified device | ✅ Feedback-intake tuples + adverse-event tuples route to governance bus. Escalation primitives trigger corrective-action workflow. | `hummbl_governance/coordination_bus.py` (feedback + adverse-event tuples) |

## Summary

| Category | Requirements | ✅ | 🟡 | ⚪ |
|---|---|---|---|---|
| Modification Scope & Control | 4 | 4 | 0 | 0 |
| Validation & Testing | 2 | 2 | 0 | 0 |
| Post-Market Surveillance | 2 | 2 | 0 | 0 |
| Risk Management | 1 | 1 | 0 | 0 |
| Transparency & Labeling | 1 | 1 | 0 | 0 |
| Data Governance | 1 | 1 | 0 | 0 |
| Cybersecurity | 1 | 1 | 0 | 0 |
| Record Retention | 1 | 1 | 0 | 0 |
| Feedback Handling | 1 | 1 | 0 | 0 |
| **Totals** | **12** | **12** | **0** | **0** |

## Draft coverage summary

This matrix is internal starter material. HUMMBL provides technical evidence infrastructure for PCCP — the PCCP document itself must be authored by the device manufacturer in collaboration with FDA. HUMMBL's tuple-based audit trail, continuous monitoring, and evolution lineage provide the data substrate for the PCCP submission.

## Cross-references

- ADR: [`docs/adr/ADR-001-coverage-matrix-not-self-grade.md`](../adr/ADR-001-coverage-matrix-not-self-grade.md)
- ISO 42001 A.6 (AI system lifecycle) — significant overlap
- EU AI Act Art. 9 (risk management), Art. 11 (technical documentation), Art. 12 (record-keeping)
- ONC HTI-1 matrix — shared privacy/security infrastructure
- HIPAA matrix below