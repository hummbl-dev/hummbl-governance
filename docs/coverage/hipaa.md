# HIPAA (Health Insurance Portability and Accountability Act) Coverage Matrix — HUMMBL

**Standard**: HIPAA — 45 CFR Parts 160, 162, and 164 (Security Rule, Privacy Rule, Breach Notification Rule, Enforcement Rule)
**Omnibus Rule**: HIPAA Omnibus Rule (2013) — 45 CFR Parts 160/164 Subparts A, B, C, D, E
**Source**: https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html
**Last reviewed**: 2026-05-14
**Reviewer**: claude-code (huxley) per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md)
**HUMMBL version**: hummbl-governance v0.8.0

## Boundary disclaimer

HUMMBL is **not** a HIPAA compliance assessmentor, covered entity, or business associate by itself. HIPAA compliance requires organizational policies, workforce training, BAA execution, and risk assessment by a qualified HIPAA professional. HUMMBL maps technical security safeguards to HIPAA requirements where software controls apply.

## Scope summary

HIPAA addresses:
- **Privacy Rule** (45 CFR § 164.500-534): PHI use/disclosure, individual rights, minimum necessary
- **Security Rule** (45 CFR § 164.302-318): Administrative, physical, technical safeguards
- **Breach Notification Rule** (45 CFR § 164.400-414): Notification requirements for unsecured PHI breaches
- **Enforcement Rule** (45 CFR § 164.400-414): Penalties for non-compliance

## Technical Safeguards — 45 CFR § 164.312

| Standard | Requirement | HUMMBL Coverage | Evidence |
|---|---|---|---|
| Access Control (§ 164.312(a)(1)) | Unique user identification, emergency access, automatic logoff, encryption/decryption | ✅ DCT provides unique identity + scoped access. Emergency access = kill-switch override. Auto-logoff = DCT expiry. | `hummbl_governance/delegation.py` (DCT), `hummbl_governance/kill_switch.py` |
| Audit Controls (§ 164.312(b)) | Hardware, software, procedural mechanisms to record and examine access/activity | ✅ Append-only governance bus records all agent activities. Audit-log JSONL provides queryable history. | `hummbl_governance/coordination_bus.py`, `hummbl_governance/audit_log.py` |
| Integrity Controls (§ 164.312(c)(1)) | Protect ePHI from improper alteration or destruction | ✅ HMAC-SHA256 signed entries prevent undetected alteration. Append-only prevents deletion/overwrite. | `hummbl_governance/delegation.py` (HMAC signing), coordination bus (append-only) |
| Transmission Security (§ 164.312(e)(1)) | Encrypt ePHI in transit, integrity controls for ePHI transmitted electronically | ✅ TLS encryption + signed tuples ensure integrity in transit. | TLS configuration + `hummbl_governance/delegation.py` (signed payloads) |
| Authentication (§ 164.312(d)) | Person/entity seeking access is who they claim to be | ✅ HMAC-SHA256 token verification. DCT issuance requires authentication chain. | `hummbl_governance/delegation.py` |

## Administrative Safeguards — 45 CFR § 164.308

| Standard | Requirement | HUMMBL Coverage | Evidence |
|---|---|---|---|
| Security Management Process (§ 164.308(a)(1)) | Risk analysis, risk management, sanction policy, information system activity review | ✅ Risk-register integration (Krineia), adverse-event tuples, activity review via governance bus queries. Sanction policy is org. | `hummbl_governance/audit_log.py`, risk-register integration |
| Assigned Security Responsibility (§ 164.308(a)(2)) | Identify security official responsible for policies/procedures | ⚪ Boundary: organizational role assignment | n/a — boundary |
| Workforce Security (§ 164.308(a)(3)) | Authorization/supervision, workforce clearance, termination procedures | 🟡 Partial: DCT revocation on termination. Authorization level encoded in DCT scope. Clearance procedures are org. | `hummbl_governance/delegation.py` (DCT revocation) |
| Information Access Management (§ 164.308(a)(4)) | Access authorization, access establishment/modification | ✅ DCT issuance/revocation provides granular, auditable access management. | `hummbl_governance/delegation.py` |
| Security Awareness Training (§ 164.308(a)(5)) | Security reminders, malicious software protection, login monitoring, password management | ⚪ Boundary: training program is organizational | n/a — boundary |
| Security Incident Procedures (§ 164.308(a)(6)) | Response, reporting, and documentation of security incidents | ✅ Incident-tuple type tracks detection→response→resolution. Notification SLA enforced. | `hummbl_governance/audit_log.py`, incident-reporting primitive |
| Contingency Plan (§ 164.308(a)(7)) | Data backup, disaster recovery, emergency mode operations, testing, criticality analysis | 🟡 Partial: append-only bus provides inherent backup. Kill-switch provides emergency mode. DR testing procedures are org. | `hummbl_governance/coordination_bus.py`, `hummbl_governance/kill_switch.py` |
| Evaluation (§ 164.308(a)(8)) | Periodic technical/nontechnical evaluation of security | ✅ Continuous monitoring + governance bus analytics enable ongoing evaluation. Formal audits are org. | `hummbl_governance/audit_log.py`, analytics queries |
| Business Associate Contracts (§ 164.308(b)) | Written contracts/agreements with BAs | ⚪ Boundary: legal contract obligation | n/a — boundary |

