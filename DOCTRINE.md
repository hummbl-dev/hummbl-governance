# DOCTRINE.md - hummbl-governance

**Status:** v0.1
**Steward:** HUMMBL Research Institute

## 1. Thesis

hummbl-governance is the canonical governance runtime for AI agent
orchestration: 26 primitives -- kill switch, circuit breaker, cost governor,
delegation tokens, audit log, identity registry, schema validator, reasoning
engine, execution assurance, physical-AI safety, and a governance Kernel
(receipts, identity, roles, laws, evidence). The core bet is that safe agent
orchestration is a library problem, not a platform problem: the primitives
should be stdlib-only, dependency-free, and embeddable in any Python runtime.

Every primitive here was proven in founder-mode's daily production before
extraction. The library is not theoretical; it is the hardened output of
running ten agents under real load and extracting what kept them from causing
harm. Zero third-party dependencies and 1,288 tests mean the runtime can be
audited line-by-line and will not break from upstream changes.

The governance Kernel is the spine: receipts, identity, roles, laws, and
evidence form a coherent substrate on which the operational primitives (kill
switch, circuit breaker, etc.) are built, so that every action is authorized,
attributed, and reconstructable.

## 2. Conceptual vocabulary

- **Governance Kernel** -- the spine of receipts, identity, roles, laws, and
  evidence on which operational primitives are built.
- **Kill switch** -- a multi-mode halt (DISENGAGED through EMERGENCY) with
  HMAC-signed state, stoppable mid-flight.
- **Circuit breaker** -- a three-state (CLOSED, HALF_OPEN, OPEN) wrapper for
  external adapters that fast-fails when a dependency is down.
- **Cost governor** -- per-agent and per-session budget tracking with
  automatic halt at a ceiling.
- **Delegation token** -- an HMAC-SHA256 signed capability token carrying
  scope, expiry, and chain-depth.
- **Audit log** -- the append-only, tamper-evident record of all governed
  actions, mapped to compliance frameworks (SOC2, GDPR, NIST).
- **Failure mode** -- a member of the FM1-FM30 taxonomy migrated from Base120,
  representing named, versioned error classes.

## 3. Design principles

1. **Stdlib-only, zero dependencies.** The library runs on Python 3.11-3.14
   with no third-party runtime deps, so it is auditable and supply-chain-safe.
2. **Proven before shipped.** Primitives are extracted from founder-mode only
   after surviving daily production load.
3. **Kernel-first.** Operational primitives build on the governance Kernel
   (receipts, identity, roles, laws, evidence), not alongside it.
4. **Tamper-evident by default.** Audit logs and kill-switch state are
   HMAC-signed; provenance is cryptographic, not conventional.
5. **Fast-fail, never hang.** Circuit breakers and cost governors ensure the
   system degrades gracefully rather than blocking indefinitely.
6. **Compliance-mappable.** Governed actions map to SOC2, GDPR, and NIST
   controls so audit output is directly usable.

## 4. Boundaries

hummbl-governance provides the primitives and Kernel; it is not an orchestration
platform, does not run agents, and does not choose which agent executes a task
-- that is hummbl-agent's control plane. It does not define mental models or
reasoning operators (that is Base120), though it consumes the failure-mode
taxonomy migrated from it. It is Python-only; TypeScript consumers integrate
via hummbl-agent's governance gateway, not by importing this library directly.
It does not persist cognitive memory or ledgers of reasoning; it logs governed
*actions*. It is not a compliance product; it produces evidence that a
compliance process consumes.

## 5. Open questions

- How should the governance Kernel handle distributed (multi-process) identity
  and receipt signing without a central authority?
- As the primitive count grows beyond 26, should the library split into
  core-governance and domain-specific extensions?
- What is the right boundary between execution assurance and physical-AI safety
  as HUMMBL expands into embodied systems?
- How can compliance mapping stay current as SOC2, GDPR, and NIST frameworks
  evolve?
- Should delegation tokens support revocation cascades, and at what performance
  cost for high-frequency agent fleets?
