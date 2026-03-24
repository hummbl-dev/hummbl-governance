# Product Requirements Document: hummbl-governance

**Version:** 0.1.0
**Date:** 2026-03-23
**Status:** Draft
**Audience:** Anthropic partner reviewers, enterprise developers evaluating the library

---

## Problem Statement

AI agent frameworks (CrewAI, LangGraph, Anthropic Agent SDK, OpenAI Agents SDK) provide orchestration but lack runtime governance primitives. Developers building multi-agent systems have no standardized way to:

- Halt agents in an emergency (graduated, not kill-9)
- Enforce budget ceilings before runaway spend
- Delegate capabilities with cryptographic proof
- Detect and recover from cascading adapter failures
- Maintain an immutable audit trail of governance decisions

Teams either build these from scratch (duplicating effort, introducing bugs) or skip them entirely (accepting risk). There is no pip-installable, framework-agnostic governance library.

## Target Users

| User | Pain Point |
|------|-----------|
| **OpenAI SDK developers** | No built-in cost controls or kill switch; agents can run up bills unchecked |
| **CrewAI / LangGraph teams** | Framework-specific solutions don't transfer; governance is ad-hoc |
| **Anthropic Agent SDK users** | Tool use needs scoped delegation; no standard for capability tokens |
| **Enterprise AI platform teams** | SOC2/GDPR compliance requires audit trails; building from scratch is expensive |
| **Solo builders / founders** | Need safety primitives without hiring a governance team |

## Product Positioning

**hummbl-governance is a governance runtime library, NOT a framework.**

It plugs into existing orchestration frameworks. It does not replace CrewAI, LangGraph, or any agent SDK. It provides the safety and compliance layer that those frameworks are missing.

```
Your Agent Framework (CrewAI, LangGraph, custom)
        │
        ▼
┌─────────────────────────────┐
│   hummbl-governance         │
│   ┌───────┐ ┌────────────┐ │
│   │Kill   │ │Circuit     │ │
│   │Switch │ │Breaker     │ │
│   ├───────┤ ├────────────┤ │
│   │Cost   │ │Delegation  │ │
│   │Governor│ │Tokens      │ │
│   ├───────┤ ├────────────┤ │
│   │Audit  │ │Agent       │ │
│   │Log    │ │Registry    │ │
│   ├───────┤              │ │
│   │Schema │              │ │
│   │Valid. │              │ │
│   └───────┘              │ │
└─────────────────────────────┘
        │
        ▼
   Python stdlib only
```

## Modules

| # | Module | One-Line Description |
|---|--------|---------------------|
| 1 | **KillSwitch** | Emergency halt with 4 graduated modes (DISENGAGED → HALT_NONCRITICAL → HALT_ALL → EMERGENCY) |
| 2 | **CircuitBreaker** | Automatic failure detection and recovery (CLOSED → OPEN → HALF_OPEN) wrapping external calls |
| 3 | **CostGovernor** | Budget tracking with soft/hard caps, per-provider spend, and ALLOW/WARN/DENY decisions |
| 4 | **DelegationToken** | HMAC-SHA256 signed capability tokens for scoped agent delegation with expiry and caveats |
| 5 | **AuditLog** | Append-only JSONL governance audit log with rotation, retention, and query API |
| 6 | **AgentRegistry** | Agent identity management with aliases, trust tiers, and deprecation tracking |
| 7 | **SchemaValidator** | Stdlib-only JSON Schema validator (Draft 2020-12 subset) for contract enforcement |

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| Zero third-party runtime dependencies | stdlib only | **Met** |
| Test coverage | 157+ tests | **Met** |
| pip-installable | `pip install hummbl-governance` | **Met** (local; PyPI pending) |
| Framework-agnostic | No imports from CrewAI, LangGraph, etc. | **Met** |
| Python version support | 3.11+ | **Met** |
| Thread-safe | All modules use locks | **Met** |
| Independent imports | Each module usable standalone | **Met** |

## Competitive Landscape

| | hummbl-governance | Microsoft Agent Governance Toolkit |
|---|---|---|
| **Approach** | Runtime library (pip install) | Azure-integrated toolkit |
| **Dependencies** | Zero (stdlib only) | Azure SDK, Azure AD |
| **Kill switch** | 4 graduated modes | Binary on/off |
| **Cost governance** | Built-in with SQLite | Delegates to Azure Cost Management |
| **Delegation** | HMAC-SHA256 tokens with caveats | Azure AD RBAC |
| **Audit** | Local JSONL with query API | Azure Monitor integration |
| **Framework lock-in** | None | Azure ecosystem |
| **Offline operation** | Full | Requires Azure connectivity |
| **License** | Apache 2.0 | MIT |

**Positioning difference:** hummbl-governance is portable and self-contained. Microsoft's toolkit requires Azure. For teams running on AWS, GCP, bare metal, or local development, hummbl-governance is the only option that works without cloud vendor lock-in.

## Non-Goals

- **Not an orchestration framework.** Use CrewAI, LangGraph, or Anthropic Agent SDK for agent coordination. hummbl-governance provides the safety layer underneath.
- **Not a SaaS platform.** This is a library you embed in your code. No hosted service, no API keys, no vendor dashboard.
- **Not a replacement for A2A.** Google's Agent-to-Agent protocol handles inter-agent communication. hummbl-governance handles what happens *within* each agent's governance boundary.
- **Not an observability platform.** The AuditLog provides compliance trails, not metrics dashboards. Pair with Prometheus/Grafana for operational monitoring.

---

*Copyright 2026 HUMMBL, LLC. Licensed under Apache 2.0.*
