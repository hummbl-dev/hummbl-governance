"""Tool-call audit hook for AI agent integrations.

This module provides a small, framework-agnostic wrapper for tool execution.
Each invocation is logged to AuditLog with intent/task context and outcome.

Usage:
    from hummbl_governance import AuditLog, ToolCallAuditor

    with AuditLog("/tmp/audit", require_signature=False) as audit:
        fence = CapabilityFence(allowed=["tool:search"])
        hook = ToolCallAuditor(
            audit_log=audit,
            intent_id="i-1",
            task_id="t-1",
            capability_fence=fence,
            signature="optional-signature",
        )

        safe_search = hook.wrap("search", search_tool)
        safe_search("query")
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from collections.abc import Mapping
from typing import Any

from hummbl_governance.audit_log import AuditLog
from hummbl_governance.capability_fence import CapabilityDenied, CapabilityFence
from hummbl_governance.transition_receipt import stable_sha256
    ) -> None:
        self._audit_log = audit_log
        self._intent_id = intent_id
        self._task_id = task_id
        self._capability_fence = capability_fence
        self._signature = signature
        self._actor_id = actor_id

        Args:
            tool_name: Human-readable tool identifier.
            tool_fn: Callable to invoke.
            capability: Optional capability string. Defaults to "tool:<tool_name>".
            context: Optional context payload or callable that builds context
                from ``*args`` / ``**kwargs`` for transition hashes.
                )
                return result

        return wrapped

    def _append_event(
        self,
        tool_name: str,
        capability: str,
        event: str,
        outcome: str,
        duration_ms: float,
        status: str,
        transition_id: str,
        error_type: str | None = None,
        terminal_outcome: str | None = None,
        event_payload: dict[str, Any] | None = None,
    ) -> None:
        """Append an audit entry for a tool invocation attempt."""
        data = {
            "event": event,
            "tool_name": tool_name,
            "capability": capability,
            "outcome": outcome,
            "status": status,
            "duration_ms": round(duration_ms, 3),
            "error_type": error_type,
            "terminal_outcome": terminal_outcome,
            "transition_id": transition_id,
        }
        if event_payload is not None:
            data.update(event_payload)

        self._audit_log.append(
            intent_id=self._intent_id,
            task_id=self._task_id,
            tuple_type="SYSTEM",
            tuple_data=data,
            signature=self._signature,
            require_signature=False if self._signature is None else None,
            contract_id=None,
            capability_token_id=None,
            verification_id=None,
            amendment_of=None,
        )
<<<<<<< HEAD

    @staticmethod
    def _coerce_context(
        context: Mapping[str, Any] | Callable[..., Mapping[str, Any]] | None,
        *,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        """Resolve optional call context to a mapping."""
        if context is None:
            return None
        if isinstance(context, Mapping):
            return dict(context)
        try:
            resolved = context(*args, **kwargs)
        except TypeError:
            return {"context_error": "context_builder_signature_error"}
        if isinstance(resolved, Mapping):
            return dict(resolved)
        return {"value": resolved}

    @staticmethod
    def _hash_payload(payload: Any) -> tuple[str, str | None]:
        """Hash a payload and return an error string if canonical serialization fails."""
        try:
            return stable_sha256(payload), None
        except (TypeError, ValueError) as exc:
            fallback = stable_sha256({"__fallback_repr__": repr(payload)})
            return fallback, f"{type(exc).__name__}: {exc}"
=======
>>>>>>> 4dd505b (feat: add tool-call audit hook for integration)
