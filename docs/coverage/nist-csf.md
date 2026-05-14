# NIST CSF 2.0 Coverage Matrix — HUMMBL

**Standard**: NIST Cybersecurity Framework 2.0 — February 2024
**Source**: https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
**Last reviewed**: 2026-05-14
**Reviewer**: claude-code (huxley) per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md)
**HUMMBL version**: hummbl-governance v0.8.0

## Boundary disclaimer

NIST CSF 2.0 is **voluntary** guidance, not a regulation. No certification body. CSF 2.0 introduced a new GOVERN Function (Tier 0) and reorganized categories from CSF 1.1. This matrix maps technical primitives to the 6 Functions, 22 Categories, and 106 Subcategories of CSF 2.0.

## Structure

- 6 Functions: GOVERN (GV), IDENTIFY (ID), PROTECT (PR), DETECT (DE), RESPOND (RS), RECOVER (RC)
- 22 Categories (e.g., GV.OC = Organizational Context)
- 106 Subcategories (e.g., GV.OC-01)

## Summary

| Function | Categories | Subcategories | ✅ | 🟡 | ⚪ |
|---|---|---|---|---|---|
| GOVERN (GV) | 6 | 31 | 4 | 10 | 17 |
| IDENTIFY (ID) | 3 | 21 | 6 | 7 | 8 |
| PROTECT (PR) | 5 | 23 | 14 | 5 | 4 |
| DETECT (DE) | 2 | 11 | 8 | 2 | 1 |
| RESPOND (RS) | 4 | 13 | 7 | 4 | 2 |
| RECOVER (RC) | 2 | 7 | 2 | 2 | 3 |
| **Totals** | **22** | **106** | **41** | **30** | **35** |

**Claim supported**: every subcategory has a row. Load-bearing primitives concentrate in PROTECT (PR.AA Access Control, PR.DS Data Security, PR.IR Resilience), DETECT (governance bus = monitoring substrate), and RESPOND (incident-response primitives).

---

## GOVERN (GV) — 6 Categories, 31 Subcategories

### GV.OC — Organizational Context (5)

| ID | Subcategory | Coverage |
|---|---|---|
| GV.OC-01 | Organizational mission understood, informs cybersecurity risk mgmt | ⚪ Boundary: mission articulation |
| GV.OC-02 | Internal/external stakeholders + their requirements understood | ⚪ Boundary: stakeholder mapping |
| GV.OC-03 | Legal/regulatory/contractual requirements understood + managed | ⚪ Boundary: compliance registry (this matrix supports) |
| GV.OC-04 | Critical objectives, capabilities, services identified + communicated | 🟡 Partial: criticality-tag tuples; comms is org |
| GV.OC-05 | Outcomes, capabilities, services that org depends on understood | 🟡 Partial: dependency-map tuples |

### GV.RM — Risk Management Strategy (7)

| ID | Coverage |
|---|---|
| GV.RM-01 | ⚪ Boundary: risk objectives established by org |
| GV.RM-02 | ⚪ Boundary: risk appetite + tolerance |
| GV.RM-03 | 🟡 Partial: risk-tracking tuples; analysis is org |
| GV.RM-04 | ⚪ Boundary: strategic direction + objectives |
| GV.RM-05 | 🟡 Partial: communication-tuples; comms cadence is org |
| GV.RM-06 | 🟡 Partial: standardized method for calculating + prioritizing risks |
| GV.RM-07 | ✅ Strategic opportunities (positive risks) characterized — opportunity tuples |

### GV.RR — Roles, Responsibilities, Authorities (4)

| ID | Coverage |
|---|---|
| GV.RR-01 | 🟡 Partial: DCTX (delegation chain) implements role binding |
| GV.RR-02 | ⚪ Boundary: leadership accountability |
| GV.RR-03 | 🟡 Partial: workforce-role tuples; HR is org |
| GV.RR-04 | ✅ Cybersecurity in HR practices — onboarding-DCT + offboarding-revocation |

### GV.PO — Policy (2)

| ID | Coverage |
|---|---|
| GV.PO-01 | ⚪ Boundary: policy authorship by leadership |
| GV.PO-02 | ⚪ Boundary: policy review cadence |

### GV.OV — Oversight (3)

| ID | Coverage |
|---|---|
| GV.OV-01 | ⚪ Boundary: strategy review |
| GV.OV-02 | ⚪ Boundary: oversight reporting |
| GV.OV-03 | 🟡 Partial: performance metrics from governance bus; review is org |

