# AI Framework Taxonomy v0.1

**Status:** DRAFT — requires verification before canonical promotion
**Origin:** External research artifact (ChatGPT synthesis), ingested 2026-07-14
**Steward:** HUMMBL Research Institute
**Verification state:** UNVERIFIED — claims, citations, and HUMMBL mappings need source-checking against canonical framework documentation before any coverage-matrix or doctrinal use
**Companion artifact:** `docs/research/ai-governance-framework-inventory.md` (498 frameworks catalogued)

---

## Verification Checklist (before promotion)

- [x] Each of the 26 framework families maps to at least one framework in the inventory (see coverage analysis below)
- [x] No phantom citations — spot-checked OECD AIM, C2PA, MITRE ATLAS (all live and accurately characterized)
- [ ] All 17 cited sources reachable and accurately characterized (3 spot-checked; 14 remaining)
- [ ] HUMMBL translations reviewed against current primitive set (25 primitives)
- [ ] Proposed YAML object model validated against `contracts/` schema conventions
- [ ] L-1 Admission layer cross-checked against existing `capability_fence` and `identity` primitives
- [ ] Stack view (L0–L10) reconciled with HUMMBL dependency-tier taxonomy (Tier 0–4)
- [ ] Sector-specific framework examples verified against current regulator publications

### Coverage analysis (taxonomy vs. inventory)

Cross-reference of the 26 taxonomy families against the 498-framework inventory. PASS = at least 3 representative frameworks; GAP = fewer than 3; CRITICAL GAP = zero.

| Family # | Family Name | Inventory IDs (sample) | Count | Status |
|---|---|---|---|---|
| 1 | Concept / terminology | 84, 352 | 2 | GAP |
| 2 | AI system-description | 85, 87 | 2 | GAP |
| 3 | Lifecycle | 86, 100, 187, 346 | 4 | PASS |
| 4 | Ethics / principles | 158, 159, 161, 238-244, 253-256, 431-433, 475-480 | 26 | PASS |
| 5 | Human-rights | 157, 221-223 | 3 | PASS |
| 6 | Regulatory | 1, 15-90, 267-318, 319-337 | ~130 | PASS |
| 7 | Compliance | 3, 5, 7, 408-412, 482 | 5 | PASS |
| 8 | Governance | 6, 98, 104, 130-152, 368-374, 448-458, 472-475, 497-498 | ~40 | PASS |
| 9 | Management-system | 6, 361 | 2 | GAP |
| 10 | Risk-management | 3, 97, 163, 188, 191, 199-201, 406-407, 450-451, 454 | 13 | PASS |
| 11 | Assurance / audit | 249-252, 258, 279, 410, 411, 459-465, 481 | 11 | PASS |
| 12 | Evaluation / benchmark | 92-94, 113, 117-118, 120-121, 122, 124-125, 129, 337, 339, 340, 347-350, 355, 357-367, 488-496 | 35 | PASS |
| 13 | Red-team / adversarial-testing | 8, 14, 164, 205-207, 379, 418-422 | 8 | PASS |
| 14 | Security | 4, 166, 167, 170-172, 338, 353-354, 356, 375-380 | 11 | PASS |
| 15 | Safety / alignment | 168, 169, 245-248, 263-266, 431, 450-451, 454 | 10 | PASS |
| 16 | Agentic AI | 11, 14, 128, 426-428, 470-471, 474-475 | 7 | PASS |
| 17 | Data governance | 95, 173-181, 381-383, 498 | 12 | PASS |
| 18 | Data quality | 95, 91-92, 362-366 | 6 | PASS |
| 19 | Documentation / transparency | 18, 19, 208-212, 88, 355, 381 | 8 | PASS |
| 20 | Privacy | 2, 29, 173-181, 381-383 | 12 | PASS |
| 21 | Human oversight / UX | 254, 290, 323-325, 343, 348, 384-387, 397-399, 442-447 | 15 | PASS |
| 22 | Content provenance / synthetic media | 18, 25, 217-218, 265, 266, 285, 289-292, 295, 302, 304, 309, 395-396 | 15 | PASS |
| 23 | Procurement / vendor-risk | 413-417, 197, 198 | 7 | PASS |
| 24 | Incident-response | 202-204, 289, 344, 314, 418 | 6 | PASS |
| 25 | Sector-specific | 182-198, 262-278, 384-405 | 39 | PASS |
| 26 | Maturity / capability | 261, 488-496, 130-152, 368-374 | 25 | PASS |

