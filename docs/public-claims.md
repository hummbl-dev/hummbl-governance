# Public Claims

Status: public claim ledger
Last updated: 2026-07-03
Current package metadata: `pyproject.toml` version `1.2.0`

This ledger keeps public claims evidence-backed. A claim should be promoted
only when its status is `verified` or when it is explicitly framed as planned,
draft, pending, or source-candidate.

## Claim Status Table

| Claim | Status | Receipt | Promotion rule |
|---|---|---|---|
| Package version is `1.2.0` | verified | `pyproject.toml` declares `version = "1.2.0"` | May be stated as package metadata. |
| Runtime dependencies are zero | verified | `pyproject.toml` has `dependencies = []` | May be stated as zero third-party runtime dependencies. |
| CI tests Python 3.11, 3.12, and 3.13 | verified | `.github/workflows/ci.yml` matrix includes 3.11, 3.12, 3.13 | May be stated as CI-tested on 3.11-3.13. |
| Python 3.14 is supported | not verified | CI matrix and `pyproject.toml` classifiers do not include 3.14 at this audit | Do not claim support until CI includes 3.14 and passes. |
| Current local test inventory is 1970 collected tests | verified-locally | `python -m pytest --collect-only -q` on 2026-07-03 collected 1970 tests from the working tree based on `1a5a2e18ea0fb2fa9ef0bd64badc291784b2a073` | May be stated as local collection evidence. |
| Current local functional test suite passes without coverage enforcement | verified-locally | `python -m pytest tests/ -q --no-cov` on 2026-07-03 passed 1970 tests on the local working tree later committed as `42215e6c8b878a9b1b68053a551173d3e8700130` | May be stated with the exact command, commit, and local scope. |
| Current coverage-enforced test command passes | verified-locally | `python -m pytest tests/ -q --cov=hummbl_governance --cov-report=term --cov-fail-under=80` on 2026-07-03 passed 1970 tests with 82.61% total coverage on the local working tree later committed as `42215e6c8b878a9b1b68053a551173d3e8700130` | May be stated with the exact command, commit, and local scope. |
| 34 implemented governance primitives exist | verified | `PRIMITIVES.md` lists 26 existing primitives and 8 implemented expansion primitives | May be stated as implemented package primitive inventory. |
| 7 MCP server entry points exist | verified | `pyproject.toml` `[project.scripts]` lists 7 `*-mcp` entry points | May be stated as entry-point inventory. Tool counts require a separate receipt. |
| Production-tested / runs daily in production | needs receipt | No production operations receipt captured in this pass | Do not use for promotion until receipt exists. |
| Extracted from founder-mode with 15,600+ tests and 14 CI workflows | needs receipt | Depends on another repo and current live state | Do not use for promotion until independently verified. |
| OWASP Top 10 for Agentic Applications engineering mapping | source-candidate | README has an engineering mapping; no third-party attestation | Phrase as engineering mapping, not certification or coverage guarantee. |
| SOC2/GDPR/NIST/EU AI Act mappings | source-candidate | Coverage docs exist, but validation state varies | Phrase as evidence mapping support, not compliance certification. |

## Required Receipts Before Promotion

- Full coverage-enforced test pass receipt for the target commit.
- Build and wheel install smoke receipt.
- Link check for README and public docs.
- Secret scan with allowlisted fixture/demo patterns.
- GitHub settings receipt for description, topics, homepage, Issues,
  Discussions, Pages, Wiki, branch protection, and security features.
- PyPI page receipt for current version, project URLs, classifiers, and trusted
  publishing posture.
- Claim inventory receipt for README, package metadata, and release docs.

## Wording Rules

- Use "CI-tested on Python 3.11 through 3.13" only while the CI matrix excludes
  Python 3.14. Do not include a Python 3.14 classifier until CI covers it.
- Use "engineering mapping" for framework tables unless a third-party
  attestation exists.
- Use "zero third-party runtime dependencies" only for package runtime deps;
  test and tooling extras may still use third-party packages.
- Do not use production, customer, benchmark, or extraction claims without a
  current receipt.
