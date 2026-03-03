"""Kill Switch -- Emergency Halt System with graduated response.

Four modes:
1. DISENGAGED: Normal operation.
2. HALT_NONCRITICAL: Queue non-critical tasks, continue critical.
3. HALT_ALL: Stop all new work, complete in-flight.
4. EMERGENCY: Immediate halt, preserve all state.

Supports critical task exemptions, subscriber notifications,
persistent state with HMAC-SHA256 integrity protection, and
event history.

Stdlib-only. Zero third-party dependencies.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class KillSwitchMode(Enum):
    """Kill switch engagement modes."""

    DISENGAGED = auto()
    HALT_NONCRITICAL = auto()  # Queue non-critical, continue critical
    HALT_ALL = auto()          # Stop new work, complete in-flight
    EMERGENCY = auto()         # Immediate halt, preserve state


@dataclass(frozen=True)
class KillSwitchEvent:
    """Record of a kill switch state change.

    Attributes:
        timestamp: ISO format UTC timestamp.
        mode: Kill switch mode at time of event.
        reason: Human-readable explanation.
        triggered_by: Component or user that triggered the change.
        affected_tasks: Number of tasks affected (for engagements).
    """

    timestamp: str
    mode: KillSwitchMode
    reason: str
    triggered_by: str
    affected_tasks: int = 0


class KillSwitchEngagedError(Exception):
    """Raised when an operation is blocked by an engaged kill switch."""

    def __init__(self, reason: str, mode: KillSwitchMode | None = None):
        self.reason = reason
        self.mode = mode
        super().__init__(f"Kill switch engaged: {reason}")


class KillSwitch:
    """Emergency halt system with graduated response.

    Provides service-level circuit breaking to prevent cascading failures.

    Features:
        - Three engagement levels (HALT_NONCRITICAL, HALT_ALL, EMERGENCY).
        - Critical task exemptions (always-allowed tasks).
        - Event history with optional persistence.
        - Subscriber notifications for state changes.
        - HMAC-SHA256 integrity on persisted state.
        - Zero third-party dependencies.

    Thread Safety:
        This implementation is NOT thread-safe. For multi-threaded use,
        wrap calls in appropriate synchronization.

    Args:
        state_dir: Directory for persistent state storage.
                   If None, persistence is disabled.
        critical_tasks: Set of task types that continue even in
                        HALT_NONCRITICAL and HALT_ALL modes.
                        If None, uses the default set.
    """

    # Default tasks that continue even in HALT_NONCRITICAL mode
    DEFAULT_CRITICAL_TASKS: frozenset[str] = frozenset([
        "safety_monitoring",
        "data_persistence",
        "audit_logging",
        "kill_switch_itself",
        "cost_tracking",
        "feedback_store",
    ])

    def __init__(
        self,
        state_dir: Path | str | None = None,
        critical_tasks: frozenset[str] | None = None,
    ):
        self._mode = KillSwitchMode.DISENGAGED
        self._history: List[KillSwitchEvent] = []
        self._subscribers: List[Callable[[KillSwitchEvent], None]] = []
        self._state_dir = Path(state_dir) if state_dir is not None else None
        self._critical_tasks = critical_tasks or self.DEFAULT_CRITICAL_TASKS

    @property
    def mode(self) -> KillSwitchMode:
        """Current kill switch mode."""
        return self._mode

    @property
    def engaged(self) -> bool:
        """True if kill switch is engaged (not DISENGAGED)."""
        return self._mode != KillSwitchMode.DISENGAGED

    @property
    def history(self) -> List[KillSwitchEvent]:
        """Event history (read-only copy)."""
        return self._history.copy()

    @property
    def critical_tasks(self) -> frozenset[str]:
        """Set of task types considered critical."""
        return self._critical_tasks

    @classmethod
    def load_from_file(cls, state_dir: Path | str) -> KillSwitch:
        """Load kill switch state from persistent storage.

        Args:
            state_dir: Directory containing kill_switch_state.json.

        Returns:
            KillSwitch instance with restored state, or fresh instance
            if file is missing or corrupt.
        """
        state_dir = Path(state_dir)
        state_file = state_dir / "kill_switch_state.json"
        ks = cls(state_dir=state_dir)

        if not state_file.exists():
            return ks

        try:
            with open(state_file, encoding="utf-8") as f:
                data = json.load(f)

            # Verify HMAC signature if DCT_SECRET is set
            secret = cls._get_signing_secret()
            signature = data.pop("signature", None)
            if secret and signature:
                if not cls._verify_state_signature(data, signature, secret):
                    logger.warning(
                        "Kill switch state file has invalid HMAC signature "
                        "-- possible tampering. Starting fresh."
                    )
                    return ks
            elif secret and not signature:
                logger.info(
                    "Kill switch state file has no signature (pre-HMAC). "
                    "Will be signed on next persist."
                )

            mode_str = data.get("mode", "DISENGAGED")
            ks._mode = KillSwitchMode[mode_str]

            if ks._mode != KillSwitchMode.DISENGAGED:
                event = KillSwitchEvent(
                    timestamp=data.get(
                        "engaged_at", datetime.now(timezone.utc).isoformat()
                    ),
                    mode=ks._mode,
                    reason=data.get("reason", "Restored from file"),
                    triggered_by=data.get("triggered_by", "system"),
                    affected_tasks=0,
                )
                ks._history.append(event)
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            pass

        return ks

    def subscribe(self, callback: Callable[[KillSwitchEvent], None]) -> None:
        """Subscribe to kill switch state changes.

        Args:
            callback: Function called with KillSwitchEvent on each state change.
                     Subscriber errors are silently ignored.
        """
        self._subscribers.append(callback)

    @staticmethod
    def _get_signing_secret() -> bytes | None:
        """Get HMAC signing secret from environment."""
        secret = os.environ.get("DCT_SECRET")
        if secret:
            return secret.encode("utf-8")
        return None

    @staticmethod
    def _compute_state_signature(data: dict[str, Any], secret: bytes) -> str:
        """Compute HMAC-SHA256 signature over kill switch state payload."""
        canonical = json.dumps(data, separators=(",", ":"), sort_keys=True)
        mac = hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256)
        return mac.hexdigest()

    @staticmethod
    def _verify_state_signature(
        data: dict[str, Any], signature: str, secret: bytes
    ) -> bool:
        """Verify HMAC-SHA256 signature of persisted state."""
        expected = KillSwitch._compute_state_signature(data, secret)
        return hmac.compare_digest(expected, signature)

    def _persist(self) -> None:
        """Persist current state to file if state_dir is configured."""
        if self._state_dir is None:
            return

        state_file = self._state_dir / "kill_switch_state.json"
        self._state_dir.mkdir(parents=True, exist_ok=True)

        last_event = self._history[-1] if self._history else None

        data = {
            "mode": self._mode.name,
            "engaged_at": last_event.timestamp if last_event else None,
            "reason": last_event.reason if last_event else None,
            "triggered_by": last_event.triggered_by if last_event else None,
        }

        secret = self._get_signing_secret()
        if secret:
            data["signature"] = self._compute_state_signature(
                {k: v for k, v in data.items() if k != "signature"}, secret
            )

        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            state_file.chmod(0o600)
        except OSError:
            pass

    def _notify(self, event: KillSwitchEvent) -> None:
        """Notify subscribers of state change."""
        for callback in self._subscribers:
            try:
                callback(event)
            except Exception:
                continue

    def engage(
        self,
        mode: KillSwitchMode,
        reason: str,
        triggered_by: str,
        affected_tasks: int = 0,
    ) -> KillSwitchEvent:
        """Engage the kill switch.

        Args:
            mode: Engagement level (must not be DISENGAGED).
            reason: Human-readable explanation.
            triggered_by: Component or user triggering engagement.
            affected_tasks: Estimated number of tasks affected.

        Returns:
            KillSwitchEvent record of the engagement.

        Raises:
            ValueError: If mode is DISENGAGED (use disengage() instead).
        """
        if mode == KillSwitchMode.DISENGAGED:
            raise ValueError("Use disengage() to clear kill switch, not engage()")

        self._mode = mode

        event = KillSwitchEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            mode=mode,
            reason=reason,
            triggered_by=triggered_by,
            affected_tasks=affected_tasks,
        )

        self._history.append(event)
        self._notify(event)
        self._persist()

        return event

    def disengage(self, triggered_by: str, reason: str | None = None) -> KillSwitchEvent:
        """Disengage the kill switch.

        Args:
            triggered_by: Component or user disengaging.
            reason: Optional override reason.

        Returns:
            KillSwitchEvent record of the disengagement.
        """
        previous_mode = self._mode
        self._mode = KillSwitchMode.DISENGAGED

        disengage_reason = reason or f"Disengaged from {previous_mode.name}"

        event = KillSwitchEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            mode=KillSwitchMode.DISENGAGED,
            reason=disengage_reason,
            triggered_by=triggered_by,
            affected_tasks=0,
        )

        self._history.append(event)
        self._notify(event)
        self._persist()

        return event

    def check_task_allowed(self, task_type: str) -> Dict[str, Any]:
        """Check if a task is allowed under current kill switch mode.

        Args:
            task_type: Type/category of task being checked.

        Returns:
            Dict with:
                - allowed: bool
                - action: str ("allow", "queue", or "block")
                - reason: str (if blocked)
                - note: str (if allowed with conditions)
        """
        is_critical = task_type in self._critical_tasks

        if self._mode == KillSwitchMode.DISENGAGED:
            return {"allowed": True, "action": "allow"}

        if self._mode == KillSwitchMode.HALT_NONCRITICAL:
            if is_critical:
                return {
                    "allowed": True,
                    "action": "allow",
                    "note": "critical task exempted",
                }
            return {
                "allowed": False,
                "action": "queue",
                "reason": f"Kill switch engaged ({self._mode.name}): {task_type} queued",
            }

        if self._mode in (KillSwitchMode.HALT_ALL, KillSwitchMode.EMERGENCY):
            if is_critical and self._mode == KillSwitchMode.HALT_ALL:
                return {
                    "allowed": True,
                    "action": "allow",
                    "note": "critical only",
                }
            return {
                "allowed": False,
                "action": "block",
                "reason": f"Kill switch engaged ({self._mode.name}): {task_type} blocked",
            }

        return {
            "allowed": False,
            "action": "block",
            "reason": "Unknown kill switch state",
        }

    def check_or_raise(self, task_type: str) -> None:
        """Check task and raise exception if not allowed.

        Args:
            task_type: Type/category of task being checked.

        Raises:
            KillSwitchEngagedError: If task is blocked by kill switch.
        """
        result = self.check_task_allowed(task_type)
        if not result["allowed"]:
            raise KillSwitchEngagedError(result["reason"], self._mode)

    def get_status(self) -> Dict[str, Any]:
        """Get current kill switch status summary.

        Returns:
            Dict with mode, engagement status, count, and last engagement.
        """
        engagement_count = len(
            [e for e in self._history if e.mode != KillSwitchMode.DISENGAGED]
        )

        last_engagement = None
        for event in reversed(self._history):
            if event.mode != KillSwitchMode.DISENGAGED:
                last_engagement = {
                    "timestamp": event.timestamp,
                    "mode": event.mode.name,
                    "reason": event.reason,
                    "triggered_by": event.triggered_by,
                }
                break

        return {
            "mode": self._mode.name,
            "engaged": self.engaged,
            "engagement_count": engagement_count,
            "last_engagement": last_engagement,
            "total_events": len(self._history),
        }

    def get_history(
        self,
        limit: int | None = None,
        engaged_only: bool = False,
    ) -> List[KillSwitchEvent]:
        """Get kill switch event history.

        Args:
            limit: Maximum number of events to return (None for all).
            engaged_only: If True, only return engagement events.

        Returns:
            List of KillSwitchEvent records (newest first if limited).
        """
        events = self._history.copy()

        if engaged_only:
            events = [e for e in events if e.mode != KillSwitchMode.DISENGAGED]

        if limit:
            events = events[-limit:]

        return events
