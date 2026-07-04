#!/usr/bin/env python3
"""Quality analysis pass that maps monitor signals to policy recommendations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import importlib.util

try:
    from . import monitor
except Exception:  # pragma: no cover - direct script execution
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    monitor_path = Path(__file__).resolve().parents[2] / "founder_mode" / "quality" / "monitor.py"
    monitor_spec = importlib.util.spec_from_file_location("founder_mode.quality.monitor", monitor_path)
    if monitor_spec is None or monitor_spec.loader is None:
        raise
    monitor = importlib.util.module_from_spec(monitor_spec)
    sys.modules["founder_mode.quality.monitor"] = monitor
    monitor_spec.loader.exec_module(monitor)


def classify_risk(score: int) -> str:
    if score >= 90:
        return "healthy"
    if score >= 70:
        return "controlled"
    if score >= 50:
        return "unstable"
    return "critical"


def recommendations(snapshot: monitor.QualitySnapshot) -> list[str]:
    recs: list[str] = []
    if snapshot.todo_count > 30:
        recs.append("Reduce inline TODO count before hardening gate.")
    if snapshot.fixme_count > 10:
        recs.append("Resolve FIXME markers in active service scripts.")
    if snapshot.test_files == 0:
        recs.append("Add baseline tests for changed modules.")
    if snapshot.total_py_files and snapshot.risk_score < 70:
        recs.append("Schedule focused cleanup before adding more automation.")
    if not recs:
        recs.append("No immediate quality blockers identified.")
    return recs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze quality telemetry for admission advice")
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = monitor.build_snapshot(Path(args.repo))
    report = {
        "risk_band": classify_risk(snapshot.risk_score),
        "risk_score": snapshot.risk_score,
        "admit": snapshot.risk_score >= 70,
        "recommendations": recommendations(snapshot),
        "snapshot": snapshot.__dict__,
    }
    print(json.dumps(report, indent=2) if args.json else _render_text(report))
    return 0


def _render_text(report: dict[str, object]) -> str:
    lines = [
        f"risk_band={report['risk_band']}",
        f"risk_score={report['risk_score']}",
        f"admit={report['admit']}",
    ]
    lines.extend(f"- {item}" for item in report["recommendations"])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
