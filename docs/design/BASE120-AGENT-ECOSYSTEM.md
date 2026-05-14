# Base120 Agent Ecosystem — Design Document

## Concept: 600 Named Contributor Agents

Every HUMMBL Base120 mental model becomes an **agent class**, and each model's top 5 primary contributors (sourced from `hummbl-bibliography`) become **named agent instances** grounded in evidence.

### Architecture

```
Base120 Mental Model (Agent Class)
 ├── Contributor Agent 1 (named, SOUL.md, DCT-bound)
 ├── Contributor Agent 2
 ├── Contributor Agent 3
 ├── Contributor Agent 4
 └── Contributor Agent 5
```

- **120 mental models × 5 contributors = 600 named agents**
- **No contributor duplication** across models (each agent is unique)
- **All grounded** in hummbl-bibliography entries — every knowledge claim traceable to source

### Agent Identity Stack

Each of the 600 agents has:

| Layer | Artifact | Purpose |
|---|---|---|
| **SOUL.md** | Agent identity contract | Purpose, boundaries, capabilities, prohibitions |
| **SKILL.md** (×N) | Skill manifest | Each skill the agent can invoke, with safety classification |
| **DCT** | Delegation token | Cryptographically scoped permissions |
| **Lineage** | EvolutionLineage entry | Parent model, creation provenance, fitness baseline |
| **Telemetry** | Convergence + drift tracking | Behavioral monitoring over time |

### Mental Model → Agent Mapping

Each mental model agent class has:
- **Canonical reasoning pattern**: The model's transformation (e.g., DE1 = "Define the problem by examining the obvious")
- **Applicability criteria**: When this model should be invoked
- **Output contract**: What the agent produces (analysis, recommendation, reframe)
- **Boundary conditions**: When to defer to other models or to operator

### Contributor Agents

Each contributor agent:
- **Inherits** the reasoning pattern of their parent mental model
- **Is specialized** by their bibliographic grounding — they think through the lens of their source material
- **Has a knowledge boundary** defined by their bibliography entries
- **Can collaborate** with other contributor agents across models (cross-pollination)

### SOUL.md for Agents vs. SOUL.md for Mental Models

| Aspect | Model-Level Soul | Contributor Agent Soul |
|---|---|---|
| Purpose | Reasoning pattern description | Apply this pattern through evidence-based lens |
| Capabilities | Problem types this model addresses | Same + bibliographic expertise areas |
| Boundaries | When NOT to use this model | Knowledge boundary from bibliography |
| Drift Tolerance | Convergence threshold for model output | Lower tolerance — contributor identity is more specific |
| Telemetry | Model-level convergence scores | Agent-level convergence + model-level convergence |

## Do Skills Have Souls? → Skill Manifests

Skills don't have SOUL.md — they have **SKILL.md manifests**:

| SOUL.md (Agents) | SKILL.md (Skills) |
|---|---|
| Purpose, boundaries, prohibitions | Capability description, I/O contract |
| Drift tolerance | Safety classification |
| Telemetry schema | Dependency declaration |
| Lineage | Drift sensitivity |
| Escalation gates | Input/output validation rules |

Skills are **tools** — they don't have agency, so they don't need souls. But they do need manifests for safe composition.

## Do Daemons Have Souls? → Behavioral Envelopes

Deterministic daemons CAN have souls, reframed as **behavioral envelopes**:

- **Formal specification of expected I/O mappings**
- **Drift detection baseline** (BehaviorMonitor snapshot)
- **Anomaly escalation**: if daemon output deviates from envelope → SOUL_VIOLATION alert
- **The soul of a daemon is its formal specification of normalcy**

This is actually the most interesting angle — a daemon with a soul is a daemon that can detect when it's "no longer itself."

## Do SOUL.md Files Change Over Time? → Governed Mutation

**Yes, but only through governed mutation:**

### Mutation Types
| Type | Trigger | Process | Telemetry Signal |
|---|---|---|---|
| **Operator-initiated** | Human updates purpose/boundaries | CRAB protocol (Check→Reason→Act→Bus) | `SOUL_MUTATION` bus tuple |
| **Drift-adaptive** | ConvergenceDetector flags shift | Requires operator review before acceptance | `DRIFT_ALERT` with convergence delta |
| **Evolutionary** | Lineage variant shows better fitness | EvolutionLineage records parent→child diff | `LINEAGE_DRIFT` tuple |
| **Corruptive** | Unexplained behavioral deviation | Auto-escalate to kill-switch + alert | `SOUL_VIOLATION` critical alert |

