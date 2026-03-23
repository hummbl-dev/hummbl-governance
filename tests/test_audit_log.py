"""Tests for hummbl_governance.audit_log."""

import tempfile
from pathlib import Path

import pytest

from hummbl_governance.audit_log import (
    AuditEntry,
    AuditLog,
    E_AUDIT_IMMUTABLE,
    E_AMENDMENT_TARGET_MISSING,
    E_EVIDENCE_REQUIRED,
    E_VERIFICATION_REF_INVALID,
)


class TestAuditEntry:
    """Test AuditEntry serialization."""

    def test_to_jsonl_round_trip(self):
        import json
        entry = AuditEntry(
            timestamp="2026-01-01T00:00:00Z",
            entry_id="entry-1",
            intent_id="intent-1",
            task_id="task-1",
            tuple_type="CONTRACT",
            tuple_data={"name": "test"},
            signature="sig-123",
        )
        line = entry.to_jsonl()
        parsed = json.loads(line)
        restored = AuditEntry.from_dict(parsed)
        assert restored.entry_id == "entry-1"
        assert restored.tuple_type == "CONTRACT"
        assert restored.tuple_data == {"name": "test"}

    def test_optional_fields(self):
        import json
        entry = AuditEntry(
            timestamp="2026-01-01T00:00:00Z",
            entry_id="entry-1",
            intent_id="intent-1",
            task_id="task-1",
            tuple_type="CONTRACT",
            tuple_data={},
            contract_id="contract-1",
            amendment_of="entry-0",
        )
        line = entry.to_jsonl()
        parsed = json.loads(line)
        assert parsed["contract_id"] == "contract-1"
        assert parsed["amendment_of"] == "entry-0"


class TestAuditLogAppend:
    """Test append operations."""

    def test_append_with_signature(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir)
            ok, err = log.append(
                intent_id="i1", task_id="t1",
                tuple_type="CONTRACT",
                tuple_data={"name": "test"},
                signature="sig-123",
            )
            assert ok is True
            assert err is None
            log.close()

    def test_append_without_signature_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=True)
            ok, err = log.append(
                intent_id="i1", task_id="t1",
                tuple_type="CONTRACT",
                tuple_data={"name": "test"},
            )
            assert ok is False
            assert err == E_AUDIT_IMMUTABLE
            log.close()

    def test_append_without_signature_allowed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            ok, err = log.append(
                intent_id="i1", task_id="t1",
                tuple_type="CONTRACT",
                tuple_data={"name": "test"},
            )
            assert ok is True
            log.close()

    def test_attest_requires_verification_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            ok, err = log.append(
                intent_id="i1", task_id="t1",
                tuple_type="ATTEST",
                tuple_data={"verdict": "pass"},
            )
            assert ok is False
            assert err == E_EVIDENCE_REQUIRED
            log.close()

    def test_attest_verification_ref_must_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            ok, err = log.append(
                intent_id="i1", task_id="t1",
                tuple_type="ATTEST",
                tuple_data={"verdict": "pass"},
                verification_id="nonexistent",
            )
            assert ok is False
            assert err == E_VERIFICATION_REF_INVALID
            log.close()


class TestAuditLogQuery:
    """Test query operations."""

    def test_query_by_intent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            log.append("i1", "t1", "CONTRACT", {"n": 1})
            log.append("i2", "t2", "CONTRACT", {"n": 2})
            log.close()

            log2 = AuditLog(tmpdir, require_signature=False)
            results = list(log2.query_by_intent("i1"))
            assert len(results) == 1
            assert results[0].intent_id == "i1"
            log2.close()

    def test_query_by_task(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            log.append("i1", "t1", "CONTRACT", {"n": 1})
            log.append("i1", "t2", "DCT", {"n": 2})
            log.close()

            log2 = AuditLog(tmpdir, require_signature=False)
            results = list(log2.query_by_task("t1"))
            assert len(results) == 1
            log2.close()

    def test_query_by_entry_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            log.append("i1", "t1", "CONTRACT", {"n": 1})
            log.close()

            log2 = AuditLog(tmpdir, require_signature=False)
            entries = list(log2.query_by_intent("i1"))
            assert len(entries) == 1
            found = log2.query_by_entry_id(entries[0].entry_id)
            assert found is not None
            assert found.intent_id == "i1"
            log2.close()

    def test_query_by_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            log.append("i1", "t1", "CONTRACT", {"n": 1}, contract_id="c1")
            log.append("i1", "t2", "DCT", {"n": 2}, contract_id="c2")
            log.close()

            log2 = AuditLog(tmpdir, require_signature=False)
            results = list(log2.query_by_contract("c1"))
            assert len(results) == 1
            log2.close()

    def test_query_with_type_filter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            log.append("i1", "t1", "CONTRACT", {"n": 1})
            log.append("i1", "t2", "DCT", {"n": 2})
            log.close()

            log2 = AuditLog(tmpdir, require_signature=False)
            results = list(log2.query_by_intent("i1", tuple_type="CONTRACT"))
            assert len(results) == 1
            assert results[0].tuple_type == "CONTRACT"
            log2.close()


class TestAuditLogAmendments:
    """Test amendment chain tracking."""

    def test_amendment_of_existing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            log.append("i1", "t1", "CONTRACT", {"v": 1})
            log.close()

            log2 = AuditLog(tmpdir, require_signature=False)
            original = list(log2.query_by_intent("i1"))[0]
            ok, err = log2.append(
                "i1", "t1", "CONTRACT", {"v": 2},
                amendment_of=original.entry_id,
            )
            assert ok is True
            log2.close()

    def test_amendment_of_missing_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            ok, err = log.append(
                "i1", "t1", "CONTRACT", {"v": 2},
                amendment_of="nonexistent",
            )
            assert ok is False
            assert err == E_AMENDMENT_TARGET_MISSING
            log.close()

    def test_query_amendments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, require_signature=False)
            log.append("i1", "t1", "CONTRACT", {"v": 1})
            log.close()

            log2 = AuditLog(tmpdir, require_signature=False)
            original = list(log2.query_by_intent("i1"))[0]
            log2.append("i1", "t1", "CONTRACT", {"v": 2}, amendment_of=original.entry_id)
            log2.close()

            log3 = AuditLog(tmpdir, require_signature=False)
            amendments = list(log3.query_amendments(original.entry_id))
            assert len(amendments) == 1
            assert amendments[0].tuple_data == {"v": 2}
            log3.close()


class TestAuditLogContextManager:
    """Test context manager protocol."""

    def test_context_manager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with AuditLog(tmpdir, require_signature=False) as log:
                log.append("i1", "t1", "CONTRACT", {"n": 1})

            # Verify data persisted
            with AuditLog(tmpdir, require_signature=False) as log2:
                results = list(log2.query_by_intent("i1"))
                assert len(results) == 1


class TestAuditLogRetention:
    """Test retention enforcement."""

    def test_enforce_retention_no_old_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(tmpdir, retention_days=180)
            deleted = log.enforce_retention()
            assert deleted == 0
            log.close()
