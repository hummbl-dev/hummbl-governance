"""Tests for the coverage matrix ratchet gate (scripts/coverage_ratchet.py).

Verifies:
1. Ratchet passes when current >= baseline
2. Ratchet fails when current < baseline (regression detected)
3. Ratchet suggests raising baseline when current > baseline
4. --init-baseline creates a valid baseline file
5. Missing baseline file exits with code 2
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "coverage_ratchet.py"


def _run_ratchet(baseline: str, report: str, *extra: str) -> tuple[int, str]:
    """Run the ratchet script and return (exit_code, stdout)."""
    cmd = [sys.executable, str(SCRIPT), "--baseline", baseline, "--report", report, *extra]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def _make_report(path: Path, validated: int, fulfilled: int, failed: int) -> None:
    """Create a minimal evidence validation report JSON."""
    data = {
        "test-matrix.md": {
            "totals": {"fulfilled": fulfilled},
            "fulfilled_validation": {
                "rows_passed": validated,
                "rows_failed": failed,
                "rows_without_refs": failed,
            },
        }
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def _make_baseline(path: Path, validated: int, fulfilled: int, pct: float) -> None:
    """Create a ratchet baseline file."""
    data = {
        "validated_count": validated,
        "fulfilled_count": fulfilled,
        "validated_pct": pct,
        "description": "Test baseline",
    }
    path.write_text(json.dumps(data), encoding="utf-8")


class TestCoverageRatchetPass:
    def test_ratchet_passes_when_current_matches_baseline(self, tmp_path):
        report = tmp_path / "report.json"
        baseline = tmp_path / "baseline.json"
        _make_report(report, validated=5, fulfilled=100, failed=95)
        _make_baseline(baseline, validated=5, fulfilled=100, pct=5.0)
        rc, output = _run_ratchet(str(baseline), str(report))
        assert rc == 0
        assert "RATCHET PASSED" in output

    def test_ratchet_passes_when_current_exceeds_baseline(self, tmp_path):
        report = tmp_path / "report.json"
        baseline = tmp_path / "baseline.json"
        _make_report(report, validated=10, fulfilled=100, failed=90)
        _make_baseline(baseline, validated=5, fulfilled=100, pct=5.0)
        rc, output = _run_ratchet(str(baseline), str(report))
        assert rc == 0
        assert "RATCHET PASSED with improvement" in output
        assert "+5" in output


class TestCoverageRatchetFail:
    def test_ratchet_fails_on_regression(self, tmp_path):
        report = tmp_path / "report.json"
        baseline = tmp_path / "baseline.json"
        _make_report(report, validated=3, fulfilled=100, failed=97)
        _make_baseline(baseline, validated=5, fulfilled=100, pct=5.0)
        rc, output = _run_ratchet(str(baseline), str(report))
        assert rc == 1
        assert "RATCHET FAILED" in output
        assert "regressed" in output
        assert "3" in output and "5" in output


class TestCoverageRatchetInitBaseline:
    def test_init_baseline_creates_file(self, tmp_path):
        report = tmp_path / "report.json"
        baseline = tmp_path / "baseline.json"
        _make_report(report, validated=7, fulfilled=50, failed=43)
        rc, output = _run_ratchet(str(baseline), str(report), "--init-baseline")
        assert rc == 0
        assert "BASELINE SET" in output
        assert baseline.exists()
        data = json.loads(baseline.read_text())
        assert data["validated_count"] == 7
        assert data["fulfilled_count"] == 50


class TestCoverageRatchetMissingBaseline:
    def test_missing_baseline_exits_2(self, tmp_path):
        report = tmp_path / "report.json"
        baseline = tmp_path / "nonexistent.json"
        _make_report(report, validated=5, fulfilled=100, failed=95)
        rc, output = _run_ratchet(str(baseline), str(report))
        assert rc == 2
        assert "Baseline file not found" in output


class TestCoverageRatchetPromotionThreshold:
    def test_promotion_notice_when_threshold_reached(self, tmp_path):
        report = tmp_path / "report.json"
        baseline = tmp_path / "baseline.json"
        _make_report(report, validated=60, fulfilled=100, failed=40)
        _make_baseline(baseline, validated=5, fulfilled=100, pct=5.0)
        rc, output = _run_ratchet(str(baseline), str(report), "--promote-threshold", "50.0")
        assert rc == 0
        assert "PROMOTION THRESHOLD REACHED" in output
        assert "60.0%" in output

    def test_no_promotion_notice_below_threshold(self, tmp_path):
        report = tmp_path / "report.json"
        baseline = tmp_path / "baseline.json"
        _make_report(report, validated=5, fulfilled=100, failed=95)
        _make_baseline(baseline, validated=5, fulfilled=100, pct=5.0)
        rc, output = _run_ratchet(str(baseline), str(report), "--promote-threshold", "50.0")
        assert rc == 0
        assert "PROMOTION THRESHOLD" not in output
        assert "gap:" in output
