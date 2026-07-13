#!/usr/bin/env python3
"""Runtime health surface for local agent tooling."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


try:
    from .. import state_authority
except Exception:  # pragma: no cover - direct script execution
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.append(str(repo_root))
    authority_path = repo_root / "founder_mode" / "state_authority.py"
    authority_spec = importlib.util.spec_from_file_location("founder_mode.state_authority", authority_path)
    if authority_spec is None or authority_spec.loader is None:
        raise
    state_authority = importlib.util.module_from_spec(authority_spec)
    sys.modules["founder_mode.state_authority"] = state_authority
    authority_spec.loader.exec_module(state_authority)


EXPECTED_TOOLSET = [
    "scripts/agent_toolset_scaffold.py",
    "scripts/issue_pr_draft_coverage.py",
    "scripts/pr_census.py",
    "scripts/claim_drift.py",
    "scripts/check-dependencies.py",
    "scripts/anvil_git_signing_audit.py",
    "scripts/audit-github-actions.py",
    "scripts/financial_pulse.py",
    "scripts/ops/keepalive_fleet_loop.py",
    "founder_mode/services/health.py",
]


@dataclass
class HealthCheck:
    name: str
    status: str
    detail: str


def run_cmd(cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def check_files(root: Path) -> HealthCheck:
    missing = [path for path in EXPECTED_TOOLSET if not (root / path).exists()]
    if missing:
        return HealthCheck(
            "core_toolset_files",
            "warn",
            f"missing {len(missing)} files",
        )
    return HealthCheck("core_toolset_files", "pass", "all required files present")


def check_git(root: Path) -> HealthCheck:
    proc = run_cmd(["git", "status", "--short"], cwd=str(root))
    if proc.returncode != 0:
        return HealthCheck("git_access", "warn", "git status failed")
    return HealthCheck("git_access", "pass", "git status available")


def check_authority() -> HealthCheck:
    try:
        actor = state_authority.current_actor()
        state_authority.require_actor("health_check")
        return HealthCheck("actor_authority", "pass", actor)
    except Exception as exc:
        return HealthCheck("actor_authority", "warn", str(exc))


def check_python() -> HealthCheck:
    major = f"{sys.version_info.major}.{sys.version_info.minor}"
    return HealthCheck("python_version", "pass", major)


def gather_health(root: Path) -> dict[str, object]:
    checks = [check_files(root), check_git(root), check_authority(), check_python()]
    status = "pass"
    if any(item.status != "pass" for item in checks):
        status = "warn"
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repo": str(root),
        "status": status,
        "checks": [check.__dict__ for check in checks],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run lightweight health probes")
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--strict", action="store_true", help="Fail on non-pass checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo).resolve()
    report = gather_health(root)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Health: {report['status']}")
        for check in report["checks"]:
            print(f"- {check['name']}: {check['status']} ({check['detail']})")
    if args.strict and report["status"] != "pass":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
