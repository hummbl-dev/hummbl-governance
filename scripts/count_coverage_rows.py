"""Authoritative row-marker counter for coverage matrices.

Counts ✅/🟡/⚪/⛔ glyphs in matrix data rows ONLY (excluding header rows,
separator rows, legend tables, and prose). Source of truth for matrix totals.

Stdlib-only. Output is JSON, one line per matrix.

Implements hummbl-governance#30 — generate or remove unverified totals.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STATES = ("✅", "🟡", "⚪", "⛔")

ROW_RE = re.compile(r"^\s*\|[^|\n]+(?:\|[^|\n]*)+\|\s*$")
SEPARATOR_RE = re.compile(r"^\s*\|(?:\s*:?-{3,}:?\s*\|)+\s*$")
LEGEND_LABELS = ("Fulfilled", "Partial", "Boundary", "Out of scope")


def count_rows(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    n = len(lines)

    counts = {s: 0 for s in STATES}
    data_row_count = 0

    i = 0
    while i < n:
        line = lines[i]
        if not ROW_RE.match(line):
            i += 1
            continue
        # Skip if next line is separator (this line is a header)
        if i + 1 < n and SEPARATOR_RE.match(lines[i + 1]):
            i += 2
            continue
        # Skip separator rows themselves (defensive; covered above too)
        if SEPARATOR_RE.match(line):
            i += 1
            continue
        # Skip legend table rows: any cell exactly matches a legend label
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if any(c == lbl for c in cells for lbl in LEGEND_LABELS):
            i += 1
            continue
        # Skip the vertical summary table rows (e.g., "| ✅ Fulfilled | 5 |").
        # Distinguishing feature: cell 1 has a state glyph + label like "Fulfilled".
        first_cell = cells[0] if cells else ""
        if any(
            (state in first_cell and lbl in first_cell)
            for state in STATES
            for lbl in LEGEND_LABELS
        ):
            i += 1
            continue
        # Skip the chapter/section breakdown rows in summary tables, which have
        # multiple integer cells but represent breakdown, not data. Heuristic:
        # if the line has a state glyph in a body cell (not in cell 0 alone),
        # it's a data row. Summary breakdown rows typically have integers in
        # cells 2+ but no inline state glyphs.
        has_glyph = any(state in line for state in STATES)
        if not has_glyph:
            i += 1
            continue
        # Count occurrences in this row
        data_row_count += 1
        for state in STATES:
            counts[state] += line.count(state)
        i += 1

    return {
        "path": str(path),
        "rows_counted": data_row_count,
        "counts": counts,
        "total_markers": sum(counts.values()),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--matrix-dir", type=Path, default=Path("docs/coverage"))
    p.add_argument("--format", choices=("json", "human"), default="human")
    args = p.parse_args(argv)

    files = sorted(
        f for f in args.matrix_dir.glob("*.md") if f.name != "README.md"
    )
    fleet = {s: 0 for s in STATES}
    fleet_rows = 0

    results = []
    for f in files:
        r = count_rows(f)
        results.append(r)
        for s in STATES:
            fleet[s] += r["counts"][s]
        fleet_rows += r["rows_counted"]

    if args.format == "json":
        print(json.dumps({"matrices": results, "fleet_totals": fleet, "fleet_rows": fleet_rows}, indent=2))
    else:
        for r in results:
            name = Path(r["path"]).name
            c = r["counts"]
            print(
                f"{name:30s} rows={r['rows_counted']:3d}  "
                f"✅={c['✅']:3d}  🟡={c['🟡']:3d}  ⚪={c['⚪']:3d}  ⛔={c['⛔']:3d}"
            )
        print()
        print(
            f"{'FLEET TOTALS':30s} rows={fleet_rows:3d}  "
            f"✅={fleet['✅']:3d}  🟡={fleet['🟡']:3d}  ⚪={fleet['⚪']:3d}  ⛔={fleet['⛔']:3d}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
