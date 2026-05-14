# hummbl-governance — OWASP AI Security Solutions Landscape Submission

**Submission for**: AI Security Solutions Landscape (Agentic AI) — Q3 2026 Cycle
**Submitted by**: HUMMBL, LLC (Reuben Bowlby)
**Date**: 2026-05-14
**Package Version**: hummbl-governance v0.8.0
**License**: Apache-2.0
**Repository**: https://github.com/hummbl-dev/hummbl-governance
**PyPI**: https://pypi.org/project/hummbl-governance/
**MCP Servers**: 7 MCP servers exposing 32+ JSON-RPC governance tools

---

## 1. Solution Overview

**hummbl-governance** is a stdlib-only Python library providing 25+ governance primitives for AI agent orchestration. It operates at the DevOps–SecOps intersection, implementing the control plane for autonomous AI systems without requiring runtime wrapping or agent SDK modifications.

### Core Differentiators

| Dimension | hummbl-governance |
|-----------|-------------------|
| Dependency model | **Zero third-party runtime deps** (stdlib only) |
| Architecture | Governance-as-library — primitives embed directly into agent pipelines |
| Scope | Full agent lifecycle: pre-execution gates → runtime enforcement → post-hoc audit |
| Interoperability | 7 MCP servers (32+ tools) for integration with any LLM framework |
| Maturity | 927 passing tests, Python 3.11–3.14, in production since 2025 |

### Governance Primitives (25 total)

| Category | Primitives |
|----------|------------|
| **Emergency Control** | Kill switch (4 modes: DISENGAGED → HALT_NONCRITICAL → HALT_ALL → EMERGENCY) |
| **Resilience** | Circuit breaker (3-state FSM: CLOSED → OPEN → HALF_OPEN) |
| **Cost Governance** | Cost governor with SQLite-backed budget tracking (ALLOW/WARN/DENY) |
| **Identity & Access** | Delegation tokens (HMAC-SHA256, time-bound, caveat-constrained), agent identity registry, trust scoring |
| **Audit & Provenance** | Append-only JSONL audit log, cognitive ledger (CLP), amendment chains |
| **Validation** | JSON Schema validator (stdlib-only, Draft 2020-12 subset), output review gates |
| **Coordination** | TSV governance bus, flock-based locking, MCP servers (7) |
| **Safety** | Sandbox policy (graduated verification), scope gate hooks, behavioral monitors |
| **Reasoning** | Governance reasoning engine with rule application and conflict detection |

---

## 2. OWASP Agentic Top 10 Coverage

**Coverage snapshot: 3 FULL · 5 PARTIAL · 2 NONE**

Improvement from v0.1 (4 FULL / 4 PARTIAL / 2 NONE) → v0.8 (3 FULL / 5 PARTIAL / 2 NONE). Note: coverage distribution shifted toward PARTIAL as more risk categories gained partial primitive coverage.

| # | OWASP Risk | Coverage | Modules | Gap |
|---|-----------|----------|---------|-----|
| 1 | Excessive Agency | **PARTIAL** | kill_switch, delegation, identity, cost_governor | No application-level permission enforcement |
| 2 | Tool Misuse | **PARTIAL** | schema_validator, delegation, audit_log | No semantic parameter validation |
| 3 | Memory Poisoning | **PARTIAL** | audit_log, identity, kill_switch | No runtime context integrity |
| 4 | Intent Hijacking | **PARTIAL** | delegation, kill_switch, audit_log | No real-time intent monitoring |
| 5 | Planning Chain Coercion | **PARTIAL** | delegation, audit_log, kill_switch | No formal plan verification |
| 6 | Insufficient Output Validation | **PARTIAL** | schema_validator, audit_log | No semantic/content-safety filtering |
| 7 | Unsafe Code Execution | **NONE** | — | Execution sandbox layer (out of scope) |
| 8 | DoS / Resource Exhaustion | **FULL** | cost_governor, circuit_breaker, kill_switch, delegation | — |
| 9 | Supply Chain Vulnerabilities | **FULL** | stdlib-only, schema_validator, identity | No model-provider attestation |
| 10 | Logging & Monitoring Failures | **FULL** | audit_log, kill_switch, circuit_breaker, cost_governor | No built-in alerting transport |

### Coverage Gains Since v0.1 (London Summit Q2 submission)

| Risk | v0.1 → v0.8 |
|------|-------------|
| Excessive Agency | FULL → PARTIAL (refined to acknowledge app-layer gap) |
| Tool Misuse | PARTIAL → PARTIAL (added schema_validator coverage) |
| Memory Poisoning | PARTIAL → PARTIAL (added identity module) |
| Intent Hijacking | PARTIAL → PARTIAL (added audit_log forensics) |
| Supply Chain | FULL → FULL (confirmed with SBOM artifacts) |
| Logging | FULL → FULL (added cost_governor callbacks) |

---

## 3. Architecture & Integration

### Deployment Model

```
┌─────────────────────────────────────────────┐
│         Agent Application Layer             │
│  (Customer's LLM app / agent orchestrator)  │
├─────────────────────────────────────────────┤
│  hummbl-governance (stdlib-only Python)      │
│  ├── KillSwitch        ─┐                   │
│  ├── CircuitBreaker     ├── Control Plane   │
│  ├── CostGovernor       ├── Policy Layer    │
│  ├── DelegationToken    ├── Identity Layer  │
│  ├── AuditLog           ├── Audit Layer     │
│  ├── SchemaValidator    ├── Validation      │
│  └── MCP Servers        └── Integration     │
├─────────────────────────────────────────────┤
│         Infrastructure Layer                 │
│  (Execution sandbox, network policy, OS)     │
└─────────────────────────────────────────────┘
```

### Integration Points

hummbl-governance integrates via:

