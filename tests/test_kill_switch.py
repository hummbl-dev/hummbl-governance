"""Tests for KillSwitch -- Emergency Halt System.

Coverage of modes, engagement/disengagement, task filtering,
subscribers, persistence, status, and history.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from hummbl_governance.kill_switch import (
    KillSwitch,
    KillSwitchEvent,
    KillSwitchMode,
    KillSwitchEngagedError,
)


class TestKillSwitchMode:
    """Test KillSwitchMode enum."""

    def test_mode_values(self):
        modes = list(KillSwitchMode)
        values = [m.value for m in modes]
        assert len(values) == len(set(values))

    def test_mode_names(self):
        assert KillSwitchMode.DISENGAGED.name == "DISENGAGED"
        assert KillSwitchMode.HALT_NONCRITICAL.name == "HALT_NONCRITICAL"
        assert KillSwitchMode.HALT_ALL.name == "HALT_ALL"
        assert KillSwitchMode.EMERGENCY.name == "EMERGENCY"


class TestKillSwitchEvent:
    """Test KillSwitchEvent dataclass."""

    def test_event_creation(self):
        event = KillSwitchEvent(
            timestamp="2024-01-01T00:00:00Z",
            mode=KillSwitchMode.HALT_ALL,
            reason="Test reason",
            triggered_by="test",
            affected_tasks=5,
        )
        assert event.timestamp == "2024-01-01T00:00:00Z"
        assert event.mode == KillSwitchMode.HALT_ALL
        assert event.reason == "Test reason"
        assert event.triggered_by == "test"
        assert event.affected_tasks == 5

    def test_event_defaults(self):
        event = KillSwitchEvent(
            timestamp="2024-01-01T00:00:00Z",
            mode=KillSwitchMode.DISENGAGED,
            reason="Test",
            triggered_by="test",
        )
        assert event.affected_tasks == 0

    def test_event_is_frozen(self):
        event = KillSwitchEvent(
            timestamp="2024-01-01T00:00:00Z",
            mode=KillSwitchMode.HALT_ALL,
            reason="Test",
            triggered_by="test",
        )
        with pytest.raises(AttributeError):
            event.reason = "New reason"


class TestKillSwitchEngagedError:
    """Test KillSwitchEngagedError exception."""

    def test_error_creation(self):
        error = KillSwitchEngagedError("Test reason")
        assert error.reason == "Test reason"
        assert error.mode is None
        assert "Test reason" in str(error)

    def test_error_with_mode(self):
        error = KillSwitchEngagedError("Test reason", KillSwitchMode.HALT_ALL)
        assert error.reason == "Test reason"
        assert error.mode == KillSwitchMode.HALT_ALL


class TestKillSwitchInitialization:
    """Test KillSwitch initialization."""

    def test_default_init(self):
        ks = KillSwitch()
        assert ks.mode == KillSwitchMode.DISENGAGED
        assert not ks.engaged
        assert ks.history == []
        assert ks._state_dir is None

    def test_init_with_state_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            ks = KillSwitch(state_dir=state_dir)
            assert ks._state_dir == state_dir

    def test_mode_property(self):
        ks = KillSwitch()
        assert ks.mode == KillSwitchMode.DISENGAGED
        ks._mode = KillSwitchMode.HALT_ALL
        assert ks.mode == KillSwitchMode.HALT_ALL

    def test_engaged_property(self):
        ks = KillSwitch()
        assert not ks.engaged
        ks._mode = KillSwitchMode.HALT_NONCRITICAL
        assert ks.engaged
        ks._mode = KillSwitchMode.HALT_ALL
        assert ks.engaged
        ks._mode = KillSwitchMode.EMERGENCY
        assert ks.engaged

    def test_custom_critical_tasks(self):
        custom = frozenset(["my_task_a", "my_task_b"])
        ks = KillSwitch(critical_tasks=custom)
        assert ks.critical_tasks == custom


class TestKillSwitchSubscribe:
    """Test subscriber functionality."""

    def test_subscribe_adds_callback(self):
        ks = KillSwitch()
        callback = lambda e: None
        ks.subscribe(callback)
        assert callback in ks._subscribers

    def test_subscribe_multiple_callbacks(self):
        ks = KillSwitch()
        callbacks = [lambda e: None for _ in range(3)]
        for cb in callbacks:
            ks.subscribe(cb)
        assert len(ks._subscribers) == 3

    def test_notify_calls_subscribers(self):
        ks = KillSwitch()
        events = []

        def callback1(e):
            events.append(("cb1", e))

        def callback2(e):
            events.append(("cb2", e))

        ks.subscribe(callback1)
        ks.subscribe(callback2)

        event = KillSwitchEvent(
            timestamp="2024-01-01T00:00:00Z",
            mode=KillSwitchMode.HALT_ALL,
            reason="Test",
            triggered_by="test",
        )
        ks._notify(event)

        assert len(events) == 2
        assert events[0] == ("cb1", event)
        assert events[1] == ("cb2", event)

    def test_notify_handles_subscriber_errors(self):
        ks = KillSwitch()

        def failing_callback(e):
            raise ValueError("Subscriber error")

        def working_callback(e):
            working_callback.called = True
        working_callback.called = False

        ks.subscribe(failing_callback)
        ks.subscribe(working_callback)

        event = KillSwitchEvent(
            timestamp="2024-01-01T00:00:00Z",
            mode=KillSwitchMode.HALT_ALL,
            reason="Test",
            triggered_by="test",
        )

        ks._notify(event)
        assert working_callback.called


class TestKillSwitchEngage:
    """Test engage functionality."""

    def test_engage_changes_mode(self):
        ks = KillSwitch()
        ks.engage(mode=KillSwitchMode.HALT_ALL, reason="Test", triggered_by="test")
        assert ks.mode == KillSwitchMode.HALT_ALL
        assert ks.engaged

    def test_engage_returns_event(self):
        ks = KillSwitch()
        event = ks.engage(
            mode=KillSwitchMode.HALT_ALL,
            reason="Test reason",
            triggered_by="test_user",
            affected_tasks=10,
        )
        assert isinstance(event, KillSwitchEvent)
        assert event.mode == KillSwitchMode.HALT_ALL
        assert event.reason == "Test reason"
        assert event.triggered_by == "test_user"
        assert event.affected_tasks == 10
        assert event.timestamp is not None

    def test_engage_adds_to_history(self):
        ks = KillSwitch()
        event = ks.engage(mode=KillSwitchMode.HALT_ALL, reason="Test", triggered_by="test")
        assert len(ks._history) == 1
        assert ks._history[0] == event

    def test_engage_notifies_subscribers(self):
        ks = KillSwitch()
        notified_events = []
        ks.subscribe(lambda e: notified_events.append(e))
        event = ks.engage(mode=KillSwitchMode.HALT_ALL, reason="Test", triggered_by="test")
        assert len(notified_events) == 1
        assert notified_events[0] == event

    def test_engage_rejects_disengaged_mode(self):
        ks = KillSwitch()
        with pytest.raises(ValueError, match="Use disengage"):
            ks.engage(mode=KillSwitchMode.DISENGAGED, reason="Test", triggered_by="test")

    def test_engage_multiple_modes(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_NONCRITICAL, "Reason 1", "user1")
        assert ks.mode == KillSwitchMode.HALT_NONCRITICAL
        ks.engage(KillSwitchMode.HALT_ALL, "Reason 2", "user2")
        assert ks.mode == KillSwitchMode.HALT_ALL
        ks.engage(KillSwitchMode.EMERGENCY, "Reason 3", "user3")
        assert ks.mode == KillSwitchMode.EMERGENCY


class TestKillSwitchDisengage:
    """Test disengage functionality."""

    def test_disengage_clears_mode(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "test")
        ks.disengage(triggered_by="test")
        assert ks.mode == KillSwitchMode.DISENGAGED
        assert not ks.engaged

    def test_disengage_returns_event(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "test")
        event = ks.disengage(triggered_by="disengage_user")
        assert isinstance(event, KillSwitchEvent)
        assert event.mode == KillSwitchMode.DISENGAGED
        assert "HALT_ALL" in event.reason
        assert event.triggered_by == "disengage_user"

    def test_disengage_custom_reason(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "test")
        event = ks.disengage(triggered_by="admin", reason="Manual override")
        assert event.reason == "Manual override"

    def test_disengage_adds_to_history(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "test")
        ks.disengage(triggered_by="test")
        assert len(ks._history) == 2

    def test_disengage_notifies_subscribers(self):
        ks = KillSwitch()
        notified_events = []
        ks.subscribe(lambda e: notified_events.append(e))
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "test")
        ks.disengage(triggered_by="test")
        assert len(notified_events) == 2
        assert notified_events[1].mode == KillSwitchMode.DISENGAGED

    def test_disengage_from_disengaged(self):
        ks = KillSwitch()
        event = ks.disengage(triggered_by="test")
        assert event.mode == KillSwitchMode.DISENGAGED
        assert "DISENGAGED" in event.reason


class TestKillSwitchCheckTask:
    """Test check_task_allowed functionality."""

    def test_disengaged_allows_all(self):
        ks = KillSwitch()
        result = ks.check_task_allowed("any_task")
        assert result["allowed"] is True
        assert result["action"] == "allow"

    def test_halt_noncritical_allows_critical(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_NONCRITICAL, "Test", "test")
        for task in KillSwitch.DEFAULT_CRITICAL_TASKS:
            result = ks.check_task_allowed(task)
            assert result["allowed"] is True, f"{task} should be allowed"
            assert result["action"] == "allow"
            assert "critical" in result.get("note", "").lower()

    def test_halt_noncritical_queues_noncritical(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_NONCRITICAL, "Test", "test")
        result = ks.check_task_allowed("briefing_generation")
        assert result["allowed"] is False
        assert result["action"] == "queue"
        assert "queued" in result["reason"].lower()

    def test_halt_all_allows_critical(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "test")
        for task in KillSwitch.DEFAULT_CRITICAL_TASKS:
            result = ks.check_task_allowed(task)
            assert result["allowed"] is True, f"{task} should be allowed"
            assert result["action"] == "allow"

    def test_halt_all_blocks_noncritical(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "test")
        result = ks.check_task_allowed("briefing_generation")
        assert result["allowed"] is False
        assert result["action"] == "block"
        assert "blocked" in result["reason"].lower()

    def test_emergency_blocks_all(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.EMERGENCY, "Test", "test")
        for task in KillSwitch.DEFAULT_CRITICAL_TASKS:
            result = ks.check_task_allowed(task)
            assert result["allowed"] is False, f"{task} should be blocked in EMERGENCY"
        result = ks.check_task_allowed("any_task")
        assert result["allowed"] is False

    def test_critical_tasks_default(self):
        expected = {
            "safety_monitoring",
            "data_persistence",
            "audit_logging",
            "kill_switch_itself",
            "cost_tracking",
            "feedback_store",
        }
        assert KillSwitch.DEFAULT_CRITICAL_TASKS == expected


class TestKillSwitchCheckOrRaise:
    """Test check_or_raise functionality."""

    def test_check_or_raise_allows(self):
        ks = KillSwitch()
        ks.check_or_raise("briefing_generation")

    def test_check_or_raise_raises_when_blocked(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "Test reason", "test")
        with pytest.raises(KillSwitchEngagedError) as exc_info:
            ks.check_or_raise("briefing_generation")
        assert "HALT_ALL" in str(exc_info.value)
        assert exc_info.value.mode == KillSwitchMode.HALT_ALL


class TestKillSwitchStatus:
    """Test get_status functionality."""

    def test_status_disengaged(self):
        ks = KillSwitch()
        status = ks.get_status()
        assert status["mode"] == "DISENGAGED"
        assert status["engaged"] is False
        assert status["engagement_count"] == 0
        assert status["last_engagement"] is None
        assert status["total_events"] == 0

    def test_status_engaged(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "user")
        status = ks.get_status()
        assert status["mode"] == "HALT_ALL"
        assert status["engaged"] is True
        assert status["engagement_count"] == 1
        assert status["last_engagement"] is not None
        assert status["last_engagement"]["mode"] == "HALT_ALL"
        assert status["last_engagement"]["reason"] == "Test"
        assert status["last_engagement"]["triggered_by"] == "user"
        assert status["total_events"] == 1

    def test_status_multiple_engagements(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_NONCRITICAL, "R1", "u1")
        ks.disengage("u2")
        ks.engage(KillSwitchMode.HALT_ALL, "R2", "u3")
        status = ks.get_status()
        assert status["engagement_count"] == 2
        assert status["last_engagement"]["reason"] == "R2"


class TestKillSwitchHistory:
    """Test get_history functionality."""

    def test_history_empty(self):
        ks = KillSwitch()
        assert ks.get_history() == []

    def test_history_records_events(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "test")
        ks.disengage("test")
        history = ks.get_history()
        assert len(history) == 2
        assert history[0].mode == KillSwitchMode.HALT_ALL
        assert history[1].mode == KillSwitchMode.DISENGAGED

    def test_history_limit(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_NONCRITICAL, "R1", "u1")
        ks.disengage("u2")
        ks.engage(KillSwitchMode.HALT_ALL, "R2", "u3")
        history = ks.get_history(limit=2)
        assert len(history) == 2
        assert history[0].mode == KillSwitchMode.DISENGAGED
        assert history[1].mode == KillSwitchMode.HALT_ALL

    def test_history_engaged_only(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "R1", "u1")
        ks.disengage("u2")
        history = ks.get_history(engaged_only=True)
        assert len(history) == 1
        assert history[0].mode == KillSwitchMode.HALT_ALL


class TestKillSwitchPersistence:
    """Test persistence functionality."""

    def test_persist_on_engage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            ks = KillSwitch(state_dir=state_dir)
            ks.engage(KillSwitchMode.HALT_ALL, "Test", "user")
            state_file = state_dir / "kill_switch_state.json"
            assert state_file.exists()
            data = json.loads(state_file.read_text())
            assert data["mode"] == "HALT_ALL"
            assert data["reason"] == "Test"
            assert data["triggered_by"] == "user"

    def test_persist_on_disengage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            ks = KillSwitch(state_dir=state_dir)
            ks.engage(KillSwitchMode.HALT_ALL, "Test", "user")
            ks.disengage("user2")
            state_file = state_dir / "kill_switch_state.json"
            data = json.loads(state_file.read_text())
            assert data["mode"] == "DISENGAGED"

    def test_no_persist_without_state_dir(self):
        ks = KillSwitch(state_dir=None)
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "user")
        # No error, no file created

    def test_load_from_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            state_file = state_dir / "kill_switch_state.json"
            data = {
                "mode": "HALT_ALL",
                "engaged_at": "2024-01-01T00:00:00Z",
                "reason": "Loaded",
                "triggered_by": "loader",
            }
            state_file.write_text(json.dumps(data))
            ks = KillSwitch.load_from_file(state_dir)
            assert ks.mode == KillSwitchMode.HALT_ALL
            assert ks.engaged
            assert len(ks._history) == 1
            assert ks._history[0].reason == "Loaded"

    def test_load_from_file_with_tampered_hmac_starts_fresh(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            state_file = state_dir / "kill_switch_state.json"
            monkeypatch.setenv("DCT_SECRET", "unit-test-secret")

            payload = {
                "mode": "HALT_ALL",
                "engaged_at": "2024-01-01T00:00:00Z",
                "reason": "Original reason",
                "triggered_by": "loader",
            }
            signature = KillSwitch._compute_state_signature(
                payload, b"unit-test-secret"
            )
            tampered_payload = dict(payload)
            tampered_payload["reason"] = "Tampered reason"
            tampered_payload["signature"] = signature
            state_file.write_text(json.dumps(tampered_payload))

            ks = KillSwitch.load_from_file(state_dir)
            assert ks.mode == KillSwitchMode.DISENGAGED
            assert not ks.engaged

    def test_load_from_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            ks = KillSwitch.load_from_file(state_dir)
            assert ks.mode == KillSwitchMode.DISENGAGED
            assert not ks.engaged

    def test_load_from_corrupt_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            state_file = state_dir / "kill_switch_state.json"
            state_file.write_text("not valid json")
            ks = KillSwitch.load_from_file(state_dir)
            assert ks.mode == KillSwitchMode.DISENGAGED

    def test_load_from_file_with_invalid_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            state_file = state_dir / "kill_switch_state.json"
            state_file.write_text(json.dumps({"mode": "INVALID_MODE"}))
            ks = KillSwitch.load_from_file(state_dir)
            assert ks.mode == KillSwitchMode.DISENGAGED

    def test_persist_handles_write_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            ks = KillSwitch(state_dir=state_dir)
            ks.engage(KillSwitchMode.HALT_ALL, "Test", "user")
            os.chmod(state_dir, 0o555)
            try:
                ks.disengage("user")
                assert not ks.engaged
            finally:
                os.chmod(state_dir, 0o755)

    def test_roundtrip_engage_persist_load_verify(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            ks1 = KillSwitch(state_dir=state_dir)
            ks1.engage(KillSwitchMode.EMERGENCY, "Critical failure", "system")
            ks2 = KillSwitch.load_from_file(state_dir)
            assert ks2.mode == KillSwitchMode.EMERGENCY
            assert ks2._history[0].reason == "Critical failure"


class TestKillSwitchIntegration:
    """Integration tests."""

    def test_full_lifecycle(self):
        ks = KillSwitch()
        events_log = []
        ks.subscribe(lambda e: events_log.append(e))

        assert not ks.engaged
        assert ks.check_task_allowed("any_task")["allowed"]

        ks.engage(
            KillSwitchMode.HALT_NONCRITICAL,
            "High load",
            "monitor",
            affected_tasks=5,
        )
        assert ks.engaged
        assert ks.mode == KillSwitchMode.HALT_NONCRITICAL
        assert not ks.check_task_allowed("briefing")["allowed"]
        assert ks.check_task_allowed("safety_monitoring")["allowed"]

        ks.engage(KillSwitchMode.HALT_ALL, "Escalated", "admin")
        assert ks.mode == KillSwitchMode.HALT_ALL

        ks.disengage("admin", "Issue resolved")
        assert not ks.engaged
        assert ks.mode == KillSwitchMode.DISENGAGED

        assert len(events_log) == 3
        assert len(ks.get_history()) == 3

    def test_state_persisted_and_loaded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            ks1 = KillSwitch(state_dir=state_dir)
            ks1.engage(KillSwitchMode.HALT_ALL, "Test", "user")
            ks2 = KillSwitch.load_from_file(state_dir)
            assert ks2.mode == KillSwitchMode.HALT_ALL
            assert ks2._state_dir == state_dir


class TestKillSwitchEdgeCases:
    """Edge case tests."""

    def test_subscriber_error_during_engage(self):
        ks = KillSwitch()

        def failing_sub(e):
            raise RuntimeError("Subscriber failed")

        ks.subscribe(failing_sub)
        ks.engage(KillSwitchMode.HALT_ALL, "Test", "user")
        assert ks.engaged

    def test_multiple_engage_same_mode(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "R1", "u1")
        ks.engage(KillSwitchMode.HALT_ALL, "R2", "u2")
        assert ks.mode == KillSwitchMode.HALT_ALL
        assert len(ks.get_history()) == 2

    def test_empty_task_type(self):
        ks = KillSwitch()
        result = ks.check_task_allowed("")
        assert result["allowed"]

    def test_none_task_type(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_NONCRITICAL, "Test", "test")
        result = ks.check_task_allowed(None)  # type: ignore
        assert not result["allowed"]


class TestTopLevelImport:
    """Test top-level package imports."""

    def test_import_kill_switch(self):
        from hummbl_governance import KillSwitch, KillSwitchMode, KillSwitchEvent, KillSwitchEngagedError

        ks = KillSwitch()
        assert ks.mode == KillSwitchMode.DISENGAGED
        assert issubclass(KillSwitchEngagedError, Exception)
