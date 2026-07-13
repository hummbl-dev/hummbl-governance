#!/usr/bin/env python3
"""Fleet keepalive watchdog used for agent and local infra liveness checks."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


DEFAULT_TARGETS = ("act_runner", "runner", "self-hosted", "anvil")


@dataclass
class ProbeSample:
    timestamp: str
    found: dict[str, bool]
    missing: list[str]


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )


def process_present(name: str) -> bool:
    if os.name == "nt":
        proc = run_cmd(["tasklist"])
        haystack = proc.stdout.lower()
    else:
        proc = run_cmd(["ps", "-eo", "comm"])
        haystack = proc.stdout.lower()
    return name.lower() in haystack


def probe_once(targets: tuple[str, ...]) -> ProbeSample:
    found: dict[str, bool] = {}
    missing: list[str] = []
    for target in targets:
        is_up = process_present(target)
        found[target] = is_up
        if not is_up:
            missing.append(target)
    return ProbeSample(
        timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
        found=found,
        missing=missing,
    )


def emit_sample(sample: ProbeSample, target: Path | None = None) -> None:
    line = json.dumps({
        "timestamp": sample.timestamp,
        "found": sample.found,
        "missing": sample.missing,
    })
    if target is None:
        print(line)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fp:
            fp.write(line + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run keepalive probes in loop or one-shot")
    parser.add_argument("--targets", nargs="+", default=list(DEFAULT_TARGETS), help="Process tokens to check")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between probes")
    parser.add_argument("--iterations", type=int, default=1, help="How many samples to take")
    parser.add_argument("--max-miss", type=int, default=1, help="Fail after this many misses in a sample")
    parser.add_argument("--emit-file", help="Append JSONL samples to this file")
    parser.add_argument("--strict", action="store_true", help="Fail when misses exceed max-miss")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets = tuple(args.targets)
    emit_path = Path(args.emit_file) if args.emit_file else None
    fail_count = 0

    for _ in range(max(args.iterations, 1)):
        sample = probe_once(targets)
        emit_sample(sample, emit_path)
        missing = len(sample.missing)
        if missing > args.max_miss:
            fail_count += 1
            print(f"{sample.timestamp} WARN missing={missing}: {', '.join(sample.missing)}")
        else:
            print(f"{sample.timestamp} OK keepalive: {sample.found}")
        if _ != args.iterations - 1:
            time.sleep(args.interval)

    if args.strict and fail_count:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
