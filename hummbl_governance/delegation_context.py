"""Delegation Context — chain-depth enforcement for delegated agent actions.

Provides the DelegationContext class for enforcing maximum delegation
chain depth. Agents cannot escalate privilege by chaining delegations
past the configured depth.

Stdlib-only. No third-party dependencies.

Example:
    from hummbl_governance.delegation_context import DelegationContext

    dctx = DelegationContext(parent=token, max_depth=3)
    child = dctx.delegate(operations=["read"], resources=["docs/*"])
    if dctx.depth_exceeded(child):
        raise PermissionError("Delegation chain too deep")
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
import threading
import uuid
from typing import Any

__all__ = [
    "DelegationContext",
    "DelegationContextManager",
]


@dataclass
class DelegationContext:
    """Context for a delegation chain with depth enforcement.

    Wraps a parent token and enforces a maximum chain depth. Each
    call to delegate() produces a child context with depth+1. If
    depth exceeds max_depth, the delegation is refused.

    Attributes:
        parent: Parent token ID or token object.
        max_depth: Maximum allowed delegation depth.
        depth: Current depth (0 for root).
        token_id: This context's token ID.
        created_at: UTC timestamp.
    """

    parent: Any
    max_depth: int = 3
    depth: int = 0
    token_id: str = ""
    operations: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def __post_init__(self) -> None:
        if not self.token_id:
            self.token_id = f"dctx-{uuid.uuid4()}"

    def delegate(
        self,
        operations: list[str] | None = None,
        resources: list[str] | None = None,
    ) -> "DelegationContext":
        """Create a child delegation context (depth + 1).

        Args:
            operations: Operations for the child context.
            resources: Resources for the child context.

        Returns:
            New DelegationContext at depth+1.

        Raises:
            PermissionError: If delegation chain exceeds max_depth.
        """
        new_depth = self.depth + 1
        if new_depth > self.max_depth:
            raise PermissionError(
                f"Delegation chain depth {new_depth} exceeds max_depth {self.max_depth}"
            )
        return DelegationContext(
            parent=self.token_id,
            max_depth=self.max_depth,
            depth=new_depth,
            operations=list(operations) if operations is not None else list(self.operations),
            resources=list(resources) if resources is not None else list(self.resources),
        )

    def depth_exceeded(self, context: "DelegationContext") -> bool:
        """Check if a context's depth exceeds the max_depth."""
        return context.depth > self.max_depth

    def can_delegate(self) -> bool:
        """Check if this context can delegate further."""
        return self.depth + 1 <= self.max_depth

    def to_dict(self) -> dict[str, Any]:
        return {
            "parent": str(self.parent),
            "max_depth": self.max_depth,
            "depth": self.depth,
            "token_id": self.token_id,
            "operations": self.operations,
            "resources": self.resources,
            "created_at": self.created_at,
        }


class DelegationContextManager:
    """Manager for tracking multiple delegation contexts.

    Useful when an orchestrator needs to track delegation chains across
    multiple agents and enforce per-chain depth limits.
    """

    def __init__(self, default_max_depth: int = 3) -> None:
        self._contexts: dict[str, DelegationContext] = {}
        self._default_max_depth = default_max_depth
        self._lock = threading.Lock()

    def create_context(
        self,
        parent: Any,
        max_depth: int | None = None,
    ) -> DelegationContext:
        """Create and register a new delegation context."""
        ctx = DelegationContext(
            parent=parent,
            max_depth=max_depth or self._default_max_depth,
        )
        with self._lock:
            self._contexts[ctx.token_id] = ctx
        return ctx

    def get_context(self, token_id: str) -> DelegationContext | None:
        with self._lock:
            return self._contexts.get(token_id)

    def delegate(self, token_id: str) -> DelegationContext:
        """Delegate from an existing context."""
        with self._lock:
            ctx = self._contexts.get(token_id)
            if ctx is None:
                raise KeyError(f"Unknown context: {token_id}")
            child = ctx.delegate()
            self._contexts[child.token_id] = child
        return child
