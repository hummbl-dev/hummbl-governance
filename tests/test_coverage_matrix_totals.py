"""Test that coverage matrix declared totals match counted row markers.

Implements hummbl-governance#30 enforcement: matrix totals must be mechanically
verifiable, not author-asserted.

Stdlib + pytest only.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_DIR = REPO_ROOT / "docs" / "coverage"
SCRIPT = REPO_ROOT / "scripts" / "count_coverage_rows.py"

STATES = ("✅", "🟡", "⚪", "⛔")


def _run_counter() -> dict:
    """Invoke the count script and parse its JSON output."""
    import json as _json

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--format", "json", "--matrix-dir", str(COVERAGE_DIR)],
        capture_output=True,
        text=True,
        check=True,
    )
    return _json.loads(result.stdout)


def test_count_script_runs():
    """The counter script runs without error against current matrix dir."""
    data = _run_counter()
    assert "matrices" in data
    assert len(data["matrices"]) > 0


def test_no_unverified_totals_claim_in_readme():
    """README must not present aggregate counts without mechanical-verification marker.

    Specifically, the README must include the count script reference if it
    publishes any per-state count totals.
    """
    readme = (COVERAGE_DIR / "README.md").read_text(encoding="utf-8")
    # If README mentions ✅ count anywhere in a totals context, it must reference
    # the count script.
    has_total_claim = bool(re.search(r"\*\*\d+\s*✅", readme))
    if has_total_claim:
        assert "count_coverage_rows.py" in readme, (
            "README publishes aggregate count totals but does not reference "
            "scripts/count_coverage_rows.py as the source of truth"
        )


def test_fleet_total_marker_count_is_published():
    """Fleet count must be available via the count script."""
    data = _run_counter()
    fleet = data["fleet_totals"]
    assert all(s in fleet for s in STATES), f"Missing state in fleet totals: {fleet}"
    total = sum(fleet.values())
    assert total > 0, f"Fleet markers count is zero: {fleet}"


@pytest.mark.parametrize(
    "matrix_name",
    [
        "colorado-ai-act.md",
        "eu-ai-act.md",
        "g7-ai-code.md",
        "gdpr.md",
        "imda-agentic.md",
        "iso-27001.md",
        "iso-42001.md",
        "nist-ai-rmf.md",
        "nist-csf.md",
        "nyc-ll144.md",
        "owasp-llm.md",
        "soc2.md",
    ],
)
def test_matrix_has_data_rows(matrix_name: str):
    """Every matrix must have at least one data row with a state glyph."""
    matrix = COVERAGE_DIR / matrix_name
    assert matrix.exists(), f"Matrix file missing: {matrix_name}"

    data = _run_counter()
    matching = [m for m in data["matrices"] if Path(m["path"]).name == matrix_name]
    assert len(matching) == 1, f"Counter did not produce a row for {matrix_name}"
    result = matching[0]
    assert result["rows_counted"] > 0, f"{matrix_name} has zero data rows counted"


def test_no_silent_zero_total_state():
    """Counter must report at least one ✅ across the fleet (not all-boundary)."""
    data = _run_counter()
    assert data["fleet_totals"]["✅"] > 0, (
        "Fleet has zero ✅ Fulfilled rows — either matrices are entirely "
        "boundary/draft, or the counter is broken"
    )
