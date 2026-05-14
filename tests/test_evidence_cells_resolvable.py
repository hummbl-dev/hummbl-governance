"""Test that coverage matrix evidence cells are resolvable or explicitly marked draft.

Implements hummbl-governance#29 enforcement: every backtick-quoted code reference
in matrix Evidence columns must either resolve against the real CLI / file system
or carry an explicit [DRAFT ...] marker.

Stdlib + pytest only.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate_evidence_cells.py"
COVERAGE_DIR = REPO_ROOT / "docs" / "coverage"


def _run_validator_strict() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--matrix-dir", str(COVERAGE_DIR), "--strict"],
        capture_output=True,
        text=True,
        check=False,
    )


def test_validator_script_runs():
    """The validator runs against current matrices."""
    result = _run_validator_strict()
    assert result.returncode in (0, 1), f"Validator crashed: {result.stderr}"


def test_no_unresolvable_evidence_cells_in_strict_mode():
    """Every compliance_mapper invocation either uses real CLI flags or is [DRAFT]-marked.

    The strict-mode exit code is 1 if any unresolvable cells remain. This test
    asserts exit-0, meaning the relabel pass has fully covered the matrix corpus.
    """
    result = _run_validator_strict()
    assert result.returncode == 0, (
        f"Validator found unresolvable evidence cells (exit={result.returncode}).\n"
        f"Output:\n{result.stdout}\n"
        f"Fix: either implement the missing CLI flag in compliance_mapper.py, "
        f"or run scripts/relabel_unresolvable_evidence.py to apply [DRAFT] prefix."
    )


def test_relabel_script_is_idempotent():
    """Re-running the relabel script does not double-prefix already-drafted cells."""
    relabel_script = REPO_ROOT / "scripts" / "relabel_unresolvable_evidence.py"
    # Dry-run a second time; should report all skipped (already drafted)
    result = subprocess.run(
        [sys.executable, str(relabel_script), "--matrix-dir", str(COVERAGE_DIR), "--dry-run"],
        capture_output=True,
        text=True,
        check=True,
    )
    # If anything in TOTAL relabeled is non-zero on a fresh dry-run, the previous
    # pass didn't fully take effect.
    assert "TOTAL relabeled: 0" in result.stdout, (
        f"Relabel script is not idempotent — second pass would change files.\n"
        f"Output:\n{result.stdout}"
    )