**Summary:** 23 of 26 families PASS (≥3 frameworks). 3 GAP: concept/terminology (2), system-description (2), management-system (2). 0 CRITICAL GAP. All 498 inventory frameworks map to at least one family.

### L-1 Admission layer analysis

**Status:** No dedicated admission frameworks found in the inventory. Procurement (family 23) and governance approval gates (family 8) touch admission-adjacent concepts, but no framework is explicitly focused on "admission" as a distinct pre-governance layer. This confirms the taxonomy's thesis that admission is the most under-specified control surface in the current AI framework landscape — and the gap HUMMBL is positioned to fill.

---

## Premise

AI frameworks should be treated as a **taxonomy of control systems**, not a simple list of "governance vs compliance."

### Core taxonomic definition

An **AI framework** is a structured way to define, constrain, evaluate, operate, or evidence some aspect of an AI system, AI organization, AI use case, AI model, AI agent, AI dataset, or AI-mediated decision.

The root object is:

> **AI Framework = bounded structure for AI authority, obligation, risk, design, operation, evaluation, assurance, or evidence.**

Compliance and governance are only two branches.

---

## 0. Meta-taxonomic frameworks

These define the language and conceptual model used by all other frameworks.

| Subtype | Purpose | Example artifacts |
|---|---|---|
| **Terminology frameworks** | Define shared vocabulary: AI system, model, data, actor, lifecycle, risk, trustworthiness | Glossary, ontology, term registry |
| **System-description frameworks** | Describe what an AI system is made of | system boundary, components, interfaces, dependency map |
| **Lifecycle frameworks** | Define stages from conception to retirement | lifecycle map, phase gates, change-control record |

Examples include ISO/IEC 22989 for AI concepts and terminology, ISO/IEC 23053 for describing ML-based AI systems, and ISO/IEC 5338 for AI system lifecycle processes. ([ISO][1])

**HUMMBL translation:** this is the **grammar layer**. Before governance, risk, or compliance, the system needs names for objects, actors, authority, evidence, gates, and state.

---

## 1. Principles / ethics frameworks

These define what AI should respect.

| Subtype | Core question |
|---|---|
| **Responsible AI principles** | What values must guide development and deployment? |
| **Human-rights frameworks** | How does AI affect rights, dignity, autonomy, and due process? |
| **Fairness frameworks** | How are bias, disparate impact, and allocative harms managed? |
| **Transparency principles** | What must users, affected parties, operators, or regulators know? |
| **Accountability principles** | Who is responsible when AI causes harm? |

Examples: OECD AI Principles, Microsoft Responsible AI principles, corporate responsible AI standards. OECD's AI Principles focus on trustworthy AI that respects human rights and democratic values. ([OECD][2])

**Failure mode:** principles become decorative if not mapped to controls, owners, evidence, and gates.

---

## 2. Regulatory frameworks

These define what law or public authority requires.

| Subtype | Core question |
|---|---|
| **Horizontal AI regulation** | What applies across sectors? |
| **Risk-class regulation** | Is the system prohibited, high-risk, limited-risk, or low-risk? |
| **Sector regulation** | What rules apply in healthcare, finance, defense, education, employment, etc.? |
| **Consumer-protection regulation** | Are claims deceptive, discriminatory, unsafe, or unfair? |
| **Data-protection regulation** | Does the system process personal, sensitive, biometric, or protected data? |

The EU AI Act is a risk-based regulatory framework with levels including unacceptable risk, high risk, limited risk, and minimal/no risk. ([Digital Strategy EU][3])

**HUMMBL translation:** regulatory frameworks define **external authority constraints**. They are not the whole governance system, but they can impose hard gates.

---

## 3. Compliance frameworks

