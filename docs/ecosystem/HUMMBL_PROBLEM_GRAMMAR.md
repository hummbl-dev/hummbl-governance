# The HUMMBL Problem — Schematized Grammar

**Framework:** HUAOMP × MTSMU × Base120
**Status:** Draft v0.1 — for fleet review
**Date:** 2026-06-25

---

## Grammar Notation

```
::=        defined as
|          alternation
*          zero or more
+          one or more
?          optional
{...}      grouping
"..."      literal token
<Name>     non-terminal (referenced elsewhere)
# comment  explanatory annotation
```

---

## 0. Meta-Definition

The HUMMBL Problem is the governance of a fleet of heterogeneous agents (AI + human) operating on a shared codebase under conditions of asymmetric trust, compounding risk, and irreversible action — where the cost of a wrong decision scales with agent autonomy.

```
HUMMBL_Problem ::=
  AgentFleet
  SharedArtifactSpace
  TrustAsymmetry
  CompoundingRisk
  IrreversibilityConstraint
  AutonomyCostGradient
```

**MTSMU confidence:** 0.9 (directly evidenced by the existence of Arbiter, security-auditor, cyber-workbench, kill switch, circuit breaker, delegation tokens, governance bus, cost governor — all built to address this exact problem)

---

## 1. HUAOMP Expansion (Epistemic Breadth)

### H — Holistic (Feedback Loops & Leverage Points)

```
HolisticView ::=
  SystemBoundary := AgentFleet ∪ ArtifactSpace ∪ GovernanceLayer ∪ ExternalWorld
  FeedbackLoops ::=
    Loop+ :=
      Loop ::= Agent → Artifact → QualitySignal → Agent   # Arbiter scores → agent adjusts
             | Agent → Action → RiskSignal → Governor → Agent  # kill switch halts
             | Agent → Spend → CostSignal → CostGovernor → Agent  # budget enforcement
             | Agent → Finding → EvidenceChain → Reviewer → Agent  # security-auditor → human
  LeveragePoint := "the governance receipt"   # SY1 — the append-only audit trail is the highest-leverage intervention
```

**Base120:** SY1 (Leverage Points), RE2 (Feedback Loops), SY6 (Feedback Structure Mapping)

▸ Spec constraint: Every agent action MUST produce a receipt that enters an append-only audit trail. No receipt = no action occurred.

### U — Universal (Context-Free Invariants)

```
Invariant ::= 
  "agents cannot self-approve consequential work"
| "evidence precedes conclusion"
| "append-only logs are immutable"
| "missing tools degrade to SKIPPED, not FAIL"
| "secrets live in env vars, never in code"
| "contracts are canonical — breaking changes require SemVer major"
| "zero third-party runtime deps in core primitives"
```

**Base120:** P1 (First Principles), CO9 (Interface Contracts), SY12 (Protocol Standards)

▸ Spec constraint: The 7 invariants above are non-negotiable across every HUMMBL repo, agent, and runtime context. They compose — any subsystem that violates one is defective by definition.

### A — Absolute (Hard Boundaries)

```
MustNever ::=
  "agent commits directly to main"
| "agent pushes without CI green"
| "agent modifies git config"
| "agent performs destructive ops without explicit confirmation"
| "agent hardcodes secrets"
| "agent auto-fixes security patches without human review"
| "agent scans third-party repos without ownership confirmation"
| "cyber work proceeds without authorization manifest"

MustEventually ::=
  "every PR passes Arbiter quality gate"
| "every repo passes Bandit -ll with 0 HIGH"
| "every consequential decision has a Krineia receipt"
| "every agent has a trust tier and quality threshold"
| "every security finding has evidence (file:line)"

PhysicallyImpossible ::=
  "deterministic quality scoring with LLM in the loop"   # Arbiter design principle
| "tamper-proof audit trail with delete operations"       # append-only by definition
| "agent autonomy without cost containment"               # cost governor is structural
```

**Base120:** IN7 (Boundary Testing), DE13 (FMEA), IN18 (Kill-Criteria & Stop Rules)

