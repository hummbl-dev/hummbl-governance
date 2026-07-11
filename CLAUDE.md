# CLAUDE.md

## Project

**hummbl-governance** — Governance primitives for AI agent orchestration. v1.1.0, tests (verify with: `pytest --collect-only -q | tail -1`), zero third-party runtime dependencies.

Standalone Python package extracted from founder-mode. Provides governance primitives (verify with: `python -c 'import hummbl_governance; print(len([x for x in dir(hummbl_governance) if not x.startswith("_")]))'`) across safety, cost, identity, compliance, reasoning, coordination, physical-AI, execution assurance, and governance Kernel. Ships MCP servers (verify with: `find . -name 'mcp_*.py' | wc -l`) exposing all primitives as JSON-RPC tools.

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
python -m pytest tests/ -v --cov=hummbl_governance --cov-fail-under=80
```

## Primitives (26)

| Category | Modules |
|---|---|
| Governance Kernel | `kernel` — receipts, identity, roles, laws, evidence, sequence, authority, schedule |
| Safety | `kill_switch`, `circuit_breaker`, `output_validator`, `capability_fence` |
| Cost & Budget | `cost_governor` |
| Identity & Auth | `identity`, `delegation` |
| Audit & Compliance | `audit_log`, `compliance_mapper`, `stride_mapper` |
| Reasoning & Contract | `reasoning`, `contract_net`, `schema_validator` |
| Coordination | `coordination_bus`, `lamport_clock`, `convergence_guard` |
| Behavior & Health | `reward_monitor`, `health_probe`, `lifecycle` |
| Physical AI | `physical_governor` |
| Execution Assurance | `eal` |
| Error Taxonomy | `errors`, `failure_modes`, `evolution_lineage` |
| Exports | `ValidationError` (from schema_validator) |

## MCP Servers (7)

Entry points via `hummbl-*-mcp` CLI commands or direct `python -m`:

| Server | Tools | Wraps |
|---|---|---|
| `mcp_server.py` | 10 | KillSwitch, CircuitBreaker, CostGovernor, AuditLog, ComplianceMapper, HealthProbe |
| `mcp_compliance.py` | 5 | NIST AI RMF, SOC2, ISO crosswalk, STRIDE, evidence export |
| `mcp_sandbox.py` | 5 | CapabilityFence, OutputValidator sandbox |
| `mcp_identity.py` | 10 | AgentRegistry, DelegationTokenManager, LamportClock |
| `mcp_agent_monitor.py` | 11 | BehaviorMonitor, ConvergenceDetector, GovernanceLifecycle, EvolutionLineage |
| `mcp_reasoning.py` | — | ReasoningEngine, SchemaValidator, ContractNetManager |
| `mcp_physical.py` | 6 | KinematicGovernor, pHRISafetyMonitor |

## CI

- **Gitea** (canonical): Windows self-hosted runner, Python 3.13.13. Uses `& "$env:PYTHON"` pattern — do NOT use bare `python` or `actions/setup-python@v5`.
- **GitHub** (mirror): ubuntu-latest, Python 3.11 / 3.12 / 3.13 matrix.

## Key Conventions

- Python 3.11+ required (3.14 classifiers present; treat as experimental)
- Zero third-party runtime dependencies (stdlib only)
- Test dependencies (pytest, pytest-cov) in `[test]` extras only
- All modules independently importable from `hummbl_governance`
- Thread-safe implementations throughout
- Apache 2.0 license
- Coverage threshold: 80% (enforced in CI)
