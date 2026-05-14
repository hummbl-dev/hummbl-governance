# ONC Health IT Certification (HTI-1) Coverage Matrix — HUMMBL

**Standard**: ONC Health IT Certification Program — HTI-1 Final Rule (2024 update)
**Effective**: January 1, 2026 (compliance date TBD per final rule timeline)
**Source**: https://www.healthit.gov/test-method/standardized-api-patient-and-population-services
**Last reviewed**: 2026-05-14
**Reviewer**: claude-code (huxley) per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md)
**HUMMBL version**: hummbl-governance v0.8.0

## Boundary disclaimer

HUMMBL is **not** an ONC-authorized certification body. ONC Health IT Certification requires accredited testing by ONC-ATCBs (e.g., Drummond Group, ICSA Labs). This matrix maps HUMMBL technical primitives to the HTI-1 requirements that are addressable through software controls. Certification engagement is customer-org responsibility.

## Scope summary

HTI-1 Final Rule (42 CFR Part 17) updates certification criteria for EHR, HIE, and patient-access API products under the ONC Health IT Certification Program. The 2024 update adds requirements for electronic visit verification (EVV), prior authorization API (FHIR-based), and enhanced interoperability. Key certification areas relevant to HUMMBL:

- Patient Access API (§ 170.315 g.10)
- Provider Directory (§ 170.315 g.11)
- Payer-to-Payer Data Exchange (§ 170.315 g.12)
- Electronic Visit Verification (§ 170.315 g.13)
- Prior Authorization API (§ 170.315 g.14)
- TEFCA/Common Agreement compliance
- Privacy & Security (cross-ref HIPAA, 45 CFR Part 160/164)

## Coverage matrix

| Certification Criterion | Requirement | HUMMBL Coverage | Evidence |
|---|---|---|---|
| g.10 Patient Access API | Patients can access electronic health info via FHIR API | 🟡 Partial: audit-trail primitives for API access logging; FHIR implementation is product-layer | `hummbl_governance/audit_log.py` (access audit trail) |
| g.11 Provider Directory | Accurate, current provider directory data exchange | ⚪ Boundary: data accuracy is directory-system responsibility | n/a — boundary |
| g.12 Payer-to-Payer Data Exchange | Secure electronic health info exchange between payers | ✅ Secure data exchange primitives: TLS + signed tuples + DCT-scoped access | `hummbl_governance/delegation.py`, TLS config |
| g.13 Electronic Visit Verification | Verify patient location + provider identity during telehealth encounters | ⚪ Boundary: EVV requires real-time location/provider verification systems | n/a — boundary |
| g.14 Prior Authorization API | FHIR-based prior auth request/response within defined timeframes | 🟡 Partial: workflow-tuple tracking for prior auth state machine; FHIR API is product-layer | `hummbl_governance/coordination_bus.py` (workflow state tuples) |
| Privacy & Security (164.312) | Technical safeguards: access control, audit controls, integrity, transmission security | ✅ Comprehensive: DCT access control, append-only audit logs, HMAC integrity, TLS | `hummbl_governance/delegation.py`, `hummbl_governance/audit_log.py`, `hummbl_governance/circuit_breaker.py` |
| Privacy & Security (164.308) | Administrative safeguards: risk analysis, workforce training, incident procedures | 🟡 Partial: risk-register + incident-tuple infrastructure; policies are org responsibility | `hummbl_governance/audit_log.py`, risk-register integration |
| BA Agreement Requirements (164.308(b)(1)) | Business associate agreements with appropriate safeguards | ⚪ Boundary: legal-contract obligation | n/a — boundary |
| Breach Notification (164.400-414) | Notify HHS + individuals within 60 days of breach discovery | ✅ Breach-detection tuple + 60-day notification SLA primitive | `hummbl_governance/audit_log.py` (breach detector), notification primitive |
| Minimum Necessary (164.502(b), 164.514(d)) | Limit PHI disclosure to minimum necessary for purpose | ✅ DCT scope-binding enforces minimum-necessary access per delegation | `hummbl_governance/delegation.py` (scope binding) |
| Individual Right of Access (164.524) | Patients can request and receive their PHI | ✅ DSAR export generates FHIR-compatible access response | `hummbl_governance/compliance_mapper.py` (DSAR export) |
| Accounting of Disclosures (164.528) | Patients can request accounting of PHI disclosures | ✅ Disclosure-event tuples logged on governance bus, queryable per patient | `hummbl_governance/coordination_bus.py` (disclosure tuples) |

## Summary

| Section | Criteria | ✅ | 🟡 | ⚪ |
|---|---|---|---|---|
| Patient Access (g.10) | 1 | 0 | 1 | 0 |
| Provider Directory (g.11) | 1 | 0 | 0 | 1 |
| Payer-to-Payer (g.12) | 1 | 1 | 0 | 0 |
| EVV (g.13) | 1 | 0 | 0 | 1 |
| Prior Auth (g.14) | 1 | 0 | 1 | 0 |
| Privacy & Security (164) | 7 | 5 | 1 | 1 |
| **Totals** | **12** | **6** | **3** | **3** |

## Cross-references

- ADR: [`docs/adr/ADR-001-coverage-matrix-not-self-grade.md`](../adr/ADR-001-coverage-matrix-not-self-grade.md)
- HIPAA matrix below — significant overlap with Privacy & Security criteria
- EU AI Act Art. 13 (transparency) overlaps with Patient Access API
- NIST AI RMF overlaps with Privacy & Security safeguards