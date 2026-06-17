"""Receipt Engine — K1 invariant enforcement.

Every action that affects shared state produces a structured, signed,
append-only receipt. No receipt = no proof = no authority.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .invariants import KernelInvariant, KernelPanic

logger = logging.getLogger(__name__)

# Best-effort corpus adapter import
try:
    from ..corpus_adapter import CorpusAdapter
except ImportError:
    CorpusAdapter = None  # type: ignore[misc,assignment]

        self.state_dir = state_dir
        self.receipts_dir = state_dir / "receipts"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.signing_secret = signing_secret or self._load_or_generate_secret()
        self.corpus_adapter = corpus_adapter
        self._io_lock = threading.RLock()
    def validate(self, receipt: Receipt) -> bool:
        """Validate a receipt's signature and structure.

        Returns True if valid, False if signature mismatch.
        """
        return receipt.verify_signature(self.signing_secret)

    def list_for_agent(self, agent_id: str) -> list[Receipt]:
        """List all receipts for an agent."""
        receipt_file = self.receipts_dir / f"{agent_id}.jsonl"
        if not receipt_file.exists():
            return []
        receipts: list[Receipt] = []
        with self._io_lock:
            try:
                text = receipt_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # File has invalid UTF-8 bytes — try with errors='replace'
                text = receipt_file.read_text(encoding="utf-8", errors="replace")
        for line in text.strip().split("\n"):
            if not line:
                continue
            try:
                receipts.append(Receipt(**json.loads(line)))
            except (json.JSONDecodeError, TypeError):
                # Corrupted line — skip and continue
                continue
        return receipts

    def last_for_agent(self, agent_id: str) -> Receipt | None:
        """Get the most recent receipt for an agent."""
        receipts = self.list_for_agent(agent_id)
        return receipts[-1] if receipts else None

    def verify_chain(self, agent_id: str) -> tuple[bool, str]:
        """Verify the hash chain for an agent's receipts.

        Returns (valid, last_hash).
        """
        receipts = self.list_for_agent(agent_id)
        if not receipts:
            return True, ""

        prev_hash = ""
        for receipt in receipts:
            if receipt.prev_receipt_hash != prev_hash:
                return False, receipt.compute_hash()
            if not self.validate(receipt):
                return False, receipt.compute_hash()
            prev_hash = receipt.compute_hash()
        return True, prev_hash
