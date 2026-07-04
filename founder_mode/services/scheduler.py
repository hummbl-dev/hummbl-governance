#!/usr/bin/env python3
"""Simple scheduling utilities used by local agent automation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScheduledTask:
    name: str
    cadence_minutes: int
    next_run_utc: str


def next_run(last: dt.datetime, cadence_minutes: int) -> str:
    return (last + dt.timedelta(minutes=cadence_minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_default_plan(now: dt.datetime | None = None) -> list[ScheduledTask]:
    now = now or dt.datetime.now(dt.timezone.utc).replace(tzinfo=dt.timezone.utc)
    return [
        ScheduledTask("toolset_inventory", 60 * 24, next_run(now, 60 * 24)),
        ScheduledTask("health_check", 30, next_run(now, 30)),
        ScheduledTask("quality_scan", 120, next_run(now, 120)),
        ScheduledTask("dependency_audit", 60 * 6, next_run(now, 60 * 6)),
    ]


def parse_state(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def persist_plan(plan: list[ScheduledTask], path: Path) -> None:
    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "tasks": [task.__dict__ for task in plan],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def render_plan(plan: list[ScheduledTask]) -> str:
    lines = ["# Agent scheduler plan"]
    lines.append("")
    for item in plan:
        lines.append(f"- {item.name}: {item.next_run_utc} every {item.cadence_minutes}m")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute minimal task schedule")
    parser.add_argument("--state", default="founder_mode/_state/scheduler.json", help="State output path")
    parser.add_argument("--tick", type=int, default=30, help="Default cadence in minutes for added tasks")
    parser.add_argument("--task-name", default="", help="Append a one-off task name to schedule file")
    parser.add_argument("--as-json", action="store_true", help="Output JSON only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state_path = Path(args.state)
    previous = parse_state(state_path)
    plan = build_default_plan()
    if args.task_name:
        plan.append(
            ScheduledTask(
                args.task_name,
                max(1, args.tick),
                next_run(dt.datetime.now(dt.timezone.utc), args.tick),
            )
        )
    persist_plan(plan, state_path)

    if args.as_json:
        print(json.dumps({
            "state": str(state_path),
            "previous": previous,
            "plan": [task.__dict__ for task in plan],
        }, indent=2))
    else:
        print(render_plan(plan))
        if previous:
            print(f"\nPrevious state keys: {list(previous.keys())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
