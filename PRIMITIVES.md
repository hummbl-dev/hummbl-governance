# HUMMBL Governance Primitives — Complete Reference

**Version:** v1.2.2
**Existing primitives:** 26 (P1-P26)
**Implemented expansion primitives:** 8 (P27-P31, P34, P36, P38) — schemas, modules, and tests
**Proposed primitives:** 6 (P32-P33, P35, P37, P39-P40) — not yet started
**Kernel invariants:** K1-K11 (K1-K8 enforced on every receipt path; K9-K11 enum-defined, schema-backed, tested, and exposed through Kernel validation methods — full-path mandatory enforcement is limited to call sites that invoke those methods)
**Doctrine invariants:** D1-D7 (D1-D5 enforced on every promotion path; D6 enforced via contestability primitive; D7 enforced via `assert_invariant_change_gated()` when artifact has `amendment_type` field — see D7 bypassability note below)

This document is the canonical reference for all HUMMBL governance primitives. For the research analysis behind the proposed primitives, see `docs/research/hummbl-primitive-expansion-v0.1.md` and `docs/research/hummbl-primitive-matrix-v0.1.md`.

---

## Invariants

### Kernel invariants (K1-K11) — enforced by `kernel/invariants.py`

| ID | Name | Invariant | Enforcing engine |
|---|---|---|---|
| K1 | RECEIPT | Every action that affects shared state produces a structured, signed receipt | `ReceiptEngine` |
| K2 | LAW | Every receipt is evaluated against at least one scaling law | `LawEngine` |
| K3 | IDENTITY | Every agent has a single canonical identity, trust tier, and capability vector | `IdentityEngine` |
| K4 | TEMPORAL | Every receipt has a sequence_id for total ordering within its agent context | `SequenceEngine` |
| K5 | EVIDENCE | Every claim in a receipt is graded or marked speculative | `EvidenceEngine` |
| K6 | AUTHORITY | Every authority exercise is scoped, limited, and leaves a receipt | `AuthorityEngine` |
| K7 | ROLE | Every role is a runtime claim, not a static assignment | `IdentityEngine` |
| K8 | DOCTRINE | Every fleet artifact respects the doctrine invariants D1-D7 | `DoctrineEngine` |
| K9 | REVERSIBILITY | Every governed durable-state mutation or irreversible external side effect declares a rollback path or is explicitly marked irreversible with a recorded risk acceptance | `Kernel.validate_rollback()` → `rollback.py` (API-exposed; mandatory only at call sites that invoke it) |
| K10 | RECOVERY | Re-engagement after halt, quarantine, or open breaker requires root-cause verification, evidence collection, and operator approval | `Kernel.validate_recovery()` → `recovery_verifier.py` (API-exposed; mandatory only at call sites that invoke it) |
| K11 | INTEGRITY | Receipt sequences are complete and unbroken. Sequence gaps and hash-chain breaks trigger KernelPanic | `Kernel.check_receipt_integrity()` → `receipt_integrity_monitor.py` (API-exposed; mandatory only at call sites that invoke it) |

### Doctrine invariants (D1-D7) — enforced by `kernel/doctrine_engine.py`

| ID | Name | Invariant |
|---|---|---|
| D1 | ZERO_TRUST | Playground is zero-trust: no playground artifact influences fleet state without passing the Seed gate |
| D2 | FALSIFIABILITY | A hypothesis without a falsifier is not a seed. It is philosophy. |
| D3 | NO_INHERITED_AUTHORITY | Credibility is earned per artifact, not borrowed from lineage |
| D4 | DIVERGENCE_CONTAINED | Novelty generation must not destabilize convergent operations |
| D5 | NO_AUTO_PROMOTION | No stage promotes itself. Every gate requires operator approval. |
| D6 | CONTESTABILITY | Affected parties can flag AI-mediated decisions for human review, suspending the decision's effects until review completes. Requires evidence or justification, not just a bare flag. |
| D7 | DOCTRINE_AMENDMENT | No invariant or doctrine amendment may take effect without operator approval and a recorded receipt. Ungated amendments are blocked. |

