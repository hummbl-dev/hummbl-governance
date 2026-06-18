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

import json
import os
import random
import string
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from hummbl_governance.kernel import (
    AuthorityEngine,
    EvidenceEngine,
    IdentityEngine,
    Kernel,
    LawEngine,
    ReceiptEngine,
    ScheduleEngine,
    SequenceEngine,
)
from hummbl_governance.kernel.invariants import KernelInvariant, KernelPanic


def _tmp() -> Path:
    return Path(tempfile.mkdtemp(prefix="kernel_eval_"))


def _make_kernel(tmpdir: Path) -> Kernel:
    return Kernel.boot(state_dir=tmpdir)


# ===========================================================================
# 1. ADVERSARIAL EVALS
# ===========================================================================

class TestPerformance:
    """Measure performance under load."""

    def test_1000_receipts_latency(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            kernel = _make_kernel(Path(tmpdir))
            start = time.time()
            for i in range(1000):
                receipt = kernel.create_receipt("perf", "BULK", payload={"i": i})
                kernel.store_receipt(receipt)
            elapsed = time.time() - start
            print(f"\n    1000 receipts in {elapsed:.2f}s ({1000/elapsed:.0f}/sec)")
            assert elapsed < 30

    def test_10000_sequence_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SequenceEngine(Path(tmpdir))
            start = time.time()
            for _ in range(10000):
                engine.next("perf-agent")
            elapsed = time.time() - start
            print(f"\n    10000 sequence IDs in {elapsed:.2f}s")
            assert engine.current("perf-agent") == 10000

    def test_large_payload_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReceiptEngine(Path(tmpdir))
            big_data = "x" * (1024 * 1024)
            start = time.time()
            receipt = engine.create(agent_id="big", action_type="BULK", payload={"data": big_data})
            engine.store(receipt)
            elapsed = time.time() - start
            print(f"\n    1MB receipt in {elapsed:.2f}s")
            assert elapsed < 5
            loaded = engine.list_for_agent("big")[0]
            assert len(loaded.payload["data"]) == 1024 * 1024

    def test_bulk_identity_registration(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IdentityEngine(Path(tmpdir))
            start = time.time()
            for i in range(100):
                engine.register(f"bulk-{i}")
            elapsed = time.time() - start
            print(f"\n    100 agents in {elapsed:.2f}s")
            assert elapsed < 5
            assert len(engine._identities) == 100


# ===========================================================================
# 7. FUZZING EVALS
# ===========================================================================
