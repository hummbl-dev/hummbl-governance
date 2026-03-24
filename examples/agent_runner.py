#!/usr/bin/env python3
"""Demo: Agent runner with safety guardrails.

Shows the full pattern: an agent executes tasks protected by a circuit
breaker and kill switch, with all events logged to the coordination bus.

Usage:
    python examples/agent_runner.py
"""

import random
import tempfile
from pathlib import Path

from hummbl_governance import (
    BusWriter,
    CircuitBreaker,
    KillSwitch,
    KillSwitchMode,
)
from hummbl_governance.circuit_breaker import CircuitBreakerOpen
from hummbl_governance.kill_switch import KillSwitchEngagedError


def flaky_external_service(success_rate: float = 0.7) -> str:
    """Simulates an external service that fails intermittently."""
    if random.random() > success_rate:
        raise ConnectionError("Service unavailable")
    return "result-ok"


def main():
    # Setup
    bus_path = Path(tempfile.mkdtemp()) / "demo_bus.tsv"
    bus = BusWriter(bus_path)
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=2.0,
        on_state_change=lambda old, new: bus.post(
            "agent-runner", "all", "STATUS",
            f"Circuit breaker: {old.name} -> {new.name}",
        ),
    )
    ks = KillSwitch()

    bus.post("agent-runner", "all", "STATUS", "Agent starting")

    # Execute tasks
    tasks = ["fetch_data", "process_data", "generate_report", "send_notification", "cleanup"]

    for task_name in tasks:
        # Check kill switch first
        result = ks.check_task_allowed(task_name)
        if not result["allowed"]:
            bus.post("agent-runner", "all", "STATUS", f"Task '{task_name}' blocked by kill switch")
            print(f"  BLOCKED: {task_name} (kill switch: {ks.mode.name})")
            continue

        # Execute through circuit breaker
        try:
            svc_result = breaker.call(flaky_external_service, 0.6)
            bus.post("agent-runner", "all", "STATUS", f"Task '{task_name}' completed: {svc_result}")
            print(f"  OK: {task_name}")
        except CircuitBreakerOpen as e:
            bus.post("agent-runner", "all", "STATUS", f"Task '{task_name}' skipped: breaker open")
            print(f"  SKIPPED: {task_name} (breaker open, {e.failure_count} failures)")
            # Engage kill switch if breaker is open
            if not ks.engaged:
                ks.engage(KillSwitchMode.HALT_NONCRITICAL, reason="Circuit breaker open", triggered_by="agent-runner")
                print(f"  >> Kill switch engaged: HALT_NONCRITICAL")
        except ConnectionError as e:
            bus.post("agent-runner", "all", "STATUS", f"Task '{task_name}' failed: {e}")
            print(f"  FAILED: {task_name} ({e})")

    bus.post("agent-runner", "all", "STATUS", "Agent finished")

    # Print bus log
    print(f"\n--- Bus log ({bus_path}) ---")
    for msg in bus.read_all():
        print(f"  [{msg['timestamp']}] {msg['from']} > {msg['to']}: {msg['message']}")

    print(f"\nKill switch events: {len(ks.get_history())}")
    print(f"Circuit breaker state: {breaker.state.name}")
    print(f"Circuit breaker failures: {breaker.failure_count}")


if __name__ == "__main__":
    random.seed(42)  # Reproducible demo
    main()