> **D7 bypassability note:** D7 enforcement in `DoctrineEngine.promote()` is field-triggered — it only fires when the artifact dict has an `amendment_type` field. A malformed invariant-change artifact that omits `amendment_type` would bypass the gate. Closing this gap requires one of: (a) schema route requiring all invariant/doctrine files to pass `validate_doctrine_amendment`, (b) filename/path classifier for invariant/doctrine mutation, (c) content classifier for K/D invariant changes, or (d) CI gate that rejects changes to invariant/doctrine surfaces without an amendment record. This is a known residual risk, not a closed control.

---

## Existing primitives (P1-P26)

### Governance Kernel (P25-P26)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P25 | `kernel/admission_control` | Bounded admission-control for governed permission of state transitions. 5 gates: authority, executor, scope, evidence, receipt | D5 (NO_AUTO_PROMOTION) |
| P26 | `kernel/receipt_engine` | SHA-256 hash-chained receipts with agent-scoped storage. Every action affecting shared state produces a signed receipt | K1 (RECEIPT) |

### Safety (P1-P4)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P1 | `kill_switch` | Emergency halt system with 4 graduated modes (DISENGAGED, HALT_NONCRITICAL, HALT_ALL, EMERGENCY) | — |
| P2 | `circuit_breaker` | Automatic failure detection and recovery across 3 states (CLOSED, HALF_OPEN, OPEN) | — |
| P3 | `output_validator` | Rule-based content validation: PII detection, injection detection, blocklists, length bounds | — |
| P4 | `capability_fence` | Soft sandbox enforcing capability boundaries per agent role. Extends delegation tokens | — |

### Cost & Budget (P5)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P5 | `cost_governor` | Budget tracking with soft/hard caps and ALLOW/WARN/DENY decisions. SQLite-backed | — |

### Identity & Auth (P6-P7)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P6 | `identity` | Agent registry with configurable aliases, trust tiers, and canonicalization | K3 (IDENTITY) |
| P7 | `delegation` | HMAC-SHA256 signed capability tokens for agent delegation chains with scope, expiry, chain-depth | K6 (AUTHORITY) |

### Audit & Compliance (P8-P10)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P8 | `audit_log` | Append-only JSONL governance audit log with daily rotation and retention | K1 (RECEIPT) |
| P9 | `compliance_mapper` | Map governance traces to SOC2, GDPR, NIST AI RMF, ISO 27001, ISO 42001 controls | — |
| P10 | `stride_mapper` | Map agent interactions to STRIDE threat categories with mitigation suggestions | — |

### Reasoning & Contract (P11-P13)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P11 | `reasoning` | Structured governance reasoning engine with rule application, conflict detection, and decision tracing. Base120 mental models | — |
| P12 | `contract_net` | Market-based task allocation protocol for multi-agent systems (Smith 1980) | — |
| P13 | `schema_validator` | Stdlib-only JSON Schema validator (Draft 2020-12 subset) | — |

### Coordination (P14-P16)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P14 | `coordination_bus` | Append-only TSV message bus with flock locking and HMAC signing | — |
| P15 | `lamport_clock` | Hardened logical clock for causal ordering of distributed agent events | K4 (TEMPORAL) |
| P16 | `convergence_guard` | Detect instrumental convergence patterns in agent behavior | — |

### Behavior & Health (P17-P19)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P17 | `reward_monitor` | Behavioral drift and reward gaming detector (Leike et al. 2018) | — |
| P18 | `health_probe` | Composable health probe framework with latency tracking | — |
| P19 | `lifecycle` | NIST AI RMF orchestrator composing kill switch, circuit breaker, cost governor, and audit log | — |

### Physical AI (P20)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P20 | `physical_governor` | Kinematic constraints and pHRI safety modes for physical-AI deployments | — |

### Execution Assurance (P21)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P21 | `eal` | Execution Assurance Layer — Arbiter-verified code quality in execution receipts | — |

### Error Taxonomy (P22-P24)

