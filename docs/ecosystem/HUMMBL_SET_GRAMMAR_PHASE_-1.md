# HUMMBL Set Grammar — Phase -1 Admission

```yaml
phase: -1
name: HUMMBL Set Grammar Admission
status: PHASE_-1_OPEN
canon_level: candidate_only
date: 2026-06-25
promotion_allowed: false
next_phase: Phase 0 schema-seed design
primary_rule: "Nothing admitted here is canon yet. This phase collects, names,
  separates, and stress-tests candidate object families before schema or promotion."
```

> **Primary thesis:** HUMMBL needs a governed object grammar where Problem,
> Question, Claim, Evidence, Decision, Task, Prompt, Gate, Receipt, Artifact,
> Protocol, and Canon remain **distinct but composable**. Prompts are invocation
> artifacts, not sources of truth. Evidence grounds. Decisions authorize.
> Receipts attest. Canon is promoted governed knowledge.

---

## 1. Phase -1 Objective

> What reusable object types does HUMMBL need in order to govern interdisciplinary
> problems, questions, tasks, prompts, evidence, decisions, gates, and receipts
> without collapsing them into one vague "knowledge pack"?

This is an **admission/discovery phase**, not an implementation phase. The goal
is to prevent premature schema lock-in.

---

## 2. Core Finding

The original four object types are necessary but incomplete:

| Object   | Function                                                         |
|----------|------------------------------------------------------------------|
| Problem  | Names a gap, tension, harm, opportunity, or unresolved condition |
| Question | Converts problem-space into inquiry                              |
| Task     | Converts decision into execution                                 |
| Prompt   | Invokes a model/agent/tool                                       |

They cover inquiry and execution but lack governance, evidence, evaluation,
semantic, context, and output layers. Without those, prompts and tasks become
overloaded with governance responsibility they should not carry.

---

## 3. Form Distinction: Set vs Pack vs Registry vs Ledger vs Graph

| Form         | Meaning                                                              |
|--------------|----------------------------------------------------------------------|
| **Set**      | Curated group of related objects                                     |
| **Pack**     | Portable/use-ready bundle, usually for reuse or distribution         |
| **Registry** | Authoritative index of entities, capabilities, artifacts, or records |
| **Ledger**   | Chronological or decision-bearing record                             |
| **Library**  | Reusable patterns, templates, primitives, or procedures              |
| **Suite**    | Evaluation/test collection                                           |
| **Bundle**   | Receipt/evidence/document collection tied to a process               |
| **Graph**    | Network of entities and relationships                                |

> **Implication:** HUMMBL Problem Sets may not be enough. Interdisciplinary
> problem work likely needs **Problem Graphs** or **Problem Constellations**,
> because the problems intersect, depend on, amplify, and constrain each other.

---

## 4. Candidate Top-Level Object Families

### A. Inquiry Objects

| Object              | Function                                              |
|---------------------|-------------------------------------------------------|
| Problem Set         | Group related problems                                |
| Problem Graph       | Interdisciplinary, mutually entangled problems        |
| Question Set        | Organize inquiry                                      |
| Hypothesis Set      | Possible explanations or solution theories            |
| Claim Set           | Answers are made of claims — mandatory                |
| Assumption Set      | Prevent hidden beliefs from becoming invisible doctrine|

### B. Evidence Objects

| Object              | Function                                              |
|---------------------|-------------------------------------------------------|
| Source Pack         | Curated sources for reuse                             |
| Evidence Set        | Grounds claims with verified evidence                 |
| Corpus Set          | Body of text/data for analysis                        |
| Reference Set       | Citations and cross-references                        |
| Receipt Bundle      | Attestation collection tied to a process              |
| Observation Log     | Chronological record of observed events               |

> **Critical:** Prompt Pack ≠ Evidence Pack. A prompt can generate analysis.
> Evidence grounds the analysis. These must remain distinct.

### C. Governance Objects

| Object              | Function                                              |
|---------------------|-------------------------------------------------------|
| Gate Set            | Validation checkpoints                                |
| Decision Ledger     | Chronological record of authoritative decisions       |
| Risk Register       | Tracked risks with likelihood, impact, mitigation     |
| Constraint Set      | Hard limits on what may be done                       |
| Policy Set          | Rules governing behavior                              |
| Authority Map       | Who/what has permission to do what                    |
| Exception Set       | Documented deviations from policy                     |
| Invariant Set       | Non-negotiable conditions that must always hold       |

