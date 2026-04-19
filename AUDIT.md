# Repository Audit Report

**Date:** 2026-04-19
**Package:** hummbl-governance v0.4.0
**Python:** 3.11+
**Test suite:** 591 tests, all passing (2.61s)

---

## v0.4.0 Release Audit

The v0.4.0 release introduces major enhancements for physical-AI alignment and execution assurance.

### New Primitives
- **KinematicGovernor**: Enforces velocity, force, and jerk constraints.
- **pHRISafetyMonitor**: Graduated safety modes (NORMAL/CAUTION/EMERGENCY) based on human proximity and collision detection.

### Enhancements
- **Arbiter-Verified EAL**: `eal.py` now supports verifying receipts against Arbiter code quality scores (`E_CODE_QUALITY_FAIL`).
- **Reasoning Kernel**: Expanded support for systems thinking (S1) and recursive correction (RE1) prompts.

### Finding Resolutions
- **[RESOLVED] L2. No test coverage for reasoning.py**: v0.4.0 includes comprehensive tests for the reasoning engine.
- **[RESOLVED] H3. Inconsistent type hints in reasoning.py**: Synchronized with Python 3.11+ conventions.

---

## Executive Summary (Historical - v0.3.0)

The codebase is well-structured with strong fundamentals: zero runtime dependencies, consistent locking patterns, parameterized SQL queries, and comprehensive test coverage across 19 of 20 source modules. However, the audit identified **3 critical**, **5 high**, **7 medium**, and **4 low** severity findings across code, tests, and infrastructure.

---

## CRITICAL Findings

### C1. Deadlock risk in `audit_log.py:287-297`

`_append_async()` holds `_buffer_lock` (line 289) then calls `_flush_buffer()` (line 292), which acquires `_lock` and `_buffer_lock` together (line 297: `with self._lock, self._buffer_lock:`). If another thread holds `_lock` and waits for `_buffer_lock`, classic ABBA deadlock occurs.

**Fix:** Call `_flush_buffer()` outside the `_buffer_lock` context, or restructure to avoid nested acquisition.

### C2. Race condition in `contract_net.py:163-169`

`TaskAnnouncement` is created with `phase=ContractPhase.ANNOUNCED` (line 163), stored in the shared dict (line 168), then mutated to `BIDDING` (line 169) — all inside the lock. However, the object is mutable and the initial phase value is observable between creation and mutation if ever accessed outside the lock.

**Fix:** Initialize `phase` directly as `ContractPhase.BIDDING`, eliminating the mutation.

### C3. Potential lock-reentry in `audit_log.py:292`

When `_flush_buffer()` is called from within `_append_async()`, `_buffer_lock` is already held. Python's `threading.Lock` is non-reentrant — if `_flush_buffer()` attempts to re-acquire `_buffer_lock` (line 297), and the lock implementation evaluates left-to-right (`_lock` first, then `_buffer_lock`), the second `_buffer_lock` acquisition will deadlock on the same thread.

**Fix:** Use `threading.RLock` for `_buffer_lock`, or refactor to avoid re-acquisition.

---

## HIGH Findings

### H1. ReDoS vulnerability in `schema_validator.py:137-142`

User-supplied regex patterns in JSON schemas are compiled and executed via `re.search()` without timeout protection. Malicious patterns (e.g., `(a+)+b`) on crafted input can cause exponential CPU time.

**Fix:** Wrap `re.search()` with a timeout mechanism or limit pattern complexity.

### H2. PII regex false positives in `output_validator.py:50-58`

The phone number regex (`\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b`) matches arbitrary 10-digit sequences (dates, product codes). The credit card regex (`\b\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b`) has no Luhn check. Both cause legitimate agent output to be flagged as PII violations.

**Fix:** Add Luhn validation for credit cards; tighten phone regex with stricter prefix/format requirements.

### H3. Inconsistent type hints in `reasoning.py:13,34,37,43,48`

Uses legacy `Dict`, `Optional` from `typing` while the rest of the codebase uses Python 3.11+ builtins (`dict[str, Any]`, `str | None`). Inconsistent with project conventions.

**Fix:** Replace `Dict` with `dict`, `Optional[X]` with `X | None`.

### H4. `KillSwitchMode` KeyError on corrupt state file (`kill_switch.py:208`)

`KillSwitchMode[mode_str]` raises `KeyError` if the persisted mode string is invalid. While `KeyError` is caught on line 219, the error path is non-obvious and should be explicit.

**Fix:** Use a try/except or `.get()` pattern with a safe fallback and warning log.

### H5. Version mismatch across MCP servers

`pyproject.toml` and `__init__.py` declare version `0.3.0`, but all three MCP servers hardcode `SERVER_VERSION = "0.1.0"`:
- `mcp_server.py:59`
- `mcp_compliance.py:49`
- `mcp_sandbox.py:45`

**Fix:** Sync all `SERVER_VERSION` values to `0.3.0`.

---

## MEDIUM Findings

