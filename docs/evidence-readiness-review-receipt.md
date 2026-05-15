# Evidence Readiness Review Receipt

Status: Draft
Date: 2026-05-15

## Purpose

Map HUMMBL evidence-readiness packets to governance review receipts.

This is a review-control surface, not a legal-advice surface. It records whether
an evidence packet is safe to relay to the intended audience.

## Review Receipt Scope

Use this receipt for:

- attorney consult packets;
- relay-safe client summaries;
- counterargument premortems;
- claim verification tables;
- public-use case-study candidates derived from matter work.

Do not store raw confidential evidence in the receipt. Store hashes, paths,
review verdicts, and evidence references.

## Verdicts

| Verdict | Meaning |
|---|---|
| `APPROVE_FOR_RELAY` | No blocking defects; intended audience can receive |
| `APPROVE_WITH_P2` | Relay allowed; important non-blocking caveats remain |
| `BLOCKED_P1` | Relay blocked until significant defects are fixed |
| `BLOCKED_P0` | Relay blocked; breach/fabrication/data exposure or equivalent |

## Finding Severities

| Severity | Meaning |
|---|---|
| `P0` | Breach, fabrication, data exposure, or irreversible high-impact defect |
| `P1` | Factual error, scope breach, legal-boundary breach, or relay-blocking inconsistency |
| `P2` | Important ambiguity, missed edge case, or incomplete operationalization |
| `P3` | Style, clarity, or low-risk cleanup |

## Required Fields

```json
{
  "schema_version": "evidence-readiness-review-receipt.v0.1",
  "receipt_id": "uuid",
  "created_at": "2026-05-15T00:00:00Z",
  "matter_id": "hashed-or-local-id",
  "data_classification": "CLIENT_CONFIDENTIAL",
  "intended_audience": "attorney|client|operator|internal|public",
  "packet_paths": [
    "05_attorney_packet/consult-brief.md",
    "06_relay_safe/client-summary.md"
  ],
  "source_manifest_ref": {
    "path": "01_sources/manifest.md",
    "sha256": "hex"
  },
  "reviewer": {
    "id": "codex",
    "role": "critical_peer"
  },
  "verdict": "APPROVE_WITH_P2",
  "findings": [
    {
      "severity": "P2",
      "item": "Q14",
      "status": "OPEN",
      "summary": "Demand-letter floor remains under-operationalized"
    }
  ],
  "claim_honesty": {
    "unsupported_claims": 0,
    "interpretations_labeled": true,
    "legal_questions_reserved_for_counsel": true,
    "public_use_approved": false
  },
  "relay_decision": {
    "allowed": true,
    "conditions": [
      "Do not share with opposing-side actors"
    ]
  }
}
```

## Relationship To Existing EAL Receipts

The EAL receipt schema records deterministic action execution and integrity.
Evidence-readiness review receipts record human/agent review disposition.

Mapping:

| Evidence Readiness Field | EAL Analog |
|---|---|
| `receipt_id` | `execution_id` |
| `packet_paths` | `actions[].params_evidence_id` |
| `source_manifest_ref.sha256` | `evidence[].sha256` |
| `verdict` | `actions[].boundary_assertion.decision` plus review note |
| `findings` | evidence blob referenced by hash |
| `relay_decision.allowed` | boundary assertion |

Do not force these into the EAL schema until a compatibility decision is made.
For now, use this as an adapter spec.

## Claim-Honesty Checks

Before `APPROVE_FOR_RELAY` or `APPROVE_WITH_P2`, reviewer must verify:

- every material factual claim maps to a source;
- unsupported claims are removed or marked `UNKNOWN`;
- interpretations are labeled;
- legal advice is converted into questions for counsel;
- public claims have separate consent and approval;
- no confidential content appears in bus posts, public issues, PR bodies, or
  marketing drafts.

## Public-Use Gate

Set `public_use_approved` to `false` by default.

Public use requires:

1. recorded consent;
2. redaction or synthetic rewrite;
3. claim-honesty table;
4. operator/legal approval;
5. non-author review.

## Open Questions

- JSON schema draft now lives at
  `hummbl_governance/data/evidence_readiness_review_receipt.schema.json`.
- Should the verdict enum be shared with legal/paralegal repos?
- Should P0/P1 findings automatically trigger a bus-safe `BLOCKED` receipt with
  no confidential details?
- Should public-use approval be represented as a separate receipt type?
