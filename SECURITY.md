# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.8.x   | Yes       |
| < 0.8   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in hummbl-governance, please report it responsibly:

1. **Email:** reuben@hummbl.io
2. **Do NOT** open a public GitHub issue for security vulnerabilities
3. Include: description of the vulnerability, steps to reproduce, and potential impact
4. You can expect an initial response within 48 hours

## Scope

This policy covers the `hummbl_governance` Python package and its 25 governance
primitives covering safety, cost, identity, compliance, reasoning, coordination,
physical-AI, and execution assurance. Full primitive inventory in the project
README and `PRIMITIVES.md`.

## Audit-log signature semantics

The `AuditLog.append()` method requires a non-empty `signature` field on each
entry by default (`require_signature=True`) but does NOT cryptographically
verify the signature against the entry body — the field is presence-checked,
not HMAC-verified. Tamper detection on the audit log is the responsibility of
an external verifier; entries are an append-only attestation record, not a
self-verifying cryptographic chain. See `hummbl_governance/audit_log.py` and
`tests/test_audit_log.py` for current behavior. HMAC-verified append is
tracked as a roadmap item.
