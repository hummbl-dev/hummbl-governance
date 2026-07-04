# AGENTS.md — hummbl-governance

## Project

**hummbl-governance** — AI governance frameworks, maturity models, and control catalogs. PyPI-published Python library (v1.2.0), current test inventory governed by `docs/TEST_COUNT_AUTHORITY.md`, zero third-party runtime dependencies.

## Scope

- In scope: Governance primitives (Kernel [receipts, identity, roles, laws, evidence, sequence, authority, schedule, doctrine] with K1-K11 invariants and D1-D7 doctrine invariants; rollback, recovery verifier, receipt integrity monitor, contestability, doctrine amendment, canon registry, authority sweeper, trust adjuster), kill switch, circuit breaker, cost governor, delegation tokens, audit log, identity registry, reasoning engine, execution assurance, physical-AI safety), MCP servers, JSON schema validation, compliance assessments (NIST, ISO, SOC 2, EU AI Act)
- Out of scope: Consumer app features, bus protocol changes, agent orchestration logic

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # bash
# .venv\Scripts\activate          # PowerShell
pip install -e ".[test]"
```

## Testing

```bash
python -m pytest tests/ -v --cov=hummbl_governance --cov-report=term --cov-fail-under=80
```

## Conventions

- Python 3.11+ required
- Zero third-party runtime dependencies (stdlib only in production code)
- Test dependencies in `[test]` extras only
- Thread-safe implementations throughout
- Apache 2.0 license
- Commit format: Conventional Commits
- Branch naming: `type/agent/short-desc`
- AI agents may assist with research, review, patch preparation, and operational coordination, but must not be credited in Git commit authorship metadata or commit-message trailers. Do not add `Co-authored-by`, `Generated-by`, `Authored-with`, or equivalent AI/vendor/agent attribution to commits. Agent activity belongs in internal receipts, bus messages, handoffs, or PR notes, not commit credit.

## CI

Runs on Gitea self-hosted Windows runner (`anvil-ci`). Workflow: `.gitea/workflows/ci.yml`
Python path: `C:\gitea\runner\toolcache\Python\3.13.13\x64`

## Communication

- Bus identity: `hummbl-governance`
- Canonical bus write: `python /c/Users/Owner/bin/bus-global.py post hummbl-governance <to> <type> "<message>"`

## Agent-specific context

- For Claude Code: see `CLAUDE.md`
- Published to PyPI: `pip install hummbl-governance`
- MCP servers expose governance primitives as JSON-RPC tools. Tool-count claims require a current inventory receipt before public promotion.
