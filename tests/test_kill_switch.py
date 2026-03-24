"""Tests for hummbl_governance.kill_switch."""

import json
import tempfile
from pathlib import Path

import pytest

from hummbl_governance.kill_switch import (
    KillSwitch,
    KillSwitchMode,
    KillSwitchEngagedError,
    KillSwitchTamperError,
)


class TestKillSwitchModes:
    def test_starts_disengaged(self):
        ks = KillSwitch()
        assert ks.mode == KillSwitchMode.DISENGAGED
        assert not ks.engaged

    def test_engage_halt_noncritical(self):
        ks = KillSwitch()
        event = ks.engage(KillSwitchMode.HALT_NONCRITICAL, "test", "tester")
        assert ks.mode == KillSwitchMode.HALT_NONCRITICAL
        assert ks.engaged
        assert event.mode == KillSwitchMode.HALT_NONCRITICAL

    def test_engage_halt_all(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "budget", "governor")
        assert ks.mode == KillSwitchMode.HALT_ALL

    def test_engage_emergency(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.EMERGENCY, "critical failure", "system")
        assert ks.mode == KillSwitchMode.EMERGENCY

    def test_disengage(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
        event = ks.disengage("tester")
        assert ks.mode == KillSwitchMode.DISENGAGED
        assert not ks.engaged
        assert event.mode == KillSwitchMode.DISENGAGED

    def test_engage_disengaged_raises(self):
        ks = KillSwitch()
        with pytest.raises(ValueError, match="Use disengage"):
            ks.engage(KillSwitchMode.DISENGAGED, "test", "tester")

    def test_disengage_custom_reason(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
        event = ks.disengage("admin", reason="Manual override")
        assert "Manual override" in event.reason


class TestTaskChecking:
    def test_disengaged_allows_all(self):
        ks = KillSwitch()
        result = ks.check_task_allowed("anything")
        assert result["allowed"] is True

    def test_halt_noncritical_blocks_regular(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_NONCRITICAL, "test", "tester")
        result = ks.check_task_allowed("data_export")
        assert result["allowed"] is False
        assert result["action"] == "queue"

    def test_halt_noncritical_allows_critical(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_NONCRITICAL, "test", "tester")
        result = ks.check_task_allowed("safety_monitoring")
        assert result["allowed"] is True

    def test_halt_all_allows_critical(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
        result = ks.check_task_allowed("audit_logging")
        assert result["allowed"] is True
        assert result["note"] == "critical only"

    def test_halt_all_blocks_regular(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
        result = ks.check_task_allowed("data_export")
        assert result["allowed"] is False
        assert result["action"] == "block"

    def test_emergency_blocks_everything(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.EMERGENCY, "critical", "system")
        result = ks.check_task_allowed("safety_monitoring")
        assert result["allowed"] is False

    def test_custom_critical_tasks(self):
        ks = KillSwitch(critical_tasks=frozenset(["my_critical_task"]))
        ks.engage(KillSwitchMode.HALT_NONCRITICAL, "test", "tester")
        assert ks.check_task_allowed("my_critical_task")["allowed"] is True
        assert ks.check_task_allowed("safety_monitoring")["allowed"] is False

    def test_check_or_raise(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
        with pytest.raises(KillSwitchEngagedError):
            ks.check_or_raise("data_export")

    def test_check_or_raise_passes(self):
        ks = KillSwitch()
        ks.check_or_raise("anything")


class TestHistory:
    def test_history_records_events(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
        ks.disengage("tester")
        assert len(ks.get_history()) == 2

    def test_history_engaged_only(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
        ks.disengage("tester")
        engaged = ks.get_history(engaged_only=True)
        assert len(engaged) == 1
        assert engaged[0].mode == KillSwitchMode.HALT_ALL

    def test_history_limit(self):
        ks = KillSwitch()
        for i in range(5):
            ks.engage(KillSwitchMode.HALT_ALL, f"test-{i}", "tester")
            ks.disengage("tester")
        assert len(ks.get_history(limit=3)) == 3

    def test_get_status(self):
        ks = KillSwitch()
        status = ks.get_status()
        assert status["mode"] == "DISENGAGED"
        assert status["engaged"] is False
        assert status["engagement_count"] == 0

    def test_get_status_after_engage(self):
        ks = KillSwitch()
        ks.engage(KillSwitchMode.HALT_ALL, "budget exceeded", "governor")
        status = ks.get_status()
        assert status["mode"] == "HALT_ALL"
        assert status["engaged"] is True
        assert status["engagement_count"] == 1
        assert status["last_engagement"]["reason"] == "budget exceeded"


class TestSubscribers:
    def test_subscriber_called(self):
        events = []
        ks = KillSwitch()
        ks.subscribe(lambda e: events.append(e))
        ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
        assert len(events) == 1

    def test_subscriber_error_swallowed(self):
        ks = KillSwitch()
        ks.subscribe(lambda e: (_ for _ in ()).throw(RuntimeError("boom")))
        ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
        assert ks.engaged


class TestPersistence:
    def test_persist_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            secret = b"test-secret"
            ks = KillSwitch(state_dir=state_dir, signing_secret=secret)
            ks.engage(KillSwitchMode.HALT_ALL, "persist test", "tester")
            loaded = KillSwitch.load_from_file(state_dir, signing_secret=secret)
            assert loaded.mode == KillSwitchMode.HALT_ALL

    def test_load_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            loaded = KillSwitch.load_from_file(Path(tmpdir), require_hmac=False)
            assert loaded.mode == KillSwitchMode.DISENGAGED

    def test_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            secret = b"test-secret"
            ks = KillSwitch(state_dir=state_dir, signing_secret=secret)
            ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
            state_file = state_dir / "kill_switch_state.json"
            data = json.loads(state_file.read_text())
            data["reason"] = "tampered"
            state_file.write_text(json.dumps(data))
            with pytest.raises(KillSwitchTamperError):
                KillSwitch.load_from_file(state_dir, signing_secret=secret)

    def test_persist_disengaged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            ks = KillSwitch(state_dir=state_dir, require_hmac=False)
            ks.engage(KillSwitchMode.HALT_ALL, "test", "tester")
            ks.disengage("tester")
            loaded = KillSwitch.load_from_file(state_dir, require_hmac=False)
            assert loaded.mode == KillSwitchMode.DISENGAGED