### M1. `object.__setattr__` on frozen dataclasses (`health_probe.py:57-63,98-104`)

`ProbeResult` and `HealthReport` are `frozen=True` dataclasses but use `object.__setattr__()` in `__post_init__` to mutate `timestamp` fields, defeating immutability guarantees.

**Fix:** Compute timestamps before construction, or use a factory function.

### M2. Negative Lamport clock values accepted (`lamport_clock.py:44-79`)

`LamportClock.__init__` and `receive()` accept negative integers without validation. Negative logical timestamps are semantically invalid and a malicious `remote_timestamp` can force arbitrary clock jumps.

**Fix:** Add `if initial < 0: raise ValueError(...)` and validate `remote_timestamp >= 0`.

### M3. TOCTOU in file collection (`compliance_mapper.py:77-97`)

`_collect_files()` globs governance JSONL files, then iterates over them. Files can be deleted between the glob and the read. The error is silently caught downstream, potentially missing governance records.

**Fix:** Catch `FileNotFoundError` explicitly per-file with a warning log.

### M4. Silent expiry parse failure in `delegation.py:118`

`DelegationToken.is_expired()` catches `ValueError` and `TypeError` and returns `True` (expired). This silently masks bugs where tokens are created with malformed timestamps.

**Fix:** Log a warning on parse failure before returning `True`.

### M5. SECURITY.md outdated

- Version table lists only `0.1.x` — project is at `0.3.0`
- Scope section lists "7 modules" — project now has 20+ primitives
- Contact email is personal (`reuben@hummbl.io`), not a dedicated security address

**Fix:** Update version table, module count, and consider a `security@hummbl.io` alias.

### M6. CORS wildcard in `api_server.py:98,110`

CORS headers set to `"*"` allows any origin. Acceptable for local dev but dangerous if deployed.

**Fix:** Document production deployment must restrict `Access-Control-Allow-Origin`, or make it configurable.

### M7. `arbiter_data.db` committed to git

A 64KB SQLite database is tracked in version control. `.gitignore` has `*.db` but the file was committed before the pattern was added.

**Fix:** `git rm --cached arbiter_data.db`

---

## LOW Findings

### L1. Nested `hummbl-governance/` directory artifact

A `hummbl-governance/` subdirectory exists inside the repo containing duplicate/stale files (LICENSE, README, SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, dependabot.yml, codeql.yml). Appears to be a merge artifact.

**Fix:** `git rm -r hummbl-governance/`

### L2. No test coverage for `reasoning.py`

`ReasoningEngine`, `ApplyResult`, and `Base120Model` have zero test coverage. This is the only source module without a corresponding test file.

**Fix:** Add `tests/test_reasoning.py` covering model loading, prompt generation, LLM output parsing, and error paths.

### L3. No test for `__init__.py` exports

The package exports 43 classes/enums/constants from `__init__.py`. No smoke test validates that all exports are importable and that `__all__` is accurate.

**Fix:** Add a smoke test that iterates `__all__` and verifies each symbol is importable.

### L4. Flaky timing-dependent tests

Several tests rely on `time.sleep()` with tight margins:
- `test_circuit_breaker.py::test_half_open_after_timeout` — 20ms sleep after 10ms timeout
- `test_contract_net.py::test_expired_announcement` — `deadline_seconds=0.0`
- `test_compliance_mapper.py` — midnight-UTC boundary sensitivity

**Fix:** Mock `time.time()` or use deterministic clock fixtures.

---

## Infrastructure Summary

| Component | Status | Notes |
|-----------|--------|-------|
| pyproject.toml | Good | Correct packaging, zero deps verified |
| CI (ci.yml) | Good | Missing explicit `permissions:` block |
| .gitignore | Good | Comprehensive patterns |
| dependabot.yml | Good | pip + actions, properly scoped |
| CONTRIBUTING.md | Good | Accurate setup instructions |
| SECURITY.md | Outdated | See M5 |
| Python servers | Secure | No injection/RCE vectors; parameterized queries |
| Examples | Good | Correct imports, safe patterns |

## Test Suite Summary

| Metric | Value |
|--------|-------|
| Total tests | 476 |
| Pass rate | 100% |
| Runtime | 0.81s |
| Modules tested | 19/20 (missing: reasoning.py) |
| Flaky risk | Low (3 timing-dependent tests) |

## Conventions Compliance

| Convention | Status |
|------------|--------|
| Python 3.11+ | Pass |
| Zero runtime deps | Pass (verified: `dependencies = []`) |
| Stdlib only | Pass (no third-party imports in hummbl_governance/) |
| Thread-safe | Mostly pass (see C1, C2, C3) |
| Apache 2.0 | Pass |

---

## Recommended Priority

1. **Immediate:** C1/C3 (deadlock in audit_log), C2 (contract_net race)
2. **High:** H1 (ReDoS), H5 (version sync), M7 (remove db from git), L1 (remove nested dir)
3. **Medium:** H2-H4, M1-M6
4. **Low:** L2-L4 (test coverage gaps, flaky tests)