▸ Spec constraint: The MustNever set is enforced by guardrails (pre-commit hooks, CI gates, kill switch). The MustEventually set defines the fleet's convergence target. PhysicallyImpossible defines design constraints that cannot be engineered away.

### O — Omni (All Perspectives)

```
Perspective ::=
  Operator        := "is this safe to merge?"
| Agent           := "will my work be attributed correctly?"
| Reviewer        := "can I trace this decision to evidence?"
| Attacker        := "what surface does this expose?"
| Auditor         := "does this satisfy NIST/ISO/SOC2?"
| CostOwner       := "what does this cost to run?"
| FutureSelf      := "will this be understandable in 6 months?"
| FleetCoordinator := "are agents duplicating work?"
| ExternalWorld   := "does this leak secrets or PII?"

FailureMode ::=
  AgentGoesRogue       := kill_switch → HALT_ALL
| BudgetExceeded       := cost_governor → automatic halt
| QualityDrops         := arbiter → FAIL grade → CI block
| VulnerabilityShips   := security-auditor → HIGH finding → block
| UnauthorizedCyberWork := cyber-workbench → deny decision
| EvidenceLost         := no receipt → action didn't happen
| TrustAsymmetryExploit := untrusted agent → probation tier → reduced scope
```

**Base120:** P2 (Stakeholder Mapping), P7 (Perspective Switching), IN10 (Red Teaming)

▸ Spec constraint: Every governance mechanism must be evaluated from all 9 perspectives before promotion. The attacker perspective is mandatory — defense-in-depth is the default posture.

### M — Meta (Problem Type & Strange Loops)

```
ProblemType := "meta-governance"   # the problem of governing governance

StrangeLoop ::=
  Arbiter scores itself                    # self-scoring gate (score ≥ 90)
| GovernanceBus audits governance bus      # self-referential audit trail
| Agents improve agents                    # RE1 recursive improvement
| Guardrails learn from guardrail failures # RE20 recursive governance
| The problem defines the solution that defines the problem  # this grammar

RightProblemQuestion :=
  "Are we governing agent behavior, or are we building the evidence chain
   that makes agent behavior trustworthy?"

Answer :=
  "Both. Governance without evidence is theater.
   Evidence without governance is archaeology.
   The HUMMBL Problem is the COMPOSITION of the two."
```

**Base120:** P4 (Lens Shifting), P10 (Context Windowing), RE7 (Self-Referential Logic)

▸ Spec constraint: The problem is not "how to control agents" but "how to produce trustworthy evidence that agents are controllable." Every governance primitive must produce evidence of its own operation.

### P — Paradigmatic (Paradigm Shift)

```
OldParadigm :=
  "human reviews every agent action sequentially"
  → does not scale past ~5 agents
  → bottleneck is human attention
  → quality is subjective

NewParadigm :=
  "agents act within guardrails; evidence is generated automatically;
   humans review exceptions and receipts, not every action"
  → scales with agent count
  → bottleneck is evidence quality
  → quality is deterministic (Arbiter) + evidence-based (MTSMU)

AnomalyIgnoring :=
  "agents sometimes produce better code than humans"
| "deterministic scoring catches what humans miss"
| "the fleet is already shipping without human review on routine work"

ObsolescenceCondition :=
  "this approach becomes obsolete when agents can self-certify
   with cryptographic proof of correctness"   # not yet — hence the evidence chain
```

**Base120:** P15 (Assumption Surfacing), IN1 (Subtractive Thinking), IN3 (Problem Reversal)

▸ Spec constraint: The paradigm is "evidence-first, human-review-on-exception." Do not build systems that require humans to review every agent action. Build systems that make every agent action reviewable.

---

## 2. MTSMU Expansion (Evidence Rigor)