These define how obligations are mapped, tested, and evidenced.

| Subtype | Core question |
|---|---|
| **Control-mapping frameworks** | Which controls satisfy which obligations? |
| **Audit-readiness frameworks** | What evidence must be retained? |
| **Policy-conformance frameworks** | Are teams following internal AI policy? |
| **Regulatory-compliance frameworks** | Are legal duties satisfied? |
| **Contractual-compliance frameworks** | Are vendor, customer, or partner AI obligations satisfied? |

Typical artifacts: control matrix, policy map, evidence ledger, audit packet, exception log, compliance attestation.

**HUMMBL translation:** compliance is **obligation-conformance evidence**.

---

## 4. Governance frameworks

These define authority, decision rights, supervision, and accountability.

| Subtype | Core question |
|---|---|
| **Enterprise AI governance** | Who owns AI strategy, risk, review, and approval? |
| **Use-case governance** | Which AI use cases are allowed? |
| **Model governance** | Who may train, deploy, modify, retire, or override models? |
| **Data governance** | Who may use what data, for what purpose, under what conditions? |
| **Agent governance** | Who may delegate authority to AI agents? |
| **Board / executive governance** | What rises to leadership review? |
| **Exception governance** | Who can waive a rule, and how is that waiver receipted? |

Typical artifacts: AI policy, approval board, RACI, decision ledger, risk acceptance memo, exception register, authority matrix, model inventory, agent registry.

**HUMMBL translation:** governance is **authority-bound state control**.

---

## 5. Management-system frameworks

These define the organizational operating system for AI.

| Subtype | Core question |
|---|---|
| **AI management system** | How does the organization systematically manage AI? |
| **Continuous-improvement framework** | How are policies reviewed and improved? |
| **Organizational accountability framework** | Are roles, objectives, audits, reviews, and corrective actions defined? |
| **Integrated management framework** | How does AI management connect to security, privacy, quality, and risk? |

ISO/IEC 42001 is an AI management system standard for organizations developing, providing, or using AI systems; it specifies requirements and guidance for establishing, maintaining, and improving an AI management system. ([ISO][4])

**Distinction:** governance decides authority. A management system institutionalizes it.

---

## 6. Risk-management frameworks

These define how AI risk is identified, measured, treated, monitored, and accepted.

| Subtype | Risk focus |
|---|---|
| **Enterprise AI risk** | Organizational, legal, financial, reputational, operational |
| **Model risk** | Invalid outputs, drift, instability, overfitting, poor validation |
| **Human-impact risk** | Harm to users, workers, customers, patients, citizens |
| **Societal risk** | Misinformation, discrimination, labor displacement, institutional trust |
| **Safety risk** | Physical, medical, infrastructure, or catastrophic harm |
| **Security risk** | Abuse, attack, compromise, exfiltration |
| **Residual-risk framework** | What risk remains after controls? |

NIST AI RMF is organized around Govern, Map, Measure, and Manage functions, while ISO/IEC 23894 provides AI-specific risk-management guidance. ([NIST AI Resource Center][5])

**HUMMBL translation:** risk frameworks answer: **what can go wrong, how bad is it, what gates reduce it, and who accepts the remainder?**

---

## 7. Assurance / audit frameworks

These define how claims about AI systems are verified.

| Subtype | Core question |
|---|---|
| **Internal assurance** | Can the organization prove its own claims? |
| **Third-party assurance** | Can an independent party verify trustworthiness? |
| **Certification frameworks** | Can a system or organization be certified against a standard? |
| **Conformity assessment** | Does the system conform to specified requirements? |
| **Audit frameworks** | Is the evidence sufficient, traceable, and reliable? |
| **AI testing frameworks** | Has the model/system been tested against claimed properties? |

AI Verify is an AI governance testing framework and toolkit for assessing responsible AI implementation against recognized governance principles. The UK has also been developing a third-party AI assurance ecosystem. ([AI Verify Foundation][6])

**HUMMBL translation:** assurance is **claim-verification infrastructure**.

---

## 8. Evaluation frameworks

These define how AI performance and behavior are measured.

