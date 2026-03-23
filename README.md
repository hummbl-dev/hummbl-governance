# hummbl-governance

[![PyPI](https://img.shields.io/pypi/v/hummbl-governance)](https://pypi.org/project/hummbl-governance/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-157%20passing-green)]()

Governance primitives for AI agent orchestration. Zero third-party dependencies. Stdlib-only Python 3.11+.

```bash
pip install hummbl-governance
```

## Modules

| Module | Description |
|--------|-------------|
| `KillSwitch` | Emergency halt system with 4 graduated modes |
| `CircuitBreaker` | Automatic failure detection and recovery (3 states) |
| `CostGovernor` | SQLite-backed budget tracking with ALLOW/WARN/DENY decisions |
| `DelegationToken` | HMAC-SHA256 signed capability tokens for agent delegation |
| `AuditLog` | Append-only JSONL governance audit log with rotation |
| `AgentRegistry` | Configurable agent identity, aliases, and trust tiers |
| `SchemaValidator` | Stdlib-only JSON Schema validator (Draft 2020-12 subset) |

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

## License

Apache 2.0. Copyright 2026 HUMMBL, LLC.