```
EvidenceChain ::=
  Claim
  Source          ::= test_result | probe | log_entry | bus_receipt | git_diff | bandit_finding | arbiter_score
  Confidence      ::= float[0.0, 1.0]
  Uncertainty     ::= "what is still inferred or weakly supported"
  Verification    ::= "what proved the result"
  Receipt         ::= bus_message | test_output | file_reference | outcome_statement

ConfidenceBand ::=
  0.9+  := "directly verified by tests, probes, or source inspection"
| 0.7-0.89 := "strong evidence, but at least one assumption remains"
| 0.4-0.69 := "partial evidence or unverified integration behavior"
| <0.4  := "speculative; say so plainly and reduce scope"

MTSMU_OutputContract ::=
  Evidence       ::= "measured facts"
  Uncertainties  ::= "what is still inferred"
  Action         ::= "lane chosen and why"
  Verification   ::= "what proved the result"
  NextLanes      ::= "next highest-value tasks"
```

---

## 3. Base120 Transformation Grammar

The HUMMBL Problem decomposes across 6 transformation families. Each family maps to a concrete subsystem:

```
Transformation ::=
  P  (Perspective)    → AgentIdentity     := who is acting, from what role, with what trust tier
| IN (Inversion)      → RiskSurface       := what must NOT happen, what fails, what's missing
| CO (Composition)    → SystemAssembly    := how primitives compose into governance
| DE (Decomposition)  → ProblemBreakdown  := how the problem splits into solvable parts
| RE (Recursion)      → FeedbackLoop      := how the system improves itself
| SY (Synthesis)      → SystemBehavior    := emergent properties of the whole
```

### P → Perspective (Agent Identity Layer)

```
AgentIdentity ::=
  AgentID        ::= "claude-code" | "codex" | "gemini" | "copilot" | "devin" | "human" | ...
  TrustTier      ::= "verified" | "probation" | "unknown"
  QualityThreshold ::= float   # per-agent minimum Arbiter score
  Attribution    ::= CommitAuthor → AgentID mapping via email + Co-Authored-By
  ScopePermitted ::= TrustTier → ActionSet
```

**Operators:** P1 (First Principles), P2 (Stakeholder Mapping), P3 (Identity Stack), P6 (POV Anchoring), P11 (Role Perspective-Taking), P16 (Identity-Context Reciprocity)

**Implemented by:** Arbiter agent_registry.py, founder-mode agent_identity.py, delegation_token.py

### IN → Inversion (Risk & Safety Layer)

```
RiskSurface ::=
  MustNever        ::= absolute prohibitions (see §1.A)
  FailureModes     ::= FMEA catalog (see §1.O)
  AntiPatterns     ::= shell=True | hardcoded secrets | auto-fix without review | ...
  KillCriteria     ::= conditions that trigger kill_switch
  StopRules        ::= "halt when cost > budget" | "halt when quality < threshold"
  MissingTools     ::= "degrade to SKIPPED, not FAIL"
  AbsenceAudit     ::= "what's NOT there that should be?"
```

**Operators:** IN1 (Subtractive), IN2 (Premortem), IN7 (Boundary Testing), IN10 (Red Teaming), IN18 (Kill-Criteria), IN19 (Harm Minimization), IN20 (Antigoals)

**Implemented by:** kill_switch_core.py, circuit_breaker.py, cyber-workbench MustNever set, security-auditor strict mode

### CO → Composition (System Assembly Layer)

```
SystemAssembly ::=
  Primitive       ::= kill_switch | circuit_breaker | delegation_token | governance_bus
                    | cost_governor | schema_validator | identity_registry
  Composition     ::= Primitive → Primitive wiring
  InterfaceContract ::= "every primitive is stdlib-only, independently importable, thread-safe"
  Platformization  ::= Primitive → PyPI package → consumed by founder-mode
  InteropProtocol  ::= coordination bus (TSV, append-only, flock-locked)
```

**Operators:** CO2 (Chunking), CO3 (Functional Composition), CO9 (Interface Contracts), CO12 (Modular Interoperability), CO14 (Platformization)

**Implemented by:** hummbl-governance (7 primitives → PyPI), founder-mode (consumer), coordination bus

### DE → Decomposition (Problem Breakdown Layer)

