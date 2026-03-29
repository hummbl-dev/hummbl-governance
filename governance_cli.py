#!/usr/bin/env python3
"""hummbl governance CLI — Governance-as-Code for AI agents.

Like `terraform plan` but for AI governance. Define policies, check state,
enforce compliance.

Usage:
    hummbl init [--dir DIR]      Initialize governance state directory
    hummbl status                Show all governance primitive states
    hummbl plan [--policy FILE]  Show what governance actions would be taken
    hummbl apply [--policy FILE] Apply governance policy
    hummbl audit [--days N]      Audit governance log for compliance
    hummbl score                 Score current governance posture (0-100)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hummbl_governance import (
    KillSwitch,
    CircuitBreaker,
    CostGovernor,
)


def get_state_dir():
    return Path(os.environ.get("GOVERNANCE_STATE_DIR", ".governance"))


def cmd_init(args):
    """Initialize governance state directory."""
    state_dir = Path(args.dir) if args.dir else get_state_dir()
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "audit").mkdir(exist_ok=True)
    (state_dir / "costs.db").touch(exist_ok=True)

    # Write default policy
    policy = {
        "version": "1.0",
        "kill_switch": {"critical_tasks": ["health_check", "audit_log"]},
        "circuit_breaker": {"failure_threshold": 5, "recovery_timeout": 60},
        "cost_governor": {"soft_cap": 50.0, "hard_cap": 100.0, "currency": "USD"},
        "compliance": {"frameworks": ["soc2", "nist", "owasp"]},
    }
    policy_file = state_dir / "policy.json"
    if not policy_file.exists():
        with open(policy_file, "w") as f:
            json.dump(policy, f, indent=2)
        print(f"Created policy: {policy_file}")

    print(f"Governance initialized at: {state_dir}")
    print("  audit/     — Append-only JSONL audit log")
    print("  costs.db   — Cost governor SQLite database")
    print("  policy.json — Governance policy definition")


def cmd_status(args):
    """Show governance primitive states."""
    state_dir = get_state_dir()
    if not state_dir.exists():
        print(f"ERROR: No governance state at {state_dir}. Run: hummbl init")
        sys.exit(1)

    ks = KillSwitch(state_dir=state_dir)
    cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
    cg = CostGovernor(db_path=str(state_dir / "costs.db"))
    budget = cg.check_budget_status()

    print(f"Governance Status | {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}")
    print("=" * 50)
    print(f"  Kill Switch:     {ks.mode.name if hasattr(ks.mode, 'name') else ks.mode}")
    print(f"  Circuit Breaker: {cb.state.name if hasattr(cb.state, 'name') else cb.state}")
    spend = getattr(budget, 'current_spend', 0)
    decision = getattr(budget, 'decision', 'UNKNOWN')
    decision_name = decision.name if hasattr(decision, 'name') else str(decision)
    print(f"  Cost Governor:   ${spend:.2f} | Decision: {decision_name}")
    print(f"  State Dir:       {state_dir}")


def cmd_plan(args):
    """Show what governance actions would be taken."""
    state_dir = get_state_dir()
    policy_file = Path(args.policy) if args.policy else state_dir / "policy.json"

    if not policy_file.exists():
        print(f"ERROR: No policy at {policy_file}. Run: hummbl init")
        sys.exit(1)

    with open(policy_file) as f:
        policy = json.load(f)

    print(f"Governance Plan | policy: {policy_file}")
    print("=" * 50)
    print()

    # Check kill switch config
    ks_policy = policy.get("kill_switch", {})
    print("Kill Switch:")
    print(f"  Critical tasks: {ks_policy.get('critical_tasks', [])}")
    print()

    # Check circuit breaker config
    cb_policy = policy.get("circuit_breaker", {})
    print("Circuit Breaker:")
    print(f"  Failure threshold: {cb_policy.get('failure_threshold', 5)}")
    print(f"  Recovery timeout:  {cb_policy.get('recovery_timeout', 60)}s")
    print()

    # Check cost governor config
    cg_policy = policy.get("cost_governor", {})
    print("Cost Governor:")
    print(f"  Soft cap: ${cg_policy.get('soft_cap', 50.0):.2f}")
    print(f"  Hard cap: ${cg_policy.get('hard_cap', 100.0):.2f}")
    print()

    # Compliance frameworks
    compliance = policy.get("compliance", {})
    print("Compliance Frameworks:")
    for fw in compliance.get("frameworks", []):
        print(f"  - {fw.upper()}")

    print()
    print("No changes needed. Run 'hummbl apply' to enforce.")


def cmd_apply(args):
    """Apply governance policy."""
    state_dir = get_state_dir()
    policy_file = Path(args.policy) if args.policy else state_dir / "policy.json"

    if not policy_file.exists():
        print(f"ERROR: No policy at {policy_file}. Run: hummbl init")
        sys.exit(1)

    with open(policy_file) as f:
        policy = json.load(f)

    print("Applying governance policy...")

    # Initialize primitives with policy values
    ks_policy = policy.get("kill_switch", {})
    KillSwitch(
        state_dir=state_dir,
        critical_tasks=ks_policy.get("critical_tasks"),
    )
    print("  Kill switch: configured")

    cb_policy = policy.get("circuit_breaker", {})
    CircuitBreaker(
        failure_threshold=cb_policy.get("failure_threshold", 5),
        recovery_timeout=cb_policy.get("recovery_timeout", 60),
    )
    print("  Circuit breaker: configured")

    cg_policy = policy.get("cost_governor", {})
    CostGovernor(
        db_path=str(state_dir / "costs.db"),
        soft_cap=cg_policy.get("soft_cap", 50.0),
        hard_cap=cg_policy.get("hard_cap", 100.0),
    )
    print("  Cost governor: configured")

    print()
    print("Governance policy applied successfully.")


def cmd_audit(args):
    """Audit governance log."""
    state_dir = get_state_dir()
    audit_dir = state_dir / "audit"
    if not audit_dir.exists():
        print("No audit logs found.")
        return

    # Count entries
    total = 0
    files = sorted(audit_dir.glob("*.jsonl"))
    for f in files:
        with open(f) as fh:
            total += sum(1 for line in fh if line.strip())

    print(f"Governance Audit | {len(files)} log files, {total} entries")
    print("=" * 50)
    if total == 0:
        print("  No audit entries. Governance actions generate audit trails automatically.")
    else:
        print(f"  Log files: {[f.name for f in files[-5:]]}")
        print(f"  Total entries: {total}")


def _score_kill_switch(state_dir):
    """Score kill switch component."""
    ks = KillSwitch(state_dir=state_dir)
    if not ks.engaged:
        return 20, "Kill switch: DISENGAGED (normal) +20"
    return 10, f"Kill switch: {ks.mode} (engaged, investigate) +10"


def _score_policy(state_dir):
    """Score policy file component."""
    if (state_dir / "policy.json").exists():
        return 15, "Policy file: exists +15"
    return 0, "Policy file: MISSING +0 (run hummbl init)"


def _score_cost_governor(state_dir):
    """Score cost governor component."""
    if not (state_dir / "costs.db").exists():
        return 0, "Cost governor: no database +0"
    cg = CostGovernor(db_path=str(state_dir / "costs.db"))
    budget = cg.check_budget_status()
    decision = getattr(budget, 'decision', None)
    decision_name = decision.name if hasattr(decision, 'name') else str(decision)
    if decision_name == "ALLOW":
        return 20, "Cost governor: within budget +20"
    if decision_name == "WARN":
        return 10, "Cost governor: WARNING +10"
    return 0, "Cost governor: DENY +0"


def _score_audit_log(state_dir):
    """Score audit log component."""
    audit_dir = state_dir / "audit"
    if audit_dir.exists() and any(audit_dir.glob("*.jsonl")):
        return 20, "Audit log: active +20"
    if audit_dir.exists():
        return 10, "Audit log: directory exists but empty +10"
    return 0, "Audit log: MISSING +0"


def _score_compliance(state_dir):
    """Score compliance frameworks component."""
    policy_file = state_dir / "policy.json"
    if not policy_file.exists():
        return 0, None
    with open(policy_file) as f:
        policy = json.load(f)
    frameworks = policy.get("compliance", {}).get("frameworks", [])
    if len(frameworks) >= 2:
        return 15, f"Compliance: {len(frameworks)} frameworks +15"
    if len(frameworks) == 1:
        return 8, "Compliance: 1 framework +8"
    return 0, "Compliance: no frameworks +0"


def _score_to_cli_grade(score):
    """Convert numeric score to letter grade."""
    if score >= 95:
        return "A+"
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def cmd_score(args):
    """Score governance posture."""
    state_dir = get_state_dir()
    if not state_dir.exists():
        print("ERROR: No governance state. Run: hummbl init")
        sys.exit(1)

    score = 0
    max_score = 100
    findings = []

    scorers = [
        _score_kill_switch,
        _score_policy,
        _score_cost_governor,
        _score_audit_log,
        _score_compliance,
    ]
    for scorer in scorers:
        pts, finding = scorer(state_dir)
        score += pts
        if finding:
            findings.append(finding)

    # Circuit breaker (always available)
    score += 10
    findings.append("Circuit breaker: available +10")

    grade = _score_to_cli_grade(score)
    print(f"Governance Score: {score}/{max_score} ({grade})")
    print("=" * 50)
    for f in findings:
        print(f"  {f}")


def main():
    parser = argparse.ArgumentParser(prog="hummbl", description="Governance-as-Code CLI")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize governance state")
    p_init.add_argument("--dir", help="State directory (default: .governance)")

    sub.add_parser("status", help="Show governance state")

    p_plan = sub.add_parser("plan", help="Show governance plan")
    p_plan.add_argument("--policy", help="Policy file path")

    p_apply = sub.add_parser("apply", help="Apply governance policy")
    p_apply.add_argument("--policy", help="Policy file path")

    p_audit = sub.add_parser("audit", help="Audit governance log")
    p_audit.add_argument("--days", type=int, default=30, help="Days to audit")

    sub.add_parser("score", help="Score governance posture")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "plan":
        cmd_plan(args)
    elif args.command == "apply":
        cmd_apply(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "score":
        cmd_score(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
