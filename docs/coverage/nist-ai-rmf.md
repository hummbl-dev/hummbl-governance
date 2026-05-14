# NIST AI RMF 1.0 Coverage Matrix — HUMMBL

**Standard**: NIST AI Risk Management Framework 1.0 (NIST AI 100-1) — January 2023
**Source**: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
**Last reviewed**: 2026-05-14
**Reviewer**: claude-code (huxley) per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md)
**HUMMBL version**: hummbl-governance v0.8.0

## Boundary disclaimer

NIST AI RMF is a **voluntary** framework, not a regulation. There is no certification body for AI RMF; conformance is self-attested or third-party-assessed via consulting engagements. HUMMBL maps technical primitives to AI RMF subcategories; framework adoption (governance structure, organizational priorities, AI risk tolerance) is the customer organization's responsibility.

## Structure

NIST AI RMF organizes around 4 Functions (GOVERN, MAP, MEASURE, MANAGE), each with Categories and Subcategories. The framework includes ~70 subcategories across the 4 functions.

## Summary

| Function | Subcategories | ✅ | 🟡 | ⚪ |
|---|---|---|---|---|
| GOVERN | ~19 | 4 | 8 | 7 |
| MAP | ~18 | 3 | 9 | 6 |
| MEASURE | ~20 | 8 | 8 | 4 |
| MANAGE | ~13 | 5 | 6 | 2 |
| **Totals** | **~70** | **20** | **31** | **19** |

**Draft coverage intent (not public claim): every NIST AI RMF subcategory has a row. Load-bearing primitives concentrate in MEASURE (measurement infrastructure is what HUMMBL is) and MANAGE (kill-switch + incident-response primitives).

---

## GOVERN — Policies, processes, procedures, and practices

### GOVERN 1 — Policies, processes, procedures (govern.1.1–1.7)

| ID | Subcategory | Coverage |
|---|---|---|
| GV-1.1 | Legal and regulatory requirements involving AI are understood, managed, documented | ⚪ Boundary: org legal-reg mapping; supported by this matrix index |
| GV-1.2 | Characteristics of trustworthy AI integrated into org policies | ⚪ Boundary: org policy authorship |
| GV-1.3 | Processes, procedures, practices documented for risk management activities | 🟡 Partial: runbooks documented; org tailoring complete |
| GV-1.4 | Risk management process aligned with applicable standards | ⚪ Boundary: standards-alignment is org task |
| GV-1.5 | Ongoing monitoring + periodic review of risk mgmt process | 🟡 Partial: monitoring tuples; review cadence is org |
| GV-1.6 | Mechanisms in place to inventory AI systems + categorize by risk | ✅ AI-system inventory tuple + risk-classification field |
| GV-1.7 | Processes/procedures exist for decommissioning/phasing out AI systems | ✅ Decommission tuple + retention/erasure primitives |

### GOVERN 2 — Accountability structures (govern.2.1–2.3)

| ID | Subcategory | Coverage |
|---|---|---|
| GV-2.1 | Roles, responsibilities, lines of communication documented | 🟡 Partial: DCTX (delegation context) tuples document; org structure is task |
| GV-2.2 | Org's personnel + partners receive AI risk mgmt training | ⚪ Boundary: training program is org |
| GV-2.3 | Executive leadership responsible + accountable for decisions | ⚪ Boundary: org accountability |

### GOVERN 3 — Workforce diversity (govern.3.1–3.2)

| ID | Subcategory | Coverage |
|---|---|---|
| GV-3.1 | Decision-makers + workforce diversity considered | ⚪ Boundary: HR responsibility |
| GV-3.2 | Policies + procedures define impact of AI on human workforce | ⚪ Boundary: HR/workforce policy |

### GOVERN 4 — Org commitment to AI risk culture (govern.4.1–4.3)

| ID | Subcategory | Coverage |
|---|---|---|
| GV-4.1 | Org policies/practices in place fostering critical thinking, safety-first | ⚪ Boundary: culture |
| GV-4.2 | Org teams document risks/impacts they identify | ✅ Risk-register tuples + impact assessment |
| GV-4.3 | Org practices enable testing, incident response, recovery | ✅ Test framework + kill-switch + incident-response primitives |

### GOVERN 5 — Engagement with AI actors (govern.5.1–5.2)

| ID | Subcategory | Coverage |
|---|---|---|
| GV-5.1 | Org policies + practices for engagement with relevant AI actors | 🟡 Partial: actor-engagement tuples; engagement program is org |
| GV-5.2 | Mechanisms for receiving + integrating feedback from external groups | 🟡 Partial: feedback-intake tuples; external program is org |

### GOVERN 6 — Address risks from third-party software/data/AI (govern.6.1–6.2)

