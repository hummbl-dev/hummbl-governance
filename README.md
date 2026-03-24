# hummbl-governance

[![PyPI](https://img.shields.io/pypi/v/hummbl-governance)](https://pypi.org/project/hummbl-governance/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-476%20passing-green)]()

Governance primitives for AI agent orchestration. Zero third-party dependencies. Stdlib-only Python 3.11+.

```bash
pip install hummbl-governance
```

## Modules

| Module | Description |
|--------|-------------|
| `audit_log` | Append-only JSONL governance audit log |
| `capability_fence` | Soft sandbox enforcing capability boundaries (ASI-07) |
| `circuit_breaker` | Automatic failure detection and recovery (3 states) |
| `compliance_mapper` | Map governance traces to SOC2, GDPR, and OWASP controls |
| `contract_net` | Market-based task allocation for multi-agent systems |
| `convergence_guard` | Detect instrumental convergence in agent behavior |
| `coordination_bus` | Append-only TSV message bus with HMAC signing and policy levels |
| `cost_governor` | Budget tracking with soft/hard caps |
| `delegation` | HMAC-SHA256 signed capability tokens for agent delegation |
| `health_probe` | Generic health checking framework |
| `identity` | Configurable agent identity, aliases, and trust tiers |
| `kill_switch` | Emergency halt system with 4 graduated modes |
| `lamport_clock` | Logical clock for causal ordering of distributed events |
| `lifecycle` | NIST AI RMF orchestrator composing existing modules |
| `output_validator` | Rule-based content validation for agent outputs (ASI-06) |
| `reward_monitor` | Behavioral drift and reward gaming detector |
| `schema_validator` | Stdlib-only JSON Schema validator (Draft 2020-12 subset) |
| `stride_mapper` | Map agent interactions to STRIDE threat categories |

## Installation

```bash
pip install hummbl-governance
```

## Quick Start

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

Learn more at [hummbl.io](https://hummbl.io).

## License

Apache 2.0. Copyright 2026 HUMMBL, LLC.
