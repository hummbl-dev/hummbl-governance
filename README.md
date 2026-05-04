# hummbl-governance

[![PyPI](https://img.shields.io/pypi/v/hummbl-governance)](https://pypi.org/project/hummbl-governance/)
[![CI](https://github.com/hummbl-dev/hummbl-governance/actions/workflows/ci.yml/badge.svg)](https://github.com/hummbl-dev/hummbl-governance/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/hummbl-governance)](https://pypi.org/project/hummbl-governance/)
[![Tests](https://img.shields.io/badge/tests-637%20passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)]()

**hummbl-governance** is a Python library that provides 25 governance primitives for AI agent orchestration, including kill switch, circuit breaker, cost governor, delegation tokens, reasoning engine, execution assurance, physical-AI safety, and audit logging. It has zero third-party dependencies (stdlib only), 637 passing tests, and supports Python 3.11 through 3.14.

```bash
pip install hummbl-governance
```

## What's New in v0.5.0

- **LamportClock hardening** -- causal integrity checks for distributed audit logs; epoch-aware state handling across agents.
- **EvolutionLineage** -- in-memory lineage tracking for eAI variants; `VariantRecord`, `ModificationRecord`, `EvolutionDriftReport`.
- **FailureModes catalog** -- structured `FailureModeRecord` and `ErrorRecord` taxonomy; `all_failure_modes()`, `classify_subclass()`, `get_errors_for_fm()`.
- **Errors taxonomy** -- `HummblError`, `FailureMode`, `fm_to_errors()` as top-level exports.

### v0.4.0 highlights
- **KinematicGovernor** -- deterministic motion constraints (velocity, force, jerk) for physical-AI safety.
- **pHRISafetyMonitor** -- graduated pHRI safety modes (NORMAL/CAUTION/EMERGENCY).
- **Execution Assurance Layer (EAL)** -- Arbiter-verified code quality in execution receipts (`E_CODE_QUALITY_FAIL`).
- **ReasoningEngine** -- structured governance reasoning with rule application, conflict detection, and decision tracing.
- **ValidationError** -- top-level export from `hummbl_governance`.

## Usage Example

```python
from hummbl_governance import KillSwitch, KillSwitchMode, CircuitBreaker, CostGovernor

ks = KillSwitch()
ks.engage(KillSwitchMode.HALT_ALL, reason="Budget exceeded", triggered_by="cost_governor")
print(ks.check_task_allowed("data_export"))  # {"allowed": False, ...}

cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
result = cb.call(my_function, arg1, arg2)  # Opens after 3 failures

gov = CostGovernor(":memory:", soft_cap=50.0, hard_cap=100.0)
gov.record_usage(provider="anthropic", model="claude-4", tokens_in=1000, tokens_out=500, cost=0.015)
status = gov.check_budget_status()  # status.decision in ("ALLOW", "WARN", "DENY")
```

## Features

- **25 governance primitives** covering safety, cost, identity, compliance, reasoning, coordination, physical-AI, and execution assurance
- **637 tests** with full coverage across all modules
- **Zero dependencies** -- Python stdlib only, no pip conflicts
- **Thread-safe** -- all modules use appropriate locking primitives
- **Independently importable** -- use only the modules you need
- **Python 3.11 - 3.14** supported and tested

## All 25 Primitives

| Module | Description |
|--------|-------------|
| `kill_switch` | Emergency halt system with 4 graduated modes (DISENGAGED, HALT_NONCRITICAL, HALT_ALL, EMERGENCY) |
| `circuit_breaker` | Automatic failure detection and recovery across 3 states (CLOSED, HALF_OPEN, OPEN) |
| `cost_governor` | Budget tracking with soft/hard caps and ALLOW/WARN/DENY decisions |
| `delegation` | HMAC-SHA256 signed capability tokens for agent delegation chains |
| `audit_log` | Append-only JSONL governance audit log with rotation and retention |
| `identity` | Agent registry with configurable aliases, trust tiers, and canonicalization |
| `schema_validator` | Stdlib-only JSON Schema validator (Draft 2020-12 subset) with top-level `ValidationError` export |
| `coordination_bus` | Append-only TSV message bus with flock locking and HMAC signing |
| `compliance_mapper` | Map governance traces to SOC2, GDPR, and OWASP controls |
| `health_probe` | Composable health probe framework with latency tracking |
| `output_validator` | Rule-based content validation for agent outputs (PII detection, injection detection, blocklists) |
| `capability_fence` | Soft sandbox enforcing capability boundaries per agent role |
| `stride_mapper` | Map agent interactions to STRIDE threat categories with mitigation suggestions |
| `lifecycle` | NIST AI RMF orchestrator composing kill switch, circuit breaker, cost governor, and audit log |
| `contract_net` | Market-based task allocation protocol for multi-agent systems |
| `convergence_guard` | Detect instrumental convergence patterns in agent behavior |
| `reward_monitor` | Behavioral drift and reward gaming detector |
| `lamport_clock` | Hardened logical clock for causal ordering of distributed agent events (v0.5.0) |
| `reasoning` | Structured governance reasoning engine with rule application, conflict detection, and decision tracing |
| `eal` | Execution Assurance Layer -- Arbiter-verified code quality in execution receipts |
| `physical_governor` | Kinematic constraints and pHRI safety modes for physical-AI deployments |
| `errors` | `HummblError`, `FailureMode`, and `fm_to_errors()` -- typed error taxonomy |
| `failure_modes` | Structured failure mode catalog with classification and error cross-reference |
| `evolution_lineage` | In-memory lineage tracking for eAI variants with drift detection |
| `ValidationError` | Top-level exception for schema validation failures (exported from `schema_validator`) |

## Why hummbl-governance?

**No dependency conflicts.** hummbl-governance uses only Python stdlib. It installs in under 1 second and never conflicts with your existing packages. Every governance module is independently importable -- use `KillSwitch` without pulling in `CostGovernor`.

**Built for multi-agent systems.** The library provides primitives that AI orchestration platforms actually need: delegation tokens with HMAC-SHA256 signing, a coordination bus with mutual exclusion, kill switch with 4 graduated halt modes, and circuit breakers wrapping external adapters.

**Compliance-aware by design.** The `compliance_mapper` maps governance events to SOC2, GDPR, and OWASP controls. The `stride_mapper` produces STRIDE threat analysis for agent interactions. These modules generate audit evidence, not just runtime safety.

**Production-tested.** The governance primitives were extracted from [founder-mode](https://github.com/hummbl-dev/founder-mode), a multi-runtime AI orchestration platform with 15,600+ tests and 14 CI workflows across its full surface. The governance layer extracted here has 637 dedicated tests and runs daily in production.

## hummbl-governance vs Alternatives

| Capability | hummbl-governance | Raw stdlib | LangChain Guardrails | CrewAI Guardrails |
|------------|:-----------------:|:----------:|:--------------------:|:-----------------:|
| Zero dependencies | Yes | Yes | No (requires langchain) | No (requires crewai) |
| Kill switch (graduated modes) | 4 modes | DIY | No | No |
| Circuit breaker | 3 states | DIY | No | No |
| Cost governance (budget caps) | Soft + hard caps | DIY | No | No |
| Delegation tokens (HMAC signed) | Yes | DIY | No | No |
| Append-only audit log | Yes | DIY | Partial | No |
| Agent identity registry | Yes | DIY | No | No |
| STRIDE threat mapping | Yes | No | No | No |
| SOC2/GDPR/OWASP compliance mapping | Yes | No | No | No |
| JSON Schema validation (stdlib) | Draft 2020-12 | No | Requires jsonschema | Requires pydantic |
| Governance reasoning engine | Yes | No | No | No |
| Thread-safe | Yes | Varies | Varies | Varies |
| Modules work standalone | Yes | N/A | No (framework lock-in) | No (framework lock-in) |

## OWASP Top 10 for Agentic Applications (2026) Coverage

hummbl-governance addresses all 10 risks in the [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/). Every row below links to the primitive and its test suite.

| OWASP Risk | Primitive(s) | Tests | How |
|------------|-------------|-------|-----|
| **ASI01** Agent Goal Hijack | [`KillSwitch`](hummbl_governance/kill_switch.py) | [27](tests/test_kill_switch.py) | 4-mode graduated shutdown (DISENGAGED → EMERGENCY). Survives process restart. Stops hijacked agents mid-execution. |
| **ASI02** Tool Misuse | [`CapabilityFence`](hummbl_governance/capability_fence.py) | [27](tests/test_capability_fence.py) | Allowlist/blocklist enforcement per tool. Agents cannot invoke tools outside their granted capabilities. |
| **ASI03** Identity & Privilege Abuse | [`DelegationTokenManager`](hummbl_governance/delegation.py), [`AgentRegistry`](hummbl_governance/identity.py) | [16](tests/test_delegation.py) + [26](tests/test_identity.py) | HMAC-signed scoped tokens with chain-depth limits. Identity registry with trust tiers and alias canonicalization. |
| **ASI04** Supply Chain | Zero dependencies | — | Stdlib-only. No transitive dependencies to compromise. `pip audit` finds nothing because there is nothing to audit. |
| **ASI05** Unexpected Code Execution | [`OutputValidator`](hummbl_governance/output_validator.py), [`InjectionDetector`](hummbl_governance/output_validator.py) | [49](tests/test_output_validator.py) | Prompt injection detection, blocked-term filtering, and content validation before agent output reaches downstream systems. |
| **ASI06** Memory & Context Poisoning | [`BusWriter`](hummbl_governance/coordination_bus.py), [`AuditLog`](hummbl_governance/audit_log.py) | [63](tests/test_coordination_bus.py) + [17](tests/test_audit_log.py) | Append-only governance bus with content hashing. Tamper-evident audit log. Poisoned entries are detectable. |
| **ASI07** Insecure Inter-Agent Comms | [`LamportClock`](hummbl_governance/lamport_clock.py), [`ContractNetManager`](hummbl_governance/contract_net.py) | [20](tests/test_lamport_clock.py) + [19](tests/test_contract_net.py) | Hardened logical clocks for causal ordering. Contract Net protocol for structured multi-agent task allocation with bid verification. |
| **ASI08** Cascading Failures | [`CircuitBreaker`](hummbl_governance/circuit_breaker.py), [`HealthProbe`](hummbl_governance/health_probe.py) | [17](tests/test_circuit_breaker.py) + [30](tests/test_health_probe.py) | CLOSED/HALF_OPEN/OPEN state machine isolates failing components. Health probes detect degradation before cascade. |
| **ASI09** Human-Agent Trust Exploitation | [`ReasoningEngine`](hummbl_governance/reasoning.py), [`ComplianceMapper`](hummbl_governance/compliance_mapper.py) | [7](tests/test_explain.py) + [34](tests/test_compliance_mapper.py) | Structured decision traces explain *why* a governance decision was made. Compliance mapping to NIST/ISO provides external validation anchor. |
| **ASI10** Rogue Agents | [`BehaviorMonitor`](hummbl_governance/reward_monitor.py), [`GovernanceLifecycle`](hummbl_governance/lifecycle.py) | [20](tests/test_reward_monitor.py) + [17](tests/test_lifecycle.py) | Jensen-Shannon divergence detects behavioral drift from baseline. Lifecycle FSM enforces PROVISIONED → ACTIVE → SUSPENDED → DECOMMISSIONED transitions. |

**Total: 637 tests across 25 primitives. 10/10 OWASP coverage. Zero dependencies.**

For the formal governance primitive underlying all 10 mitigations, see [The Governance Tuple](https://doi.org/10.5281/zenodo.19646940) (Bowlby, 2026).

## Research

The evidence base behind hummbl-governance is documented in the [AI Slop Crisis](https://github.com/hummbl-dev/hummbl-dev/tree/main/docs/research/ai-slop-crisis) research corpus:

- [Why Libraries, Not Platforms](https://github.com/hummbl-dev/hummbl-dev/tree/main/docs/research/ai-slop-crisis#why-libraries-not-platforms) -- the architectural thesis behind stdlib-only, independently importable governance primitives
- [Vendor Comparison Table](https://github.com/hummbl-dev/hummbl-dev/tree/main/docs/research/ai-slop-crisis#vendor-comparison) -- how hummbl-governance compares to platform-locked alternatives across dependency count, modularity, and compliance coverage

## Newsletter

Subscribe to the **HUMMBL Slop Tracker** for monthly AI governance intelligence: [hummbl.substack.com](https://hummbl.substack.com)

Read [Issue #1](https://hummbl.substack.com/p/issue-1) for the inaugural edition.

## FAQ

### How do I add a kill switch to my AI agent system?

Install hummbl-governance and use the `KillSwitch` class. It provides 4 graduated modes: `DISENGAGED` (normal operation), `HALT_NONCRITICAL` (stop non-essential tasks), `HALT_ALL` (stop everything except monitoring), and `EMERGENCY` (immediate full shutdown). Call `ks.check_task_allowed("task_name")` before each agent action.

```python
from hummbl_governance import KillSwitch, KillSwitchMode
ks = KillSwitch()
ks.engage(KillSwitchMode.HALT_NONCRITICAL, reason="High error rate", triggered_by="monitor")
```

### How do I track AI API costs and enforce budget limits?

Use `CostGovernor` with soft and hard caps. Record each API call with `record_usage()`, then call `check_budget_status()` to get an ALLOW, WARN, or DENY decision. The soft cap triggers warnings; the hard cap blocks further spending.

```python
from hummbl_governance import CostGovernor
gov = CostGovernor(":memory:", soft_cap=50.0, hard_cap=100.0)
gov.record_usage(provider="openai", model="gpt-4", tokens_in=500, tokens_out=200, cost=0.02)
```

### How do I implement delegation tokens for multi-agent AI systems?

Use `DelegationTokenManager` to create HMAC-SHA256 signed tokens that grant specific operations to specific agents. Tokens are scoped by issuer, subject, allowed operations, and an optional binding to a task and contract. Validate tokens before executing delegated actions.

```python
from hummbl_governance import DelegationTokenManager
from hummbl_governance.delegation import TokenBinding
mgr = DelegationTokenManager(secret=b"shared-secret")
token = mgr.create_token(issuer="orchestrator", subject="worker", ops_allowed=["read", "write"],
                         binding=TokenBinding("task-1", "contract-1"))
valid, error = mgr.validate_token(token)
```

### Does hummbl-governance work without any third-party packages?

Yes. Every module uses only Python stdlib (3.11+). There are zero entries in the `dependencies` list in `pyproject.toml`. Test dependencies (pytest) are isolated in `[test]` extras. This means no dependency conflicts, no supply chain risk from transitive dependencies, and fast installs.

### How do I generate compliance evidence for SOC2 or GDPR from my AI system?

Use `ComplianceMapper` to map governance audit log entries to compliance framework controls. Pass your `AuditLog` entries through the mapper to produce a `ComplianceReport` that links each governance event to the relevant SOC2, GDPR, or OWASP control. Use `StrideMapper` for threat-level analysis of agent interactions.

```python
from hummbl_governance import ComplianceMapper, AuditLog
mapper = ComplianceMapper()
report = mapper.map_events(audit_entries)  # Returns ComplianceReport with control mappings
```

## Extended Quick Start

```python
from hummbl_governance import (
    KillSwitch, KillSwitchMode,
    CircuitBreaker,
    CostGovernor,
    DelegationToken, DelegationTokenManager,
    AuditLog,
    AgentRegistry,
    SchemaValidator,
)

# Kill Switch
ks = KillSwitch()
ks.engage(KillSwitchMode.HALT_ALL, reason="Budget exceeded", triggered_by="cost_governor")
result = ks.check_task_allowed("data_export")
# result["allowed"] == False

# Circuit Breaker
cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
result = cb.call(some_function, arg1, arg2)

# Cost Governor
gov = CostGovernor(":memory:", soft_cap=50.0, hard_cap=100.0)
gov.record_usage(provider="anthropic", model="claude-4", tokens_in=1000, tokens_out=500, cost=0.015)
status = gov.check_budget_status()
# status.decision in ("ALLOW", "WARN", "DENY")

# Delegation Tokens
mgr = DelegationTokenManager(secret=b"my-secret")
from hummbl_governance.delegation import TokenBinding
token = mgr.create_token(
    issuer="orchestrator", subject="worker",
    ops_allowed=["read"], binding=TokenBinding("task-1", "contract-1"),
)
valid, error = mgr.validate_token(token)

# Agent Registry
registry = AgentRegistry()
registry.register_agent("orchestrator", trust="high")
registry.add_alias("orch-1", "orchestrator")
registry.canonicalize("orch-1")  # -> "orchestrator"
```

## Design Principles

- **Zero third-party runtime dependencies** -- stdlib only (Python 3.11+)
- **Thread-safe** -- all modules use appropriate locking
- **Configurable** -- no hardcoded agent names or paths
- **Independently importable** -- each module works standalone

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
python -m pytest tests/ -v
```

## HUMMBL Ecosystem

This repo is part of the [HUMMBL](https://github.com/hummbl-dev) cognitive AI architecture. Related repos:

| Repo | Purpose |
|------|---------|
| [base120](https://github.com/hummbl-dev/base120) | Deterministic cognitive framework -- 120 mental models across 6 transformations |
| [mcp-server](https://github.com/hummbl-dev/mcp-server) | Model Context Protocol server for Base120 integration |
| [arbiter](https://github.com/hummbl-dev/arbiter) | Agent-aware code quality scoring and attribution |
| [agentic-patterns](https://github.com/hummbl-dev/agentic-patterns) | Stdlib-only safety patterns for agentic AI systems |
| [governed-iac-reference](https://github.com/hummbl-dev/governed-iac-reference) | Reference architecture for governed infrastructure-as-code |

## Links

- [PyPI](https://pypi.org/project/hummbl-governance/)
- [GitHub](https://github.com/hummbl-dev/hummbl-governance)
- [hummbl.io](https://hummbl.io)
- [Linktree](https://linktr.ee/hummbl)
- [HUMMBL Slop Tracker (Substack)](https://hummbl.substack.com)

## License

Apache 2.0. Copyright 2026 HUMMBL, LLC.
