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
from collections.abc import Callable
from typing import Any

from hummbl_governance.audit_log import AuditLog
from hummbl_governance.capability_fence import CapabilityDenied, CapabilityFence


class ToolCallAuditor:
    """Wrap callable tools with capability checks and governance audit logging."""

    def __init__(
        self,
        audit_log: AuditLog,
        intent_id: str,
        task_id: str,
        capability_fence: CapabilityFence | None = None,
        signature: str | None = None,
    ) -> None:
        self._audit_log = audit_log
        self._intent_id = intent_id
        self._task_id = task_id
        self._capability_fence = capability_fence
        self._signature = signature

    def wrap(
        self,
        tool_name: str,
        tool_fn: Callable[..., Any],
        *,
        capability: str | None = None,
    ) -> Callable[..., Any]:
        """Wrap a tool function so each invocation emits audit metadata.

        Args:
            tool_name: Human-readable tool identifier.
            tool_fn: Callable to invoke.
            capability: Optional capability string. Defaults to "tool:<tool_name>".

        Returns:
            Callable with identical invocation signature.
        """
        required_capability = capability or f"tool:{tool_name}"
        guard = self._capability_fence

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            started_ms = time.perf_counter_ns() / 1_000_000
            try:
                if guard is not None:
                    guard.check(required_capability)
                result = tool_fn(*args, **kwargs)
            except CapabilityDenied:
                self._append_event(
                    tool_name=tool_name,
                    capability=required_capability,
                    outcome="denied",
                    duration_ms=0.0,
                    status="blocked_by_capability",
                )
                raise
            except Exception as exc:
                elapsed_ms = time.perf_counter_ns() / 1_000_000 - started_ms
                self._append_event(
                    tool_name=tool_name,
                    capability=required_capability,
                    outcome="error",
                    duration_ms=elapsed_ms,
                    status="failed",
                    error_type=type(exc).__name__,
                )
                raise
            else:
                elapsed_ms = time.perf_counter_ns() / 1_000_000 - started_ms
                self._append_event(
                    tool_name=tool_name,
                    capability=required_capability,
                    outcome="ok",
                    duration_ms=elapsed_ms,
                    status="success",
                )
                return result

        return wrapped

    def _append_event(
        self,
        tool_name: str,
        capability: str,
        outcome: str,
        duration_ms: float,
        status: str,
        error_type: str | None = None,
    ) -> None:
        """Append an audit entry for a tool invocation attempt."""
        self._audit_log.append(
            intent_id=self._intent_id,
            task_id=self._task_id,
            tuple_type="SYSTEM",
            tuple_data={
                "event": "tool_call",
                "tool_name": tool_name,
                "capability": capability,
                "outcome": outcome,
                "status": status,
                "duration_ms": round(duration_ms, 3),
                "error_type": error_type,
            },
            signature=self._signature,
            require_signature=False if self._signature is None else None,
            contract_id=None,
            capability_token_id=None,
            verification_id=None,
            amendment_of=None,
        )
