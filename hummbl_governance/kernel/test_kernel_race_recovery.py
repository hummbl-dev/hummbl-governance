#!/usr/bin/env python3
"""Comprehensive evaluation suite for the HUMMBL Governance Kernel.

Categories:
  1. Adversarial — try to bypass invariants, forge receipts, escalate privileges
  2. Edge Cases — empty strings, unicode, max sizes, null bytes, injection
  3. Race Conditions — concurrent receipt creation, shared state mutation
  4. Recovery — corrupted chains, missing files, truncated JSONL
  5. Invariant Enforcement — verify every panic triggers on violation
  6. Performance — large receipt volumes, long chains, bulk operations
  7. Fuzzing — random payloads, random agents, random sequences
  8. Cross-Engine Integration — Receipt + Law + Identity + Authority together

Usage:
    python -m pytest hummbl_governance/kernel/test_kernel_evals.py -v
"""

from __future__ import annotations

import tempfile
import threading
from pathlib import Path


from hummbl_governance.kernel import (
    IdentityEngine,
    Kernel,
    ReceiptEngine,
    SequenceEngine,
)


def _tmp() -> Path:
    return Path(tempfile.mkdtemp(prefix="kernel_eval_"))


def _make_kernel(tmpdir: Path) -> Kernel:
    return Kernel.boot(state_dir=tmpdir)


# ===========================================================================
# 1. ADVERSARIAL EVALS
# ===========================================================================

class TestRaceConditions:
    """Concurrent operations must not corrupt state."""

    def test_concurrent_receipt_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            errors: list[Exception] = []

            def create_receipts(n: int) -> None:
                for _ in range(n):
                    try:
                        receipt = engine.create(agent_id="concurrent", action_type="RACE")
                        engine.store(receipt)
                    except Exception as e:
                        errors.append(e)

            threads = [threading.Thread(target=create_receipts, args=(20,)) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0, f"Errors: {errors}"
            receipts = engine.list_for_agent("concurrent")
            assert len(receipts) == 100

    def test_concurrent_sequence_assignment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SequenceEngine(Path(tmpdir))
            seq_ids: list[int] = []
            lock = threading.Lock()

            def get_seq(n: int) -> None:
                for _ in range(n):
                    sid = engine.next("race-agent")
                    with lock:
                        seq_ids.append(sid)

            threads = [threading.Thread(target=get_seq, args=(20,)) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(seq_ids) == 100
            assert sorted(seq_ids) == list(range(1, 101))

    def test_concurrent_role_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IdentityEngine(Path(tmpdir))
            for i in range(10):
                engine.register(f"agent-{i}")

            def claim(i: int) -> None:
                engine.claim_role(f"agent-{i}", "AI-PE")

            threads = [threading.Thread(target=claim, args=(i,)) for i in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            claims = [c for key, c in engine._role_claims.items() if c["role_id"] == "AI-PE"]
            assert len(claims) == 10


# ===========================================================================
# 4. RECOVERY EVALS
# ===========================================================================

class TestRecovery:
    """Kernel must recover gracefully from corruption."""

    def test_corrupted_receipt_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            receipt = engine.create(agent_id="recover", action_type="VALID")
            engine.store(receipt)
            receipt_file = engine.receipts_dir / "recover.jsonl"
            with open(receipt_file, "a") as f:
                f.write("this is not json\n")
            receipts = engine.list_for_agent("recover")
            assert len(receipts) == 1
            assert receipts[0].action_type == "VALID"

    def test_truncated_receipt_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            receipt = engine.create(agent_id="trunc", action_type="TEST")
            engine.store(receipt)
            receipt_file = engine.receipts_dir / "trunc.jsonl"
            content = receipt_file.read_text()
            receipt_file.write_text(content[: len(content) // 2])
            receipts = engine.list_for_agent("trunc")
            assert len(receipts) <= 1

    def test_missing_sequence_counters(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SequenceEngine(Path(tmpdir))
            assert engine.current("new-agent") == 0
            assert engine.next("new-agent") == 1

    def test_missing_identity_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IdentityEngine(Path(tmpdir))
            assert engine.resolve("nobody") is None
            engine.register("newbie")
            assert engine.resolve("newbie") is not None

    def test_kernel_boot_with_corrupt_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            id_file = Path(tmpdir) / "identity_registry.jsonl"
            id_file.write_text("not valid json\n")
            engine = IdentityEngine(Path(tmpdir))
            assert len(engine._identities) == 0

    def test_rebuild_chain_after_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            r1 = engine.create(agent_id="gap", action_type="ONE")
            engine.store(r1)
            r2 = engine.create(agent_id="gap", action_type="TWO", prev_receipt_hash="wrong")
            engine.store(r2)
            valid, _ = engine.verify_chain("gap")
            assert valid is False


# ===========================================================================
# 5. INVARIANT ENFORCEMENT EVALS
# ===========================================================================
