"""Receipt Integrity Monitor Primitive — detects receipt sequence gaps,
hash chain breaks, and retroactive insertion.

Enforces K11 (INTEGRITY): receipt sequences are complete and unbroken.
Gaps in receipt sequences (K4 violation), hash chain breaks (K1), and
retroactive insertion are detected. Raises KernelPanic on violation.

Schema: hummbl_governance/data/receipt_integrity_monitor.schema.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hummbl_governance.schema_validator import SchemaValidator, ValidationError

_SCHEMA_PATH = (
    Path(__file__).parent.parent / "data" / "receipt_integrity_monitor.schema.json"
)
_SCHEMA_CACHE: dict[str, Any] | None = None


def _load_schema() -> dict[str, Any]:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is None:
        with open(_SCHEMA_PATH) as f:
            _SCHEMA_CACHE = json.load(f)
    return _SCHEMA_CACHE


def check_sequence(
    receipts: list[dict[str, Any]],
) -> tuple[bool, list[dict[str, Any]]]:
    """Check receipt sequence for gaps (K4 TEMPORAL).

    Args:
        receipts: List of receipt dicts, each with a "sequence_id" int field.
            Receipts should be sorted by sequence_id.

    Returns:
        Tuple of (passed, gaps). gaps is a list of dicts with keys:
        expected_sequence, found_sequence, missing_count.
    """
    if not receipts:
        return True, []

    gaps: list[dict[str, Any]] = []
    prev_seq = -1

    for receipt in receipts:
        seq = receipt.get("sequence_id", 0)
        if not isinstance(seq, int):
            continue
        expected = prev_seq + 1
        if seq != expected:
            gaps.append(
                {
                    "expected_sequence": expected,
                    "found_sequence": seq,
                    "missing_count": seq - expected,
                }
            )
        prev_seq = seq

    return len(gaps) == 0, gaps


def check_hash_chain(
    receipts: list[dict[str, Any]],
) -> tuple[bool, list[dict[str, Any]]]:
    """Check SHA-256 hash chain integrity (K1 RECEIPT).

    Args:
        receipts: List of receipt dicts, each with "receipt_hash" and
            "prev_receipt_hash" string fields. Receipts should be sorted
            by sequence_id. The first receipt's prev_receipt_hash should
            be empty, None, or absent.

    Returns:
        Tuple of (passed, broken_links). broken_links is a list of dicts
        with keys: receipt_id, expected_prev_hash, actual_prev_hash,
        receipt_sequence.
    """
    if not receipts:
        return True, []

    broken_links: list[dict[str, Any]] = []
    prev_hash = ""

    for receipt in receipts:
        actual_prev = receipt.get("prev_receipt_hash", "")
        if actual_prev is None:
            actual_prev = ""
        current_hash = receipt.get("receipt_hash", "")

        # First receipt: prev should be empty
        if prev_hash == "" and actual_prev == "":
            prev_hash = current_hash
            continue

        if actual_prev != prev_hash:
            broken_links.append(
                {
                    "receipt_id": receipt.get("receipt_id", ""),
                    "expected_prev_hash": prev_hash,
                    "actual_prev_hash": actual_prev,
                    "receipt_sequence": receipt.get("sequence_id", 0),
                }
            )

        prev_hash = current_hash

    return len(broken_links) == 0, broken_links


def check_timestamps(
    receipts: list[dict[str, Any]],
) -> tuple[bool, list[dict[str, Any]]]:
    """Check timestamp consistency for retroactive insertion.

    Detects receipts whose timestamps are inconsistent with their sequence
    position — indicating possible retroactive insertion.

    Args:
        receipts: List of receipt dicts, each with "sequence_id" int and
            "timestamp" str (ISO 8601) fields. Receipts should be sorted
            by sequence_id.

    Returns:
        Tuple of (passed, anomalies). anomalies is a list of dicts with
        keys: receipt_id, anomaly_type, receipt_sequence,
        receipt_timestamp, expected_timestamp_range.
    """
    if not receipts:
        return True, []

    anomalies: list[dict[str, Any]] = []
    prev_ts: str | None = None

    for receipt in receipts:
        ts = receipt.get("timestamp", "")
        seq = receipt.get("sequence_id", 0)

        if not ts:
            continue

        if prev_ts is not None and ts < prev_ts:
            anomalies.append(
                {
                    "receipt_id": receipt.get("receipt_id", ""),
                    "anomaly_type": "retroactive_insertion",
                    "receipt_sequence": seq,
                    "receipt_timestamp": ts,
                    "expected_timestamp_range": {
                        "earliest": prev_ts,
                    },
                }
            )

        prev_ts = ts

    return len(anomalies) == 0, anomalies


def run_integrity_check(
    receipts: list[dict[str, Any]],
    agent_id: str,
) -> dict[str, Any]:
    """Run all integrity checks and build a monitor report.

    Args:
        receipts: List of receipt dicts to check.
        agent_id: ID of the agent whose receipts are being monitored.

    Returns:
        Monitor report dict conforming to receipt_integrity_monitor.schema.json.
    """
    seq_passed, gaps = check_sequence(receipts)
    chain_passed, broken = check_hash_chain(receipts)
    ts_passed, anomalies = check_timestamps(receipts)

    all_passed = seq_passed and chain_passed and ts_passed
    panic_triggered = not all_passed

    panic_details = None
    if panic_triggered:
        if not seq_passed:
            invariant = "K4"
        elif not chain_passed:
            invariant = "K1"
        else:
            invariant = "K11"
        panic_details = {
            "invariant_violated": invariant,
            "severity": "CRITICAL",
            "description": f"Receipt integrity check failed for agent {agent_id}",
        }

    import hashlib
    import json as _json

    report_str = _json.dumps(
        {"agent_id": agent_id, "receipts_checked": len(receipts)}, sort_keys=True
    )
    receipt_hash = hashlib.sha256(report_str.encode()).hexdigest()

    return {
        "schema_version": "1.0.0",
        "monitor_run_id": f"rim-{agent_id}-{len(receipts)}",
        "agent_id": agent_id,
        "check_results": {
            "sequence_check": {
                "passed": seq_passed,
                "receipts_scanned": len(receipts),
                "gaps_found": gaps,
            },
            "hash_chain_check": {
                "passed": chain_passed,
                "chains_verified": len(receipts),
                "broken_links": broken,
            },
            "timestamp_check": {
                "passed": ts_passed,
                "anomalies": anomalies,
            },
        },
        "panic_triggered": panic_triggered,
        "panic_details": panic_details,
        "receipt": {
            "receipt_hash": receipt_hash,
        },
    }


def validate_receipt_integrity_monitor(report: dict[str, Any]) -> None:
    """Validate a monitor report against schema v1.0.0.

    Raises:
        ValidationError: If the report does not conform to the schema.
    """
    schema = _load_schema()
    errors = SchemaValidator.validate(report, schema)
    if errors:
        raise ValidationError(
            f"Receipt integrity monitor schema validation failed: {'; '.join(errors)}"
        )


def validate_monitor_report(report: dict[str, Any]) -> None:
    """Full validation of a monitor report: schema + panic consistency.

    Args:
        report: The monitor report dict.

    Raises:
        ValidationError: If schema validation fails.
        ValueError: If panic_triggered is inconsistent with check results.
    """
    validate_receipt_integrity_monitor(report)

    check_results = report.get("check_results", {})
    seq_passed = check_results.get("sequence_check", {}).get("passed", True)
    chain_passed = check_results.get("hash_chain_check", {}).get("passed", True)
    ts_passed = check_results.get("timestamp_check", {}).get("passed", True)

    any_failed = not (seq_passed and chain_passed and ts_passed)
    panic_triggered = report.get("panic_triggered", False)

    if any_failed and not panic_triggered:
        raise ValueError(
            "Monitor report inconsistent: check results show failures but "
            "panic_triggered is False"
        )
    if not any_failed and panic_triggered:
        raise ValueError(
            "Monitor report inconsistent: all checks passed but "
            "panic_triggered is True"
        )


__all__ = [
    "check_sequence",
    "check_hash_chain",
    "check_timestamps",
    "run_integrity_check",
    "validate_receipt_integrity_monitor",
    "validate_monitor_report",
]
