# Contributing

Thank you for your interest in contributing to hummbl-governance.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

## Development

- Python 3.11+ required
- Zero runtime dependencies (stdlib only)
- Run tests: `python -m pytest tests/ -v`
- Run linter: `ruff check .`
- Commit format: [Conventional Commits](https://www.conventionalcommits.org/)

## Pull Requests

- All PRs require passing tests
- Maintain zero third-party runtime dependencies
- Add tests for new functionality
- Keep modules independently importable

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting with a line length of 120. Run `make lint` (or `ruff check .`) before submitting.

## Test File Conventions

- Only `import pytest` if you are using pytest fixtures, marks (`@pytest.mark.*`), or `pytest.raises` / `pytest.warns`. Plain assertion-based tests need no pytest import.
- Only import stdlib modules if they are referenced in the test body.
- Unused imports are caught by ruff (F401) and will fail the lint gate.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 license.
