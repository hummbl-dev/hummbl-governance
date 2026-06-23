# Copyright 2024-2026 HUMMBL, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""hummbl-governance -- Governance primitives for AI agent orchestration.

Standalone, stdlib-only Python package providing:
- Kernel: Governance operating system — receipts, identity, roles, laws, evidence (v1.1.0)
- KillSwitch: Emergency halt system with graduated response (4 modes)
- CircuitBreaker: Automatic failure detection and recovery (3 states)
- CostGovernor: Budget tracking with soft/hard caps and ALLOW/WARN/DENY decisions
- DelegationToken: HMAC-SHA256 signed capability tokens for agent delegation
- AuditLog: Append-only JSONL governance audit log with rotation and retention
- AgentRegistry: Configurable agent identity, aliases, and trust tiers
- SchemaValidator: Stdlib-only JSON Schema validator (Draft 2020-12 subset)
- BusWriter: Append-only TSV coordination bus with flock locking and HMAC signing
- ComplianceMapper: Map governance traces to SOC2, GDPR, OWASP, NIST AI RMF, and EU AI Act controls
- HealthCollector: Composable health probe framework with latency tracking
- OutputValidator: Rule-based content validation for agent outputs (ASI-06)
- CapabilityFence: Soft sandbox enforcing capability boundaries (ASI-07)
- EAL: Execution Assurance Layer — deterministic receipt validation against contracts
- PhysicalGovernor: Safety and kinematic constraints for physical AI (pHRI)
- LamportClock: Hardened logical clock for causal ordering (v0.5.0)
- EvolutionLineage: In-memory lineage tracking for eAI variants

All modules use only Python stdlib. Zero third-party runtime dependencies.