> **This is the highest-priority missing layer.** A HUMMBL system without
> these collapses into "smart productivity." A HUMMBL system with these
> becomes governable.
>
> Core chain: `Authority → Gate → Decision → Task → Receipt`

### D. Execution Objects

| Object              | Function                                              |
|---------------------|-------------------------------------------------------|
| Task Set            | Convert decisions into execution                      |
| Workflow Set        | Multi-step procedures                                 |
| Protocol Set        | Standardized interaction patterns                     |
| Prompt Pack         | Invocation artifacts for models/agents/tools          |
| Agent Pack          | Agent configurations and rosters                      |
| Tool Set            | Available tools and their capabilities                |
| Capability Registry | What agents/tools/humans can do                       |
| Delegation Set      | Delegated authority and scope                         |

> **Prompt Packs belong here, not at the center.** Prompts are invocation
> artifacts. They are not truth, authority, or evidence.

### E. Evaluation Objects

| Object              | Function                                              |
|---------------------|-------------------------------------------------------|
| Metric Set          | Quantitative measures                                 |
| Eval Suite          | Evaluation test collection                            |
| Benchmark Set       | Performance comparisons                               |
| Test Fixture Set    | Input/output pairs for testing                        |
| Validation Set      | Checks that something meets its spec                  |
| Failure Mode Set    | Known ways the system can fail                        |
| Adversarial Set     | Red-team / attack test cases                          |

> Every reusable pack should eventually have an eval surface.
> Prompt Packs without evals are just reusable incantations.
> Task Sets without receipts are unverified work queues.
> Claim Sets without evidence are belief clusters.

### F. Semantic Objects

| Object              | Function                                              |
|---------------------|-------------------------------------------------------|
| Definition Set      | Governed term definitions                             |
| Ontology Set        | Entity types and their relationships                  |
| Glossary Set        | Plain-language term reference                         |
| Taxonomy Set        | Classification hierarchy                              |
| Pattern Library     | Reusable solution patterns                            |
| Primitive Library   | Atomic building blocks                                |
| Transformation Map  | How one object type transforms into another           |

> This is where HUMMBL protects against semantic drift. Definitions should
> not be buried inside prompts, tasks, or markdown essays.

### G. Context Objects

| Object              | Function                                              |
|---------------------|-------------------------------------------------------|
| Context Pack        | Scope and environment for a work unit                 |
| Domain Set          | Subject-matter domains                                |
| Stakeholder Map     | Who cares, why, and with what authority               |
| Scenario Set        | Possible futures or situations                        |
| Use-Case Set        | Concrete usage scenarios                              |
| Environment Set     | Runtime/deployment environment                        |
| Market/Opportunity  | Market context and opportunity mapping                |

> Problems and questions change depending on context. The same question
> asked in AI governance vs coaching vs bioinformatics may require different
> evidence, gates, risks, claims, and tasks.

### H. Output Objects

| Object              | Function                                              |
|---------------------|-------------------------------------------------------|
| Artifact Registry   | Durable products of work                              |
| Document Set        | Written outputs                                       |
| Schema Set          | Machine-readable structure definitions                |
| Report Set          | Periodic or event-driven reports                      |
| Diagram Set         | Visual representations                                |
| Product Spec Set    | Product specifications                                |
| PRD Set             | Product requirements documents                        |
| Public Claim Set    | Claims made publicly (stricter promotion)             |
| Publication Pack    | Ready-to-publish bundles                              |

> Artifacts should carry: identity, status, version, source inputs, claims
> made, evidence used, gates passed, receipts produced, canon level.

---

## 5. Candidate Master Chain

### Inquiry-forward version

```
Context → Problem → Question → Hypothesis → Claim → Evidence
→ Decision → Task → Artifact → Gate → Receipt → Pattern → Protocol → Canon
```

### Governance-forward version

```
Context → Problem Graph → Question Set → Claim Set → Evidence Set
→ Risk Register → Decision Ledger → Task Set → Artifact Registry
→ Gate Set → Receipt Bundle → Canon
```

---

## 6. Relationship Grammar

Each object defines upstream and downstream relations:

```
Problem       → generates →  Question
Question      → elicits  →   Claim
Claim         → requires →   Evidence
Evidence      → grounds  →   Claim
Decision      → authorizes → Task
Task          → produces →   Artifact
Gate          → evaluates →  Artifact or Action
Receipt       → attests  →   Action or Validation
Pattern       → abstracts →  repeated Solution
Protocol      → standardizes → Interaction
Canon         → promotes →   validated Knowledge
```

