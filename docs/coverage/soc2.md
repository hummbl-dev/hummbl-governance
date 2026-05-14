# SOC 2 Coverage Matrix — HUMMBL

**Standard**: SOC 2 — AICPA Trust Services Criteria (2017, updated 2022). Used by service organizations to report on internal controls relevant to security, availability, processing integrity, confidentiality, privacy.
**Source**: https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2
**Last reviewed**: 2026-05-14
**Reviewer**: claude-code (huxley) per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md)
**HUMMBL version**: hummbl-governance v0.8.0

## Boundary disclaimer

HUMMBL is **not** a SOC 2 attestation. SOC 2 reports are issued only by licensed CPA firms (e.g., A-LIGN, Deloitte, EY) following an examination per AICPA Statements on Standards for Attestation Engagements (SSAE) No. 21. A SOC 2 report covers a specific service organization, a specific service, a specific time period (Type 1: point-in-time; Type 2: 6-12 months operating effectiveness), and a specific subset of Trust Services Criteria (Common Criteria + optionally Availability/Processing Integrity/Confidentiality/Privacy).

This matrix maps HUMMBL technical primitives to the SOC 2 criteria. **The matrix does not constitute a SOC 2 report.** A customer organization seeking SOC 2 attestation must engage a CPA firm separately; HUMMBL provides evidence artifacts that support such an engagement.

## Structure

SOC 2 Trust Services Criteria (TSC):
- **Common Criteria (CC)** — required for every SOC 2 engagement, ~33 criteria across 9 sections (CC1–CC9)
- **Availability (A)** — optional, 3 criteria
- **Processing Integrity (PI)** — optional, 5 criteria
- **Confidentiality (C)** — optional, 2 criteria
- **Privacy (P)** — optional, 8 sections × multiple criteria (~18 total)

Total addressed in this matrix: ~61 criteria (CC + A + PI + C + P core).

## Summary

| TSC | Criteria | ✅ | 🟡 | ⚪ |
|---|---|---|---|---|
| CC1 — Control Environment | 5 | 0 | 2 | 3 |
| CC2 — Communication + Information | 3 | 1 | 1 | 1 |
| CC3 — Risk Assessment | 4 | 1 | 2 | 1 |
| CC4 — Monitoring Activities | 2 | 2 | 0 | 0 |
| CC5 — Control Activities | 3 | 2 | 1 | 0 |
| CC6 — Logical + Physical Access Controls | 8 | 6 | 1 | 1 |
| CC7 — System Operations | 5 | 4 | 1 | 0 |
| CC8 — Change Management | 1 | 1 | 0 | 0 |
| CC9 — Risk Mitigation | 2 | 1 | 1 | 0 |
| A — Availability | 3 | 2 | 1 | 0 |
| PI — Processing Integrity | 5 | 4 | 1 | 0 |
| C — Confidentiality | 2 | 2 | 0 | 0 |
| P — Privacy (8 sections) | ~18 | 6 | 9 | 3 |
| **Totals** | **~61** | **32** | **20** | **9** |

**Draft coverage intent (not public claim): every Common Criterion + core TSC criterion has a row. Concentration of ✅ in CC6 (Access Control), CC7 (Operations), Availability, Processing Integrity, Confidentiality — the technically-implementable criteria.

---

## CC1 — Control Environment (5)

| ID | Coverage | Notes |
|---|---|---|
| CC1.1 | ⚪ Boundary | COSO Integrity + ethical values — leadership |
| CC1.2 | ⚪ Boundary | Board oversight |
| CC1.3 | 🟡 Partial | Org structure + reporting via DCTX; structure design is org |
| CC1.4 | 🟡 Partial | Commitment to competence — HR + DCT-based role binding |
| CC1.5 | ⚪ Boundary | Accountability assignment |

## CC2 — Communication and Information (3)

| ID | Coverage | Notes |
|---|---|---|
| CC2.1 | ✅ Information requirements + sources — tuple-schema enforced data quality |
| CC2.2 | 🟡 Partial | Internal communication — bus = comms substrate; comms practice is org |
| CC2.3 | ⚪ Boundary | External communication |

## CC3 — Risk Assessment (4)

| ID | Coverage | Notes |
|---|---|---|
| CC3.1 | 🟡 Partial | Risk objectives + categories — `INTENT` + adverse-event tuples (risk-register integration per Krineia connector spec) |
| CC3.2 | ✅ Identify + analyze risks — risk-identification tuples + analysis primitives |
| CC3.3 | 🟡 Partial | Fraud risk — fraud-flag tuples; assessment is org |
| CC3.4 | ⚪ Boundary | Significant change in risk profile — change-event triggers |

## CC4 — Monitoring Activities (2)

| ID | Coverage |
|---|---|
| CC4.1 | ✅ Ongoing + separate evaluations — governance bus + audit-log queries |
| CC4.2 | ✅ Evaluate + communicate deficiencies — deficiency tuples + escalation |

## CC5 — Control Activities (3)

| ID | Coverage |
|---|---|
| CC5.1 | ✅ Selection + development of controls — control-catalog tuples |
| CC5.2 | ✅ Selection + development of technology controls — primitives shipped + tested |
| CC5.3 | 🟡 Partial | Deployment through policies + procedures — policy authorship is org |

