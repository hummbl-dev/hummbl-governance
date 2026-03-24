"""Capability Fence -- Soft sandbox enforcing capability boundaries (ASI-07).

Extends delegation tokens to enforce capability boundaries at runtime.
Provides allow/deny lists, guard wrappers, and audit logging for
agent capability checks.

Usage:
    from hummbl_governance import CapabilityFence, CapabilityDenied

    fence = CapabilityFence(
        allowed=["api:read", "bus:write"],
        denied=["file:write", "shell:execute"],
    )
    fence.check("api:read")    # passes, returns True
    fence.check("file:write")  # raises CapabilityDenied

Stdlib-only. Zero third-party dependencies.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

logger = logging.getLogger(__name__)


class CapabilityDenied(Exception):
    """Raised when an agent attempts an operation outside its capability fence.

    Attributes:
        capability: The capability that was denied.
        allowed: The set of allowed capabilities.
        denied: The set of denied capabilities.
    """

    def __init__(
        self,
        capability: str,
        allowed: frozenset[str],
        denied: frozenset[str],
    ) -> None:
        self.capability = capability
        self.allowed = allowed
        self.denied = denied
        super().__init__(
            f"Capability denied: {capability!r} "
            f"(allowed={sorted(allowed)}, denied={sorted(denied)})"
        )


@dataclass(frozen=True)
class AuditEntry:
    """Record of a capability check."""

    timestamp: str
    capability: str
    decision: str  # "allow" or "deny"
    reason: str


class CapabilityFence:
    """Soft sandbox enforcing capability boundaries via delegation tokens.

    Capability strings use the format "resource:action" (e.g., "api:read",
    "file:write", "shell:execute").

    Resolution logic:
    1. If capability is in denied set -> deny
    2. If allowed set is non-empty and capability is not in it -> deny
    3. Otherwise -> allow

    Thread-safe. All state access is lock-protected.

    Args:
        allowed: Capabilities explicitly allowed. If non-empty, only these
            capabilities are permitted (allowlist mode).
        denied: Capabilities explicitly denied. Always takes precedence
            over allowed.
        audit_log: Optional list to append AuditEntry records to.
    """

    def __init__(
        self,
        allowed: list[str] | None = None,
        denied: list[str] | None = None,
        audit_log: list[AuditEntry] | None = None,
    ) -> None:
        self._allowed = frozenset(allowed) if allowed else frozenset()
        self._denied = frozenset(denied) if denied else frozenset()
        self._audit_log = audit_log
        self._lock = threading.Lock()

    @property
    def allowed(self) -> frozenset[str]:
        """The set of allowed capabilities."""
        return self._allowed

    @property
    def denied(self) -> frozenset[str]:
        """The set of denied capabilities."""
        return self._denied

    def check(self, capability: str) -> bool:
        """Check if a capability is permitted.

        Args:
            capability: Capability string to check (e.g., "file:write").

        Returns:
            True if the capability is allowed.

        Raises:
            CapabilityDenied: If the capability is not permitted.
        """
        with self._lock:
            decision, reason = self._resolve(capability)
            self._audit(capability, decision, reason)
            if decision == "deny":
                raise CapabilityDenied(capability, self._allowed, self._denied)
            return True

    def guard(self, fn: Callable[..., Any], capability: str, *args: Any, **kwargs: Any) -> Any:
        """Wrap a function call with a capability check.

        Args:
            fn: Function to call if capability is allowed.
            capability: Capability required to execute the function.
            *args: Positional arguments passed to fn.
            **kwargs: Keyword arguments passed to fn.

        Returns:
            The return value of fn(*args, **kwargs).

        Raises:
            CapabilityDenied: If the capability is not permitted.
        """
        self.check(capability)
        return fn(*args, **kwargs)

    @classmethod
    def from_delegation_token(
        cls,
        token: Any,
        denied: list[str] | None = None,
        audit_log: list[AuditEntry] | None = None,
    ) -> CapabilityFence:
        """Create a CapabilityFence from an existing DelegationToken.

        Uses the token's ops_allowed as the allowed set.

        Args:
            token: A DelegationToken with an ops_allowed attribute.
            denied: Additional denied capabilities.
            audit_log: Optional audit log list.

        Returns:
            A new CapabilityFence instance.
        """
        ops = list(token.ops_allowed) if hasattr(token, "ops_allowed") else []
        return cls(allowed=ops, denied=denied, audit_log=audit_log)

    def _resolve(self, capability: str) -> tuple[str, str]:
        """Resolve a capability check to allow/deny with reason.

        Returns:
            Tuple of (decision, reason).
        """
        if capability in self._denied:
            return "deny", f"{capability!r} is in denied set"
        if self._allowed and capability not in self._allowed:
            return "deny", f"{capability!r} is not in allowed set"
        return "allow", "permitted"

    def _audit(self, capability: str, decision: str, reason: str) -> None:
        """Record a capability check in the audit log if configured."""
        if self._audit_log is not None:
            entry = AuditEntry(
                timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                capability=capability,
                decision=decision,
                reason=reason,
            )
            self._audit_log.append(entry)
