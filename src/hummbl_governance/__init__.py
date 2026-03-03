"""hummbl-governance -- Agent Runtime Governance primitives.

Ship agents that govern themselves.

Five battle-tested primitives for building AI agents with built-in
governance: DelegationToken, DelegationContext, GovernanceBus,
CircuitBreaker, KillSwitch.

Quickstart::

    from hummbl_governance import DelegationToken, DelegationContext, GovernanceBus, CircuitBreaker, KillSwitch

All primitives are stdlib-only (zero third-party dependencies).
"""

__version__ = "0.1.0"

# -- DelegationToken ---------------------------------------------------------
from hummbl_governance.delegation_token import (
    DelegationCapabilityToken as DelegationToken,
    DelegationTokenManager,
    ResourceSelector,
    Caveat,
    TokenBinding,
    DelegationCapabilityToken,
    IDP_E_DCT_VIOLATION,
    IDP_E_TOKEN_EXPIRED,
    IDP_E_TOKEN_INVALID,
    IDP_E_BINDING_MISMATCH,
    create_token,
    validate_token,
    get_token_manager,
)

# Attach convenience aliases for README-style usage:
#   DelegationToken.Manager, DelegationToken.Binding
DelegationToken.Manager = DelegationTokenManager  # type: ignore[attr-defined]
DelegationToken.Binding = TokenBinding  # type: ignore[attr-defined]

# -- DelegationContext --------------------------------------------------------
from hummbl_governance.delegation_context import (
    DelegationContext,
    DelegationContextManager,
    DelegationBudget,
    DCTXStatus,
    IDP_E_DEPTH_EXCEEDED,
    IDP_E_INVALID_STATE_TRANSITION,
    IDP_E_REPLAN_LIMIT,
    DEFAULT_MAX_CHAIN_DEPTH,
    DEFAULT_MAX_REPLANS,
    create_root_context,
    create_child_context,
)

# -- GovernanceBus ------------------------------------------------------------
from hummbl_governance.governance_bus import (
    GovernanceBus,
    GovernanceEntry,
    DEFAULT_RETENTION_DAYS,
    ROTATION_SIZE_BYTES,
    IDP_E_AUDIT_INCOMPLETE,
    IDP_E_AUDIT_IMMUTABLE,
)

# -- CircuitBreaker -----------------------------------------------------------
from hummbl_governance.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpen,
    CircuitBreakerState,
)

# -- KillSwitch ---------------------------------------------------------------
from hummbl_governance.kill_switch import (
    KillSwitch,
    KillSwitchMode,
    KillSwitchEvent,
    KillSwitchEngagedError,
)

__all__ = [
    # Version
    "__version__",
    # DelegationToken
    "DelegationToken",
    "DelegationCapabilityToken",
    "DelegationTokenManager",
    "ResourceSelector",
    "Caveat",
    "TokenBinding",
    "IDP_E_DCT_VIOLATION",
    "IDP_E_TOKEN_EXPIRED",
    "IDP_E_TOKEN_INVALID",
    "IDP_E_BINDING_MISMATCH",
    "create_token",
    "validate_token",
    "get_token_manager",
    # DelegationContext
    "DelegationContext",
    "DelegationContextManager",
    "DelegationBudget",
    "DCTXStatus",
    "IDP_E_DEPTH_EXCEEDED",
    "IDP_E_INVALID_STATE_TRANSITION",
    "IDP_E_REPLAN_LIMIT",
    "DEFAULT_MAX_CHAIN_DEPTH",
    "DEFAULT_MAX_REPLANS",
    "create_root_context",
    "create_child_context",
    # GovernanceBus
    "GovernanceBus",
    "GovernanceEntry",
    "DEFAULT_RETENTION_DAYS",
    "ROTATION_SIZE_BYTES",
    "IDP_E_AUDIT_INCOMPLETE",
    "IDP_E_AUDIT_IMMUTABLE",
    # CircuitBreaker
    "CircuitBreaker",
    "CircuitBreakerOpen",
    "CircuitBreakerState",
    # KillSwitch
    "KillSwitch",
    "KillSwitchMode",
    "KillSwitchEvent",
    "KillSwitchEngagedError",
]
