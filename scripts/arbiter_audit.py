#!/usr/bin/env python3
"""Arbiter audit for CI job."""

import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "arbiter", "score", ".", "--json"],
    capture_output=True,
    text=True,
)
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
if result.returncode != 0:
    raise SystemExit(result.returncode)

payload_start = result.stdout.find("{")
if payload_start == -1:
    raise SystemExit("arbiter score did not emit JSON output")

report = json.loads(result.stdout[payload_start:])
score = float(report["overall"])
if score < 90.0:
    raise SystemExit(f"Arbiter score {score} is below the 90.0 threshold")

print(f"Arbiter score {score} meets threshold")
