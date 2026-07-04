#!/usr/bin/env python3
"""Quality signal monitor for local repo and claim governance scripts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class QualitySnapshot:
    timestamp: str
    total_py_files: int
    total_md_files: int
    test_files: int
    todo_count: int
    fixme_count: int
    risk_score: int
    raw_metrics: dict[str, object]


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def count_patterns(path: Path) -> tuple[int, int]:
    text = read_file(path).lower()
    todos = len(re.findall(r"\btodo\b", text))
    fixmes = len(re.findall(r"\bfixme\b", text))
    return todos, fixmes


def collect_metrics(root: Path) -> dict[str, int]:
    py_files = list(root.rglob("*.py"))
    md_files = list(root.glob("**/*.md"))
    test_files = [path for path in py_files if "tests" in str(path)]
    total_todos = 0
    total_fixmes = 0
    for file in py_files + md_files:
        if ".venv" in str(file) or ".git" in str(file):
            continue
        try:
            todos, fixmes = count_patterns(file)
            total_todos += todos
            total_fixmes += fixmes
        except OSError:
            continue
    return {
        "py_files": len(py_files),
        "md_files": len(md_files),
        "test_files": len(test_files),
        "todo": total_todos,
        "fixme": total_fixmes,
    }


def score_quality(metrics: dict[str, int]) -> int:
    score = 100
    score -= metrics["todo"] * 3
    score -= metrics["fixme"] * 5
    if metrics["py_files"] == 0:
        score -= 30
    if metrics["test_files"] == 0:
        score -= 20
    return max(score, 0)


def build_snapshot(root: Path) -> QualitySnapshot:
    metrics = collect_metrics(root)
    score = score_quality(metrics)
    return QualitySnapshot(
        timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
        total_py_files=metrics["py_files"],
        total_md_files=metrics["md_files"],
        test_files=metrics["test_files"],
        todo_count=metrics["todo"],
        fixme_count=metrics["fixme"],
        risk_score=score,
        raw_metrics={"raw": metrics},
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor quality and technical debt signals")
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo).resolve()
    if not root.exists():
        raise SystemExit(f"repo path not found: {root}")
    snapshot = build_snapshot(root)
    if args.json:
        print(json.dumps(snapshot.__dict__, indent=2))
    else:
        print(f"timestamp={snapshot.timestamp}")
        print(f"py_files={snapshot.total_py_files}")
        print(f"md_files={snapshot.total_md_files}")
        print(f"tests={snapshot.test_files}")
        print(f"todo={snapshot.todo_count}")
        print(f"fixme={snapshot.fixme_count}")
        print(f"risk_score={snapshot.risk_score}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
