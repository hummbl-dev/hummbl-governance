"""Coverage matrix ratchet gate — prevents regression in evidence validation.

Compares current evidence validation results against a frozen baseline.
Fails if the validated row count regresses below the baseline.
Passes if current >= baseline (improvement or no change).

The baseline file (docs/coverage/ratchet-baseline.json) is a committed artifact.
It can only be raised by an explicit baseline-update commit; CI never lowers it.

Ratchet policy:
  - current_validated < baseline_validated  → FAIL (regression detected)
  - current_validated >= baseline_validated → PASS
  - If current > baseline, print a suggestion to raise the baseline

Promotion threshold:
  When validated_pct >= PROMOTION_THRESHOLD (default 50%), the CI job
  should flip continue-on-error to false. This script prints a promotion
  notice when the threshold is reached but does not auto-promote.

Exit codes:
  0 — ratchet passes (current >= baseline)
  1 — ratchet fails (regression: current < baseline)
  2 — baseline file missing or invalid

Usage:
  python scripts/coverage_ratchet.py [--baseline docs/coverage/ratchet-baseline.json]
                                     [--report docs/coverage/EVIDENCE_VALIDATION.json]
                                     [--promote-threshold 50]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_baseline(path: Path) -> dict:
    """Load the ratchet baseline file."""
    if not path.exists():
        print(f"ERROR: Baseline file not found: {path}", file=sys.stderr)
        print("Create it with: python scripts/coverage_ratchet.py --init-baseline", file=sys.stderr)
        sys.exit(2)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "validated_count" not in data:
        print(f"ERROR: Baseline file missing 'validated_count' key: {path}", file=sys.stderr)
        sys.exit(2)
    return data


def _load_report(path: Path) -> dict:
    """Load the evidence validation JSON report."""
    if not path.exists():
        print(f"ERROR: Validation report not found: {path}", file=sys.stderr)
        print("Run: python scripts/build_evidence_validation_report.py", file=sys.stderr)
        sys.exit(2)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _compute_current(report: dict) -> dict:
    """Compute aggregate stats from the validation report."""
    total_ful = sum(d["totals"]["fulfilled"] for d in report.values())
    total_validated = sum(d["fulfilled_validation"]["rows_passed"] for d in report.values())
    total_failed = sum(d["fulfilled_validation"]["rows_failed"] for d in report.values())
    pct = round(100.0 * total_validated / total_ful, 1) if total_ful else 0.0
    return {
        "fulfilled_count": total_ful,
        "validated_count": total_validated,
        "failed_count": total_failed,
        "validated_pct": pct,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Coverage matrix ratchet gate")
    parser.add_argument(
        "--baseline", type=str, default="docs/coverage/ratchet-baseline.json",
        help="Path to ratchet baseline file",
    )
    parser.add_argument(
        "--report", type=str, default="docs/coverage/EVIDENCE_VALIDATION.json",
        help="Path to evidence validation JSON report",
    )
    parser.add_argument(
        "--promote-threshold", type=float, default=50.0,
        help="Validated %% at which the CI job should flip to blocking (default: 50)",
    )
    parser.add_argument(
        "--init-baseline", action="store_true",
        help="Initialize or raise the baseline to current validated count",
    )
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    report_path = Path(args.report)

    report = _load_report(report_path)
    current = _compute_current(report)

    if args.init_baseline:
        baseline = {
            "validated_count": current["validated_count"],
            "fulfilled_count": current["fulfilled_count"],
            "validated_pct": current["validated_pct"],
            "description": "Frozen baseline for coverage-matrix ratchet. CI fails if validated_count drops below this value. Raise by re-running --init-baseline after improving evidence coverage.",
        }
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with baseline_path.open("w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"BASELINE SET: {baseline_path}")
        print(f"  validated_count: {current['validated_count']}")
        print(f"  fulfilled_count: {current['fulfilled_count']}")
        print(f"  validated_pct: {current['validated_pct']}%")
        return 0

    baseline = _load_baseline(baseline_path)
    baseline_count = baseline["validated_count"]
    current_count = current["validated_count"]

    print(f"RATCHET CHECK")
    print(f"  baseline validated: {baseline_count}")
    print(f"  current validated:  {current_count}")
    print(f"  current fulfilled:  {current['fulfilled_count']}")
    print(f"  current pct:        {current['validated_pct']}%")

    if current_count < baseline_count:
        print(f"\n::error::RATCHET FAILED: validated count regressed from {baseline_count} to {current_count}")
        print(f"::error::Regression of {baseline_count - current_count} validated rows. Fix the broken evidence refs or restore the baseline.")
        return 1

    if current_count > baseline_count:
        delta = current_count - baseline_count
        print(f"\n::notice::RATCHET PASSED with improvement: +{delta} validated rows above baseline")
        print(f"::notice::To raise the baseline, run: python scripts/coverage_ratchet.py --init-baseline")
    else:
        print(f"\n::notice::RATCHET PASSED: validated count matches baseline ({current_count})")

    # Promotion threshold check
    if current["validated_pct"] >= args.promote_threshold:
        print(f"\n::warning::PROMOTION THRESHOLD REACHED: {current['validated_pct']}% >= {args.promote_threshold}%")
        print(f"::warning::Consider flipping continue-on-error to false in .github/workflows/ci.yml")
    else:
        gap = args.promote_threshold - current["validated_pct"]
        print(f"\n  promotion threshold: {args.promote_threshold}% (gap: {gap:.1f}pp)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