| Subtype | Evaluates |
|---|---|
| **Capability evals** | What can the model/system do? |
| **Task-performance evals** | Does it perform the intended task? |
| **Reliability evals** | How often does it fail? |
| **Robustness evals** | Does performance hold under perturbation? |
| **Fairness evals** | Does performance differ across groups or contexts? |
| **Safety evals** | Does it produce harmful behavior? |
| **Regression evals** | Did a change make behavior worse? |
| **Agent evals** | Does the agent plan, call tools, recover, stop, and obey boundaries? |
| **Human-centered evals** | Does the system help real users in real workflows? |

Typical artifacts: benchmark suite, test harness, red-team report, eval receipt, acceptance threshold, regression dashboard.

**Failure mode:** benchmark pass != real-world safety. Evals need context, use-case fit, and operational monitoring.

---

## 9. Red-team / adversarial-testing frameworks

These define how to actively attack or stress-test AI systems.

| Subtype | Tests for |
|---|---|
| **Jailbreak testing** | Can safety instructions be bypassed? |
| **Prompt-injection testing** | Can untrusted content override developer/system intent? |
| **Data-exfiltration testing** | Can secrets or personal data leak? |
| **Tool-abuse testing** | Can the AI misuse APIs, browsers, shells, email, payments, or files? |
| **Autonomy stress testing** | Does the system overreach, loop, deceive, or self-delegate? |
| **Misuse testing** | Can users repurpose the system for harm? |

OWASP's LLM Top 10 identifies major LLM application risks, including prompt injection and sensitive information disclosure. ([OWASP Foundation][7])

**HUMMBL translation:** red-team frameworks are **adversarial gate generators**.

---

## 10. Security frameworks

These define how AI systems are protected against attack.

| Subtype | Security surface |
|---|---|
| **AI application security** | LLM apps, RAG, tools, plugins, APIs |
| **Model security** | model theft, extraction, inversion, tampering |
| **Data security** | poisoning, leakage, unauthorized training use |
| **Prompt/context security** | prompt injection, context poisoning, instruction hierarchy failure |
| **Supply-chain security** | third-party models, weights, dependencies, datasets, eval tools |
| **Runtime security** | sandboxing, access control, monitoring, rate limits |
| **Agent security** | delegated credentials, tool authority, multi-agent trust boundaries |

MITRE ATLAS is a living knowledge base of adversary tactics and techniques against AI systems. Google's Secure AI Framework is a security/privacy-oriented framework for ML-powered applications. ([MITRE ATLAS][8])

**HUMMBL translation:** security frameworks protect **integrity, confidentiality, availability, and authority boundaries**.

---

## 11. Agentic AI frameworks

These are distinct from generic AI frameworks because agents act, delegate, call tools, mutate state, and interact with other systems.

| Subtype | Core question |
|---|---|
| **Agent admission frameworks** | Should this agent be allowed to exist or act? |
| **Tool-use governance** | What tools may it call, under what authority? |
| **Delegation frameworks** | Can one agent assign work to another? |
| **Agent identity / IAM frameworks** | Does each agent have a distinct, bounded identity? |
| **Multi-agent coordination frameworks** | How do agents negotiate, escalate, and resolve conflicts? |
| **Runtime supervision frameworks** | What monitors agent behavior during execution? |
| **Reversibility frameworks** | Can agent actions be rolled back? |
| **Agent incident frameworks** | What logs are needed when an agent causes harm? |

OWASP has a dedicated Agentic AI threats and mitigations effort, and Cloud Security Alliance's MAESTRO is a threat-modeling framework for agentic AI and multi-agent systems. ([OWASP Gen AI Security Project][9])

**HUMMBL translation:** this is where the HUMMBL invariant becomes central:

> No durable state without admission, authority, executor, and receipt.

---

## 12. Data governance / data quality frameworks

These define whether data is usable, lawful, representative, high-quality, and traceable.