| ID | Module | Description | Invariant enforced |
|---|---|---|---|
| P22 | `errors` | `HummblError`, `FailureMode`, and `fm_to_errors()` — typed error taxonomy (3 layers) | — |
| P23 | `failure_modes` | Structured failure mode catalog with classification and error cross-reference | — |
| P24 | `evolution_lineage` | In-memory lineage tracking for eAI variants with drift detection | — |

---

## Expansion primitives (P27-P40)

### Implemented (P27-P31, P34, P36, P38)

| ID | Name | Description | Invariant | Module | Schema | Status |
|---|---|---|---|---|---|---|
| P27 | CanonRegistry | Governs promotion from draft to canonical status. 6 levels: draft, reviewed, validated, adopted, canonical, deprecated | D5 | `kernel/canon_registry.py` | `canon_registry.schema.json` | ✅ Implemented |
| P28 | Rollback | Enforces reversibility: every governed action declares a rollback path or is marked irreversible with risk acceptance | K9 | `kernel/rollback.py` | `rollback.schema.json` | ✅ Implemented; Kernel API exposed (mandatory at call sites that invoke `validate_rollback()`) |
| P29 | RecoveryVerifier | Gates re-engagement after halt with root-cause verification, evidence, and operator approval | K10 | `kernel/recovery_verifier.py` | `recovery_verifier.schema.json` | ✅ Implemented; Kernel API exposed (mandatory at call sites that invoke `validate_recovery()`) |
| P30 | ReceiptIntegrityMonitor | Detects receipt sequence gaps, hash chain breaks, retroactive insertion, and invalid signatures. Raises KernelPanic | K11 | `kernel/receipt_integrity_monitor.py` | `receipt_integrity_monitor.schema.json` | ✅ Implemented; Kernel API exposed (mandatory at call sites that invoke `check_receipt_integrity()`) |
| P31 | Contestability | Allows affected parties to flag AI-mediated decisions for human review, suspending effects until review completes | D6 | `kernel/contestability.py` | `contestability.schema.json` | ✅ Implemented |
| P34 | AuthoritySweeper | Provides callable sweep validation/build/run functions for expired authority grants. Finds expired grants, builds revocation records, validates them. No scheduler integration — callers must invoke `run_sweep()` periodically | K6 | `kernel/authority_sweeper.py` | `authority_sweeper.schema.json` | ✅ Implemented (callable, not scheduled) |
| P36 | TrustAdjuster | Handles evidence-backed trust-tier reductions based on compliance violations. Severity maps to tier reduction (low=1, medium=2, high=3, critical=REVOKED). Only reduces tiers — promotions must go through IdentityEngine's promotion path | K3 | `kernel/trust_adjuster.py` | `trust_adjuster.schema.json` | ✅ Implemented (reduction only) |
| P38 | DoctrineAmendment | Governs changes to invariants themselves: proposed change -> operator review -> evidence -> receipt -> promotion | D7 | `kernel/doctrine_amendment.py` | `doctrine_amendment.schema.json` | ✅ Implemented; wired into `DoctrineEngine.promote()` (field-triggered on `amendment_type` — see D7 bypassability note) |

### Not yet started (P32-P33, P35, P37, P39-P40)

| ID | Name | Description | Invariant | Status |
|---|---|---|---|---|
| P32 | DisputeResolution | Inter-agent conflict resolution primitive (from government corpus doctrine) | — | Not started |
| P33 | Succession | Authority transfer primitive for governance continuity (from government corpus doctrine) | — | Not started |
| P35 | RegulatorExport | Produces compliance evidence in regulator-accepted formats (EU AI Act technical file, SOC 2 audit packet) | — | Not started |
| P37 | Treaty | Inter-agent agreements with shared authority, mutual obligations, and dispute resolution | — | Not started |
| P39 | GovernanceFitness | Evaluates governance pattern effectiveness over time, not just compliance | — | Not started |
| P40 | DraftSweeper | Tracks draft age and flags drafts exceeding configurable maximum age for mandatory review | — | Not started |