Copyright 2026 HUMMBL, LLC. Licensed under Apache 2.0.
"""

__version__ = "1.2.0"

# Kernel — Governance operating system (v1.2.0)
from hummbl_governance.kernel import (
    Kernel,
    KernelInvariant,
    KernelPanic,
    Receipt,
    ReceiptEngine,
    LawEngine,
    IdentityEngine,
    SequenceEngine,
    EvidenceEngine,
    AuthorityEngine,
    ScheduleEngine,
    DoctrineEngine,
    Stage,
)

from hummbl_governance.kill_switch import KillSwitch, KillSwitchMode
from hummbl_governance.circuit_breaker import CircuitBreaker, CircuitBreakerState
from hummbl_governance.cost_governor import CostGovernor
from hummbl_governance.delegation import DelegationToken, DelegationTokenManager
from hummbl_governance.audit_log import AuditLog
from hummbl_governance.identity import AgentRegistry, TrustTier
from hummbl_governance.schema_validator import SchemaValidator, ValidationError
try:
    from hummbl_governance.coordination_bus import BusWriter, PolicyLevel
except ImportError:
    BusWriter = None  # fcntl not available on Windows
    PolicyLevel = None
from hummbl_governance.compliance_mapper import ComplianceMapper, ComplianceReport
from hummbl_governance.health_probe import HealthCollector, HealthProbe, HealthReport, ProbeResult
from hummbl_governance.lamport_clock import LamportClock, LamportTimestamp
from hummbl_governance.stride_mapper import StrideMapper, StrideReport, Interaction, ThreatFinding
from hummbl_governance.lifecycle import GovernanceLifecycle, AuthorizationDecision, GovernanceStatus
from hummbl_governance.contract_net import ContractNetManager, Bid, TaskAnnouncement, ContractPhase
from hummbl_governance.convergence_guard import ConvergenceDetector, ConvergentGoal, ConvergenceAlert
from hummbl_governance.reward_monitor import BehaviorMonitor, DriftReport
from hummbl_governance.output_validator import (
    OutputValidator, PIIDetector, InjectionDetector, LengthBounds, BlocklistFilter,
)
from hummbl_governance.capability_fence import CapabilityFence, CapabilityDenied
from hummbl_governance.reasoning import ReasoningEngine, ApplyResult
from hummbl_governance.eal import (
    evaluate_validation as eal_validate,
    evaluate_temporal_validation as eal_revalidate,
    evaluate_compat as eal_compat,
)
from hummbl_governance.physical_governor import KinematicGovernor, pHRISafetyMonitor, PhysicalSafetyMode
from hummbl_governance.errors import FailureMode, HummblError, fm_to_errors
from hummbl_governance.failure_modes import (
    FailureModeRecord,
    ErrorRecord,
    all_failure_modes,
    get_fm,
    classify_subclass,
    get_errors_for_fm,
    all_error_records,
)
from hummbl_governance.corpus_adapter import CorpusAdapter
from hummbl_governance.evolution_lineage import (
    EvolutionLineage,
    VariantRecord,
    ModificationRecord,
    EvolutionDriftReport,
)
from hummbl_governance.attest import Attest, AttestResult, ALLOWLIST, BLOCKLIST, CAPABILITY_FENCE
from hummbl_governance.delegation_context import DelegationContext, DelegationContextManager

# Convenience aliases — match code examples shown on hummbl.io
DCT = DelegationTokenManager  # Short alias for DelegationTokenManager
DCTX = DelegationContext  # Short alias for DelegationContext


class _B120Shortcut:
    """Lazy shortcut for Base120 ReasoningEngine access.

    Usage:
        from hummbl_governance import b120
        model = b120.get("P1")
    """

    def __init__(self) -> None:
        self._engine: ReasoningEngine | None = None

    def _ensure(self) -> ReasoningEngine:
        if self._engine is None:
            self._engine = ReasoningEngine()
        return self._engine

    def get(self, code: str):
        """Get a Base120 model by code (e.g. 'P1')."""
        return self._ensure().get_model(code)

    def prompt(self, code: str, depth: int = 1) -> str:
        """Generate a system prompt for the given model code."""
        return self._ensure().generate_system_prompt(code, depth)

    def list(self):
        """List all available models."""
        return list(self._ensure().models.values())


b120 = _B120Shortcut()

__all__ = [
    "__version__",
    # Kernel — Governance operating system (v1.1.0)
    "Kernel",
    "KernelInvariant",
    "KernelPanic",
    "Receipt",
    "ReceiptEngine",
    "LawEngine",
    "IdentityEngine",
    "SequenceEngine",
    "EvidenceEngine",
    "AuthorityEngine",
    "ScheduleEngine",
    "DoctrineEngine",
    "Stage",
    "KillSwitch",
    "KillSwitchMode",
    "CircuitBreaker",
    "CircuitBreakerState",
    "CostGovernor",
    "DelegationToken",
    "DelegationTokenManager",
    "AuditLog",
    "AgentRegistry",
    "TrustTier",
    "SchemaValidator",
    "ValidationError",
    "BusWriter",
    "PolicyLevel",
    "ComplianceMapper",
    "ComplianceReport",
    "HealthCollector",
    "HealthProbe",
    "HealthReport",
    "ProbeResult",
    "LamportClock",
    "LamportTimestamp",
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
    "ReasoningEngine",
    "ApplyResult",
    "KinematicGovernor",
    "pHRISafetyMonitor",
    "PhysicalSafetyMode",
    # Execution Assurance Layer (v0.4.0)
    "eal_validate",
    "eal_revalidate",
    "eal_compat",
    # Error taxonomy (v0.4.0)
    "FailureMode",
    "HummblError",
    "fm_to_errors",
    "FailureModeRecord",
    "ErrorRecord",
    "all_failure_modes",
    "get_fm",
    "classify_subclass",
    "get_errors_for_fm",
    "all_error_records",
    # eAI governance foundation
    "EvolutionLineage",
    "VariantRecord",
    "ModificationRecord",
    "EvolutionDriftReport",
    "CorpusAdapter",
    # Attestation (v1.2.0)
    "Attest",
    "AttestResult",
    "ALLOWLIST",
    "BLOCKLIST",
    "CAPABILITY_FENCE",
    # Delegation Context (v1.2.0)
    "DelegationContext",
    "DelegationContextManager",
    # Convenience aliases — match code examples on hummbl.io
    "DCT",
    "DCTX",
    "b120",
]
