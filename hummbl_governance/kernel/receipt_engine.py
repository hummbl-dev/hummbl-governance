"""Receipt Engine — K1 invariant enforcement.

Every action that affects shared state produces a structured, signed,
append-only receipt. No receipt = no proof = no authority.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .invariants import KernelInvariant, KernelPanic


@dataclass
class Receipt:
    """A structured, signed record of an agent action."""

    receipt_id: str
    agent_id: str
    sequence_id: int
    prev_receipt_hash: str
    timestamp: str
    action_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    law_checks: list[str] = field(default_factory=list)
    violations: list[dict[str, Any]] = field(default_factory=list)
    evidence_grade: str = "UNGRADED"
    signature: str = ""

    def canonical_json(self) -> str:
        """Return canonical JSON for hashing (excludes signature)."""
        d = asdict(self)
        d.pop("signature")
        return json.dumps(d, sort_keys=True, separators=(",", ":"))

    def compute_hash(self) -> str:
        """Compute SHA-256 of canonical form."""
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def verify_signature(self, secret: bytes) -> bool:
        """Verify HMAC-SHA256 signature."""
        expected = hmac.new(
            secret, self.canonical_json().encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(self.signature, expected)


class ReceiptEngine:
    """Engine for creating, signing, storing, and validating receipts."""

    def __init__(self, state_dir: Path, signing_secret: bytes | None = None) -> None:
        self.state_dir = state_dir
        self.receipts_dir = state_dir / "receipts"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.signing_secret = signing_secret or self._load_or_generate_secret()

    def _load_or_generate_secret(self) -> bytes:
        """Load existing signing secret or generate a new one."""
        secret_path = self.state_dir / ".kernel_secret"
        if secret_path.exists():
            return secret_path.read_bytes()
        secret = os.urandom(32)
        secret_path.write_bytes(secret)
        os.chmod(secret_path, 0o600)
        return secret

    def create(
        self,
        agent_id: str,
        action_type: str,
        payload: dict[str, Any] | None = None,
        law_checks: list[str] | None = None,
        evidence_grade: str = "UNGRADED",
        prev_receipt_hash: str = "",
        sequence_id: int = 0,
    ) -> Receipt:
        """Create a new receipt.

        Raises KernelPanic if K1 would be violated (e.g., empty agent_id).
        """
        if not agent_id:
            raise KernelPanic(
                KernelInvariant.RECEIPT,
                "Receipt requires agent_id (K1)",
            )
        if not action_type:
            raise KernelPanic(
                KernelInvariant.RECEIPT,
                "Receipt requires action_type (K1)",
            )

        receipt = Receipt(
            receipt_id=f"r-{uuid.uuid4().hex[:12]}",
            agent_id=agent_id,
            sequence_id=sequence_id,
            prev_receipt_hash=prev_receipt_hash,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            action_type=action_type,
            payload=payload or {},
            law_checks=law_checks or [],
            evidence_grade=evidence_grade,
        )
        receipt.signature = self._sign(receipt)
        return receipt

    def _sign(self, receipt: Receipt) -> str:
        """Sign a receipt with HMAC-SHA256."""
        return hmac.new(
            self.signing_secret,
            receipt.canonical_json().encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def store(self, receipt: Receipt) -> str:
        """Store receipt in append-only JSONL.

        Returns the receipt_id.
        """
        receipt_file = self.receipts_dir / f"{receipt.agent_id}.jsonl"
        with open(receipt_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(receipt), sort_keys=True) + "\n")
        return receipt.receipt_id

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