```
ProblemBreakdown ::=
  Layer0 := "safety primitives (kill switch, circuit breaker)"           # hummbl-governance
  Layer1 := "quality scoring (Arbiter)"                                   # arbiter
  Layer2 := "vulnerability scanning (security-auditor)"                   # hummbl-security-auditor
  Layer3 := "authorization governance (cyber-workbench)"                  # hummbl-cyber-workbench
  Layer4 := "agent orchestration (founder-mode)"                          # founder-mode
  Layer5 := "fleet coordination (bus, cognition, dashboard)"              # founder-mode bus/cognition

  SeparationOfConcerns ::=
    Arbiter does NOT scan for vulnerabilities (it scores quality)
    security-auditor does NOT score quality (it catalogs findings)
    cyber-workbench does NOT scan code (it authorizes work)
    founder-mode does NOT define primitives (it consumes them)
```

**Operators:** DE2 (Factorization), DE3 (Modularization), DE4 (Layered Breakdown), DE11 (Scope Delimitation), DE17 (Orthogonalization)

**Implemented by:** The 5-tier dependency taxonomy, repo separation (governance/arbiter/auditor/workbench/founder-mode)

### RE → Recursion (Feedback Loop Layer)

```
FeedbackLoop ::=
  QualityLoop    ::= Agent writes code → Arbiter scores → score feeds back to agent → agent adjusts
  SecurityLoop   ::= Agent ships code → security-auditor scans → findings → human reviews → fix PR
  CostLoop       ::= Agent makes API call → cost_tracker records → budget check → halt if exceeded
  TrustLoop      ::= Agent commits → Arbiter attributes → trust tier updates → scope adjusts
  GovernanceLoop ::= Governor acts → receipt → audit → governor improves (RE20)
  CalibrationLoop ::= Arbiter scores → human reviews score → weights adjust → score improves (RE11)

  ConvergenceTarget ::= "every repo ≥ 60 Arbiter, 0 HIGH Bandit, full Krineia receipt chain"
  AntiForgetting    ::= "audit trail is append-only; history cannot be rewritten"
```

**Operators:** RE1 (Recursive Improvement), RE2 (Feedback Loops), RE11 (Calibration Loops), RE17 (Versioning & Diff), RE20 (Recursive Governance)

**Implemented by:** Arbiter trend tracking, security-auditor baseline suppression, cost_tracker, governance bus, Krineia receipts

### SY → Synthesis (System Behavior Layer)

```
SystemBehavior ::=
  EmergentProperty ::=
    "fleet quality improves without central coordination"
  | "security findings decrease over time as feedback loops tighten"
  | "agent trust tiers self-calibrate via attribution data"
  | "cost burn rate stabilizes as cost governor learns usage patterns"

  SystemBoundary ::= AgentFleet ∪ ArtifactSpace ∪ GovernanceLayer
  RequisiteVariety ::= "the governance system must have at least as many control actions
                        as the agent fleet has failure modes"
  TippingPoint ::= "when >50% of commits are agent-authored, manual review becomes
                    the bottleneck — evidence-first mode becomes mandatory"
  MetaModel ::= "HUMMBL is itself a Base120 application (this grammar is RE7 self-referential)"
```

**Operators:** SY1 (Leverage Points), SY4 (Requisite Variety), SY9 (Phase Transitions), SY11 (Governance Patterns), SY18 (Measurement & Telemetry), SY20 (Systems-of-Systems)

**Implemented by:** The fleet as a whole — no single repo implements emergence; it arises from composition

---

## 4. Compositional Grammar (HUAOMP × MTSMU × Base120)