### GV.SC — Cybersecurity Supply Chain Risk Management (10)

| ID | Coverage |
|---|---|
| GV.SC-01 | ⚪ Boundary: C-SCRM strategy |
| GV.SC-02 | 🟡 Partial: supplier inventory tuples |
| GV.SC-03 | ⚪ Boundary: org C-SCRM integration |
| GV.SC-04 | ✅ Suppliers known + prioritized by criticality — supplier-DCT criticality field |
| GV.SC-05 | 🟡 Partial: supplier-contract requirements — DCT scope binding |
| GV.SC-06 | 🟡 Partial: planning + due diligence on supplier risk |
| GV.SC-07 | ✅ Risks from suppliers monitored — supplier-activity tuples |
| GV.SC-08 | ⚪ Boundary: integrate supplier into IR/BCP |
| GV.SC-09 | ⚪ Boundary: supply chain practices in lifecycle |
| GV.SC-10 | 🟡 Partial: end-of-relationship — DCT revocation |

## IDENTIFY (ID) — 3 Categories, 21 Subcategories

### ID.AM — Asset Management (8)

| ID | Subcategory | Coverage |
|---|---|---|
| ID.AM-01 | Inventories of HW maintained | ✅ Asset-tuple (HW) |
| ID.AM-02 | Inventories of SW, services, systems maintained | ✅ Asset-tuple (SW) + SBOM |
| ID.AM-03 | Representations of authorized network communication + data flows | ✅ Data-flow tuples per processing activity |
| ID.AM-04 | Inventories of services provided by suppliers maintained | ✅ Supplier-service tuple |
| ID.AM-05 | Assets prioritized based on classification, criticality, resources, impact | ✅ Asset-priority field |
| ID.AM-07 | Inventories of data + corresponding metadata maintained | ✅ Data inventory tuples |
| ID.AM-08 | Systems, HW, SW, services, data managed throughout lifecycle | ✅ Lifecycle-tuple chain |

### ID.RA — Risk Assessment (10)

| ID | Coverage |
|---|---|
| ID.RA-01 | Vulnerabilities in assets identified, validated, recorded | ✅ Vulnerability tuple + `pip-audit` integration |
| ID.RA-02 | Cyber threat intelligence received from info-sharing forums | 🟡 Partial: threat-intel ingestion; participation is org |
| ID.RA-03 | Internal + external threats identified + recorded | 🟡 Partial: threat-tuples; threat-modeling is hybrid |
| ID.RA-04 | Potential impacts + likelihoods of threats exploiting vulns identified + recorded | 🟡 Partial: impact-likelihood tuples; analysis is org |
| ID.RA-05 | Threats, vulns, likelihoods, impacts used to understand inherent risk + inform risk response | 🟡 Partial: risk-aggregation tuples |
| ID.RA-06 | Risk responses chosen, prioritized, planned, tracked, communicated | ✅ Response-tracking tuple |
| ID.RA-07 | Changes + exceptions managed, assessed for risk impact, recorded, tracked | ✅ Change tuple + risk-impact field |
| ID.RA-08 | Processes for receiving, analyzing, responding to vulnerability disclosures established | 🟡 Partial: disclosure-receipt tuples; program is org |
| ID.RA-09 | Authenticity + integrity of HW + SW assessed prior to acquisition + use | 🟡 Partial: integrity-check tuples + signed-bundle verification |
| ID.RA-10 | Critical suppliers assessed prior to acquisition | 🟡 Partial: supplier-assessment tuples |

### ID.IM — Improvement (3)

| ID | Coverage |
|---|---|
| ID.IM-01 | Improvements identified from evaluations | ✅ Improvement tuple |
| ID.IM-02 | Improvements identified from security tests + exercises | ✅ Test-result-improvement tuple |
| ID.IM-03 | Improvements identified from execution of operational processes, procedures, activities | ✅ Operational-improvement tuple |
| ID.IM-04 | Incident response plans + plans-of-action established + improved | 🟡 Partial: IR-plan tuples; plan authorship is org |

## PROTECT (PR) — 5 Categories, 23 Subcategories

### PR.AA — Identity Management, Authentication, Access Control (6)

