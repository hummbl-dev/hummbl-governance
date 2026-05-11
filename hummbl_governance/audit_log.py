"""Audit Log -- Append-only JSONL governance audit log.

Implements an append-only audit log with daily file rotation,
configurable retention, HMAC integrity, and query capabilities.

Usage:
    from hummbl_governance import AuditLog

    log = AuditLog(base_dir="/tmp/audit")
    log.append(
        intent_id="intent-1",
        task_id="task-1",
        tuple_type="CONTRACT",
        tuple_data={"name": "test-contract"},
        signature="hmac-hex-here",
    )

    for entry in log.query_by_intent("intent-1"):
        print(entry.entry_id, entry.tuple_type)

Stdlib-only. Zero third-party dependencies.
"""

from __future__ import annotations

import gzip
import json
import logging
import os
import shutil
import threading
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import partial
from pathlib import Path
from typing import Any, Callable, Literal

logger = logging.getLogger(__name__)

DEFAULT_RETENTION_DAYS = 180
ROTATION_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# Error codes
E_AUDIT_INCOMPLETE = "E_AUDIT_INCOMPLETE"
E_AUDIT_IMMUTABLE = "E_AUDIT_IMMUTABLE"
E_AMENDMENT_TARGET_MISSING = "E_AMENDMENT_TARGET_MISSING"
E_VERIFICATION_REF_INVALID = "E_VERIFICATION_REF_INVALID"
E_EVIDENCE_REQUIRED = "E_EVIDENCE_REQUIRED"

# Supported tuple types
TUPLE_TYPES = ("DCTX", "CONTRACT", "EVIDENCE", "ATTEST", "DCT", "SYSTEM")
TupleType = Literal["DCTX", "CONTRACT", "EVIDENCE", "ATTEST", "DCT", "SYSTEM"]


try:
    from hummbl_library.governance.types import AuditEntry
except ImportError:
    # Fallback for environments without hummbl-library installed

    @dataclass(frozen=True)
    class AuditEntry:
        """Single entry in the governance audit log."""

        timestamp: str
        entry_id: str
        intent_id: str
        task_id: str
        tuple_type: str
        tuple_data: dict[str, Any]
        signature: str | None = None
        contract_id: str | None = None
        capability_token_id: str | None = None
        verification_id: str | None = None
        amendment_of: str | None = None

        def to_jsonl(self) -> str:
            """Serialize to JSONL line."""
            data: dict[str, Any] = {
                "timestamp": self.timestamp,
                "entry_id": self.entry_id,
                "intent_id": self.intent_id,
                "task_id": self.task_id,
                "tuple_type": self.tuple_type,
                "tuple_data": self.tuple_data,
                "signature": self.signature,
            }
            if self.contract_id is not None:
                data["contract_id"] = self.contract_id
            if self.capability_token_id is not None:
                data["capability_token_id"] = self.capability_token_id
            if self.verification_id is not None:
                data["verification_id"] = self.verification_id
            if self.amendment_of is not None:
                data["amendment_of"] = self.amendment_of
            return json.dumps(data, sort_keys=True, separators=(",", ":"))

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> AuditEntry:
            """Deserialize from dictionary."""
            return cls(
                timestamp=data["timestamp"],
                entry_id=data["entry_id"],
                intent_id=data["intent_id"],
                task_id=data["task_id"],
                tuple_type=data["tuple_type"],
                tuple_data=data["tuple_data"],
                signature=data.get("signature"),
                contract_id=data.get("contract_id"),
                capability_token_id=data.get("capability_token_id"),
                verification_id=data.get("verification_id"),
                amendment_of=data.get("amendment_of"),
            )