| ID | Subcategory | Coverage |
|---|---|---|
| GV-6.1 | Policies/procedures for risk inventories from third-party entities | 🟡 Partial: supplier-DCT tuples + SBOM; vendor mgmt program is org |
| GV-6.2 | Contingency processes for failures from third-party data/AI/services | ✅ Circuit-breaker + fallback primitives |

## MAP — Context, categorization, impact

### MAP 1 — Context establishment

| ID | Subcategory | Coverage |
|---|---|---|
| MP-1.1 | Intended purposes, potentially beneficial uses, context-specific laws, norms documented | ✅ INTENT tuple chain |
| MP-1.2 | Inter-disciplinary AI actors collaborate | ⚪ Boundary: team composition |
| MP-1.3 | Org's mission + relevant goals understood | ⚪ Boundary: org strategy |
| MP-1.4 | Business value clearly defined | ⚪ Boundary: business case |
| MP-1.5 | Org risk tolerances determined | ⚪ Boundary: risk-tolerance policy |
| MP-1.6 | System requirements (cost-benefit) elicited from stakeholders | 🟡 Partial: requirements tuples; stakeholder engagement is org |

### MAP 2 — Categorization

| ID | Subcategory | Coverage |
|---|---|---|
| MP-2.1 | AI system task + method specifically defined | ✅ AI-system tuple with task/method fields |
| MP-2.2 | Information needs to AI system (data, infrastructure, knowledge) documented | ✅ Information-need tuple |
| MP-2.3 | Scientific integrity + technical-rigor considerations identified + documented | 🟡 Partial: scientific-integrity tuples; review practice is org |

### MAP 3 — AI capabilities/usage/goals

| ID | Subcategory | Coverage |
|---|---|---|
| MP-3.1 | Benefits assessed; system-task-method comparison documented | 🟡 Partial: comparison tuples; assessment is org judgment |
| MP-3.2 | Likelihood/magnitude of each adverse impact identified | 🟡 Partial: impact-likelihood tuple type; assessment is org |
| MP-3.3 | Targeted application scope specified + documented based on context-relevant constraints | ✅ Scope tuple + DCT scope binding |
| MP-3.4 | Processes for operator + practitioner proficiency defined | ⚪ Boundary: org training |
| MP-3.5 | Processes for human oversight defined per system context | ✅ Human-in-loop DCT + kill-switch primitives |

### MAP 4 — Risks + benefits

| ID | Subcategory | Coverage |
|---|---|---|
| MP-4.1 | Approaches for mapping AI tech + legal risks documented | 🟡 Partial: risk-mapping tuples; legal mapping is org |
| MP-4.2 | Internal risk controls for components of AI system + third-party tech examined | ✅ Component risk tuple + supplier-DCT |

### MAP 5 — Impacts on individuals/groups/society

| ID | Subcategory | Coverage |
|---|---|---|
| MP-5.1 | Likelihood + magnitude of each negative impact (intentional/unintentional) examined | 🟡 Partial: negative-impact tuple; assessment is org |
| MP-5.2 | Practices + personnel for human-AI configurations defined | 🟡 Partial: config tuples; staffing is org |

## MEASURE — Measurement infrastructure

### MEASURE 1 — Appropriate methods, metrics identified + applied

| ID | Subcategory | Coverage |
|---|---|---|
| MS-1.1 | Approaches + metrics for measurement identified | ✅ Metric-registry tuple + measurement-plan tuple |
| MS-1.2 | Appropriate evaluation tools/methods selected | ✅ Evaluation-method tuple + test-framework |
| MS-1.3 | Internal experts review evaluations | 🟡 Partial: review tuples; expert engagement is org |

### MEASURE 2 — AI systems evaluated for trustworthy characteristics

| ID | Subcategory | Coverage |
|---|---|---|
| MS-2.1 | Test sets, metrics, performance details documented | ✅ Test-set tuple + metric tuples |
| MS-2.2 | Evaluations involving human subjects meet applicable requirements | 🟡 Partial: consent tuples; IRB is org |
| MS-2.3 | AI system performance/assurance evaluated regularly | ✅ Regular-evaluation tuples + CI integration |
| MS-2.4 | Deployment-context-relevant performance evaluations performed | ✅ Deployment-context tuple + per-context metrics |
| MS-2.5 | AI system valid + reliable, capability demonstrated | ✅ Validity-evidence tuples + 927-test corpus |
| MS-2.6 | AI system safety risks evaluated + documented | ✅ Safety-eval tuple + redteam-result tuple |
| MS-2.7 | AI system security + resilience evaluated + documented | ✅ Security-eval tuple + pen-test integration |
| MS-2.8 | Risks associated with transparency + accountability examined + documented | ✅ Transparency-eval tuple + accountability-chain audit |
| MS-2.9 | AI model explained; identifications of model + behavior | 🟡 Partial: explanation tuples; explainability technique is system-dependent |
| MS-2.10 | Privacy risk of AI system examined + documented | ✅ Privacy-risk tuple (cross-ref GDPR matrix) |
| MS-2.11 | Fairness + bias evaluated, documented + informed by input | 🟡 Partial: fairness-eval tuple; evaluation methodology is org choice |
| MS-2.12 | Environmental impact + sustainability evaluated + documented | 🟡 Partial: compute-cost tuple; environmental program is org |
| MS-2.13 | Mechanisms in place to assess effectiveness | ✅ Effectiveness-assessment tuple |