### Cardinality rules

```
Problem       1:N  Questions
Question      1:N  Claims
Claim         1:N  Evidence
Decision      1:N  Tasks
Task          1:1  Receipt (mandatory)
Gate          1:N  Artifacts (evaluates)
Receipt       1:1  Action (attests)
Context       1:N  Problems (scopes)
```

---

## 7. Overlap / Failure-Mode Warnings

| Overload                                    | Failure Mode                                    |
|---------------------------------------------|-------------------------------------------------|
| Prompt Pack pretending to be Evidence Set   | Unfounded claims appear grounded                |
| Task Set pretending to be Decision Ledger   | Work appears authorized without authority       |
| Problem Set pretending to be Ontology       | Definitions drift, terms become ambiguous       |
| Receipt Bundle pretending to prove truth    | Process correctness mistaken for factual truth  |
| Claim Set without Evidence Set              | Belief cluster — assertions without grounding   |
| Gate Set without Risk Register              | Validation without threat model                 |
| Prompt Pack without Eval Suite              | Reusable incantation — no quality signal        |
| Decision Ledger without Authority Map       | Decisions appear authoritative but aren't       |

---

## 8. Full Admission List (65 candidate object types)

```
01.  Problem              34. Protocol
02.  Problem Set          35. Protocol Set
03.  Problem Graph        36. Prompt
04.  Question             37. Prompt Pack
05.  Question Set         38. Agent
06.  Hypothesis           39. Agent Registry
07.  Hypothesis Set       40. Capability
08.  Claim                41. Capability Registry
09.  Claim Set            42. Tool
10.  Assumption           43. Tool Set
11.  Assumption Set       44. Artifact
12.  Source               45. Artifact Registry
13.  Source Pack          46. Receipt
14.  Evidence             47. Receipt Bundle
15.  Evidence Set         48. Metric
16.  Context              49. Metric Set
17.  Context Pack         50. Eval
18.  Stakeholder          51. Eval Suite
19.  Stakeholder Map      52. Test Fixture
20.  Constraint           53. Fixture Set
21.  Constraint Set       54. Failure Mode
22.  Invariant            55. Failure Mode Set
23.  Invariant Set        56. Pattern
24.  Risk                 57. Pattern Library
25.  Risk Register        58. Definition
26.  Gate                 59. Definition Set
27.  Gate Set             60. Ontology
28.  Decision             61. Ontology Set
29.  Decision Ledger      62. Public Claim
30.  Task                 63. Publication Pack
31.  Task Set             64. Canon Entry
32.  Workflow             65. Canon Registry
33.  Workflow Set
```

Too many for immediate implementation. Useful for discovery.

---

## 9. Priority Admission Classes (12 for next phase)

```
Problem Graph       — interdisciplinary entangled problems
Question Set        — organized inquiry
Claim Set           — answers as governed claims
Evidence Set        — grounded evidence
Assumption Set      — surfaced hidden beliefs
Decision Ledger     — authoritative decisions
Gate Set            — validation checkpoints
Receipt Bundle      — process attestation
Risk Register       — tracked risks
Task Set            — execution units
Prompt Pack         — invocation artifacts (demoted from center)
Artifact Registry   — durable outputs
```

These give the minimum viable governed object grammar.

---

## 10. What Was Missing From the Original List

Original: `Problem Sets, Question Sets, Task Sets, Prompt Packs`

Most important missing five:

```
Claim Sets          — without these, answers are ungrounded assertions
Evidence Sets       — without these, claims are beliefs
Decision Ledgers    — without these, tasks appear authorized but aren't
Gate Sets           — without these, nothing validates
Receipt Bundles     — without these, actions didn't happen
```

These are the objects that keep the system from becoming prompt-centric.

---

## 11. Candidate Object Status Model

```
seed → candidate → draft → reviewed → validated → adopted → canonical
                                                          ↓
                                              deprecated → retired
                                              rejected
```

Phase -1 default for all objects:

```yaml
status: candidate
canon_level: non_authoritative
promotion_allowed: false
```

---

## 12. Candidate Schema Fields (universal)

