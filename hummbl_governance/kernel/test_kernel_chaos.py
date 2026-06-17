#!/usr/bin/env python3
"""Chaos engineering tests for the HUMMBL Governance Kernel.

Randomly corrupt state files mid-run and verify graceful recovery.
These tests prove the Kernel is resilient to disk corruption, crashes,
and unexpected mutations.

Usage:
    python -m pytest hummbl_governance/kernel/test_kernel_chaos.py -v
"""

from __future__ import annotations

import json
import os
import random
import tempfile
from pathlib import Path

import pytest

from hummbl_governance.kernel import (
    IdentityEngine,
    Kernel,
    ReceiptEngine,
    SequenceEngine,
)
=======
from hummbl_governance.kernel.invariants import KernelInvariant, KernelPanic
>>>>>>> 675d140 (feat: extract Kernel governance OS as v1.1.0)


class TestChaosReceiptEngine:
    """Corrupt receipt files and verify recovery."""

    def test_random_line_corruption(self) -> None:
        """Corrupt 10% of lines in a receipt file; verify valid receipts still load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            # Create 100 receipts
            for i in range(100):
                receipt = engine.create(agent_id="chaos", action_type=f"STEP-{i}")
                engine.store(receipt)

            # Corrupt ~10% of lines
            receipt_file = engine.receipts_dir / "chaos.jsonl"
            lines = receipt_file.read_text().strip().split("\n")
            corrupted_count = 0
            for i in range(len(lines)):
                if random.random() < 0.10:
                    lines[i] = lines[i][: len(lines[i]) // 2] + "CORRUPTED!!!"
                    corrupted_count += 1
            receipt_file.write_text("\n".join(lines) + "\n")

            # Verify valid receipts still load
            loaded = engine.list_for_agent("chaos")
            assert len(loaded) == 100 - corrupted_count
            # All loaded receipts must have valid signatures
            for receipt in loaded:
                assert engine.validate(receipt) is True

    def test_random_byte_corruption(self) -> None:
        """Randomly flip bytes in receipt file; verify no crashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            for i in range(50):
                receipt = engine.create(agent_id="byte-chaos", action_type=f"STEP-{i}")
                engine.store(receipt)

            receipt_file = engine.receipts_dir / "byte-chaos.jsonl"
            data = bytearray(receipt_file.read_bytes())
            # Flip ~1% of bytes randomly
            for _ in range(len(data) // 100):
                idx = random.randint(0, len(data) - 1)
                data[idx] ^= 0xFF
            receipt_file.write_bytes(bytes(data))

            # Must not crash
            loaded = engine.list_for_agent("byte-chaos")
            # At least some receipts should survive
            assert len(loaded) > 0

    def test_truncate_mid_file(self) -> None:
        """Truncate file to 50%; verify partial load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            for i in range(50):
                receipt = engine.create(agent_id="trunc", action_type=f"STEP-{i}")
                engine.store(receipt)

            receipt_file = engine.receipts_dir / "trunc.jsonl"
            content = receipt_file.read_text()
            receipt_file.write_text(content[: len(content) // 2])

            loaded = engine.list_for_agent("trunc")
            # Should load some valid receipts without crashing
            assert len(loaded) <= 50
            assert len(loaded) >= 20  # At least ~half should be valid

    def test_delete_receipt_file_mid_run(self) -> None:
        """Delete receipt file after creation; verify clean empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            for i in range(10):
                receipt = engine.create(agent_id="deleted", action_type=f"STEP-{i}")
                engine.store(receipt)

            receipt_file = engine.receipts_dir / "deleted.jsonl"
            os.remove(receipt_file)

            loaded = engine.list_for_agent("deleted")
            assert loaded == []

    def test_chain_breaks_after_corruption(self) -> None:
        """Corrupt a middle receipt; verify chain detects break."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            receipts = []
            for i in range(20):
                receipt = engine.create(agent_id="chain-break", action_type=f"STEP-{i}")
                engine.store(receipt)
                receipts.append(receipt)

            # Corrupt line 10 (0-indexed: line 10 is the 11th receipt)
            receipt_file = engine.receipts_dir / "chain-break.jsonl"
            lines = receipt_file.read_text().strip().split("\n")
            lines[10] = json.dumps({"agent_id": "fake", "action_type": "FAKE"})
            receipt_file.write_text("\n".join(lines) + "\n")

            # Chain should be broken
            valid, _ = engine.verify_chain("chain-break")
            assert valid is False


class TestChaosIdentityEngine:
    """Corrupt identity registry and verify recovery."""

    def test_registry_corruption_recovery(self) -> None:
        """Corrupt 20% of identity registry lines; verify survivors load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IdentityEngine(Path(tmpdir))
            for i in range(50):
                engine.register(f"agent-{i:02d}")

            registry_file = engine.registry_file
            lines = registry_file.read_text().strip().split("\n")
            corrupted = 0
            for i in range(len(lines)):
                if random.random() < 0.20:
                    lines[i] = "not valid json {{"
                    corrupted += 1
            registry_file.write_text("\n".join(lines) + "\n")

            # Reload engine
            engine2 = IdentityEngine(Path(tmpdir))
            assert len(engine2._identities) == 50 - corrupted

    def test_role_claims_corruption(self) -> None:
        """Corrupt role claims file; verify engine recovers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IdentityEngine(Path(tmpdir))
            for i in range(20):
                engine.register(f"agent-{i}")
                engine.claim_role(f"agent-{i}", "AI-PE")

            claims_file = engine.role_claims_file
            lines = claims_file.read_text().strip().split("\n")
            for i in range(len(lines)):
                if random.random() < 0.30:
                    lines[i] = "truncated..."
            claims_file.write_text("\n".join(lines) + "\n")

            engine2 = IdentityEngine(Path(tmpdir))
            # Some claims survive, no crash
            assert len(engine2._role_claims) <= 20

    def test_empty_registry_boot(self) -> None:
        """Boot with empty identity registry file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = Path(tmpdir) / "identity_registry.jsonl"
            registry.write_text("")
            engine = IdentityEngine(Path(tmpdir))
            assert len(engine._identities) == 0

    def test_permission_denied_graceful(self) -> None:
        """Make state dir read-only; verify KernelPanics gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IdentityEngine(Path(tmpdir))
            engine.register("test")
            # Make file read-only
            os.chmod(engine.registry_file, 0o444)
            try:
                # This should fail gracefully
                with pytest.raises((PermissionError, OSError)):
                    engine.register("test2")
            finally:
                os.chmod(engine.registry_file, 0o644)


class TestChaosSequenceEngine:
    """Corrupt sequence counters and verify recovery."""

    def test_counters_corruption(self) -> None:
        """Corrupt counters JSON; verify engine resets gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SequenceEngine(Path(tmpdir))
            engine.next("agent-a")
            engine.next("agent-a")
            engine.next("agent-b")

            # Corrupt counters file
            engine.counters_file.write_text("not json")

            # Reload
            engine2 = SequenceEngine(Path(tmpdir))
            assert engine2.current("agent-a") == 0
            assert engine2.current("agent-b") == 0

    def test_counters_partial_corruption(self) -> None:
        """Counters file with valid JSON but wrong types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SequenceEngine(Path(tmpdir))
            engine.next("agent")

            # Write string instead of int
            engine.counters_file.write_text('{"agent": "not_a_number"}')

            engine2 = SequenceEngine(Path(tmpdir))
            assert engine2.current("agent") == 0


class TestChaosKernelIntegration:
    """Chaos tests at the full Kernel level."""

    def test_kernel_boot_with_corrupt_state(self) -> None:
        """Boot Kernel with partially corrupt state; verify recovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Pre-seed corrupt state
            state_dir = Path(tmpdir)
<<<<<<< HEAD
            (state_dir / "identity_registry.jsonl").write_text(
                'bad json\n{"agent_id": "good", "trust_tier": "TRUSTED"}\n'
            )
            (state_dir / "sequence_counters.json").write_text('{"bad": "json"}')
            (state_dir / "receipts").mkdir(exist_ok=True)

            # Boot should succeed despite corruption
            kernel = Kernel.boot(state_dir=state_dir)
            health = kernel.health()
            assert health["healthy"] is True

    def test_kernel_survives_missing_atlas(self) -> None:
        """Boot with missing atlas; verify degraded but functional."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Override atlas_dir to a non-existent path
            from hummbl_governance.kernel.law_engine import LawEngine
            # Manually construct kernel with no atlas
            kernel = Kernel(state_dir=Path(tmpdir))
            # Replace law engine with empty atlas
            kernel.law = LawEngine(atlas_dir=Path(tmpdir) / "nonexistent_atlas")
            kernel._boot_sequence()
            assert kernel.booted is True
            assert len(kernel.law.laws) == 0  # No atlas loaded
            health = kernel.health()
            assert health["healthy"] is True  # Degraded mode still healthy

    def test_random_corruption_mid_session(self) -> None:
        """Create receipts, corrupt some, create more, verify no crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            kernel = Kernel.boot(state_dir=Path(tmpdir))
            kernel.identity.register("chaos-agent")

            # Phase 1: Create receipts
            for i in range(20):
                receipt = kernel.create_receipt("chaos-agent", f"PHASE1-{i}")
                kernel.store_receipt(receipt)

            # Phase 2: Corrupt some receipts
            receipt_file = kernel.receipt.receipts_dir / "chaos-agent.jsonl"
            lines = receipt_file.read_text().strip().split("\n")
            for i in range(len(lines)):
                if random.random() < 0.20:
                    lines[i] = "CORRUPT"
            receipt_file.write_text("\n".join(lines) + "\n")

            # Phase 3: Continue creating receipts
            for i in range(20):
                receipt = kernel.create_receipt("chaos-agent", f"PHASE2-{i}")
                kernel.store_receipt(receipt)

            # Must not crash; at least some valid receipts exist
            loaded = kernel.receipt.list_for_agent("chaos-agent")
            assert len(loaded) > 0