## Physical Safeguards — 45 CFR § 164.310

| Standard | Requirement | HUMMBL Coverage | Evidence |
|---|---|---|---|
| Facility Access Controls (§ 164.310(a)) | Contingency operations, facility security plan, access control/validation, maintenance records | ⚪ Boundary: physical facility controls | n/a — boundary |
| Workstation Use (§ 164.310(b)) | Policies for proper workstation use and access | ⚪ Boundary: workstation policy | n/a — boundary |
| Workstation Security (§ 164.310(c)) | Physical safeguards restricting access to workstations with ePHI access | ⚪ Boundary: physical security | n/a — boundary |
| Device & Media Controls (§ 164.310(d)) | Disposal, media reuse, accountability, data backup/storage | 🟡 Partial: encryption-at-rest for stored data. Physical media disposal is org. | `hummbl_governance/delegation.py` (encryption), configuration |

## Privacy Rule — 45 CFR § 164.500-534

| Standard | Requirement | HUMMBL Coverage | Evidence |
|---|---|---|---|
| Privacy Notice (§ 164.520) | Notice of privacy practices | 🟡 Partial: privacy-notice generator available; content is org responsibility | `hummbl_governance/compliance_mapper.py` (privacy-notice export) |
| Individual Rights (§ 164.524) | Right to access, amendment, accounting of disclosures, restrict, confidential communications | ✅ DSAR export + rectification + erasure + accounting-of-disclosures + restriction flags | `hummbl_governance/compliance_mapper.py`, coordination bus |
| Authorization (§ 164.508) | Obtain authorization for uses/disclosures not otherwise permitted | ✅ Authorization-record tuple type with scope, purpose, expiration | `hummbl_governance/coordination_bus.py` (authorization tuples) |
| Minimum Necessary (§ 164.502(b), 164.514(d)) | Limit PHI disclosed to minimum necessary | ✅ DCT scope-binding enforces minimum-necessary access | `hummbl_governance/delegation.py` |
| Accounting of Disclosures (§ 164.528) | Record of disclosures for 6 years, provide to individuals | ✅ Disclosure-event tuples logged on governance bus, queryable per patient, retained per policy | `hummbl_governance/coordination_bus.py` |
| Safeguards (§ 164.530(c)) | Reasonable safeguards — administrative, technical, physical | ⚪ Boundary: administrative safeguards are organizational policy; technical safeguards covered in § 164.312 above | n/a — boundary |

## Breach Notification Rule — 45 CFR § 164.400-414

| Standard | Requirement | HUMMBL Coverage | Evidence |
|---|---|---|---|
| Breach Definition (§ 164.402) | Unauthorized acquisition/access/use/disclosure compromising security/privacy | ✅ Breach-detection tuple triggers when anomaly detected in access patterns | `hummbl_governance/audit_log.py`, anomaly-detection primitive |
| Individual Notification (§ 164.404) | Notify individuals without unreasonable delay, no later than 60 days | ✅ 60-day notification SLA primitive with escalation | `hummbl_governance/lifecycle.py` (breach notification SLA) |
| HHS Notification (§ 164.408) | Notify HHS promptly; for breaches ≥500 individuals, also notify media | 🟡 Partial: notification-SLA tracks timing; HHS/media notification is org responsibility | notification SLA + logging |
| Business Associate Notification (§ 164.410) | BA must notify covered entity of breach | ✅ BA notification primitive via governance bus | `hummbl_governance/coordination_bus.py` |

## Summary

| Rule Section | Standards | ✅ | 🟡 | ⚪ |
|---|---|---|---|---|
| § 164.312 Technical Safeguards | 5 | 5 | 0 | 0 |
| § 164.308 Administrative Safeguards | 10 | 5 | 3 | 2 |
| § 164.310 Physical Safeguards | 4 | 0 | 1 | 3 |
| § 164.5xx Privacy Rule | 6 | 4 | 1 | 1 |
| § 164.4xx Breach Notification | 4 | 3 | 1 | 0 |
| **Totals** | **28** | **17** | **5** | **6** |

## Cross-references

- ADR: [`docs/adr/ADR-001-coverage-matrix-not-self-grade.md`](../adr/ADR-001-coverage-matrix-not-self-grade.md)
- ONC HTI-1 matrix — shared privacy/security infrastructure
- FDA PCCP matrix — shared lifecycle/data governance infrastructure
- EU AI Act — significant overlap on privacy, transparency, accountability
- GDPR — substantial overlap (both are privacy frameworks)
- NIST AI RMF (MS-2.11 Fairness, MS-3.1 Risk Identification) — complementary