| Subtype | Core question |
|---|---|
| **Data provenance frameworks** | Where did the data come from? |
| **Data rights frameworks** | Can this data be used for this purpose? |
| **Consent frameworks** | Did data subjects authorize this use? |
| **Data quality frameworks** | Is the data accurate, complete, current, representative, labeled, and fit-for-purpose? |
| **Dataset documentation frameworks** | What should be known about the dataset? |
| **Data retention frameworks** | How long may data be kept? |
| **Data deletion frameworks** | Can it be removed from systems, indexes, memory, or training pipelines? |
| **Synthetic-data frameworks** | How are generated datasets labeled, validated, and bounded? |

ISO/IEC 5259 addresses data quality for analytics and machine learning, and "Datasheets for Datasets" proposed standardized dataset documentation covering motivation, composition, collection, and recommended uses. ([ISO][10])

**Failure mode:** model governance without data governance is structurally weak.

---

## 13. Documentation / transparency frameworks

These define what must be disclosed about AI systems.

| Subtype | Documents |
|---|---|
| **Model cards** | model purpose, limits, performance, evals, intended use |
| **Dataset datasheets** | dataset origin, composition, collection, limits |
| **System cards** | system-level behavior, mitigations, policies |
| **AI factsheets** | lifecycle metadata, lineage, criticality, model/service details |
| **User-facing disclosures** | when users interact with AI or receive AI-generated output |
| **Regulator-facing documentation** | technical files, risk reports, compliance evidence |
| **Internal decision records** | approvals, risk acceptance, exceptions, gates |

Model cards were introduced as short documents accompanying trained ML models with benchmarked evaluation in varied conditions; IBM AI Factsheets capture model details and lifecycle metadata for governance and compliance. ([ACM Digital Library][11])

**HUMMBL translation:** documentation frameworks produce **readable receipts**.

---

## 14. MLOps / LLMOps / operational frameworks

These define how AI systems are built, deployed, monitored, changed, and retired.

| Subtype | Controls |
|---|---|
| **Model registry frameworks** | version, owner, status, approval, lineage |
| **Pipeline frameworks** | training, fine-tuning, eval, deployment |
| **Deployment frameworks** | staging, canary, rollback, approval gates |
| **Monitoring frameworks** | drift, latency, cost, error rate, unsafe output |
| **Observability frameworks** | traces, prompts, completions, tool calls, embeddings, retrieval |
| **Change-management frameworks** | what happens when model, prompt, data, or tool changes? |
| **Retirement frameworks** | when is a model deprecated, disabled, or replaced? |

ISO/IEC 5338 is relevant here because it defines AI system lifecycle processes. ([ISO][12])

**HUMMBL translation:** operational frameworks manage **runtime state and lifecycle receipts**.

---

## 15. Safety / alignment / frontier-risk frameworks

These define how severe or catastrophic AI risks are identified and constrained.

| Subtype | Core question |
|---|---|
| **Capability-threshold frameworks** | What capabilities trigger higher controls? |
| **Responsible-scaling frameworks** | When should development/deployment slow, pause, or escalate? |
| **Preparedness frameworks** | What severe harms must be tracked before deployment? |
| **Misuse-risk frameworks** | Can the system enable bio, cyber, chemical, persuasion, or weapons misuse? |
| **Autonomy-risk frameworks** | Can it plan, replicate, evade oversight, or resist shutdown? |
| **Loss-of-control frameworks** | What if the system behaves outside intended control? |

OpenAI's Preparedness Framework tracks frontier capabilities that could create severe harm, while Anthropic's Responsible Scaling Policy is a voluntary framework for catastrophic-risk mitigation. ([OpenAI CDN][13])

**Failure mode:** safety frameworks can look strong but still fail if thresholds, stop rules, authority, and independent verification are weak.

---

## 16. Privacy frameworks

These define how AI handles personal, sensitive, confidential, or inferable information.

| Subtype | Core question |
|---|---|
| **Privacy-by-design frameworks** | Is privacy built into the system architecture? |
| **Data-minimization frameworks** | Is the system using only necessary data? |
| **Purpose-limitation frameworks** | Is data used only for declared purposes? |
| **Inference-risk frameworks** | Can AI infer sensitive facts from nonsensitive data? |
| **Memorization frameworks** | Did the model memorize personal or confidential data? |
| **Deletion / unlearning frameworks** | Can data be removed or its influence reduced? |
| **Privacy-impact assessment frameworks** | What privacy harms could occur? |

