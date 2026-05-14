# HUMMBL Coverage Matrices — Index

Every applicable control across every named framework, row-by-row.
Per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md): **completeness, not score**.

**HUMMBL version**: hummbl-governance v0.8.0
**Last index update**: 2026-05-14
**Coverage state legend**: ✅ Fulfilled · 🟡 Partial · ⚪ Boundary · ⛔ Out of scope

---

## Matrices

| Framework | Surface | ✅ | 🟡 | ⚪ | File |
|---|---:|---:|---:|---:|---|
| EU AI Act | 113 articles + 13 annexes | 23 | 19 | 71 | [`eu-ai-act.md`](./eu-ai-act.md) |
| GDPR | 99 articles | 16 | 15 | 68 | [`gdpr.md`](./gdpr.md) |
| ISO/IEC 27001:2022 | 93 Annex A controls + ISMS Clauses 4–10 | 26 | 18 | 49 | [`iso-27001.md`](./iso-27001.md) |
| ISO/IEC 42001:2023 | 38 Annex A controls + Clauses 4–10 | 15 | 19 | 4 | [`iso-42001.md`](./iso-42001.md) |
| NIST AI RMF 1.0 | ~70 subcategories (4 Functions) | 20 | 31 | 19 | [`nist-ai-rmf.md`](./nist-ai-rmf.md) |
| NIST CSF 2.0 | 106 subcategories (6 Functions) | 41 | 30 | 35 | [`nist-csf.md`](./nist-csf.md) |
| SOC 2 (TSC 2017/2022) | ~61 TSC criteria (CC + A + PI + C + P) | 32 | 20 | 9 | [`soc2.md`](./soc2.md) |
| OWASP LLM Top 10 (2025) | 10 risk categories | 8 | 2 | 0 | [`owasp-llm.md`](./owasp-llm.md) |
| Colorado AI Act (SB 24-205) | 18 obligations | 16 | 2 | 0 | [`colorado-ai-act.md`](./colorado-ai-act.md) |
| NYC Local Law 144 (AEDT) | 9 obligations | 6 | 2 | 1 | [`nyc-ll144.md`](./nyc-ll144.md) |
| Singapore IMDA Model AI Governance + Generative AI | 13 dimensions | 7 | 5 | 1 | [`imda-agentic.md`](./imda-agentic.md) |
| G7 Hiroshima AI Process Code of Conduct | 11 principles | 5 | 4 | 2 | [`g7-ai-code.md`](./g7-ai-code.md) |
| **TOTALS** | **~657 controls** | **215** | **167** | **259** | 12 frameworks |

> **These counts are enumeration evidence, not a score.** ✅ + 🟡 + ⚪ sum to the full surface of every framework. There is no implied "215 / 657 = 33%" — the denominator includes 259 ⚪ Boundary rows that explicitly identify where the control is the customer organization's responsibility, the certification body's responsibility, or outside the AI-governance-platform scope. Boundary rows are not failures; they are part of the completeness claim. Per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md), HUMMBL does not publish self-issued grades against external frameworks; the matrices are row-by-row receipts, not aggregate marks.

---

## Draft status

These matrices are internal coverage scaffolds, not public claim support yet. Do not use the aggregate counts or headline language externally until row counts, evidence cells, command examples, and boundary classifications pass validation plus operator/legal review.

The **215 ✅ Fulfilled** rows concentrate in the technical / measurement / access-control / audit-trail / lifecycle / data-governance surfaces where software primitives do the work. The **167 🟡 Partial** rows are where HUMMBL provides the technical primitive and the customer organization provides the policy, contract, or program completion. The **259 ⚪ Boundary** rows are organizational structures, regulatory institutions, civil/criminal liability mechanisms, member-state legislative regimes, and physical-security controls that no software product can implement.

## What this does NOT claim

- HUMMBL is not a certification body. Where statutory certification is required (ISO 27001 accredited registrar, SOC 2 CPA-firm attestation, EU AI Act Notified Body conformity assessment for biometric ID systems), customer organizations must engage qualified third parties.
- The matrices do not constitute legal advice. Compliance with binding law (EU AI Act, GDPR, Colorado AI Act, NYC LL144) requires customer-organization legal review and, where applicable, supervisory-authority engagement.
- "Fulfills ALL applicable" — applicability is defined per-row, not aggregated behind a percentage. The matrices are the evidence; the headline depends on the matrix, not the other way around.

## How to read the matrices

1. Start with the framework that applies to you (binding law for your jurisdiction, voluntary framework for your industry, attestation standard for your buyer).
2. Read row-by-row. Every control has an explicit coverage state.
3. For ✅ rows, the `Evidence` column must point to a validated runnable command or resolvable artifact before public use; draft/planned evidence must be labeled explicitly.
4. For 🟡 rows, both halves are named — what HUMMBL provides, what customer policy completes.
5. For ⚪ rows, the boundary is stated — why this is not addressable by a software primitive.

## Maintenance

- Each matrix versioned with `Last reviewed` date + `HUMMBL version` field
- Standards updates trigger matrix re-review (annual minimum, on-publication for binding-law updates)
- New frameworks added by appending to this index and creating `<slug>.md` under `docs/coverage/` per ADR-001

## Related artifacts

- [ADR-001 — Coverage matrix, not self-grade](../adr/ADR-001-coverage-matrix-not-self-grade.md)
- [Compliance-mapper module](../../hummbl_governance/compliance_mapper.py) — runtime evidence generators
- Prior partial mapping docs (now starter material, superseded by the matrices above):
  - [`docs/gdpr-mapping.md`](../gdpr-mapping.md)
  - [`docs/iso27001-mapping.md`](../iso27001-mapping.md)
  - [`docs/nist-csf-mapping.md`](../nist-csf-mapping.md)
  - [`docs/nist-rmf-mapping.md`](../nist-rmf-mapping.md)
  - [`docs/soc2-mapping.md`](../soc2-mapping.md)
- [OWASP_MAPPING.md](../OWASP_MAPPING.md) — narrative companion to `owasp-llm.md`
