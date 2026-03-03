"""Tests for governance_bus module.

Tests GovernanceEntry, GovernanceBus, and audit log operations.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from hummbl_governance.governance_bus import (
    DEFAULT_RETENTION_DAYS,
    IDP_E_AUDIT_INCOMPLETE,
    ROTATION_SIZE_BYTES,
    GovernanceBus,
    GovernanceEntry,
    _is_idp_enabled,
)


class TestIsIdpEnabled:
    """Test _is_idp_enabled function."""

    def test_enabled_when_true(self):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            assert _is_idp_enabled() is True

    def test_disabled_when_false(self):
        with patch.dict(os.environ, {"ENABLE_IDP": "false"}):
            assert _is_idp_enabled() is False

    def test_enabled_when_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            assert _is_idp_enabled() is True

    def test_case_insensitive(self):
        with patch.dict(os.environ, {"ENABLE_IDP": "TRUE"}):
            assert _is_idp_enabled() is True
        with patch.dict(os.environ, {"ENABLE_IDP": "True"}):
            assert _is_idp_enabled() is True


class TestGovernanceEntry:
    """Test GovernanceEntry dataclass."""

    def test_creation(self):
        entry = GovernanceEntry(
            timestamp="2026-02-17T10:00:00Z",
            entry_id="uuid-123",
            intent_id="intent-456",
            task_id="task-789",
            tuple_type="DCT",
            tuple_data={"key": "value"},
            signature="sig-abc",
        )
        assert entry.timestamp == "2026-02-17T10:00:00Z"
        assert entry.entry_id == "uuid-123"
        assert entry.intent_id == "intent-456"
        assert entry.tuple_type == "DCT"
        assert entry.tuple_data == {"key": "value"}
        assert entry.signature == "sig-abc"

    def test_creation_without_signature(self):
        entry = GovernanceEntry(
            timestamp="2026-02-17T10:00:00Z",
            entry_id="uuid-123",
            intent_id="intent-456",
            task_id="task-789",
            tuple_type="SYSTEM",
            tuple_data={"event": "test"},
        )
        assert entry.signature is None

    def test_to_jsonl(self):
        entry = GovernanceEntry(
            timestamp="2026-02-17T10:00:00Z",
            entry_id="uuid-123",
            intent_id="intent-456",
            task_id="task-789",
            tuple_type="DCT",
            tuple_data={"key": "value"},
            signature="sig-abc",
        )
        jsonl = entry.to_jsonl()
        data = json.loads(jsonl)
        assert data["timestamp"] == "2026-02-17T10:00:00Z"
        assert data["entry_id"] == "uuid-123"
        assert data["tuple_type"] == "DCT"
        assert data["tuple_data"] == {"key": "value"}
        assert data["signature"] == "sig-abc"

    def test_to_jsonl_sorts_keys(self):
        entry = GovernanceEntry(
            timestamp="2026-02-17T10:00:00Z",
            entry_id="uuid-123",
            intent_id="intent-456",
            task_id="task-789",
            tuple_type="DCT",
            tuple_data={"z": 1, "a": 2},
        )
        jsonl = entry.to_jsonl()
        assert jsonl.index('"entry_id"') < jsonl.index('"intent_id"')
        assert jsonl.index('"intent_id"') < jsonl.index('"signature"')

    def test_from_dict(self):
        data = {
            "timestamp": "2026-02-17T10:00:00Z",
            "entry_id": "uuid-123",
            "intent_id": "intent-456",
            "task_id": "task-789",
            "tuple_type": "DCT",
            "tuple_data": {"key": "value"},
            "signature": "sig-abc",
        }
        entry = GovernanceEntry.from_dict(data)
        assert entry.timestamp == "2026-02-17T10:00:00Z"
        assert entry.entry_id == "uuid-123"
        assert entry.signature == "sig-abc"

    def test_from_dict_without_signature(self):
        data = {
            "timestamp": "2026-02-17T10:00:00Z",
            "entry_id": "uuid-123",
            "intent_id": "intent-456",
            "task_id": "task-789",
            "tuple_type": "SYSTEM",
            "tuple_data": {},
        }
        entry = GovernanceEntry.from_dict(data)
        assert entry.signature is None

    def test_roundtrip(self):
        original = GovernanceEntry(
            timestamp="2026-02-17T10:00:00Z",
            entry_id="uuid-123",
            intent_id="intent-456",
            task_id="task-789",
            tuple_type="DCT",
            tuple_data={"key": "value"},
            signature="sig-abc",
        )
        jsonl = original.to_jsonl()
        data = json.loads(jsonl)
        restored = GovernanceEntry.from_dict(data)
        assert original == restored


class TestGovernanceBusInit:
    """Test GovernanceBus initialization."""

    def test_default_init(self, tmp_path: Path):
        bus = GovernanceBus(base_dir=tmp_path / "governance")
        assert bus._base_dir == tmp_path / "governance"
        assert bus._retention_days == DEFAULT_RETENTION_DAYS
        assert bus._enable_async is False
        assert bus._lock is not None

    def test_custom_init(self, tmp_path: Path):
        bus = GovernanceBus(
            base_dir=tmp_path / "custom",
            retention_days=30,
            enable_async=True,
        )
        assert bus._retention_days == 30
        assert bus._enable_async is True

    def test_creates_directory(self, tmp_path: Path):
        gov_dir = tmp_path / "new_governance"
        GovernanceBus(base_dir=gov_dir)
        assert gov_dir.exists()


class TestGovernanceBusAppend:
    """Test GovernanceBus.append() method."""

    def test_append_sync_success(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(base_dir=tmp_path / "gov")
            success, error = bus.append(
                intent_id="intent-123",
                task_id="task-456",
                tuple_type="DCT",
                tuple_data={"test": "data"},
            )
            assert success is True
            assert error is None

    def test_append_when_disabled(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "false"}):
            bus = GovernanceBus(base_dir=tmp_path / "gov")
            success, error = bus.append(
                intent_id="intent-123",
                task_id="task-456",
                tuple_type="DCT",
                tuple_data={"test": "data"},
            )
            assert success is True
            assert error is None

    def test_append_creates_file(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(base_dir=tmp_path / "gov")
            bus.append(
                intent_id="intent-123",
                task_id="task-456",
                tuple_type="DCT",
                tuple_data={"test": "data"},
            )
            log_files = list((tmp_path / "gov").glob("governance-*.jsonl"))
            assert len(log_files) == 1
            content = log_files[0].read_text()
            data = json.loads(content.strip())
            assert data["intent_id"] == "intent-123"
            assert data["tuple_type"] == "DCT"

    def test_append_async_buffer(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(
                base_dir=tmp_path / "gov",
                enable_async=True,
            )
            success, error = bus.append(
                intent_id="intent-123",
                task_id="task-456",
                tuple_type="DCT",
                tuple_data={"test": "data"},
            )
            assert success is True
            assert len(bus._buffer) == 1

    def test_append_async_flush_at_100(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(
                base_dir=tmp_path / "gov",
                enable_async=True,
            )
            for i in range(100):
                bus.append(
                    intent_id=f"intent-{i}",
                    task_id=f"task-{i}",
                    tuple_type="SYSTEM",
                    tuple_data={"i": i},
                )
            assert len(bus._buffer) == 0
            log_files = list((tmp_path / "gov").glob("governance-*.jsonl"))
            assert len(log_files) == 1


class TestGovernanceBusQuery:
    """Test GovernanceBus query methods."""

    def test_query_by_intent(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(base_dir=tmp_path / "gov")
            bus.append("intent-a", "task-1", "DCT", {"data": 1})
            bus.append("intent-b", "task-2", "DCT", {"data": 2})
            bus.append("intent-a", "task-3", "SYSTEM", {"data": 3})
            results = list(bus.query_by_intent("intent-a"))
            assert len(results) == 2
            assert all(r.intent_id == "intent-a" for r in results)

    def test_query_by_intent_with_type_filter(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(base_dir=tmp_path / "gov")
            bus.append("intent-a", "task-1", "DCT", {"data": 1})
            bus.append("intent-a", "task-2", "SYSTEM", {"data": 2})
            results = list(bus.query_by_intent("intent-a", tuple_type="DCT"))
            assert len(results) == 1
            assert results[0].tuple_type == "DCT"

    def test_query_by_task(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(base_dir=tmp_path / "gov")
            bus.append("intent-a", "task-1", "DCT", {"data": 1})
            bus.append("intent-b", "task-1", "DCT", {"data": 2})
            bus.append("intent-c", "task-2", "DCT", {"data": 3})
            results = list(bus.query_by_task("task-1"))
            assert len(results) == 2
            assert all(r.task_id == "task-1" for r in results)

    def test_query_skips_corrupted_lines(self, tmp_path: Path):
        gov_dir = tmp_path / "gov"
        gov_dir.mkdir()
        log_file = gov_dir / "governance-2026-02-17.jsonl"
        log_file.write_text(
            '{"timestamp":"2026-02-17T10:00:00Z","entry_id":"uuid-1","intent_id":"intent-1","task_id":"task-1","tuple_type":"DCT","tuple_data":{}}\n'
            "this is not valid json\n"
            '{"timestamp":"2026-02-17T10:01:00Z","entry_id":"uuid-2","intent_id":"intent-2","task_id":"task-2","tuple_type":"SYSTEM","tuple_data":{}}\n'
        )
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(base_dir=gov_dir)
            results = list(bus.query_by_intent("intent-2"))
            assert len(results) == 1
            assert results[0].intent_id == "intent-2"

    def test_query_returns_empty_when_disabled(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "false"}):
            bus = GovernanceBus(base_dir=tmp_path / "gov")
            results = list(bus.query_by_intent("intent-1"))
            assert len(results) == 0


class TestGovernanceBusRetention:
    """Test GovernanceBus retention enforcement."""

    def test_enforce_retention_deletes_old_files(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            gov_dir = tmp_path / "gov"
            old_file = gov_dir / "governance-2026-01-01.jsonl"
            old_file.parent.mkdir(parents=True, exist_ok=True)
            old_file.write_text("{}\n")

            bus = GovernanceBus(base_dir=gov_dir, retention_days=30)

            future = datetime(2026, 3, 1, tzinfo=timezone.utc)
            with patch("hummbl_governance.governance_bus.datetime") as mock_dt:
                mock_dt.now.return_value = future
                mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
                deleted = bus.enforce_retention()

            assert deleted == 1
            assert not old_file.exists()

    def test_enforce_retention_keeps_recent_files(self, tmp_path: Path):
        gov_dir = tmp_path / "gov"
        recent_file = gov_dir / "governance-2026-02-10.jsonl"
        recent_file.parent.mkdir(parents=True, exist_ok=True)
        recent_file.write_text("{}\n")

        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(base_dir=gov_dir, retention_days=90)

            now = datetime(2026, 2, 17, tzinfo=timezone.utc)
            with patch("hummbl_governance.governance_bus.datetime") as mock_dt:
                mock_dt.now.return_value = now
                mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
                deleted = bus.enforce_retention()

            assert deleted == 0
            assert recent_file.exists()

    def test_enforce_retention_returns_zero_when_disabled(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "false"}):
            bus = GovernanceBus(base_dir=tmp_path / "gov")
            deleted = bus.enforce_retention()
            assert deleted == 0


class TestGovernanceBusContextManager:
    """Test GovernanceBus context manager."""

    def test_context_manager_closes_file(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            bus = GovernanceBus(base_dir=tmp_path / "gov")
            file_handle = None
            with bus:
                bus.append("intent-1", "task-1", "DCT", {})
                assert bus._file_handle is not None
                file_handle = bus._file_handle
                assert not file_handle.closed
            assert bus._file_handle is None or file_handle.closed

    def test_context_manager_flushes_async(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            with GovernanceBus(
                base_dir=tmp_path / "gov",
                enable_async=True,
            ) as bus:
                bus.append("intent-1", "task-1", "DCT", {})
                assert len(bus._buffer) == 1
            assert len(bus._buffer) == 0


class TestGovernanceBusFileRotation:
    """Test file rotation logic."""

    def test_rotation_on_size_limit(self, tmp_path: Path):
        with patch.dict(os.environ, {"ENABLE_IDP": "true"}):
            with patch("hummbl_governance.governance_bus.ROTATION_SIZE_BYTES", 100):
                bus = GovernanceBus(base_dir=tmp_path / "gov")
                log_file = tmp_path / "gov" / bus._get_current_file().name
                log_file.parent.mkdir(parents=True, exist_ok=True)
                log_file.write_bytes(b"x" * 101)
                bus.append("intent-1", "task-1", "DCT", {})
                compressed = log_file.with_suffix(".jsonl.gz")
                assert compressed.exists() or not log_file.exists()
