"""hummbl-governance -- Governance primitives for AI agent orchestration.

Standalone, stdlib-only Python package providing:
- KillSwitch: Emergency halt system with graduated response (4 modes)
- CircuitBreaker: Automatic failure detection and recovery (3 states)
- CostGovernor: Budget tracking with soft/hard caps and ALLOW/WARN/DENY decisions
- DelegationToken: HMAC-SHA256 signed capability tokens for agent delegation
- AuditLog: Append-only JSONL governance audit log with rotation and retention
- AgentRegistry: Configurable agent identity, aliases, and trust tiers
- SchemaValidator: Stdlib-only JSON Schema validator (Draft 2020-12 subset)

All modules use only Python stdlib. Zero third-party runtime dependencies.

Copyright 2026 HUMMBL, LLC. Licensed under Apache 2.0.
"""

__version__ = "0.1.0"

from hummbl_governance.kill_switch import KillSwitch, KillSwitchMode
from hummbl_governance.circuit_breaker import CircuitBreaker, CircuitBreakerState
from hummbl_governance.cost_governor import CostGovernor
from hummbl_governance.delegation import DelegationToken, DelegationTokenManager
from hummbl_governance.audit_log import AuditLog
from hummbl_governance.identity import AgentRegistry
from hummbl_governance.schema_validator import SchemaValidator

__all__ = [
    "__version__",
    "KillSwitch",
    "KillSwitchMode",
    "CircuitBreaker",
    "CircuitBreakerState",
    "CostGovernor",
    "DelegationToken",
    "DelegationTokenManager",
    "AuditLog",
    "AgentRegistry",
    "SchemaValidator",
]
