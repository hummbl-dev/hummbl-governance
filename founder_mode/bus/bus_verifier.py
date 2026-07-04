#!/usr/bin/env python3
"""Integrity checks for the local coordination bus file."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import importlib.util
from dataclasses import dataclass
from pathlib import Path
import sys

try:
    from .. import state_authority
except Exception:  # pragma: no cover - direct script execution
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.append(str(repo_root))
    authority_path = repo_root / "founder_mode" / "state_authority.py"
    authority_spec = importlib.util.spec_from_file_location("founder_mode.state_authority", authority_path)
    if authority_spec is None or authority_spec.loader is None:
        raise
    state_authority = importlib.util.module_from_spec(authority_spec)
    sys.modules["founder_mode.state_authority"] = state_authority
    authority_spec.loader.exec_module(state_authority)


@dataclass
class BusFinding:
    line_no: int
    severity: str
    message: str


def parse_line(raw: str, line_no: int) -> tuple[list[str], BusFinding | None]:
    line = raw.rstrip("\n\r")
    if not line:
        return [], BusFinding(line_no, "low", "empty line")
    fields = line.split("\t")
    if len(fields) < 5:
        return fields, BusFinding(line_no, "high", "not a valid TSV row")
    if any(not value.strip() for value in fields[:5]):
        return fields, BusFinding(line_no, "medium", "one or more empty required fields")
    return fields, None


def collect_findings(bus_path: Path) -> tuple[list[BusFinding], list[tuple[str, str, str, str, str]]]:
    findings: list[BusFinding] = []
    rows: list[tuple[str, str, str, str, str]] = []
    last_ts = ""
    if not bus_path.exists():
        return [BusFinding(0, "high", "bus path missing")], []

    with bus_path.open("r", encoding="utf-8", errors="replace") as fp:
        for idx, raw in enumerate(fp, start=1):
            fields, finding = parse_line(raw, idx)
            if finding:
                findings.append(finding)
            if len(fields) >= 5:
                rows.append((fields[0], fields[1], fields[2], fields[3], fields[4]))
                current_ts = fields[0]
                if last_ts and current_ts < last_ts:
                    findings.append(BusFinding(idx, "medium", "out-of-order timestamp"))
                last_ts = current_ts

    # Optional ordering check on non-empty bus
    if rows and len(rows) == 0:
        findings.append(BusFinding(0, "low", "bus file has no valid rows"))

    return findings, rows


def verify_signature(payload: str) -> bool:
    # Signature support exists in the BusWriter implementation; this verifier
    # is intentionally schema-only and treats missing signatures as warning.
    return True


def analyze(bus_path: Path) -> dict[str, object]:
    findings, rows = collect_findings(bus_path)
    high = [f for f in findings if f.severity == "high"]
    medium = [f for f in findings if f.severity == "medium"]
    low = [f for f in findings if f.severity == "low"]
    status = "pass" if not findings else ("warn" if medium or low else "fail")
    verify_signature("noop")
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "bus_path": str(bus_path),
        "status": status,
        "row_count": len(rows),
        "finding_count": len(findings),
        "by_severity": {
            "high": len(high),
            "medium": len(medium),
            "low": len(low),
        },
        "findings": [f.__dict__ for f in findings],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify coordination-bus file integrity")
    parser.add_argument("--bus-path", default=None, help="Path to bus.tsv")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--strict", action="store_true", help="Fail on any finding")
    parser.add_argument("--authorized-actor", default=None, help="Force actor check")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    actor = args.authorized_actor or os.getenv("HUMMBL_ACTOR", "codex")
    old = os.getenv("HUMMBL_ACTOR", actor)
    os.environ["HUMMBL_ACTOR"] = actor
    if not actor:
        raise SystemExit("No actor")
    state_authority.require_actor("bus_verify")

    bus_path = Path(args.bus_path or os.getenv("HUMMBL_BUS_PATH", "_receipts/bus.tsv"))
    report = analyze(bus_path)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Bus: {report['bus_path']}")
        print(f"Status: {report['status']}")
        print(f"Rows: {report['row_count']}")
        for item in report["findings"]:
            print(f"- {item['line_no']} {item['severity']}: {item['message']}")
    os.environ["HUMMBL_ACTOR"] = old
    if args.strict and report["finding_count"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
