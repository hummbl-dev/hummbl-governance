# hummbl-governance Roadmap

This document outlines the strategic direction and technical evolution of the **hummbl-governance** library, aligned with the [HUMMBL Research Intelligence Framework (RIF) v6.0](https://github.com/hummbl-dev/hummbl-dev).

---

## Current Status: v1.2.1 (PyPI Metadata Alignment)

**Focus:** 34 governance primitives, 7 MCP servers, API stability guarantee, zero runtime dependencies.

- ✅ **v1.0.0** — API stability guarantee for all primitives. Sphinx docs, 25 usage examples, benchmark suite.
- ✅ **v1.1.0** — Governance Kernel (26th primitive): signed receipts, identity registry, role claims, sequence enforcement, evidence grading, authority scoping, schedule tracking, scaling-law evaluation. 12 runtime modules, 136 tests.
- ✅ **v1.2.0** — Contestability (P31), DoctrineAmendment (P38), API server auth + CORS, repo naming exception policy, and scientific grounding coordination matrix.
- ✅ **v1.2.1** — PyPI metadata patch release aligning the built long description with 34 implemented primitives, 2027 collected tests, and Python 3.11-3.13 support.
- ✅ **34 governance primitives** across safety, cost, identity, compliance, reasoning, coordination, physical-AI, execution assurance, error taxonomy, and governance kernel (K1-K11 invariants, D1-D7 doctrine invariants).
- ✅ **7 MCP servers** exposing all primitives as JSON-RPC tools (57 tools total).
- ✅ **2027 collected tests** — all passing. 4 CLI entry points.
- ✅ **Zero third-party runtime dependencies** — stdlib only.

### MCP Server Inventory

| Server                 | Version | Tools | Wraps                                                                             |
| ---------------------- | ------- | ----- | --------------------------------------------------------------------------------- |
| `mcp_server.py`        | v0.7.0  | 10    | KillSwitch, CircuitBreaker, CostGovernor, AuditLog, ComplianceMapper, HealthProbe |
| `mcp_compliance.py`    | v0.7.0  | 5     | NIST AI RMF, SOC2, ISO crosswalk, STRIDE, evidence export                         |
| `mcp_sandbox.py`       | v0.7.0  | 5     | CapabilityFence, OutputValidator sandbox                                          |
| `mcp_identity.py`      | v0.8.0  | 10    | AgentRegistry, DelegationTokenManager, LamportClock                               |
| `mcp_agent_monitor.py` | v0.8.0  | 11    | BehaviorMonitor, ConvergenceDetector, GovernanceLifecycle, EvolutionLineage       |
| `mcp_reasoning.py`     | v0.8.0  | 10    | ReasoningEngine, SchemaValidator, ContractNetManager                              |
| `mcp_physical.py`      | v0.8.0  | 6     | KinematicGovernor, pHRISafetyMonitor                                              |

---

## Shipped: v0.4.0 — v0.8.0

- ✅ **v0.4.0** — KinematicGovernator, pHRISafetyMonitor, EAL, ReasoningEngine, FailureModes taxonomy.
- ✅ **v0.5.0** — LamportClock hardening, EvolutionLineage, CI matrix (3 OS × 3 Python).
- ✅ **v0.6.0** — NIST AI RMF report, EU AI Act report, ComplianceMapper extended.
- ✅ **v0.7.0** — MCP server exposure: KillSwitch, CircuitBreaker, CostGovernor, AuditLog, ComplianceMapper, HealthCollector, CapabilityFence, OutputValidator via JSON-RPC tools.
- ✅ **v0.8.0** — Full MCP exposure: AgentRegistry, DelegationTokenManager, LamportClock, BehaviorMonitor, ConvergenceDetector, GovernanceLifecycle, EvolutionLineage, ReasoningEngine, SchemaValidator, ContractNetManager, KinematicGovernor, pHRISafetyMonitor.

---

## Phase 4: Compliance & Ecosystem (v1.3.0+)

**Focus:** Regulatory alignment (EU AI Act, ISO 42001) and framework integration.

### v1.3.0: Ecosystem Adapters

- **First-Class Adapters**: Standardized "Governed Tool" wrappers for:
  - Anthropic Agent SDK
  - CrewAI
  - LangGraph
  - MCP (Model Context Protocol)

---

## Phase 5: Formal Verification & Beyond

**Focus:** Formal verification and production maturity.

- **Formal Verification**: TLA+ or similar modeling of core concurrency/locking logic (KillSwitch, CircuitBreaker).
- **Performance Benchmarking**: Stress-testing the `hummbl` kernel under high-entropy, multi-agent scenarios.
- **Python 3.14 CI**: Add 3.14 to CI matrix once stable.

---

_Copyright 2026 HUMMBL, LLC. All rights reserved._