```yaml
id:
name:
object_type:
status:
canon_level:
version:
owner:
created_at:
updated_at:
scope:
description:
inputs:           # what this object consumes
outputs:          # what this object produces
dependencies:     # what this object requires
related_objects:  # upstream/downstream relations
claims:           # claims this object makes
evidence:         # evidence supporting those claims
assumptions:      # assumptions this object depends on
risks:            # risks this object carries
gates:            # gates this object must pass
receipts:         # receipts this object has produced
authority_required:  # what authority is needed to use this
verification_method: # how to verify this object is correct
promotion_criteria:  # what's needed to promote this object
residual_risk:    # risk that remains after mitigation
```

Not every field is required for every object. These are candidate universal fields.

---

## 13. Phase -1 Gates

### G1 — Object Separation Gate

Each object type must answer:

```
What is this?
What is it not?
What does it govern?
What governs it?
What can it produce?
What can it not produce?
```

### G2 — Overlap Gate

Detect overloaded objects (see §7).

### G3 — Relationship Gate

Each object must define upstream and downstream relations (see §6).

### G4 — Promotion Gate

No object becomes canonical without:

```
definition
schema
example
counterexample
evidence requirement
validation method
receipt requirement
```

### G5 — Prompt-Centrism Gate

```
Prompt = invocation
Evidence = grounding
Decision = authority
Receipt = attestation
Canon = promoted governed knowledge
```

Prompts must not be treated as source of truth.

---

## 14. Recommended Phase 0 Target

Do **not** implement all 65 admitted objects. Phase 0 should create a small
canonical seed:

### Core (10)

```
ProblemGraph
QuestionSet
ClaimSet
EvidenceSet
DecisionLedger
TaskSet
PromptPack
GateSet
ReceiptBundle
ArtifactRegistry
```

### Support (5)

```
ContextPack
RiskRegister
AssumptionSet
EvalSuite
OntologySet
```

**Total: 15 object families** — enough to govern real work without exploding scope.

---

## 15. Open Questions for Fleet Review

```yaml
open_questions:
  - id: OQ-1
    question: "Should interdisciplinary problem structures be called Problem Graphs, Problem Constellations, or both?"
    status: open
  - id: OQ-2
    question: "Should Claim Set become the central bridge between Question Sets and Evidence Sets?"
    status: open
  - id: OQ-3
    question: "Should every Prompt Pack require an attached Eval Suite before reuse at scale?"
    status: open
  - id: OQ-4
    question: "Should Decision Ledgers be repo-local, project-local, or global across HUMMBL governance?"
    status: open
  - id: OQ-5
    question: "Should Gate Sets be reusable templates or artifact-specific definitions?"
    status: open
  - id: OQ-6
    question: "Should Receipt Bundles be immutable append-only logs, or can they be regenerated from underlying receipts?"
    status: open
  - id: OQ-7
    question: "Should Context Pack be required before any Problem Set can be promoted?"
    status: open
  - id: OQ-8
    question: "Should Public Claim Sets require a stricter promotion path than internal Claim Sets?"
    status: open
  - id: OQ-9
    question: "Should Capability Registries be tied to agents, tools, humans, or all three?"
    status: open
  - id: OQ-10
    question: "What is the minimum object grammar needed for v0.1 without overbuilding?"
    status: open
```

---

## 16. Confidence Assessment

```yaml
claim: "The HUMMBL Set Grammar candidate object families are well-defined for Phase -1 admission"
semantic_confidence: 0.8
confidence_kind: synthesis_judgment
calibration_status: uncalibrated
basis: "operator-provided structure + existing grammar artifact (HUMMBL_PROBLEM_GRAMMAR.md) + fleet architecture review"

evidence:
  - claim: "original 4 object types are incomplete"
    source: "operator analysis + comparison against implemented governance primitives"
    verification_status: verified
  - claim: "65 candidate object types cover the necessary space"
    source: "operator-provided list + cross-reference with HUMMBL_PROBLEM_GRAMMAR families"
    verification_status: reported
  - claim: "15 object families are sufficient for Phase 0"
    source: "operator recommendation + alignment with §2.1 convergence target"
    verification_status: inferred

uncertainties:
  - "object explosion risk — 65 types may be too many even for discovery"
  - "overlap between Evidence Set and Receipt Bundle not fully resolved"
  - "relationship grammar is directional but not yet typed (composition vs aggregation vs reference)"
  - "no schema exists yet — structural validation is impossible"

next_lanes:
  - "resolve 10 open questions with operator + ChatGPT + Codex"
  - "stress-test 15 Phase 0 objects against a real HUMMBL scenario"
  - "define minimal schema stubs for the 15 Phase 0 objects"
  - "create overlap detection rules for G2 gate"
```