### Expected Telemetry Mutations Over Time

1. **Purpose drift**: Agent optimizes for proxy metrics vs. stated purpose
   - Signal: convergence_scores divergence from SOUL.md purpose
   - Detection: Weekly convergence_check against soul baseline

2. **Boundary erosion**: Agent incrementally tests prohibition edges
   - Signal: Increasing action-type entropy in monitor_snapshot
   - Detection: Entropy gaming detector

3. **Capability atrophy**: Agent stops exercising certain capabilities
   - Signal: Declining action-type diversity
   - Detection: Shannon entropy below threshold

4. **Identity fragmentation**: Inconsistent behavior across contexts
   - Signal: Convergence score variance across time windows
   - Detection: Rolling variance analysis

## Primitives

### `soul_validate(agent_id)`
Validates current behavior against SOUL.md specification.
- Returns: `{ compliant: bool, drift_score: float, violations: [...] }`

### `soul_snapshot(agent_id)`
Captures behavioral distribution as drift baseline.
- Stores in EvolutionLineage
- Returns: `{ snapshot_id, entropy, action_distribution }`

### `soul_diff(agent_id, snapshot_a, snapshot_b)`
Compares behavioral snapshots to identify mutation.
- Returns: `{ drift_magnitude, changed_action_types, risk_assessment }`

### `soul_mutation_request(agent_id, mutation_type, details)`
Submits governed mutation through CRAB protocol.
- Requires: purpose, rationale, before/after diff
- Posts PROPOSAL to bus for fleet review
- Returns: `{ request_id, status, bus_message_id }`

## Invariants

### Agent Invariants
- **I-A1**: Every agent MUST have SOUL.md before first deployment
  - Enforcement: `BLOCKED` in lifecycle_authorize if missing
- **I-A2**: Agent MUST NOT act outside capability boundary
  - Enforcement: `capability_fence` checks action against SOUL.md
- **I-A3**: Agent MUST escalate when drift_score exceeds tolerance
  - Enforcement: ConvergenceDetector triggers kill_switch
- **I-A4**: SOUL.md mutation MUST be bus-logged before taking effect
  - Enforcement: BusWriter required before mutation applies
- **I-A5**: Agent MUST NOT self-modify Prohibition Boundary
  - Enforcement: Immutable field in AgentRegistry; operator CRAB required

### Skill Invariants
- **I-S1**: Every skill MUST have SKILL.md before registration
- **I-S2**: Safety Classification MUST be respected by invoking agent
- **I-S3**: Skill drift sensitivity MUST factor into agent drift calculations
- **I-S4**: External dependencies MUST be declared

### Daemon Invariants
- **I-D1**: Every daemon MUST have behavioral baseline before production
- **I-D2**: Daemon output MUST fall within invariant envelope
- **I-D3**: Unexplained change MUST trigger SOUL_VIOLATION alert

## Implementation Roadmap

1. **Phase 1**: Define SOUL.md + SKILL.md schemas; create templates
2. **Phase 2**: Implement `soul_validate`, `soul_snapshot`, `soul_diff`
3. **Phase 3**: Integrate into CRAB protocol (Check step)
4. **Phase 4**: Implement `soul_mutation_request` with bus governance
5. **Phase 5**: Scaffold 600 contributor agents from bibliography
6. **Phase 6**: Deploy drift monitoring dashboard

## Scoped Boundaries — The Key Insight

Every agent — whether human-supervised or fully autonomous — operates within **scoped boundaries**:

- **DCT scope binding**: What actions the agent can perform
- **Capability fence**: What tools/resources the agent can access
- **Knowledge boundary**: What the agent knows (bibliography-grounded)
- **Drift tolerance**: How much behavioral deviation is acceptable
- **Escalation gates**: When to defer to operator or governance

These are not optional safety features — they are **constitutive** of agent identity. An agent without boundaries is not an agent; it's a process.