**HUMMBL translation:** privacy frameworks govern **data authority, personhood boundaries, and inference risk**.

---

## 17. Human oversight / human factors frameworks

These define how humans interact with, supervise, contest, and override AI.

| Subtype | Core question |
|---|---|
| **Human-in-the-loop frameworks** | When must a human approve or intervene? |
| **Human-on-the-loop frameworks** | When can a human supervise without approving every action? |
| **Human-out-of-the-loop frameworks** | When is automation allowed without live review? |
| **Contestability frameworks** | Can affected people challenge AI decisions? |
| **UX frameworks** | Does the interface help users understand AI uncertainty and limits? |
| **Cognitive-load frameworks** | Are humans overloaded with meaningless approvals? |
| **Automation-bias frameworks** | Are humans over-trusting AI? |

Google's People + AI Guidebook provides UX and ML guidance for creating useful AI-enabled products. ([Pair][14])

**Failure mode:** "human review" can be fake governance if the reviewer lacks time, authority, information, or ability to override.

---

## 18. Content provenance / synthetic media frameworks

These define how AI-generated or AI-modified content is labeled, authenticated, traced, and governed.

| Subtype | Core question |
|---|---|
| **Provenance frameworks** | Where did the content come from? |
| **Watermarking frameworks** | Can synthetic content be marked? |
| **Disclosure frameworks** | Must users be told content is AI-generated? |
| **Authenticity frameworks** | Can origin and edits be verified? |
| **Synthetic-media governance** | What rules govern deepfakes, voice clones, avatars, and generated media? |
| **IP / copyright frameworks** | What rights apply to training data, outputs, likeness, style, and derivative works? |

C2PA provides an open technical standard for establishing the origin and edits of digital content through Content Credentials, and Partnership on AI's Responsible Practices for Synthetic Media provides recommendations for responsible synthetic media development and deployment. ([C2PA][15])

**HUMMBL translation:** provenance frameworks are **receipt systems for media objects**.

---

## 19. Procurement / vendor-risk frameworks

These define how organizations evaluate third-party AI.

| Subtype | Core question |
|---|---|
| **Vendor due diligence** | Who built it, and can they be trusted? |
| **Model-provider risk** | What are the provider's data, security, and safety practices? |
| **Contractual AI controls** | What warranties, audit rights, indemnities, and SLAs exist? |
| **Third-party model assessment** | Can the buyer evaluate model behavior independently? |
| **Subprocessor / data-flow review** | Where does data go? |
| **Exit / portability frameworks** | Can the buyer leave the vendor safely? |

Typical artifacts: vendor AI questionnaire, contract rider, data-processing addendum, model card, SOC report, security review, DPIA, exit plan.

**Failure mode:** outsourcing AI does not outsource accountability.

---

## 20. Incident-response frameworks

These define what happens when AI fails or causes harm.

| Subtype | Core question |
|---|---|
| **AI incident classification** | What counts as an incident, near miss, or hazard? |
| **Severity frameworks** | How bad is it? |
| **Containment frameworks** | How do we stop further harm? |
| **Rollback frameworks** | Can model, prompt, data, tool, or agent state be reverted? |
| **Notification frameworks** | Who must be told: users, regulators, customers, executives? |
| **Post-incident review** | What caused it, and what gates change? |
| **Learning systems** | How are incidents aggregated into better controls? |

The OECD AI Incidents and Hazards Monitor documents AI incidents and hazards to support evidence-based policy and practice; the AI Incident Database similarly indexes real-world harms or near harms from deployed AI systems. ([OECD.AI][16])

**HUMMBL translation:** incident frameworks define **failure receipts and remediation loops**.

---

## 21. Sector-specific frameworks

These adapt AI controls to specific domains.

