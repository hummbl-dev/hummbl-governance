"""Tests for corpus_adapter module."""

from __future__ import annotations

from pathlib import Path

from hummbl_governance.kernel import Receipt, ReceiptEngine
from hummbl_governance.corpus_adapter import CorpusAdapter


class TestCorpusAdapter:
    def test_receipt_to_kernel_output(self, tmp_path: Path) -> None:
        engine = ReceiptEngine(tmp_path)
        receipt = engine.create(agent_id="devin", action_type="BUS_POST")

        adapter = CorpusAdapter(state_dir=tmp_path)
        # No corpus ingestor available (no corpus_dir), should queue locally
        result = adapter.ingest_receipt(receipt, kernel_version="1.1.0")
        assert result == receipt.receipt_id

        # Check local queue
        queue_file = tmp_path / "corpus_queue" / "pending.jsonl"
        assert queue_file.exists()

    def test_local_queue_content(self, tmp_path: Path) -> None:
        engine = ReceiptEngine(tmp_path)
        receipt = engine.create(agent_id="devin", action_type="BUS_POST")

        adapter = CorpusAdapter(state_dir=tmp_path)
        adapter.ingest_receipt(receipt)

        queue_file = tmp_path / "corpus_queue" / "pending.jsonl"
        lines = queue_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1

        import json
        entry = json.loads(lines[0])
        assert entry["kernel_output"]["kernel_name"] == "hummbl-governance"
        assert entry["kernel_output"]["receipt_ref"] == receipt.receipt_id

    def test_flush_queue_no_ingestor(self, tmp_path: Path) -> None:
        adapter = CorpusAdapter(state_dir=tmp_path)
        result = adapter.flush_queue()
        assert result == []
