# hummbl-governance Roadmap

This document outlines the strategic direction and technical evolution of the **hummbl-governance** library, aligned with the [HUMMBL Research Intelligence Framework (RIF) v6.0](https://github.com/hummbl-dev/hummbl-dev).

---

## Current Status: v0.8.0 (MCP Servers — Full Primitive Exposure)
**Focus:** Expose all 25 governance primitives as Model Context Protocol tools.

*   ✅ **mcp_server.py** (v0.7.0): KillSwitch, CircuitBreaker, CostGovernor, AuditLog, ComplianceMapper, HealthCollector via 10 JSON-RPC tools.
*   ✅ **mcp_compliance.py** (v0.7.0): NIST AI RMF, SOC2, ISO crosswalk, STRIDE, evidence export via 5 tools.
*   ✅ **mcp_sandbox.py** (v0.7.0): CapabilityFence / OutputValidator sandbox via 5 tools.
*   ✅ **mcp_identity.py** (v0.8.0): AgentRegistry, DelegationTokenManager, LamportClock via 10 tools.
*   ✅ **mcp_agent_monitor.py** (v0.8.0): BehaviorMonitor, ConvergenceDetector, GovernanceLifecycle, EvolutionLineage via 11 tools.
*   ✅ **mcp_reasoning.py** (v0.8.0): ReasoningEngine, SchemaValidator, ContractNetManager.
*   ✅ **mcp_physical.py** (v0.8.0): KinematicGovernor, pHRISafetyMonitor via 6 tools.
*   ✅ **927 tests** — all passing. 7 MCP servers, 4 CLI entry points.

---

## Shipped: v0.4.0 — v0.6.0

*   ✅ **v0.4.0** — KinematicGovernor, pHRISafetyMonitor, EAL, ReasoningEngine, FailureModes taxonomy.
*   ✅ **v0.5.0** — LamportClock hardening, EvolutionLineage, CI matrix (3 OS × 3 Python).
*   ✅ **v0.6.0** — NIST AI RMF report, EU AI Act report, ComplianceMapper extended.

---

## Phase 4: Compliance & Ecosystem (v0.9.0+)
**Focus:** Regulatory Alignment (EU AI Act, ISO 42001) and Framework Integration.

### v0.9.0: Ecosystem Adapters
*   **First-Class Adapters**: Standardized "Governed Tool" wrappers for:
    *   Anthropic Agent SDK
    *   CrewAI
    *   LangGraph
    *   MCP (Model Context Protocol)

---

## Phase 5: v1.0.0 Stability & Beyond
**Focus:** Formal Verification & Production Maturity.

*   **API Freeze**: Finalized stable interface for all 23+ governance primitives.
*   **Formal Verification**: TLA+ or similar modeling of core concurrency/locking logic (KillSwitch, CircuitBreaker).
*   **Performance Benchmarking**: Stress-testing the `hummbl` kernel under high-entropy, multi-agent scenarios.

---

*Copyright 2026 HUMMBL, LLC. All rights reserved.*
