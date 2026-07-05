# CONSTITUTION.md — hummbl-governance

**Status:** v0.1
**Steward:** HUMMBL Research Institute
**Approving human:** Reuben Bowlby
**Standard:** HUMMBL Repo Standard v0.1
**Source of record:** git

## 1. Identity

`hummbl-dev/hummbl-governance` — AI governance frameworks, maturity models, and control catalogs. PyPI-published Python library (v1.2.0), 34 implemented primitives, zero third-party runtime dependencies. Ships 7 MCP servers exposing all primitives as JSON-RPC tools. Test count governed by `docs/TEST_COUNT_AUTHORITY.md`; verify with `python -m pytest --collect-only -q tests`.

- **Class:** library
- **Visibility:** public
- **License:** Apache-2.0
- **Validation:** `python -m pytest tests/ -v --cov=hummbl_governance --cov-report=term --cov-fail-under=80`

## 2. Scope

This constitution operates under the HUMMBL Repo Standard (`hummbl-dev/hummbl-governance/docs/standards/HUMMBL_REPO_STANDARD.md`) and the operating-environment constitution on the host machine. This constitution may be stricter than both, never weaker.

## 3. Protected invariants

These invariants are constitutionally protected. They cannot be changed, weakened, or conditionally suspended without a constitutional amendment (§7), a KRINEIA receipt, and human approval.

1. **Zero third-party runtime dependencies.** The runtime dependency set is empty. All modules use Python stdlib only. Test dependencies (pytest, pytest-cov) in `[test]` extras only. Adding a third-party runtime dependency is a constitutional violation.
2. **Coverage floor.** pytest-cov `fail_under` is 80. The floor may be raised but never lowered without a constitutional amendment. Coverage configuration lives in `pyproject.toml` only.
3. **Thread-safe implementations.** All modules are independently importable and thread-safe. Breaking thread safety is a violation.
4. **MCP tool contract.** The 7 MCP servers and their tool names, argument shapes, and response envelopes are a public contract. Breaking changes require a major version bump.
5. **Apache-2.0 license.** The license is Apache-2.0, unchanged. No proprietary license may be introduced.
6. **Receipt integrity.** The Krineia chain (`_receipts/krineia/primary.jsonl`) is append-only and SHA-256-chained. No operator may rewrite history except via the documented `cut` operator.
7. **Schema stability.** JSON Schema definitions under `schemas/` are versioned. Breaking changes require a major version bump and a migration plan.
8. **Canonical standard host.** This repo is the canonical host of the HUMMBL Repo Standard. The standard document (`docs/standards/HUMMBL_REPO_STANDARD.md`) and its schema (`schemas/hummbl-repo-manifest.schema.json`) are normative. Edits require steward review.

## 4. Normative files

The following files are normative. Edits require steward review (see `CODEOWNERS`):

- `CONSTITUTION.md`
- `KRINEIA.md`
- `hummbl.repo.yaml`
- `CODEOWNERS`
- `docs/standards/HUMMBL_REPO_STANDARD.md`
- `schemas/hummbl-repo-manifest.schema.json`
- `docs/adr/`
- `AGENTS.md`

## 5. Authority

- **Steward:** HUMMBL Research Institute
- **Approving human:** Reuben Bowlby
- **Codeowners:** `CODEOWNERS`
- **Agent operating contract:** `AGENTS.md`
- **Receipt manifest:** `KRINEIA.md`

## 6. Receipt-triggering changes

The following changes require a KRINEIA receipt before admission:

- Any edit to `CONSTITUTION.md`, `KRINEIA.md`, `hummbl.repo.yaml`, or `CODEOWNERS`
- Any change to a protected invariant (Section 3)
- Any change to `docs/standards/HUMMBL_REPO_STANDARD.md` or `schemas/hummbl-repo-manifest.schema.json`
- Any change to the MCP tool contract (tool names, argument or response shapes)
- Any change to coverage floor or CI enforcement
- Any release or version bump
- Any change to `pyproject.toml` that alters the dependency contract

## 7. Amendment

Changes to this constitution require: a PR, an ADR under `docs/adr/`, a KRINEIA receipt, and human approval (Reuben Bowlby). Breaking changes bump this constitution's version (SemVer) and trigger a fleet re-audit of all repos consuming this repo's outputs.