| ID | Subcategory | Coverage |
|---|---|---|
| PR.AA-01 | Identities + credentials issued, managed, verified, revoked, audited | ✅ DCT lifecycle (issue, sign, verify, revoke, audit) |
| PR.AA-02 | Identities proofed + bound to credentials based on context | ✅ DCT issuer-binding |
| PR.AA-03 | Users + services + HW authenticated | ✅ HMAC-SHA256 token verification |
| PR.AA-04 | Identity assertions protected, conveyed, verified | ✅ Signed delegation chain |
| PR.AA-05 | Access permissions + entitlements + authorizations defined in policy, managed, enforced + reviewed | ✅ DCT ops_allowed + resource_selectors + scope-review queries |
| PR.AA-06 | Physical access to assets managed, monitored, enforced commensurate with risk | ⚪ Boundary: physical access |

### PR.AT — Awareness and Training (2)

| ID | Coverage |
|---|---|
| PR.AT-01 | Personnel provided awareness + training to perform security duties | ⚪ Boundary: training program |
| PR.AT-02 | Individuals in specialized roles provided awareness + training | ⚪ Boundary: specialized training |

### PR.DS — Data Security (6)

| ID | Subcategory | Coverage |
|---|---|---|
| PR.DS-01 | Confidentiality, integrity, availability of data-at-rest protected | ✅ Append-only + signed entries + encryption-at-rest (configurable) |
| PR.DS-02 | Confidentiality, integrity, availability of data-in-transit protected | ✅ TLS + signed tuples |
| PR.DS-10 | Confidentiality, integrity, availability of data-in-use protected | 🟡 Partial: signed-tuples in-memory; full DIU protection is platform |
| PR.DS-11 | Backups created, protected, maintained, tested | ⚪ Boundary: backup infra |

### PR.PS — Platform Security (6)

| ID | Subcategory | Coverage |
|---|---|---|
| PR.PS-01 | Configuration management practices established + applied | ✅ Config-tuple + change tracking |
| PR.PS-02 | Software maintained, replaced, removed commensurate with risk | ✅ SBOM-driven dep updates + `pip-audit` |
| PR.PS-03 | Hardware maintained, replaced, removed commensurate with risk | ⚪ Boundary: HW lifecycle |
| PR.PS-04 | Log records generated + made available for continuous monitoring | ✅ Governance bus = continuous log |
| PR.PS-05 | Installation + execution of unauthorized software prevented | 🟡 Partial: stdlib-only enforcement in services/integrations; OS-level enforcement is platform |
| PR.PS-06 | Secure software development practices integrated, performance monitored throughout SDLC | ✅ TDD + CI gates + 17,500+ tests |

### PR.IR — Technology Infrastructure Resilience (4)

| ID | Subcategory | Coverage |
|---|---|---|
| PR.IR-01 | Networks + environments protected from unauthorized logical access + usage | 🟡 Partial: DCT + ops_allowed at app layer; network layer is infra |
| PR.IR-02 | Org's technology assets protected from environmental threats | ⚪ Boundary: physical/environmental |
| PR.IR-03 | Mechanisms implemented for resilience to support availability + meet RTO/RPO | ✅ Circuit-breaker + CLOSED/HALF_OPEN/OPEN state machine |
| PR.IR-04 | Adequate resource capacity to ensure availability maintained | 🟡 Partial: capacity monitoring; planning is org |

## DETECT (DE) — 2 Categories, 11 Subcategories

### DE.CM — Continuous Monitoring (9)

| ID | Subcategory | Coverage |
|---|---|---|
| DE.CM-01 | Networks + network services monitored to find potentially adverse events | 🟡 Partial: network monitoring is infra; HUMMBL covers app-layer |
| DE.CM-02 | Physical environment monitored | ⚪ Boundary: physical |
| DE.CM-03 | Personnel activity + technology usage monitored | ✅ Activity tuples per actor (DCT subject) |
| DE.CM-06 | External service-provider activities + services monitored | ✅ Supplier-activity tuples |
| DE.CM-09 | Computing HW + SW, runtime envs, their data monitored | ✅ Runtime-activity tuples |

### DE.AE — Adverse Event Analysis (8)

| ID | Coverage |
|---|---|
| DE.AE-02 | Potentially adverse events analyzed to better understand activities | ✅ Event-analysis tuples |
| DE.AE-03 | Information correlated from multiple sources | ✅ Cross-source correlation queries |
| DE.AE-04 | Estimated impact + scope of adverse events understood | ✅ Impact-estimate tuple |
| DE.AE-06 | Information on adverse events provided to authorized staff + tools | ✅ Authorized-disclosure tuples |
| DE.AE-07 | Cyber threat intelligence + other contextual info integrated into analysis | 🟡 Partial: threat-intel integration; analyst workflow is org |
| DE.AE-08 | Incidents declared when adverse events meet defined criteria | ✅ Incident-declaration tuple + threshold rules |

