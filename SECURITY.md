# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.1.x   | Yes                |
| 1.0.x   | Yes (security fixes only) |
| < 1.0   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability in hummbl-governance, please report it responsibly:

1. **Email:** reuben@hummbl.io
2. **Do NOT** open a public GitHub issue for security vulnerabilities
3. Include: description of the vulnerability, steps to reproduce, and potential impact
4. You can expect an initial response within 48 hours

## Scope

This policy covers the `hummbl_governance` Python package (v1.1.0) and its 26
governance primitives covering safety, cost, identity, compliance, reasoning,
coordination, physical-AI, execution assurance, and the governance Kernel.
Full primitive inventory in the project README and `PRIMITIVES.md`.

The package supports Python 3.11 through 3.14 (per `pyproject.toml` classifiers).
CI-tested on Python 3.11, 3.12, and 3.13 (GitHub Actions matrix); Python 3.14
is classified but not yet CI-tested. The test suite comprises 1168 tests.

## Audit-log signature semantics

The `AuditLog.append()` method requires a non-empty `signature` field on each
entry by default (`require_signature=True`) but does NOT cryptographically
verify the signature against the entry body — the field is presence-checked,
not HMAC-verified. Tamper detection on the audit log is the responsibility of
an external verifier; entries are an append-only attestation record, not a
self-verifying cryptographic chain. See `hummbl_governance/audit_log.py` and
`tests/test_audit_log.py` for current behavior. HMAC-verified append is
tracked as a roadmap item (see [ROADMAP.md](ROADMAP.md) or open an issue at [github.com/hummbl-dev/hummbl-governance/issues](https://github.com/hummbl-dev/hummbl-governance/issues)).