### Candidates under consideration (P41-P43)

| ID | Name | Description | Source |
|---|---|---|---|
| P41 | Retirement | Governs decommissioning: verify no dependents, archive state, transfer authority, notify stakeholders | Matrix Part 2: Phi6 Retire gap |
| P42 | ConceptRegistry | Governs terminology: ensures terms in receipts/admissions have canonical definitions | Matrix Part 1: full-gap family 1 |
| P43 | RiskRegister | Dedicated risk-register primitive (family 9 is weak, only stride_mapper/failure_modes adjacent) | Matrix Part 1: weak-coverage family 9 |

---

## Primitive categories (P1-P40)

| Category | Existing | Implemented expansion | Proposed | Total |
|---|---|---|---|---|
| Governance Kernel | 2 (P25, P26) | 4 (P27-P30) | 1 (P40) | 7 |
| Safety | 4 (P1-P4) | 0 | 0 | 4 |
| Cost & Budget | 1 (P5) | 0 | 0 | 1 |
| Identity & Auth | 2 (P6, P7) | 2 (P34, P36) | 0 | 4 |
| Audit & Compliance | 3 (P8-P10) | 0 | 1 (P35) | 4 |
| Reasoning & Contract | 3 (P11-P13) | 0 | 0 | 3 |
| Coordination | 3 (P14-P16) | 0 | 2 (P32, P37) | 5 |
| Behavior & Health | 3 (P17-P19) | 0 | 1 (P39) | 4 |
| Physical AI | 1 (P20) | 0 | 0 | 1 |
| Execution Assurance | 1 (P21) | 0 | 0 | 1 |
| Error Taxonomy | 3 (P22-P24) | 0 | 0 | 3 |
| Governance Ecology | 0 | 2 (P31, P38) | 1 (P33) | 3 |
| **Total (P1-P40)** | **26** | **8** | **6** | **40** |

> **Note:** P37 (Treaty) appears in the Coordination category above. Some primitives span multiple categories (e.g., P38 DoctrineAmendment is both Governance Ecology and Governance Kernel), but each primitive is counted once in its primary category to keep the inventory total at 40.

### Candidates under consideration (P41-P43, not counted in P1-P40 total)

| Category | Candidates |
|---|---|
| Lifecycle Hygiene | 1 (P41) |
| Concept Layer | 1 (P42) |
| Risk Management | 1 (P43) |
| **Candidates total** | **3** |

---

## MCP Server exposure

| Server | Tools | Primitives exposed |
|---|---|---|
| `mcp_server` | 10 | KillSwitch, CircuitBreaker, CostGovernor, AuditLog, ComplianceMapper, HealthProbe |
| `mcp_compliance` | 5 | NIST AI RMF, SOC2, ISO crosswalk, STRIDE, evidence export |
| `mcp_sandbox` | 5 | CapabilityFence, OutputValidator |
| `mcp_identity` | 10 | AgentRegistry, DelegationTokenManager, LamportClock |
| `mcp_agent_monitor` | 11 | BehaviorMonitor, ConvergenceDetector, GovernanceLifecycle, EvolutionLineage |
| `mcp_reasoning` | 10 | ReasoningEngine, SchemaValidator, ContractNetManager |
| `mcp_physical` | 6 | KinematicGovernor, pHRISafetyMonitor |
| **Total** | **57** | — |

---

## See also

- `docs/research/hummbl-primitive-expansion-v0.1.md` — HUAOMP x MTSMU analysis proposing P27-P40
- `docs/research/hummbl-primitive-matrix-v0.1.md` — framework coverage, lifecycle, relationships, admission sub-taxonomy
- `docs/research/ai-framework-taxonomy-v0.1.md` — 26 framework families, 498-framework inventory
- `hummbl_governance/data/*.schema.json` — JSON Schema files for all governed objects
- `hummbl_governance/kernel/invariants.py` — K1-K11 enum definitions
- `hummbl_governance/kernel/doctrine_engine.py` — D1-D7 enum definitions
