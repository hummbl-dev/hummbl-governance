"""Coverage matrix row-total verifier.

Reads docs/coverage/*.md and reconciles declared summary totals against actual
row marker counts (✅, 🟡, ⚪, ⛔). Implements hummbl-governance#30 per ADR-001
evidence invariant: stated counts must match what the row data supports.

Stdlib-only (re, pathlib, sys, argparse, dataclasses). No third-party deps.

Exit codes:
  0  — all matrices reconcile
  1  — at least one matrix has a count mismatch
  2  — script-level error (file unreadable, etc.)
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# Coverage state glyphs per ADR-001 §Coverage state legend.
STATES: tuple[str, ...] = ("✅", "🟡", "⚪", "⛔")

# Regex captures any pipe-table data row whose cells are non-header.
# A header row is identified by the immediately-following separator row (|---|---|...).
ROW_RE = re.compile(r"^\s*\|[^|\n]+(?:\|[^|\n]*)+\|\s*$")
SEPARATOR_RE = re.compile(r"^\s*\|(?:\s*:?-{3,}:?\s*\|)+\s*$")


@dataclass
class MatrixReport:
    path: Path
    declared: dict[str, int] = field(default_factory=dict)
    counted: dict[str, int] = field(default_factory=dict)
    total_declared: int | None = None
    mismatches: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.mismatches


def _strip_header_rows(lines: list[str]) -> list[str]:
    """Drop any pipe-table row immediately followed by a separator row.

    The remaining rows are eligible for marker counting. We also drop separator
    rows themselves.
    """
    out: list[str] = []
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        if SEPARATOR_RE.match(line):
            i += 1
            continue
        # If this is a row and the next line is a separator, it's a header.
        if (
            ROW_RE.match(line)
            and i + 1 < n
            and SEPARATOR_RE.match(lines[i + 1])
        ):
            i += 1  # skip header
            continue
        out.append(line)
        i += 1
    return out


def _find_totals_section(lines: list[str]) -> tuple[int, int] | None:
    """Find the ## Summary section's totals row range.

    Heuristic: locate the first row whose first cell is a bolded "Totals" marker
    or contains the word "Totals" in bold. Return its line index.
    """
    for i, line in enumerate(lines):
        # Match lines like:  | **Totals** | ... | **23** | **19** | **71** |
        # Or:                | **TOTALS** | ... | 215 | 167 | 259 |
        if re.search(r"\|\s*\*\*\s*total(s)?\s*\*\*", line, re.IGNORECASE):
            return i, i
    return None


def _parse_totals_row(line: str) -> dict[str, int] | None:
    """Extract numeric counts from a totals row.

    Expected shape:  | **Totals** | optional-extra | ✅count | 🟡count | ⚪count | ⛔count? |
    We collect all integers in cells, then map them positionally per the matrix
    convention: ✅, 🟡, ⚪, (optionally ⛔). The number-cell order in totals rows
    across the 12 matrices follows ADR-001 column order.
    """
    cells = [c.strip().strip("*").strip() for c in line.strip().strip("|").split("|")]
    nums: list[int] = []
    for cell in cells:
        # Strip bold markup, parse pure-integer cells only.
        cleaned = re.sub(r"[*~`]", "", cell).strip()
        if cleaned.isdigit():
            nums.append(int(cleaned))
        elif re.match(r"^\s*\d+\s*$", cleaned):
            nums.append(int(cleaned))
    return {
        "declared_int_sequence": nums,
    } if nums else None


def _count_state_glyphs(text: str) -> Counter[str]:
    """Count occurrences of state glyphs ONLY in matrix rows.

    Excludes: the legend table (header in front-matter), boundary-disclaimer
    text, summary sentences. Strategy: only count glyphs appearing inside lines
    that match ROW_RE.
    """
    rows = [ln for ln in text.splitlines() if ROW_RE.match(ln)]
    # Drop header rows (rows immediately followed by separator)
    rows = _strip_header_rows(rows)
    # Drop legend table rows — they contain glyph in column 1 along with text
    # description in column 2 like "Fulfilled" or "Partial". Heuristic: the
    # legend rows mention "Fulfilled" / "Partial" / "Boundary" / "Out of scope"
    # in a non-data position. We exclude any row that includes "Fulfilled" or
    # "Out of scope" as a clean cell (these are the labels in the legend).
    LEGEND_LABELS = (
        "Fulfilled",
        "Partial",
        "Boundary",
        "Out of scope",
    )
    cleaned_rows = []
    for r in rows:
        # Split into cells, check if any cell is exactly a legend label
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        is_legend = any(c == lbl for c in cells for lbl in LEGEND_LABELS)
        if not is_legend:
            cleaned_rows.append(r)
    # Now count glyphs in remaining rows
    counter: Counter[str] = Counter()
    for r in cleaned_rows:
        for state in STATES:
            counter[state] += r.count(state)
    return counter


def _extract_declared_summary(text: str) -> dict[str, int] | None:
    """Try to extract declared per-state totals from the matrix summary table.

    Returns a dict like {"✅": 23, "🟡": 19, "⚪": 71, "⛔": 0, "total": 113} or
    None if no clear summary table found.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        # Look for totals row patterns. They typically have ≥4 integer cells
        # following the "Totals" label.
        if re.search(r"\*\*\s*total(s)?\s*\*\*", line, re.IGNORECASE):
            cells = [
                re.sub(r"[*~`\[\]]", "", c).strip()
                for c in line.strip().strip("|").split("|")
            ]
            # Find first numeric cell (the surface count) and following per-state ints
            ints: list[int] = []
            for c in cells:
                m = re.match(r"^\s*(\d+)\s*$", c)
                if m:
                    ints.append(int(m.group(1)))
            if len(ints) >= 4:
                # Convention across matrices: [total, ✅, 🟡, ⚪] or
                # [total, ✅, 🟡, ⚪, ⛔]. Some matrices use [✅, 🟡, ⚪] only.
                # We assume the totals row has total-then-states.
                return {
                    "total": ints[0],
                    "✅": ints[1] if len(ints) >= 2 else 0,
                    "🟡": ints[2] if len(ints) >= 3 else 0,
                    "⚪": ints[3] if len(ints) >= 4 else 0,
                    "⛔": ints[4] if len(ints) >= 5 else 0,
                }
            elif len(ints) == 3:
                # Three-int totals row, no total surface count first
                return {
                    "total": ints[0] + ints[1] + ints[2],
                    "✅": ints[0],
                    "🟡": ints[1],
                    "⚪": ints[2],
                    "⛔": 0,
                }
    return None


