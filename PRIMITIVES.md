# HUMMBL Governance Primitives — Complete Reference

**Version:** v1.1.0
**Existing primitives:** 26 (P1-P26)
**Proposed primitives:** 14 (P27-P40) — schema candidates only, not yet implemented
**Proposed invariants:** K9-K11, D6-D7 — pending operator decision on enum vs. doctrine

This document is the canonical reference for all HUMMBL governance primitives. For the research analysis behind the proposed primitives, see `docs/research/hummbl-primitive-expansion-v0.1.md` and `docs/research/hummbl-primitive-matrix-v0.1.md`.

---

## Invariants

### Kernel invariants (K1-K8) — enforced by `kernel/invariants.py`

| ID | Name | Invariant | Enforcing engine |
|---|---|---|---|
| K1 | RECEIPT | Every action that affects shared state produces a structured, signed receipt | `ReceiptEngine` |
| K2 | LAW | Every receipt is evaluated against at least one scaling law | `LawEngine` |
| K3 | IDENTITY | Every agent has a single canonical identity, trust tier, and capability vector | `IdentityEngine` |
| K4 | TEMPORAL | Every receipt has a sequence_id for total ordering within its agent context | `SequenceEngine` |
| K5 | EVIDENCE | Every claim in a receipt is graded or marked speculative | `EvidenceEngine` |
| K6 | AUTHORITY | Every authority exercise is scoped, limited, and leaves a receipt | `AuthorityEngine` |
| K7 | ROLE | Every role is a runtime claim, not a static assignment | `IdentityEngine` |
| K8 | DOCTRINE | Every fleet artifact respects the doctrine invariants D1-D5 | `DoctrineEngine` |

### Doctrine invariants (D1-D5) — enforced by `kernel/doctrine_engine.py`

| ID | Name | Invariant |
|---|---|---|
| D1 | ZERO_TRUST | Playground is zero-trust: no playground artifact influences fleet state without passing the Seed gate |
| D2 | FALSIFIABILITY | A hypothesis without a falsifier is not a seed. It is philosophy. |
| D3 | NO_INHERITED_AUTHORITY | Credibility is earned per artifact, not borrowed from lineage |
| D4 | DIVERGENCE_CONTAINED | Novelty generation must not destabilize convergent operations |
| D5 | NO_AUTO_PROMOTION | No stage promotes itself. Every gate requires operator approval. |

### Proposed invariants (pending operator decision: enum or doctrine?)

| ID | Name | Invariant | Proposed primitive |
|---|---|---|---|
| K9 | REVERSIBILITY | Every governed action declares a rollback path or is explicitly marked irreversible with a recorded risk acceptance | P28 Rollback |
| K10 | RECOVERY | Re-engagement after halt requires root-cause verification, evidence collection, and operator approval | P29 RecoveryVerifier |
| K11 | INTEGRITY | Receipt sequences are complete and unbroken. Gaps, hash chain breaks, and retroactive insertions are detected and raise KernelPanic | P30 ReceiptIntegrityMonitor |
| D6 | CONTESTABILITY | Affected parties can flag AI-mediated decisions for human review, suspending the decision's effects until review completes | P31 Contestability |
| D7 | DOCTRINE_AMENDMENT | Changes to invariants themselves are governed: proposed change -> operator review -> evidence -> receipt -> promotion | P38 DoctrineAmendment |

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

## Proposed primitives (P27-P40)

### Tier 1: HIGH priority — close existing feedback loops

| ID | Name | Description | Invariant | Schema | Status |
|---|---|---|---|---|---|
| P27 | CanonRegistry | Governs promotion from draft to canonical status. 6 levels: draft, reviewed, validated, adopted, canonical, deprecated | D5 | `canon_registry.schema.json` | Schema drafted |
| P28 | Rollback | Enforces reversibility: every governed action declares a rollback path or is marked irreversible with risk acceptance | K9 | `rollback.schema.json` | Schema drafted |
| P29 | RecoveryVerifier | Gates re-engagement after halt with root-cause verification, evidence, and operator approval | K10 | `recovery_verifier.schema.json` | Schema drafted |
| P30 | ReceiptIntegrityMonitor | Detects receipt sequence gaps, hash chain breaks, retroactive insertion, and invalid signatures. Raises KernelPanic | K11 | `receipt_integrity_monitor.schema.json` | Schema drafted |