class AuditLog:
    """Append-only governance audit log.

    Features:
        - Atomic append-only writes
        - Daily file rotation
        - Configurable retention (default 180 days)
        - Query by intent, task, entry ID, contract
        - Amendment chain tracking
        - Optional async buffering
        - Thread-safe

    Args:
        base_dir: Directory for audit log files.
        retention_days: Days to retain logs (default 180).
        enable_async: Enable async write buffering (default False).
        require_signature: If True (default), rejects unsigned entries.
        file_prefix: Prefix for log filenames (default "governance").
    """

    def __init__(
        self,
        base_dir: Path | str,
        retention_days: int = DEFAULT_RETENTION_DAYS,
        enable_async: bool = False,
        require_signature: bool = True,
        file_prefix: str = "governance",
    ):
        self._base_dir = Path(base_dir)
        self._retention_days = retention_days
        self._enable_async = enable_async
        self._require_signature = require_signature
        self._file_prefix = file_prefix

        self._base_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self._base_dir, 0o700)
        except OSError:
            pass

        self._lock = threading.RLock()
        self._buffer: list[AuditEntry] = []
        self._buffer_lock = threading.RLock()
        self._current_file: Path | None = None
        self._file_handle: Any = None

    def _get_current_file(self) -> Path:
        """Get current log file path (daily rotation)."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._base_dir / f"{self._file_prefix}-{today}.jsonl"

    def _rotate_if_needed(self) -> None:
        """Check and perform file rotation if needed."""
        current = self._get_current_file()
        if self._current_file != current:
            if self._file_handle:
                self._file_handle.close()
                self._file_handle = None
            self._current_file = current

        if current.exists() and current.stat().st_size > ROTATION_SIZE_BYTES:
            if self._file_handle:
                self._file_handle.close()
                self._file_handle = None
            compressed = current.with_suffix(".jsonl.gz")
            with open(current, "rb") as f_in, gzip.open(compressed, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            current.unlink()

    def _open_file(self) -> Any:
        """Open current log file for appending."""
        if self._file_handle is None or self._file_handle.closed:
            self._current_file = self._get_current_file()
            self._file_handle = open(self._current_file, "a", encoding="utf-8")
        return self._file_handle

    def _validate_append(
        self,
        tuple_type: str,
        signature: str | None,
        require_signature: bool | None,
        verification_id: str | None,
        amendment_of: str | None,
    ) -> str | None:
        """Validate preconditions for append. Returns error code or None."""
        sig_required = require_signature if require_signature is not None else self._require_signature
        if sig_required and not signature:
            return E_AUDIT_IMMUTABLE

        if tuple_type == "ATTEST":
            if verification_id is None:
                return E_EVIDENCE_REQUIRED
            ref_entry = self.query_by_entry_id(verification_id)
            if ref_entry is None or ref_entry.tuple_type != "EVIDENCE":
                return E_VERIFICATION_REF_INVALID

        if amendment_of is not None:
            if self.query_by_entry_id(amendment_of) is None:
                return E_AMENDMENT_TARGET_MISSING

        return None

    def append(
        self,
        intent_id: str,
        task_id: str,
        tuple_type: str,
        tuple_data: dict[str, Any],
        signature: str | None = None,
        require_signature: bool | None = None,
        contract_id: str | None = None,
        capability_token_id: str | None = None,
        verification_id: str | None = None,
        amendment_of: str | None = None,
    ) -> tuple[bool, str | None]:
        """Append entry to audit log.

        Args:
            intent_id: Root intent identifier.
            task_id: Task identifier.
            tuple_type: Type of tuple (DCTX, CONTRACT, EVIDENCE, ATTEST, DCT, SYSTEM).
            tuple_data: The tuple data.
            signature: HMAC signature.
            require_signature: Override instance-level signature requirement.
            contract_id: Cross-link to governing CONTRACT entry.
            capability_token_id: Cross-link to authorizing DCT entry.
            verification_id: Cross-link from ATTEST to EVIDENCE entry.
            amendment_of: entry_id of the entry being amended.

        Returns:
            Tuple of (success, error_code).
        """
        error = self._validate_append(
            tuple_type, signature, require_signature, verification_id, amendment_of,
        )
        if error:
            return False, error

        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            entry_id=str(uuid.uuid4()),
            intent_id=intent_id,
            task_id=task_id,
            tuple_type=tuple_type,
            tuple_data=tuple_data,
            signature=signature,
            contract_id=contract_id,
            capability_token_id=capability_token_id,
            verification_id=verification_id,
            amendment_of=amendment_of,
        )

        if self._enable_async:
            return self._append_async(entry)
        else:
            return self._append_sync(entry)

    def _append_sync(self, entry: AuditEntry) -> tuple[bool, str | None]:
        """Synchronous append with atomic write."""
        with self._lock:
            try:
                self._rotate_if_needed()
                f = self._open_file()
                f.write(entry.to_jsonl() + "\n")
                f.flush()
                os.fsync(f.fileno())
                if self._current_file:
                    try:
                        self._current_file.chmod(0o600)
                    except OSError:
                        pass
                return True, None
            except (IOError, OSError):
                return False, E_AUDIT_INCOMPLETE

    def _append_async(self, entry: AuditEntry) -> tuple[bool, str | None]:
        """Async append to buffer."""
        with self._buffer_lock:
            self._buffer.append(entry)
            if len(self._buffer) >= 100:
                return self._flush_buffer()
            return True, None

    def _flush_buffer(self) -> tuple[bool, str | None]:
        """Flush async buffer to disk."""
        with self._lock, self._buffer_lock:
            if not self._buffer:
                return True, None
            try:
                self._rotate_if_needed()
                f = self._open_file()
                for entry in self._buffer:
                    f.write(entry.to_jsonl() + "\n")
                f.flush()
                os.fsync(f.fileno())
                if self._current_file:
                    try:
                        self._current_file.chmod(0o600)
                    except OSError:
                        pass
                self._buffer.clear()
                return True, None
            except (IOError, OSError):
                return False, E_AUDIT_INCOMPLETE

    def query_by_intent(
        self, intent_id: str, tuple_type: str | None = None, since: str | None = None
    ) -> Iterator[AuditEntry]:
        """Query entries by intent_id."""
        yield from self._query(
            lambda e: e.intent_id == intent_id, tuple_type=tuple_type, since=since
        )

    def query_by_task(
        self, task_id: str, tuple_type: str | None = None
    ) -> Iterator[AuditEntry]:
        """Query entries by task_id."""
        yield from self._query(lambda e: e.task_id == task_id, tuple_type=tuple_type)

    def query_by_entry_id(self, entry_id: str) -> AuditEntry | None:
        """Query a single entry by its entry_id."""
        for entry in self._query(lambda e: e.entry_id == entry_id):
            return entry
        return None

    def query_by_contract(
        self, contract_id: str, tuple_type: str | None = None
    ) -> Iterator[AuditEntry]:
        """Query entries by contract_id cross-link."""
        yield from self._query(
            lambda e: e.contract_id == contract_id, tuple_type=tuple_type
        )

    def query_amendments(self, entry_id: str) -> Iterator[AuditEntry]:
        """Query all amendments to a given entry."""
        yield from self._query(lambda e: e.amendment_of == entry_id)

    @staticmethod
    def _parse_entries(fileobj: Any) -> Iterator[AuditEntry]:
        """Parse JSONL lines into AuditEntry objects, skipping malformed lines."""
        for line in fileobj:
            line = line.strip()
            if not line:
                continue
            try:
                yield AuditEntry.from_dict(json.loads(line))
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    def _query(
        self,
        predicate: Callable[[AuditEntry], bool],
        tuple_type: str | None = None,
        since: str | None = None,
    ) -> Iterator[AuditEntry]:
        """Internal query implementation."""
        files = sorted(
            self._base_dir.glob(f"{self._file_prefix}-*.jsonl*"), reverse=True
        )

        for filepath in files:
            opener = (
                partial(gzip.open, filepath, "rt", encoding="utf-8")
                if filepath.suffix == ".gz"
                else partial(open, filepath, "r", encoding="utf-8")
            )
            try:
                with opener() as f:
                    for entry in self._parse_entries(f):
                        if not predicate(entry):
                            continue
                        if tuple_type and entry.tuple_type != tuple_type:
                            continue
                        if since and entry.timestamp < since:
                            continue
                        yield entry
            except (IOError, OSError):
                continue

    def enforce_retention(self) -> int:
        """Enforce retention policy. Returns number of files deleted."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self._retention_days)
        deleted = 0
        for filepath in self._base_dir.glob(f"{self._file_prefix}-*.jsonl*"):
            try:
                date_str = filepath.stem.split("-")[1:4]
                file_date = datetime(
                    int(date_str[0]), int(date_str[1]), int(date_str[2]),
                    tzinfo=timezone.utc,
                )
                if file_date < cutoff:
                    filepath.unlink()
                    deleted += 1
            except (ValueError, IndexError):
                continue
        return deleted

    def explain(self, entry_id: str) -> list[AuditEntry]:
        """Trace the full audit chain for an action, answering "why did this happen?"

        Follows cross-links (contract_id, capability_token_id, amendment_of,
        verification_id) to reconstruct the governance chain that authorized
        an action. Returns entries in causal order: authorization first,
        action last.

        Implements the explicability principle from Floridi et al. (2018)
        AI4People framework: intelligibility (how?) + accountability (who?).

        Args:
            entry_id: The entry_id to explain.

        Returns:
            List of AuditEntry objects forming the explanation chain,
            ordered from root authorization to the target entry.
            Empty list if entry_id is not found.
        """
        target = self.query_by_entry_id(entry_id)
        if target is None:
            return []

        chain: list[AuditEntry] = []
        visited: set[str] = set()
        self._trace_chain(target, chain, visited)

        # Reverse to get causal order (root first, target last)
        chain.reverse()
        return chain

    def _trace_chain(
        self,
        entry: AuditEntry,
        chain: list[AuditEntry],
        visited: set[str],
    ) -> None:
        """Recursively trace cross-links to build the explanation chain."""
        if entry.entry_id in visited:
            return
        visited.add(entry.entry_id)
        chain.append(entry)

        # Follow amendment_of (this entry amends another)
        if entry.amendment_of:
            parent = self.query_by_entry_id(entry.amendment_of)
            if parent:
                self._trace_chain(parent, chain, visited)

        # Follow capability_token_id (authorized by this DCT)
        if entry.capability_token_id:
            dct = self.query_by_entry_id(entry.capability_token_id)
            if dct:
                self._trace_chain(dct, chain, visited)

        # Follow contract_id (governed by this contract)
        if entry.contract_id:
            contract = self.query_by_entry_id(entry.contract_id)
            if contract:
                self._trace_chain(contract, chain, visited)

        # Follow verification_id (attests to this evidence)
        if entry.verification_id:
            evidence = self.query_by_entry_id(entry.verification_id)
            if evidence:
                self._trace_chain(evidence, chain, visited)

    def close(self) -> None:
        """Close file handles and flush buffers."""
        if self._enable_async:
            self._flush_buffer()
        with self._lock:
            if self._file_handle and not self._file_handle.closed:
                self._file_handle.close()
                self._file_handle = None

    def __enter__(self) -> AuditLog:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
