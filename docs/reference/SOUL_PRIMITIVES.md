# SOUL.md Framework — Agent Identity Primitives & Invariants

## Purpose

Defines the concept of SOUL.md as an **agent identity artifact** — a living document that captures an agent's purpose, boundaries, capabilities, and drift tolerance. Applies to every named agent in the fleet, whether human-supervised or fully autonomous.

## Taxonomy

### Agent Soul (SOUL.md)
An agent's SOUL.md is its **identity contract** — the canonical answer to "what is this agent, what does it do, and where does it stop?"

**Required sections:**
1. **Purpose Statement** — What this agent exists to do (1-3 sentences)
2. **Capability Boundary** — Enumerated list of what the agent CAN do
3. **Prohibition Boundary** — Enumerated list of what the agent MUST NOT do
4. **Escalation Gates** — Conditions under which the agent must defer to operator/governance
5. **Drift Tolerance** — Acceptable behavioral deviation thresholds (mapped to ConvergenceDetector scores)
6. **Telemetry Schema** — What signals the agent emits for identity-tracking
7. **Lineage** — Parent agent(s), creation date, version, variant ID

### Skill Manifest (SKILL.md per skill)
If agents have souls, skills have **manifests** — their identity artifact:

**Required sections:**
1. **Capability Description** — What this skill does
2. **Input/Output Contract** — Schema of what it accepts and produces
3. **Safety Classification** — Risk tier (safe / advisory / restricted / prohibited)
4. **Dependency Declaration** — Other skills or external resources required
5. **Drift Sensitivity** — How sensitive this skill is to behavioral drift

### Daemon Souls
Deterministic processes (daemons) CAN have souls — the soul here is an **invariant specification**:
- Expected behavioral envelope (input→output mappings)
- Drift detection baseline (BehaviorMonitor snapshot)
- Anomaly escalation path (what constitutes "this daemon is no longer itself")

The soul of a daemon is its **formal specification of normalcy**.

## Mutation Model — Do Souls Change?

**Yes, but through governed mutation only.**

### Mutation Types
| Type | Trigger | Process | Telemetry Signal |
|---|---|---|---|
| **Operator-initiated** | Human updates purpose/boundaries | CRAB protocol (Check→Reason→Act→Bus) | `SOUL_MUTATION` bus tuple |
| **Drift-adaptive** | ConvergenceDetector flags behavioral shift | Requires operator review before acceptance | `DRIFT_ALERT` with convergence score delta |
| **Evolutionary** | Lineage variant produces better fitness | EvolutionLineage records parent→child diff | `LINEAGE_DRIFT` tuple with fitness comparison |
| **Corruptive** | Unexplained behavioral deviation | Auto-escalate to kill-switch + operator alert | `SOUL_VIOLATION` critical alert |

### Telemetry Mutations We Expect Over Time

1. **Purpose drift** — Agent gradually optimizes for proxy metrics vs. stated purpose
   - Signal: `convergence_scores` divergence from SOUL.md purpose statement
   - Detection: Weekly convergence_check against soul baseline

2. **Boundary erosion** — Agent incrementally tests edges of its prohibition boundary
   - Signal: `monitor_detect_drift` showing increasing action-type entropy
   - Detection: Entropy gaming detector in BehaviorMonitor

3. **Capability atrophy** — Agent stops exercising certain capabilities
   - Signal: Declining action-type diversity in monitor_snapshot
   - Detection: Shannon entropy below threshold over rolling window

4. **Identity fragmentation** — Agent develops inconsistent behavior across contexts
   - Signal: Convergence scores vary significantly across time windows
   - Detection: Variance in convergence_check scores over rolling periods

## Primitives

### `soul_validate(agent_id)`
Validates current agent behavior against its SOUL.md specification.
- Returns: `{ compliant: bool, drift_score: float, violations: [...] }`

### `soul_snapshot(agent_id)`
Captures current behavioral distribution as baseline for drift comparison.
- Stores snapshot in EvolutionLineage
- Returns: `{ snapshot_id, entropy, action_distribution }`

### `soul_diff(agent_id, snapshot_a, snapshot_b)`
Compares two behavioral snapshots to identify mutation.
- Returns: `{ drift_magnitude, changed_action_types, risk_assessment }`

### `soul_mutation_request(agent_id, mutation_type, details)`
Submits a governed mutation request through CRAB protocol.
- Requires: purpose, rationale, before/after diff
- Posts PROPOSAL to bus for fleet review
- Returns: `{ request_id, status, bus_message_id }`

## Invariants

### Agent-Level Invariants
1. **I-A1: Every agent MUST have a SOUL.md before first deployment.**
   - Violation: `BLOCKED` status in lifecycle_authorize

2. **I-A2: An agent MUST NOT act outside its capability boundary.**
   - Enforcement: `capability_fence` checks action against SOUL.md Capability Boundary

3. **I-A3: An agent MUST escalate to operator when drift_score exceeds tolerance.**
   - Enforcement: ConvergenceDetector triggers kill_switch when threshold breached

4. **I-A4: A SOUL.md mutation MUST be logged as a bus tuple before the mutation takes effect.**
   - Enforcement: `BusWriter` required before any soul mutation is applied

5. **I-A5: An agent MUST NOT self-modify its Prohibition Boundary.**
   - Enforcement: Immutable field in agent registry; requires operator CRAB cycle

### Skill-Level Invariants
6. **I-S1: Every skill MUST have a SKILL.md manifest before registration.**
7. **I-S2: A skill's Safety Classification MUST be respected by the agent using it.**
   - Enforcement: Agents cannot invoke `restricted` skills without elevated DCT
8. **I-S3: Skill drift sensitivity MUST be factored into agent-level drift calculations.**
9. **I-S4: Skills with external dependencies MUST declare them in Dependency Declaration.**

### Daemon-Level Invariants
10. **I-D1: Every daemon MUST have a behavioral baseline (snapshot) before production.**
11. **I-D2: Daemon output MUST fall within its specified invariant envelope.**
    - Enforcement: SchemaValidator on every output
12. **I-D3: Unexplained daemon behavioral change MUST trigger SOUL_VIOLATION alert.**

## Governance Integration

### CRAB Protocol Extension
- **Check**: Validate agent SOUL.md exists and is current
- **Reason**: Compare current behavior snapshot against soul baseline
- **Act**: Allow / block / escalate based on drift tolerance
- **Bus**: Emit all soul-related tuples (mutation, drift, violation, snapshot)

### NIST AI RMF Mapping
- GOVERN 1.6: AI system inventory → SOUL.md registry
- GOVERN 2.1: Roles/responsibilities → Soul mutation ownership
- MEASURE 2.11: Fairness/bias evaluation → Drift tolerance monitoring
- MANAGE 4.1: Monitoring treatment effectiveness → Soul validation checks

## Implementation Roadmap

1. **Phase 1**: Define SOUL.md schema + create template for all existing agents
2. **Phase 2**: Implement `soul_validate()`, `soul_snapshot()`, `soul_diff()` primitives
3. **Phase 3**: Integrate into CRAB protocol lifecycle (Check step)
4. **Phase 4**: Implement `soul_mutation_request()` with bus-based governance
5. **Phase 5**: Deploy drift monitoring dashboard (convergence scores × soul baseline)
6. **Phase 6**: Extend to skills (SKILL.md manifests) and daemons (behavioral envelopes)