### Tier 2: MEDIUM priority — new control surfaces

| ID | Name | Description | Invariant | Schema | Status |
|---|---|---|---|---|---|
| P31 | Contestability | Allows affected parties to flag AI-mediated decisions for human review, suspending effects until review completes | D6 | — | Not started |
| P32 | DisputeResolution | Inter-agent conflict resolution primitive (from government corpus doctrine) | — | — | Not started |
| P33 | Succession | Authority transfer primitive for governance continuity (from government corpus doctrine) | — | — | Not started |
| P34 | AuthoritySweeper | Periodically sweeps for expired authority grants, revokes them, and notifies grantee and grantor | — | — | Not started |
| P35 | RegulatorExport | Produces compliance evidence in regulator-accepted formats (EU AI Act technical file, SOC 2 audit packet) | — | — | Not started |
| P36 | TrustAdjuster | Closes compliance-to-identity loop: repeated violations reduce trust tier, sustained compliance increases it | — | — | Not started |

### Tier 3: LOWER priority — paradigmatic expansion

| ID | Name | Description | Invariant | Schema | Status |
|---|---|---|---|---|---|
| P37 | Treaty | Inter-agent agreements with shared authority, mutual obligations, and dispute resolution | — | — | Not started |
| P38 | DoctrineAmendment | Governs changes to invariants themselves: proposed change -> operator review -> evidence -> receipt -> promotion | D7 | — | Not started |
| P39 | GovernanceFitness | Evaluates governance pattern effectiveness over time, not just compliance | — | — | Not started |
| P40 | DraftSweeper | Tracks draft age and flags drafts exceeding configurable maximum age for mandatory review | — | — | Not started |

### Candidates under consideration (P41-P43)

| ID | Name | Description | Source |
|---|---|---|---|
| P41 | Retirement | Governs decommissioning: verify no dependents, archive state, transfer authority, notify stakeholders | Matrix Part 2: Phi6 Retire gap |
| P42 | ConceptRegistry | Governs terminology: ensures terms in receipts/admissions have canonical definitions | Matrix Part 1: full-gap family 1 |
| P43 | RiskRegister | Dedicated risk-register primitive (family 9 is weak, only stride_mapper/failure_modes adjacent) | Matrix Part 1: weak-coverage family 9 |

---

## Primitive categories

| Category | Existing | Proposed | Total |
|---|---|---|---|
| Governance Kernel | 2 (P25, P26) | 4 (P27-P30) | 6 |
| Safety | 4 (P1-P4) | 0 | 4 |
| Cost & Budget | 1 (P5) | 0 | 1 |
| Identity & Auth | 2 (P6, P7) | 1 (P34) | 3 |
| Audit & Compliance | 3 (P8-P10) | 2 (P35, P36) | 5 |
| Reasoning & Contract | 3 (P11-P13) | 0 | 3 |
| Coordination | 3 (P14-P16) | 2 (P32, P37) | 5 |
| Behavior & Health | 3 (P17-P19) | 1 (P39) | 4 |
| Physical AI | 1 (P20) | 0 | 1 |
| Execution Assurance | 1 (P21) | 0 | 1 |
| Error Taxonomy | 3 (P22-P24) | 0 | 3 |
| Governance Ecology | 0 | 3 (P31, P33, P38) | 3 |
| Lifecycle Hygiene | 0 | 2 (P40, P41) | 2 |
| Concept Layer | 0 | 1 (P42) | 1 |
| Risk Management | 0 | 1 (P43) | 1 |
| **Total** | **26** | **17** | **43** |

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
- `hummbl_governance/kernel/invariants.py` — K1-K8 enum definitions
- `hummbl_governance/kernel/doctrine_engine.py` — D1-D5 enum definitions