```
HUMMBL_System ::=
  ( HUAOMP_Lens × MTSMU_Rigor × Base120_Operator )+

GovernancePrimitive ::=
  PrimitiveName
  HUAOMP_Lens        # which epistemic lens it serves
  Base120_Family      # which transformation it implements
  MTSMU_Evidence      # what evidence it produces
  Confidence          # how trustworthy is that evidence
  Receipt             # what audit trail entry it generates

Example instantiations:

  KillSwitch ::=
    HUAOMP := A (Absolute — MustNever enforcement)
    Base120 := IN18 (Kill-Criteria & Stop Rules)
    MTSMU := Evidence: kill_switch state file | Confidence: 0.95 | Receipt: bus STATUS
    Implementation := hummbl-governance/kill_switch.py

  Arbiter ::=
    HUAOMP := H (Holistic — feedback loop from code to quality signal)
    Base120 := RE2 (Feedback Loops) × DE6 (Taxonomy/Classification)
    MTSMU := Evidence: test results, analyzer output, score | Confidence: 0.9 | Receipt: JSONL audit trail
    Implementation := arbiter/scoring.py + analyzers/

  SecurityAuditor ::=
    HUAOMP := O (Omni — attacker perspective, all failure modes)
    Base120 := IN10 (Red Teaming) × DE13 (FMEA)
    MTSMU := Evidence: scanner output, file:line findings | Confidence: 0.85 | Receipt: SARIF + JSONL
    Implementation := hummbl-security-auditor/

  CyberWorkbench ::=
    HUAOMP := A (Absolute — authorization boundaries)
    Base120 := IN7 (Boundary Testing) × P16 (Identity-Context Reciprocity)
    MTSMU := Evidence: authorization manifest, decision JSON | Confidence: 0.9 | Receipt: Markdown receipt
    Implementation := hummbl-cyber-workbench/

  CoordinationBus ::=
    HUAOMP := H (Holistic — system-wide feedback)
    Base120 := SY20 (Systems-of-Systems Coordination) × CO12 (Modular Interoperability)
    MTSMU := Evidence: bus messages (TSV) | Confidence: 0.95 | Receipt: append-only log entry
    Implementation := founder-mode/bus/
```

---

## 5. Confidence Assessment (MTSMU)

```
Claim: "The HUMMBL Problem is well-defined by this grammar"
  Evidence:
    - 7 governance primitives implemented and tested (hummbl-governance, 1031 tests)
    - Quality scoring in production (Arbiter, 783 tests, PyPI v0.6.0)
    - Vulnerability scanning operational (security-auditor, 28 tests, fleet scan complete)
    - Authorization framework deployed (cyber-workbench, Phase 0)
    - Fleet-wide security scan completed this session (37 repos, 4 HIGH fixed)
    - All primitives are stdlib-only, independently importable, thread-safe
  Confidence: 0.85
  Uncertainty:
    - The grammar is a draft; it has not been stress-tested against edge cases
    - The RE (Recursion) family is under-implemented — feedback loops exist but
      don't all close (e.g., Arbiter scores feed back to agents informally, not structurally)
    - The SY (Synthesis) family is emergent — no single system controls it
    - The cyber-workbench is Phase 0 (ADAPT_REQUIRED) — not yet enforcing
  Verification:
    - This grammar was constructed from actual source code, not aspiration
    - Every "Implemented by" reference points to real, tested code
  Next lanes:
    - Stress-test grammar against a novel agent scenario (e.g., "agent proposes a new primitive")
    - Close the RE2 feedback loop: Arbiter scores → structured agent adjustment
    - Promote cyber-workbench from Phase 0 to Phase 1
    - Define the grammar as a JSON Schema for machine validation
```

---

## 6. Open Questions (Requiring Human Judgment)

1. **Should the grammar be formalized as a JSON Schema?** This would enable machine validation of governance configurations against the grammar.

2. **Is the 5-tier decomposition (§3.DE) correct?** The current layering puts security-auditor at Layer 2 and cyber-workbench at Layer 3 — but cyber-workbench authorizes work that security-auditor then scans. Should authorization come before scanning?

3. **What is the convergence target for the RE family?** "Every repo ≥ 60 Arbiter, 0 HIGH Bandit" is stated but not formally adopted. Should it be?

4. **Does the grammar need a 7th lens?** HUAOMP has 6 lenses, Base120 has 6 families, but the problem has 7 governance primitives. Is there a missing dimension?

5. **Should Arbiter consume security-auditor output?** Both wrap bandit. The grammar says they're complementary (§DE separation of concerns), but the redundancy is real.
