# Repository Health Contract

## Identity

- **Repository**: `hummbl-dev/hummbl-governance`
- **Canonical URL**: `https://github.com/hummbl-dev/hummbl-governance`
- **Package**: `hummbl-governance`
- **Owner**: HUMMBL Team
- **Stewardship scope**: Zero-runtime-dependency governance primitives for AI agent orchestration, including safety, cost, identity, compliance, reasoning, coordination, physical-AI, and audit logging.

## Lifecycle

- **Status**: Active public repository and PyPI package.
- **Default branch**: `main`.
- **Current package version**: `0.8.0`.
- **Release posture**: Runtime primitives, MCP entry points, compliance mappers, and conformance fixtures may continue through reviewed pull requests.
- **Archive trigger**: Archive only if the governance primitive package is superseded by another declared canonical source of truth and PyPI ownership is updated or retired.

## Source Of Truth

- `pyproject.toml` defines package metadata, supported Python versions, runtime dependency policy, test extras, and CLI entry points.
- `hummbl_governance/` contains the importable runtime package and all shipped primitives.
- `tests/` contains the validation suite for primitives, MCP handlers, conformance fixtures, compliance mappings, and failure modes.
- `docs/*-mapping.md` records compliance mapping surfaces for SOC2, GDPR, ISO 27001, NIST CSF, NIST AI RMF, and OWASP.
- `docs/trackers/` records open governance documentation parity, unverified claims, schema freeze, and evidence provenance work.
- `README.md` is the public package overview and should not overclaim test counts, primitive counts, or framework coverage beyond current code and CI evidence.

## Required Local Validation

Before merging non-trivial code or contract changes:

```bash
python -m pip install -e ".[test]"
python -m pytest tests/ -v --cov=hummbl_governance --cov-report=term --cov-fail-under=80
ruff check .
```

Documentation-only changes should at minimum pass:

```bash
git diff --check
```

## CI Expectations

Expected GitHub Actions coverage:

- `.github/workflows/ci.yml` runs the test suite with coverage threshold 80 across Ubuntu, macOS, and Windows on Python 3.11, 3.12, and 3.13.
- `.github/workflows/ci.yml` runs clean install smoke tests from PyPI across Ubuntu, macOS, and Windows on Python 3.11, 3.12, and 3.13.
- `.github/workflows/ci.yml` verifies zero third-party runtime dependencies for the published package.
- `.github/workflows/ci.yml` runs `ruff check .`.
- `.github/workflows/ci.yml` runs an Arbiter governance score gate with a 90.0 minimum.

## Branch Protection Expectation

`main` should require pull request review and the hosted CI checks that protect package correctness, installability, linting, zero-runtime-dependency posture, and Arbiter governance score.

Branch protection is tracked centrally in `hummbl-dev/hummbl-dev#18`; do not overclaim required checks until that audit is updated.

## Operational Notes

- Core runtime code must remain stdlib-only; third-party packages belong in optional test or tooling extras unless explicitly approved.
- Breaking primitive contracts, CLI entry points, or public package metadata require SemVer review.
- Public compliance and OWASP coverage claims must stay aligned with code, tests, docs, and evidence trackers.
- Conformance fixture changes should preserve deterministic validation and include clear acceptance criteria.

## Fleet Scan Classification

Future fleet scans can classify this repository as:

- **Lifecycle**: active public package
- **Visibility**: public
- **Primary function**: AI governance primitive library
- **Validation entrypoint**: `pytest` with coverage threshold 80
- **Primary metadata owner**: HUMMBL Team