| Sector | Framework focus |
|---|---|
| **Healthcare / medical devices** | safety, clinical validation, FDA submissions, total product lifecycle |
| **Finance / banking** | model risk, explainability, fairness, credit/lending, fraud, auditability |
| **Defense / national security** | lawful use, command authority, reliability, traceability, escalation |
| **Education** | student privacy, assessment integrity, equity, teacher oversight |
| **Employment / HR** | hiring bias, transparency, adverse impact, contestability |
| **Insurance** | underwriting fairness, explainability, actuarial governance |
| **Critical infrastructure** | resilience, safety, cybersecurity, fail-safe operation |
| **Legal services** | confidentiality, unauthorized practice, citation reliability |
| **Media / journalism** | provenance, authenticity, editorial accountability |
| **Biotech / biosecurity** | dual-use screening, lab automation risk, sequence/data governance |

FDA's AI-enabled medical device guidance focuses on lifecycle management and marketing submission recommendations for AI-enabled device software functions, while U.S. banking regulators maintain model-risk-management guidance for financial institutions. ([U.S. Food and Drug Administration][17])

**Failure mode:** generic AI governance is insufficient for high-consequence sectors.

---

## 22. Maturity / capability frameworks

These define how advanced an organization is at managing AI.

| Level | Typical state |
|---|---|
| **Ad hoc** | no inventory, informal approvals, no evidence |
| **Documented** | policies exist, but weak enforcement |
| **Managed** | owners, controls, inventories, review gates |
| **Measured** | metrics, evals, audits, incident learning |
| **Adaptive** | continuous monitoring, dynamic controls, risk-based escalation |
| **Governed / receipted** | authority, gates, execution, evidence, and state change are linked |

Typical artifacts: maturity model, capability assessment, roadmap, gap analysis, remediation backlog.

**HUMMBL translation:** maturity frameworks measure **governance capability over time**.

---

## The stack view

The taxonomy above can also be compressed into a stack:

| Layer | Name | Controls |
|---|---|---|
| L0 | **Concept / taxonomy** | terms, object model, system boundary |
| L1 | **Principles** | values, ethics, human rights |
| L2 | **Law / regulation** | external obligations |
| L3 | **Governance** | authority, decision rights, accountability |
| L4 | **Risk** | risk identification, scoring, treatment, acceptance |
| L5 | **Compliance** | control mapping, evidence, audit readiness |
| L6 | **Assurance** | independent verification, testing, certification |
| L7 | **Engineering / lifecycle** | build, deploy, monitor, change, retire |
| L8 | **Security / safety** | adversarial resilience, misuse prevention, harm controls |
| L9 | **Operations / incident** | runtime monitoring, rollback, incident response |
| L10 | **Receipts / provenance** | durable evidence, lineage, traceability |

For HUMMBL/BaseN, one layer before everything else:

| Layer | Name | Meaning |
|---|---|---|
| L-1 | **Admission** | decides whether an AI use case, model, agent, tool, memory, dataset, or durable state transition is allowed to enter the system at all |

That is the layer most existing frameworks under-specify.

---

## Clean distinction among the main branches

### Compliance framework
> Proves required obligations were followed.
Example output: audit evidence, control matrix, attestation.

### Governance framework
> Defines authority, ownership, approval, supervision, escalation, and accountability.
Example output: decision ledger, authority matrix, approval gate.

### Risk framework
> Identifies what can go wrong and how risk is treated.
Example output: risk register, residual-risk memo, mitigation plan.

### Assurance framework
> Verifies whether claims about the AI system are true.
Example output: independent test report, eval receipt, certification.

### Operational framework
> Runs and monitors the system through its lifecycle.
Example output: deployment pipeline, model registry, rollback plan.

### Safety framework
> Prevents severe harm, misuse, autonomy failure, or loss of control.
Example output: capability thresholds, red-team results, stop conditions.

### Security framework
> Protects the AI system from adversarial compromise.
Example output: threat model, access-control plan, prompt-injection defenses.

### Admission framework
> Decides whether something may become durable system state.
Example output: admission packet, authority record, gate result, receipt.

---

## Proposed HUMMBL object model

For HUMMBL purposes, each framework should be represented as a governed object:

