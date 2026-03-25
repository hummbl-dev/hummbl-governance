# hummbl-governance

[![PyPI](https://img.shields.io/pypi/v/hummbl-governance)](https://pypi.org/project/hummbl-governance/)
[![CI](https://github.com/hummbl-dev/hummbl-governance/actions/workflows/ci.yml/badge.svg)](https://github.com/hummbl-dev/hummbl-governance/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/hummbl-governance)](https://pypi.org/project/hummbl-governance/)
[![Tests](https://img.shields.io/badge/tests-476%20passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)]()

**hummbl-governance** is a Python library that provides 18 governance modules for AI agent orchestration, including kill switch, circuit breaker, cost governor, delegation tokens, and audit logging. It has zero third-party dependencies (stdlib only), 476 passing tests, and supports Python 3.11 through 3.14.

```bash
pip install hummbl-governance
```

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

- **18 modules** covering safety, cost, identity, compliance, and coordination
- **476 tests** with full coverage across all modules
- **Zero dependencies** -- Python stdlib only, no pip conflicts
- **Thread-safe** -- all modules use appropriate locking primitives
- **Independently importable** -- use only the modules you need
- **Python 3.11 - 3.14** supported and tested

## All 18 Modules

| Module | Description |
|--------|-------------|
| `kill_switch` | Emergency halt system with 4 graduated modes (DISENGAGED, HALT_NONCRITICAL, HALT_ALL, EMERGENCY) |
| `circuit_breaker` | Automatic failure detection and recovery across 3 states (CLOSED, HALF_OPEN, OPEN) |
| `cost_governor` | Budget tracking with soft/hard caps and ALLOW/WARN/DENY decisions |
| `delegation` | HMAC-SHA256 signed capability tokens for agent delegation chains |
| `audit_log` | Append-only JSONL governance audit log with rotation and retention |
| `identity` | Agent registry with configurable aliases, trust tiers, and canonicalization |
| `schema_validator` | Stdlib-only JSON Schema validator (Draft 2020-12 subset) |
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
| `lamport_clock` | Logical clock for causal ordering of distributed agent events |

## Why hummbl-governance?

**No dependency conflicts.** hummbl-governance uses only Python stdlib. It installs in under 1 second and never conflicts with your existing packages. Every governance module is independently importable -- use `KillSwitch` without pulling in `CostGovernor`.

**Built for multi-agent systems.** The library provides primitives that AI orchestration platforms actually need: delegation tokens with HMAC-SHA256 signing, a coordination bus with mutual exclusion, kill switch with 4 graduated halt modes, and circuit breakers wrapping external adapters.

**Compliance-aware by design.** The `compliance_mapper` maps governance events to SOC2, GDPR, and OWASP controls. The `stride_mapper` produces STRIDE threat analysis for agent interactions. These modules generate audit evidence, not just runtime safety.

**Production-tested.** All 18 modules were extracted from [founder-mode](https://github.com/foundermode-ai/founder-mode), a multi-runtime AI orchestration platform with 7,700+ tests and 14 CI workflows. The governance layer runs daily in production.

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
| Thread-safe | Yes | Varies | Varies | Varies |
| Modules work standalone | Yes | N/A | No (framework lock-in) | No (framework lock-in) |

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

## License

Apache 2.0. Copyright 2026 HUMMBL, LLC.
