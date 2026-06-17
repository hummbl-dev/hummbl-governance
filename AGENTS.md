# AGENTS.md — hummbl-governance

## Project

**hummbl-governance** — AI governance frameworks, maturity models, and control catalogs. PyPI-published Python library (v1.1.0), 1032 tests, zero third-party runtime dependencies.

## Scope

- In scope: Governance primitives (Kernel [receipts, identity, roles, laws, evidence], kill switch, circuit breaker, cost governor, delegation tokens, audit log, identity registry, reasoning engine, execution assurance, physical-AI safety), MCP servers, JSON schema validation, compliance assessments (NIST, ISO, SOC 2, EU AI Act)
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

## CI

Runs on Gitea self-hosted Windows runner (`anvil-ci`). Workflow: `.gitea/workflows/ci.yml`
Python path: `C:\gitea\runner\toolcache\Python\3.13.13\x64`

## Communication

- Bus identity: `hummbl-governance`
- Canonical bus write: `python /c/Users/Owner/bin/bus-global.py post hummbl-governance <to> <type> "<message>"`

## Agent-specific context

- For Claude Code: see `CLAUDE.md`
- Published to PyPI: `pip install hummbl-governance`
- MCP servers expose 15 governance primitives as 32 JSON-RPC tools (v1.0.0)
