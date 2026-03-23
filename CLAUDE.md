# CLAUDE.md

## Project

**hummbl-governance** -- Governance primitives for AI agent orchestration.

Standalone Python package extracted from founder-mode. Provides kill switch, circuit breaker, cost governor, delegation tokens, audit log, identity registry, and JSON schema validation.

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
python -m pytest tests/ -v
```

## Key Conventions

- Python 3.11+ required
- Zero third-party runtime dependencies (stdlib only)
- Test dependencies (pytest) in `[test]` extras only
- All modules independently importable from `hummbl_governance`
- Thread-safe implementations throughout
- Apache 2.0 license