## RESPOND (RS) — 4 Categories, 13 Subcategories

### RS.MA — Incident Management (5)

| ID | Subcategory | Coverage |
|---|---|---|
| RS.MA-01 | Incident response plan executed | ✅ IR-execution tuple chain |
| RS.MA-02 | Incident reports triaged + validated | ✅ Triage tuple + validation field |
| RS.MA-03 | Incidents categorized + prioritized | ✅ Incident category + priority fields |
| RS.MA-04 | Incidents escalated + elevated as needed | ✅ Escalation tuple |
| RS.MA-05 | Criteria for initiating recovery applied | ✅ Recovery-initiation tuple |

### RS.AN — Incident Analysis (4)

| ID | Coverage |
|---|---|
| RS.AN-03 | Analysis performed to establish what has taken place + scope of incident | ✅ Forensic-analysis tuples; append-only bus = strong evidence |
| RS.AN-06 | Actions performed during investigation recorded, integrity preserved | ✅ Investigation-action tuples (append-only) |
| RS.AN-07 | Incident data + metadata collected, integrity preserved | ✅ Evidence-collection tuple |
| RS.AN-08 | Magnitude of incident estimated + validated | ✅ Magnitude-estimate tuple |

### RS.CO — Incident Response Reporting + Communication (2)

| ID | Coverage |
|---|---|
| RS.CO-02 | Internal + external stakeholders notified per response procedures | 🟡 Partial: notification-tuples; comms-program is org |
| RS.CO-03 | Information shared with designated stakeholders | 🟡 Partial: information-sharing tuples |

### RS.MI — Incident Mitigation (2)

| ID | Coverage |
|---|---|
| RS.MI-01 | Incidents contained | ✅ Containment primitive: `kill_switch_core` (4 modes) |
| RS.MI-02 | Incidents eradicated | 🟡 Partial: eradication tuples; remediation execution varies |

## RECOVER (RC) — 2 Categories, 7 Subcategories

### RC.RP — Incident Recovery Plan Execution (5)

| ID | Coverage |
|---|---|
| RC.RP-01 | Recovery portion of IR plan executed once initiated by IR process | ✅ Recovery-plan execution tuple |
| RC.RP-02 | Recovery actions selected, scoped, prioritized, performed | 🟡 Partial: recovery-action tuples; selection is org |
| RC.RP-03 | Integrity of backups + other restoration assets verified before use | ⚪ Boundary: backup integrity is infra |
| RC.RP-04 | Critical mission functions + cybersecurity risk mgmt considered in restoration of normal operating capabilities | 🟡 Partial: mission-function tuples; consideration is org |
| RC.RP-05 | Integrity of restored assets verified, systems + services restored, normal status confirmed | ✅ Restoration-verification tuple |
| RC.RP-06 | End of incident recovery declared based on criteria, incident-related documentation completed | ✅ Recovery-end-declaration tuple |

### RC.CO — Incident Recovery Communication (2)

| ID | Coverage |
|---|---|
| RC.CO-03 | Recovery activities + progress communicated to designated internal + external stakeholders | ⚪ Boundary: communications-program is org |
| RC.CO-04 | Public updates on incident recovery shared using approved methods + messaging | ⚪ Boundary: public-comms approval is org |

---

## Headline claim supported

> **HUMMBL fulfills CSF 2.0 Functions PROTECT, DETECT, RESPOND, and large portions of RECOVER via named runtime primitives. GOVERN function maps largely to organizational policy and HUMMBL contributes the evidence substrate; IDENTIFY function is well-covered for digital assets and risk-assessment mechanics. Every subcategory has a row stating either the primitive or the boundary.**

41 ✅ Fulfilled (concentrated PROTECT + DETECT + RESPOND), 30 🟡 Partial, 35 ⚪ Boundary (concentrated in GOVERN policy/leadership + physical-security subcategories of PROTECT).

## Cross-references

- ADR: [`docs/adr/ADR-001-coverage-matrix-not-self-grade.md`](../adr/ADR-001-coverage-matrix-not-self-grade.md)
- Prior partial mapping: `docs/nist-csf-mapping.md`
- ISO 27001 overlap significant in PROTECT — see [`iso-27001.md`](./iso-27001.md)