1. **Direct Python import** — `from hummbl_governance import KillSwitch, CircuitBreaker`
2. **MCP servers** — 7 servers expose 32+ tools via JSON-RPC (stdio/HTTP)
3. **CLI entry points** — `hummbl-governance-mcp`, `hummbl-compliance-mcp`, etc.
4. **Governance bus** — TSV-based coordination bus for multi-agent systems

### MCP Server Inventory

| Server | Tools | Purpose |
|--------|-------|---------|
| `mcp_server.py` | 10 | Core governance: kill switch, circuit breaker, cost, audit, compliance |
| `mcp_compliance.py` | 5 | NIST, SOC 2, ISO crosswalks, STRIDE analysis |
| `mcp_sandbox.py` | 5 | Sandbox lifecycle: create, validate, destroy |
| `mcp_identity.py` | 10 | Identity registry, delegation, Lamport clock |
| `mcp_agent_monitor.py` | 11 | Behavioral monitoring, convergence detection |
| `mcp_reasoning.py` | — | Governance reasoning engine |
| `mcp_physical.py` | 6 | Physical-AI safety (kinematic governor, pHRI) |

---

## 4. Evidence & Testing

### Test Infrastructure

| Metric | Value |
|--------|-------|
| Total tests | 927 |
| Passing | 927 (100%) |
| Python versions | 3.11, 3.12, 3.13, 3.14 |
| CI | GitHub Actions (badge live) |
| Coverage | `--cov` integrated |

### Governance Testing

Tests cover:
- Kill switch mode transitions and task exemptions
- Circuit breaker CLOSED→OPEN→HALF_OPEN→CLOSED cycles
- Cost governor budget enforcement (soft/hard caps across providers)
- Delegation token lifecycle (create → delegate → validate → revoke)
- Token binding and caveat enforcement
- Audit log append-only invariants and amendment chains
- Schema validation (type, required, enum, pattern, bounds)
- Agent identity registry CRUD and trust tier management
- Behavioral monitor convergence detection

### Compliance Automation

Pre-built compliance reports (auto-generated):
- **NIST AI RMF** — GOVERN, MAP, MEASURE, MANAGE functions
- **EU AI Act** — Articles 9, 10, 12, 13, 14, 17 (High-Risk)
- **SOC 2** — Trust Service Criteria mapping
- **ISO 27001** — Annex A crosswalk
- **GDPR** — Articles 5, 32, 35 alignment
- **ISO 42001** — AI management system

---

## 5. Differentiation from Competitors

| Feature | hummbl-governance | Aqua Security | Lasso Security | Prompt Armor |
|---------|-------------------|---------------|----------------|-------------|
| Runtime dependency | None (stdlib) | Agent required | Agent required | SDK integration |
| Library vs. platform | Embeddable library | SaaS platform | SaaS platform | SaaS platform |
| Kill switch | 4-mode graduated | N/A | N/A | N/A |
| Delegation tokens | HMAC-SHA256 tokens | N/A | N/A | N/A |
| Circuit breaker | 3-state per adapter | N/A | N/A | N/A |
| MCP integration | 7 native servers | N/A | N/A | N/A |
| Supply chain | Zero deps + SBOM | N/A | N/A | N/A |
| Audit log | Append-only JSONL | Cloud logging | Cloud logging | Cloud logging |
| Cost governance | Native SQLite | N/A | N/A | N/A |

---

## 6. Gaps & Roadmap

### Known Gaps (with remediation plans)

| Gap | Risk | Severity | Remediation Target |
|-----|------|----------|--------------------|
| No execution sandboxing | ASI07 | HIGH | Document recommended sandboxes (gVisor, Firecracker) |
| No semantic output filtering | ASI06 | MEDIUM | Content-safety filter in Q3 2026 |
| No real-time intent monitoring | ASI04 | MEDIUM | IntentVerifier in Q3 2026 |
| No model-provider attestation | ASI09 | LOW | Supplier DCT enhancements |
| No built-in alerting transport | ASI10 | LOW | Webhook/SMTP alert adapters |

### 6-Month Roadmap

- **Q3 2026**: Sandbox integration documentation, content-safety filter prototype
- **Q4 2026**: IntentVerifier module, MCP server GA stabilization
- **Q1 2027**: Alerting transport adapters, model-provider attestation pilot

---

## 7. Community & Governance

- **Open source**: Apache-2.0, zero dependencies
- **Community**: 144+ service modules, 14,400+ tests across founder-mode ecosystem
- **Governance**: Multi-agent peer review protocol (CRAB), ISO 42001 alignment
- **Bus**: 153+ daily messages, 81,700+ messages across 117-day history
- **Adoption**: 7 MCP servers for any LLM framework integration

---

## 8. Submission Artifacts

| Artifact | Location |
|----------|----------|
| Library source | `founder_mode/` (inclusive of governance primitives) |
| OWASP Agentic Top 10 mapping | `PROJECTS/hummbl-governance/docs/OWASP_MAPPING.md` |
| OWASP LLM Top 10 coverage matrix | `PROJECTS/hummbl-governance/docs/coverage/owasp-llm.md` |
| Compliance maturities (NIST, SOC2, ISO, GDPR) | `PROJECTS/hummbl-governance/docs/coverage/` |
| Corrective action register | `founder_mode/docs/governance/CORRECTIVE_ACTION_REGISTER.md` |
| Peer review protocol | `founder_mode/docs/reference/PEER_REVIEW_PROTOCOL_v0.1.md` |
| MCP server code | `hummbl-governance/mcp_*.py` |
| Test suite | 927 tests, `hummbl-governance/tests/` |
| AAR (self-review steward shift) | `founder_mode/docs/operations/AAR_opencode_steward-shift_2026-05-14.md` |