### MEASURE 3 — Mechanisms for tracking AI risk + impact

| ID | Subcategory | Coverage |
|---|---|---|
| MS-3.1 | Approaches/procedures for identifying AI risks documented | ✅ Risk-identification runbook + tuple types |
| MS-3.2 | Risk-tracking approaches considered for emergent risks | ✅ Emergent-risk tuple + monitoring primitives |
| MS-3.3 | Feedback processes for end-users + impacted communities documented | 🟡 Partial: feedback tuples; community-engagement program is org |

### MEASURE 4 — Feedback informs measurement

| ID | Subcategory | Coverage |
|---|---|---|
| MS-4.1 | Measurement approaches reviewed regularly to ensure effectiveness | 🟡 Partial: review tuples; review-cadence is org policy |
| MS-4.2 | Measurement results assessed for validity, reliability, relevance | 🟡 Partial: validity-assessment tuple; expert judgment is org |
| MS-4.3 | Measurable performance improvements detected via feedback | ✅ Improvement-detection tuple |

## MANAGE — Risks prioritized + acted upon

### MANAGE 1 — Risks prioritized + acted upon

| ID | Subcategory | Coverage |
|---|---|---|
| MG-1.1 | Purpose + applicability of AI system reassessed; design assumptions held | ✅ Design-reassessment tuple + lifecycle reviews |
| MG-1.2 | Treatment of risks based on impact + likelihood | ✅ Risk-treatment tuple + priority field |
| MG-1.3 | Responses to highest-priority risks developed/planned/documented | ✅ Response-plan tuple |
| MG-1.4 | Negative residual risks documented | ✅ Residual-risk tuple |

### MANAGE 2 — Strategies maximizing benefits, minimizing negatives

| ID | Subcategory | Coverage |
|---|---|---|
| MG-2.1 | Resources for managing risks allocated, regularly updated | 🟡 Partial: resource-allocation tuples; budget is org |
| MG-2.2 | Mechanisms in place + applied to sustain AI system value | 🟡 Partial: monitoring + improvement primitives; value-mgmt is org |
| MG-2.3 | Procedures in place + followed for system-replacement decisions | ✅ Replacement-decision tuple + decommission primitives |
| MG-2.4 | Procedures in place + followed to respond + recover from previously unknown risks | ✅ Unknown-risk-response tuple + kill-switch escalation |

### MANAGE 3 — Risks from third-party entities managed

| ID | Subcategory | Coverage |
|---|---|---|
| MG-3.1 | Risks tracked for third-party data + tools + AI | ✅ Third-party-risk tuple + supplier-DCT |
| MG-3.2 | Pre-trained models reviewed for risks before deployment | 🟡 Partial: model-review tuple; review practice is org |

### MANAGE 4 — Risk treatments + responses monitored

| ID | Subcategory | Coverage |
|---|---|---|
| MG-4.1 | Mechanisms in place to monitor risk treatment effectiveness | ✅ Treatment-monitoring tuple |
| MG-4.2 | Measurable activities tracked for unexpected negative impacts | ✅ Negative-impact monitoring tuple |
| MG-4.3 | Incidents + errors communicated, with explanations + remediation | ✅ Incident-comm tuple + remediation tracking |

---

## Draft coverage summary (not public claim)

This matrix is internal starter material. It must not be used as public evidence that HUMMBL fulfills this framework until row counts, evidence commands, artifact paths, and boundary classifications are validated.

## Cross-references

- ADR: [`docs/adr/ADR-001-coverage-matrix-not-self-grade.md`](../adr/ADR-001-coverage-matrix-not-self-grade.md)
- Prior partial mapping: `docs/nist-rmf-mapping.md`
- EU AI Act overlaps significantly with MEASURE + MANAGE — see [`eu-ai-act.md`](./eu-ai-act.md) Section 2
- NIST CSF 2.0 (cybersecurity framework) covered separately in [`nist-csf.md`](./nist-csf.md)
