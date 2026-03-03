# hummbl-governance

**Agent Runtime Governance** -- five battle-tested primitives for building AI agents that govern themselves.

*Ship agents that govern themselves.*

---

## What is this?

`hummbl-governance` provides five standalone governance primitives extracted from production agent infrastructure. Each primitive is stdlib-only (zero third-party dependencies), thread-safe where noted, and designed to compose with any agent framework.

| Primitive | Purpose |
|-----------|---------|
| **DelegationToken** | HMAC-SHA256 signed capability tokens for agent-to-agent delegation |
| **DelegationContext** | DCTX state machine with chain depth enforcement and budget tracking |
| **GovernanceBus** | Append-only JSONL audit log with rotation and retention |
| **CircuitBreaker** | Automatic failure detection and recovery (CLOSED / OPEN / HALF_OPEN) |
| **KillSwitch** | Graduated emergency halt system (DISENGAGED / HALT_NONCRITICAL / HALT_ALL / EMERGENCY) |

## Installation

```bash
pip install hummbl-governance
```

Requires Python 3.11+. Zero runtime dependencies.

## Quickstart

### DelegationToken

HMAC-SHA256 signed tokens that bind agent capabilities to specific tasks and contracts. Enforce least-privilege delegation between agents.

```python
from hummbl_governance import DelegationToken

manager = DelegationToken.Manager(secret=b"your-signing-secret")

# Create a scoped token
token = manager.create_token(
    issuer="orchestrator",
    subject="worker-agent",
    ops_allowed=["read_file", "write_file"],
    binding=DelegationToken.Binding(task_id="task-123", contract_id="contract-456"),
    expiry_minutes=120,
)

# Validate before use
is_valid, error_code = manager.validate_token(token)
assert is_valid

# Enforce least privilege
is_allowed, error = manager.check_least_privilege(token, "read_file")
assert is_allowed
```

### GovernanceBus

Append-only audit log for governance events. Supports daily rotation, configurable retention, and query by intent or task.

```python
from hummbl_governance import GovernanceBus

bus = GovernanceBus(base_dir="/var/log/governance", retention_days=180)

# Append an audit entry
success, error = bus.append(
    intent_id="intent-abc",
    task_id="task-123",
    tuple_type="DCT",
    tuple_data={"action": "delegated", "to": "worker-agent"},
)

# Query by intent
for entry in bus.query_by_intent("intent-abc"):
    print(f"{entry.timestamp}: {entry.tuple_type} -- {entry.tuple_data}")

# Query by task
for entry in bus.query_by_task("task-123"):
    print(entry.to_jsonl())
```

### CircuitBreaker

Classic three-state circuit breaker for wrapping external service calls. Tracks consecutive failures and auto-recovers after a configurable timeout.

```python
from hummbl_governance import CircuitBreaker, CircuitBreakerOpen

cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)

try:
    result = cb.call(external_api_call, arg1, arg2)
except CircuitBreakerOpen:
    result = fallback_value

# State inspection
print(cb.state)          # CircuitBreakerState.CLOSED
print(cb.failure_count)  # 0

# State change notifications
def on_change(old_state, new_state):
    print(f"Circuit breaker: {old_state.name} -> {new_state.name}")

cb = CircuitBreaker(on_state_change=on_change)
```

### KillSwitch

Graduated emergency halt with four modes. Supports critical task exemptions, subscriber notifications, and persistent state.

```python
from hummbl_governance import KillSwitch, KillSwitchMode

ks = KillSwitch()

# Engage with graduated response
ks.engage(
    mode=KillSwitchMode.HALT_NONCRITICAL,
    reason="Budget threshold exceeded",
    triggered_by="cost_governor",
)

# Check if a task is allowed
result = ks.check_task_allowed("briefing_generation")
if not result["allowed"]:
    print(f"Blocked: {result['reason']}")

# Critical tasks continue even in HALT_NONCRITICAL
result = ks.check_task_allowed("safety_monitoring")
assert result["allowed"]  # Critical tasks are exempt

# Disengage when resolved
ks.disengage(triggered_by="admin", reason="Budget replenished")

# Persistent state (survives restarts)
ks = KillSwitch(state_dir="/var/lib/governance")
ks.engage(KillSwitchMode.HALT_ALL, "Incident", "system")
# State written to /var/lib/governance/kill_switch_state.json

# Load from persisted state
ks = KillSwitch.load_from_file("/var/lib/governance")
print(ks.mode)  # KillSwitchMode.HALT_ALL
```

## Feature Flags

DelegationToken and GovernanceBus support the `ENABLE_IDP` environment variable:

- `ENABLE_IDP=true` (default): Full enforcement -- tokens are validated, audit entries are written
- `ENABLE_IDP=false`: Bypass mode -- all tokens pass validation, no audit entries written

This allows gradual rollout in existing systems.

## Design Principles

1. **Stdlib only.** Zero third-party runtime dependencies. These primitives run anywhere Python runs.
2. **Thread safe.** CircuitBreaker and GovernanceBus use internal locks for concurrent access. KillSwitch documents its threading model.
3. **Fail safe.** Subscriber errors are swallowed. Persistence failures do not crash the system. Invalid state files result in clean defaults.
4. **Composable.** Each primitive works independently. Combine them to build governance layers for any agent architecture.

## License

Apache 2.0. See [LICENSE](LICENSE).

## Links

- Homepage: [hummbl.io](https://hummbl.io)
- Repository: [github.com/hummbl-dev/hummbl-governance](https://github.com/hummbl-dev/hummbl-governance)
- Issues: [github.com/hummbl-dev/hummbl-governance/issues](https://github.com/hummbl-dev/hummbl-governance/issues)
