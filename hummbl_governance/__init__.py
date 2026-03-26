"""hummbl-governance -- Governance primitives for AI agent orchestration.

Standalone, stdlib-only Python package providing:
- KillSwitch: Emergency halt system with graduated response (4 modes)
- CircuitBreaker: Automatic failure detection and recovery (3 states)
- CostGovernor: Budget tracking with soft/hard caps and ALLOW/WARN/DENY decisions
- DelegationToken: HMAC-SHA256 signed capability tokens for agent delegation
- AuditLog: Append-only JSONL governance audit log with rotation and retention
- AgentRegistry: Configurable agent identity, aliases, and trust tiers
- SchemaValidator: Stdlib-only JSON Schema validator (Draft 2020-12 subset)
- BusWriter: Append-only TSV coordination bus with flock locking and HMAC signing
- ComplianceMapper: Map governance traces to SOC2, GDPR, and OWASP controls
- HealthCollector: Composable health probe framework with latency tracking
- OutputValidator: Rule-based content validation for agent outputs (ASI-06)
- CapabilityFence: Soft sandbox enforcing capability boundaries (ASI-07)

All modules use only Python stdlib. Zero third-party runtime dependencies.

Copyright 2026 HUMMBL, LLC. Licensed under Apache 2.0.
"""

__version__ = "0.2.0"

from hummbl_governance.kill_switch import KillSwitch, KillSwitchMode
from hummbl_governance.circuit_breaker import CircuitBreaker, CircuitBreakerState
from hummbl_governance.cost_governor import CostGovernor
from hummbl_governance.delegation import DelegationToken, DelegationTokenManager
from hummbl_governance.audit_log import AuditLog
from hummbl_governance.identity import AgentRegistry
from hummbl_governance.schema_validator import SchemaValidator
try:
    from hummbl_governance.coordination_bus import BusWriter, PolicyLevel
except ImportError:
    BusWriter = None  # fcntl not available on Windows
    PolicyLevel = None
from hummbl_governance.compliance_mapper import ComplianceMapper, ComplianceReport
from hummbl_governance.health_probe import HealthCollector, HealthProbe, HealthReport, ProbeResult
from hummbl_governance.lamport_clock import LamportClock
from hummbl_governance.stride_mapper import StrideMapper, StrideReport, Interaction, ThreatFinding
from hummbl_governance.lifecycle import GovernanceLifecycle, AuthorizationDecision, GovernanceStatus
from hummbl_governance.contract_net import ContractNetManager, Bid, TaskAnnouncement, ContractPhase
from hummbl_governance.convergence_guard import ConvergenceDetector, ConvergentGoal, ConvergenceAlert
from hummbl_governance.reward_monitor import BehaviorMonitor, DriftReport
from hummbl_governance.output_validator import (
    OutputValidator, PIIDetector, InjectionDetector, LengthBounds, BlocklistFilter,
)
from hummbl_governance.capability_fence import CapabilityFence, CapabilityDenied

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
    "BusWriter",
    "PolicyLevel",
    "ComplianceMapper",
    "ComplianceReport",
    "HealthCollector",
    "HealthProbe",
    "HealthReport",
    "ProbeResult",
    "LamportClock",
    "StrideMapper",
    "StrideReport",
    "Interaction",
    "ThreatFinding",
    "GovernanceLifecycle",
    "AuthorizationDecision",
    "GovernanceStatus",
    "ContractNetManager",
    "Bid",
    "TaskAnnouncement",
    "ContractPhase",
    "ConvergenceDetector",
    "ConvergentGoal",
    "ConvergenceAlert",
    "BehaviorMonitor",
    "DriftReport",
    "OutputValidator",
    "PIIDetector",
    "InjectionDetector",
    "LengthBounds",
    "BlocklistFilter",
    "CapabilityFence",
    "CapabilityDenied",
]
