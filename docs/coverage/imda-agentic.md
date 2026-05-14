# Singapore IMDA Model AI Governance Framework + Agentic AI Coverage Matrix — HUMMBL

**Standard**: Singapore Model AI Governance Framework (2nd ed., 2020) + Model AI Governance Framework for Generative AI (May 2024) + IMDA / AI Verify guidance
**Source**: https://www.imda.gov.sg/-/media/imda/files/sgs/-/media/imda/files/programmes/ai-verify/model-ai-governance-framework-for-generative-ai
**Last reviewed**: 2026-05-14
**Reviewer**: claude-code (huxley) per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md)
**HUMMBL version**: hummbl-governance v0.8.0

## Boundary disclaimer

The Singapore Model AI Governance Framework is **voluntary** guidance. No certification body. AI Verify is an open-source testing framework. This matrix maps HUMMBL primitives to the 9 dimensions of the Generative AI framework and the broader Model AI Governance Framework's 4 key areas.

## Structure — Model AI Governance Framework (4 key areas)

| Area | Key questions | Coverage |
|---|---|---|
| Internal governance structures + measures | Who is accountable? Roles + responsibilities? Risk management? Monitoring? | 🟡 Partial: DCT/DCTX captures roles; org structure is task |
| Determining the level of human involvement | Risk-based human oversight, from human-in-the-loop to human-out-of-the-loop | ✅ INTENT + DCT + kill_switch primitives (cross-ref EU AI Act Art. 14) |
| Operations management | Data preparation, model selection, training, validation, deployment, monitoring | ✅ Lifecycle tuple chain (cross-ref ISO 42001 A.6) |
| Stakeholder interaction + communication | Transparency, explainability, communication | 🟡 Partial: transparency + explainability primitives; org communication is task |

## Structure — Generative AI Framework (9 dimensions)

| Dimension | Coverage | Notes |
|---|---|---|
| 1. Accountability | 🟡 Partial | DCTX delegation chain = accountability allocation; org policy completes |
| 2. Data | ✅ | Dataset tuples + provenance chain + quality primitives (cross-ref ISO 42001 A.7) |
| 3. Trusted Development + Deployment | ✅ | Lifecycle tuple + V&V + deployment tuples + signed audit trail |
| 4. Incident Reporting | ✅ | Incident tuple + notification SLA + escalation (cross-ref EU AI Act Art. 73) |
| 5. Testing + Assurance | ✅ | 927 governance tests + redteam tuples + safety-eval primitives |
| 6. Security | ✅ | HMAC-SHA256 delegation tokens + Bandit/Semgrep + pip-audit blocking |
| 7. Content Provenance | ✅ | C2PA integration (`services/c2pa_mcp`) + content-provenance tuples |
| 8. Safety + Alignment | 🟡 Partial | Alignment-eval tuples + RLHF-evidence primitives; alignment-evaluation methodology is research |
| 9. AI for Public Good | ⚪ Boundary | Civic-impact framing is org strategy |

## Summary

| Component | Items | ✅ | 🟡 | ⚪ |
|---|---|---|---|---|
| Model AI Governance Framework (4 areas) | 4 | 2 | 2 | 0 |
| Generative AI Framework (9 dimensions) | 9 | 6 | 2 | 1 |
| **Totals** | **13** | **8** | **4** | **1** |

---

## Headline claim supported

> **HUMMBL fulfills the technical dimensions of Singapore's Generative AI Framework — Data, Trusted Development + Deployment, Incident Reporting, Testing + Assurance, Security, Content Provenance — and supports the Accountability dimension via DCT delegation chains. The Model AI Governance Framework's 4 key areas are 50% directly addressable (Human Involvement + Operations Management) and 50% require organizational completion (Internal Governance + Stakeholder Communication). Every dimension has a row.**

8 ✅ Fulfilled, 4 🟡 Partial, 1 ⚪ Boundary (AI for Public Good — civic strategy framing).

## Cross-references

- ADR: [`docs/adr/ADR-001-coverage-matrix-not-self-grade.md`](../adr/ADR-001-coverage-matrix-not-self-grade.md)
- Content-provenance overlap with C2PA — `services/c2pa_mcp` (Tier-2 admitted dep)
- Significant overlap with EU AI Act + NIST AI RMF + ISO 42001 — see those matrices
