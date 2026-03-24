"""Governance Bus -- Append-only JSONL audit log.

Implements an append-only governance event store with daily file rotation,
configurable retention, and query capabilities. All operations are stdlib-only
and feature-flagged behind the ENABLE_IDP environment variable.
"""

from __future__ import annotations

import gzip
import json
import os
import shutil
import threading
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import partial
from pathlib import Path
from typing import Any, Literal


def _is_idp_enabled() -> bool:
    """Check if IDP feature flag is enabled (runtime check)."""
    return os.environ.get("ENABLE_IDP", "true").lower() == "true"


# Retention configuration
DEFAULT_RETENTION_DAYS = 180  # EU AI Act Art 26(5) recommends minimum 6 months
ROTATION_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# Error codes
IDP_E_AUDIT_INCOMPLETE = "IDP_E_AUDIT_INCOMPLETE"
IDP_E_AUDIT_IMMUTABLE = "IDP_E_AUDIT_IMMUTABLE"


@dataclass(frozen=True)
class GovernanceEntry:
    """Single entry in the governance audit log.

    Attributes:
        timestamp: ISO8601 UTC timestamp.
        entry_id: UUID for this entry.
        intent_id: Root intent (links delegation tree).
        task_id: Specific task identifier.
        tuple_type: Type of governance tuple.
        tuple_data: The actual governance data.
        signature: Optional HMAC signature for integrity.
    """

    timestamp: str
    entry_id: str
    intent_id: str
    task_id: str
    tuple_type: Literal["DCTX", "CONTRACT", "EVIDENCE", "ATTEST", "DCT", "SYSTEM"]
    tuple_data: dict[str, Any]
    signature: str | None = None

    def to_jsonl(self) -> str:
        """Serialize to JSONL line."""
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "entry_id": self.entry_id,
                "intent_id": self.intent_id,
                "task_id": self.task_id,
                "tuple_type": self.tuple_type,
                "tuple_data": self.tuple_data,
                "signature": self.signature,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GovernanceEntry:
        """Deserialize from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            entry_id=data["entry_id"],
            intent_id=data["intent_id"],
            task_id=data["task_id"],
            tuple_type=data["tuple_type"],
            tuple_data=data["tuple_data"],
            signature=data.get("signature"),
        )


class GovernanceBus:
    """Append-only governance audit log.

    Thread-safe for concurrent writes. Supports daily file rotation,
    configurable retention, and query by intent_id or task_id.

    Args:
        base_dir: Directory for audit log files. Required.
        retention_days: Days to retain logs (default: 180).
        enable_async: Enable async write buffering (default: False).
    """

    def __init__(
        self,
        base_dir: Path | str,
        retention_days: int = DEFAULT_RETENTION_DAYS,
        enable_async: bool = False,
    ):
        self._base_dir = Path(base_dir)
        self._retention_days = retention_days
        self._enable_async = enable_async

        # Ensure directory exists with restrictive permissions
        self._base_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self._base_dir, 0o700)
        except OSError:
            pass  # Best-effort on permission hardening

        # Thread lock for concurrent writes
        self._lock = threading.RLock()

        # Async buffer (if enabled)
        self._buffer: list[GovernanceEntry] = []
        self._buffer_lock = threading.RLock()

        # Current file handle (lazy init)
        self._current_file: Path | None = None
        self._file_handle: Any = None

    def _get_current_file(self) -> Path:
        """Get current log file path (daily rotation)."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._base_dir / f"governance-{today}.jsonl"

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
            shutil.copy2(current, compressed)
            current.unlink()

    def _open_file(self) -> Any:
        """Open current log file for appending."""
        if self._file_handle is None or self._file_handle.closed:
            self._current_file = self._get_current_file()
            self._file_handle = open(self._current_file, "a", encoding="utf-8")
        return self._file_handle

    def append(
        self,
        intent_id: str,
        task_id: str,
        tuple_type: Literal["DCTX", "CONTRACT", "EVIDENCE", "ATTEST", "DCT", "SYSTEM"],
        tuple_data: dict[str, Any],
        signature: str | None = None,
    ) -> tuple[bool, str | None]:
        """Append entry to governance log.

        Args:
            intent_id: Root intent identifier.
            task_id: Task identifier.
            tuple_type: Type of governance tuple.
            tuple_data: The tuple data.
            signature: Optional HMAC signature.

        Returns:
            Tuple of (success, error_code).
        """
        if not _is_idp_enabled():
            return True, None

        entry = GovernanceEntry(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            entry_id=self._generate_entry_id(),
            intent_id=intent_id,
            task_id=task_id,
            tuple_type=tuple_type,
            tuple_data=tuple_data,
            signature=signature,
        )

        if self._enable_async:
            return self._append_async(entry)
        else:
            return self._append_sync(entry)

    def _append_sync(self, entry: GovernanceEntry) -> tuple[bool, str | None]:
        """Synchronous append with atomic write."""
        with self._lock:
            try:
                self._rotate_if_needed()
                f = self._open_file()
                f.write(entry.to_jsonl() + "\n")
                f.flush()
                os.fsync(f.fileno())
                return True, None
            except (IOError, OSError):
                return False, IDP_E_AUDIT_INCOMPLETE

    def _append_async(self, entry: GovernanceEntry) -> tuple[bool, str | None]:
        """Async append to buffer (flushed periodically)."""
        with self._buffer_lock:
            self._buffer.append(entry)
            if len(self._buffer) >= 100:
                return self._flush_buffer()
            return True, None

    def _flush_buffer(self) -> tuple[bool, str | None]:
        """Flush async buffer to disk."""
        with self._lock:
            with self._buffer_lock:
                if not self._buffer:
                    return True, None

                try:
                    self._rotate_if_needed()
                    f = self._open_file()
                    for entry in self._buffer:
                        f.write(entry.to_jsonl() + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                    self._buffer.clear()
                    return True, None
                except (IOError, OSError):
                    return False, IDP_E_AUDIT_INCOMPLETE

    def _generate_entry_id(self) -> str:
        """Generate unique entry ID."""
        return str(uuid.uuid4())

    def query_by_intent(
        self,
        intent_id: str,
        tuple_type: (
            Literal["DCTX", "CONTRACT", "EVIDENCE", "ATTEST", "DCT", "SYSTEM"] | None
        ) = None,
        since: str | None = None,
    ) -> Iterator[GovernanceEntry]:
        """Query entries by intent_id.

        Args:
            intent_id: Intent to query.
            tuple_type: Optional filter by tuple type.
            since: Optional ISO8601 timestamp filter.

        Yields:
            GovernanceEntry objects matching query.
        """
        if not _is_idp_enabled():
            return

        yield from self._query(
            lambda e: e.intent_id == intent_id,
            tuple_type=tuple_type,
            since=since,
        )

    def query_by_task(
        self,
        task_id: str,
        tuple_type: (
            Literal["DCTX", "CONTRACT", "EVIDENCE", "ATTEST", "DCT", "SYSTEM"] | None
        ) = None,
    ) -> Iterator[GovernanceEntry]:
        """Query entries by task_id.

        Args:
            task_id: Task to query.
            tuple_type: Optional filter by tuple type.

        Yields:
            GovernanceEntry objects matching query.
        """
        if not _is_idp_enabled():
            return

        yield from self._query(
            lambda e: e.task_id == task_id,
            tuple_type=tuple_type,
        )

    def _query(
        self,
        predicate: callable,
        tuple_type: (
            Literal["DCTX", "CONTRACT", "EVIDENCE", "ATTEST", "DCT", "SYSTEM"] | None
        ) = None,
        since: str | None = None,
    ) -> Iterator[GovernanceEntry]:
        """Internal query implementation."""
        files = sorted(self._base_dir.glob("governance-*.jsonl*"), reverse=True)

        for filepath in files:
            if filepath.suffix == ".gz":
                opener = partial(gzip.open, filepath, "rt", encoding="utf-8")
            else:
                opener = partial(open, filepath, "r", encoding="utf-8")

            try:
                with opener() as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            entry = GovernanceEntry.from_dict(data)

                            if not predicate(entry):
                                continue
                            if tuple_type and entry.tuple_type != tuple_type:
                                continue
                            if since and entry.timestamp < since:
                                continue

                            yield entry
                        except (json.JSONDecodeError, KeyError, TypeError):
                            continue
            except (IOError, OSError):
                continue

    def enforce_retention(self) -> int:
        """Enforce retention policy by deleting old logs.

        Returns:
            Number of files deleted.
        """
        if not _is_idp_enabled():
            return 0

        cutoff = datetime.now(timezone.utc) - timedelta(days=self._retention_days)
        deleted = 0

        for filepath in self._base_dir.glob("governance-*.jsonl*"):
            try:
                date_str = filepath.stem.split("-")[1:4]
                file_date = datetime(
                    int(date_str[0]),
                    int(date_str[1]),
                    int(date_str[2]),
                    tzinfo=timezone.utc,
                )
                if file_date < cutoff:
                    filepath.unlink()
                    deleted += 1
            except (ValueError, IndexError):
                continue

        return deleted

    def close(self) -> None:
        """Close file handles and flush buffers."""
        if self._enable_async:
            self._flush_buffer()

        with self._lock:
            if self._file_handle and not self._file_handle.closed:
                self._file_handle.close()
                self._file_handle = None

    def __enter__(self) -> GovernanceBus:
        """Context manager entry."""
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit."""
        self.close()