## CC6 — Logical and Physical Access Controls (8) — **load-bearing**

| ID | Coverage |
|---|---|
| CC6.1 | ✅ Logical access security — DCT delegation + ops_allowed |
| CC6.2 | ✅ Authorization + registration of users — DCT issuance |
| CC6.3 | ✅ Authentication credentials — HMAC-SHA256 signed tokens |
| CC6.4 | ⚪ Boundary | Physical access — facility security |
| CC6.5 | ✅ Logical access prevented when no longer required — DCT revocation |
| CC6.6 | ✅ Logical access restricted via boundary protections — DCT scope binding |
| CC6.7 | ✅ Transmission + movement of information — TLS + signed tuples |
| CC6.8 | 🟡 Partial | Prevention/detection of unauthorized software — stdlib-only at app layer; OS layer is platform |

## CC7 — System Operations (5)

| ID | Coverage |
|---|---|
| CC7.1 | ✅ Detection of new vulnerabilities — `pip-audit` blocking + Bandit + Semgrep |
| CC7.2 | ✅ Monitoring + analysis of security events — governance bus monitoring |
| CC7.3 | ✅ Incident management procedures — IR tuple chain |
| CC7.4 | ✅ Incident communications — incident-comm tuple + escalation |
| CC7.5 | 🟡 Partial | Recovery — backup integrity is infra; service-level recovery covered |

## CC8 — Change Management (1)

| CC8.1 | ✅ Change management process — change tuples + signed audit trail + Conventional Commits + PR review |

## CC9 — Risk Mitigation (2)

| ID | Coverage |
|---|---|
| CC9.1 | ✅ Risk mitigation activities — risk-treatment tuple + circuit-breaker primitives |
| CC9.2 | 🟡 Partial | Vendor + business partner risk — supplier-DCT + SBOM; due-diligence program is org |

## Availability (A) — 3 criteria

| ID | Coverage |
|---|---|
| A1.1 | ✅ Capacity demand + management — capacity-monitoring tuples + circuit-breaker overload handling |
| A1.2 | 🟡 Partial | Environmental protection + recovery — backup infra is platform |
| A1.3 | ✅ Recovery + business continuity — circuit-breaker state machine + IR recovery tuples |

## Processing Integrity (PI) — 5 criteria

| ID | Coverage |
|---|---|
| PI1.1 | ✅ Procedures to ensure complete, valid, accurate inputs — tuple-schema validation at ingress |
| PI1.2 | ✅ Procedures to detect + correct errors during processing — error tuples + correction primitives |
| PI1.3 | ✅ Procedures to ensure complete, valid, accurate processing — append-only + signed processing tuples |
| PI1.4 | 🟡 Partial | Outputs delivered timely, complete, accurate — delivery-confirmation tuples; SLA tracking is config |
| PI1.5 | ✅ Procedures protect data inputs, processing, outputs through retention | `hummbl_governance/coordination_bus.py` (append-only bus), `hummbl_governance/delegation.py` (signed entries), `hummbl_governance/lifecycle.py` (retention) |

## Confidentiality (C) — 2 criteria

| ID | Coverage |
|---|---|
| C1.1 | ✅ Confidential information identified + protected — classification tag + restricted access via DCT |
| C1.2 | ✅ Confidential information retained, transferred, destroyed per agreements + retention policies — retention/erasure tuples |

## Privacy (P) — 8 sections, ~18 criteria

The Privacy TSC overlaps heavily with GDPR; rows summarized here, with detail in [`gdpr.md`](./gdpr.md).

| Section | Topic | Coverage summary |
|---|---|---|
| P1 — Privacy notice | Provide notice + obtain consent | ✅ (cross-ref GDPR Art. 13/14, Art. 7) |
| P2 — Choice + consent | Obtain consent, communicate purposes, document refusal | ✅ Consent-record tuples |
| P3 — Collection | Limit collection to identified purposes | ✅ Tuple-schema enforces declared-field-only |
| P4 — Use, retention, disposal | Use only for stated purposes, retain only as needed, dispose securely | ✅ Purpose-tag + retention + erasure tuples |
| P5 — Access | Provide individuals access to their info | ✅ DSAR export (GDPR Art. 15) |
| P6 — Disclosure to third parties | Disclose only per purposes + consent | 🟡 Partial: disclosure tuples + downstream DCT propagation |
| P7 — Quality | Maintain accuracy + completeness | ✅ Rectification tuple |
| P8 — Monitoring + enforcement | Monitor compliance, address complaints + violations | 🟡 Partial: monitoring tuples + complaint-intake; resolution is org |

Per the GDPR matrix, the technical privacy criteria are ✅ Fulfilled. The boundary rows in P6-P8 reflect customer-org policies and program execution.

---

## Draft coverage summary (not public claim)

This matrix is internal starter material. It must not be used as public evidence that HUMMBL fulfills this framework until row counts, evidence commands, artifact paths, and boundary classifications are validated.

## Cross-references

- ADR: [`docs/adr/ADR-001-coverage-matrix-not-self-grade.md`](../adr/ADR-001-coverage-matrix-not-self-grade.md)
- Prior partial mapping: `docs/soc2-mapping.md`
- Privacy criteria detail in [`gdpr.md`](./gdpr.md)
- Security overlap with [`iso-27001.md`](./iso-27001.md) Annex A
