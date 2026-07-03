---
name: Docs or claim correction
about: Report stale docs, unsupported claims, or missing receipts
title: "docs: "
labels: docs, claim-check, needs-triage
assignees: ""
---

## Claim Or Doc Surface

Link or quote the smallest relevant claim.

## Concern

- [ ] Stale version or support wording
- [ ] Missing receipt
- [ ] Overstated compliance/security/readiness wording
- [ ] Broken link
- [ ] Public/private boundary issue
- [ ] Other:

## Evidence

Attach current source, command output, CI run, release page, package metadata, or
other receipt.

## Proposed Resolution

- [ ] Add receipt
- [ ] Soften wording
- [ ] Mark planned/draft/source-candidate
- [ ] Remove claim
- [ ] Move private/internal content out of public docs

## Public / Private Boundary

- [ ] This issue contains no secrets, customer data, private operations, or unreleased strategy.

## Acceptance Criteria

- [ ] Claim status is updated in `docs/public-claims.md` when relevant.
- [ ] Public wording matches available receipts.
- [ ] Links and references are current.