```yaml
ai_framework:
  id: string
  name: string
  family:
    - governance | compliance | risk | assurance | safety | security | lifecycle | data | agentic | sector | incident | provenance
  scope:
    - organization | use_case | system | model | dataset | agent | tool | output | incident | vendor
  authority_source:
    - law | regulator | standard | internal_policy | contract | operator | community_norm
  lifecycle_phase:
    - admission | design | build | test | deploy | monitor | change | incident | retire
  primary_question: string
  required_artifacts:
    - policy
    - register
    - risk_assessment
    - eval_report
    - decision_record
    - audit_evidence
    - incident_report
    - receipt
  gates:
    - gate_id
    - gate_name
    - pass_condition
    - evidence_required
  residual_risk:
    owner: string
    accepted_by: string
    review_date: date
  receipts:
    - receipt_id
    - timestamp
    - authority
    - executor
    - evidence_hash
```

**Verification note:** This YAML schema is a PROPOSAL. It must be validated against `contracts/` schema conventions and the existing `hummbl.repo.yaml` registry format before any tooling consumes it.

---

## The exhaustive top-level map

The full taxonomy includes at least these **26 AI framework families**:

1. Concept / terminology frameworks
2. AI system-description frameworks
3. Lifecycle frameworks
4. Ethics / principles frameworks
5. Human-rights frameworks
6. Regulatory frameworks
7. Compliance frameworks
8. Governance frameworks
9. Management-system frameworks
10. Risk-management frameworks
11. Assurance / audit frameworks
12. Evaluation / benchmark frameworks
13. Red-team / adversarial-testing frameworks
14. Security frameworks
15. Safety / alignment frameworks
16. Agentic AI frameworks
17. Data governance frameworks
18. Data quality frameworks
19. Documentation / transparency frameworks
20. Privacy frameworks
21. Human oversight / UX frameworks
22. Content provenance / synthetic media frameworks
23. Procurement / vendor-risk frameworks
24. Incident-response frameworks
25. Sector-specific frameworks
26. Maturity / capability frameworks

---

## Conclusion

AI frameworks should be taxonomized by the control surface they govern: authority, obligation, risk, evidence, system lifecycle, data, model behavior, agent action, human impact, security, safety, provenance, incident response, and sector constraints.

For HUMMBL, the missing category worth making explicit is:

> **Admission-Controlled AI Frameworks** — frameworks that decide what gets admitted into durable state before governance, compliance, or assurance even begin.

---

## References

[1]: https://www.iso.org/standard/74296.html "ISO/IEC 22989:2022 - Artificial intelligence"
[2]: https://www.oecd.org/en/topics/sub-issues/ai-principles.html "AI principles"
[3]: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai "AI Act | Shaping Europe's digital future - European Union"
[4]: https://www.iso.org/standard/42001 "ISO/IEC 42001:2023 - AI management systems"
[5]: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ "AI RMF Core - AIRC - NIST AI Resource Center"
[6]: https://aiverifyfoundation.sg/what-is-ai-verify/ "What is AI Verify"
[7]: https://owasp.org/www-project-top-10-for-large-language-model-applications/ "OWASP Top 10 for Large Language Model Applications"
[8]: https://atlas.mitre.org/ "MITRE ATLAS"
[9]: https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/ "Agentic AI - OWASP Lists Threats and Mitigations"
[10]: https://www.iso.org/standard/81088.html "ISO/IEC 5259-1:2024 - Artificial intelligence — Data quality"
[11]: https://dl.acm.org/doi/10.1145/3287560.3287596 "Model Cards for Model Reporting | Proceedings of the ..."
[12]: https://www.iso.org/standard/81118.html "ISO/IEC 5338:2023 - AI system life cycle processes"
[13]: https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf "Preparedness Framework"
[14]: https://pair.withgoogle.com/guidebook/ "People + AI Guidebook - Home"
[15]: https://c2pa.org/ "C2PA | Verifying Media Content Sources"
[16]: https://oecd.ai/en/incidents "AIM: AI Incidents and Hazards Monitor"
[17]: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/artificial-intelligence-enabled-device-software-functions-lifecycle-management-and-marketing "Artificial Intelligence-Enabled Device Software Functions"