def verify_matrix(path: Path) -> MatrixReport:
    """Compare declared summary totals to actual row marker counts."""
    report = MatrixReport(path=path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        report.mismatches.append(f"read error: {e}")
        return report

    counted = _count_state_glyphs(text)
    report.counted = dict(counted)

    declared = _extract_declared_summary(text)
    if declared is None:
        report.mismatches.append("no totals table found")
        return report
    report.declared = declared
    report.total_declared = declared.get("total")

    for state in STATES:
        d = declared.get(state, 0)
        c = counted.get(state, 0)
        if d != c:
            report.mismatches.append(
                f"{state}: declared={d}, counted={c}, delta={c - d:+d}"
            )

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify coverage-matrix declared totals match counted row markers."
    )
    parser.add_argument(
        "--matrix-dir",
        type=Path,
        default=Path("docs/coverage"),
        help="Directory containing matrix .md files (default: docs/coverage)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print summary; suppress per-state detail",
    )
    args = parser.parse_args(argv)

    if not args.matrix_dir.is_dir():
        print(f"ERROR: {args.matrix_dir} is not a directory", file=sys.stderr)
        return 2

    files = sorted(
        p
        for p in args.matrix_dir.glob("*.md")
        if p.name not in ("README.md",)
    )
    if not files:
        print(f"ERROR: no matrix files found in {args.matrix_dir}", file=sys.stderr)
        return 2

    all_ok = True
    total_decl = Counter()
    total_count = Counter()

    for path in files:
        report = verify_matrix(path)
        for s, n in report.declared.items():
            if s in STATES:
                total_decl[s] += n
        for s, n in report.counted.items():
            total_count[s] += n
        status = "OK" if report.ok else "MISMATCH"
        print(f"[{status}] {path.name}")
        if not report.ok:
            all_ok = False
            for m in report.mismatches:
                print(f"  - {m}")
        elif not args.quiet:
            d = report.declared
            print(
                f"  ✅={d.get('✅', 0)} 🟡={d.get('🟡', 0)} "
                f"⚪={d.get('⚪', 0)} ⛔={d.get('⛔', 0)}"
            )

    print()
    print("=== Fleet totals (across all matrices) ===")
    for state in STATES:
        d = total_decl[state]
        c = total_count[state]
        mark = "✓" if d == c else "✗"
        print(f"  {state}  declared={d}  counted={c}  {mark}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
