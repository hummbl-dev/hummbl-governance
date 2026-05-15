import json
from pathlib import Path

from hummbl_governance.schema_validator import SchemaValidator


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "hummbl_governance"
    / "data"
    / "evidence_readiness_review_receipt.schema.json"
)


def _valid_receipt():
    return {
        "schema_version": "evidence-readiness-review-receipt.v0.1",
        "receipt_id": "synthetic-review-001",
        "created_at": "2026-05-15T11:00:00Z",
        "matter_id": "synthetic-employment-separation",
        "data_classification": "PUBLIC_SYNTHETIC",
        "intended_audience": "client",
        "packet_paths": [
            "06_relay_safe/client-summary.md",
            "99_audit/review-receipt.md",
        ],
        "source_manifest_ref": {
            "path": "01_sources/manifest.md",
            "sha256": "a" * 64,
        },
        "reviewer": {
            "id": "codex",
            "role": "critical_peer",
        },
        "verdict": "APPROVE_WITH_P2",
        "findings": [
            {
                "severity": "P2",
                "item": "signing-bonus note",
                "status": "OPEN",
                "summary": "Counsel should evaluate favorable and adverse readings.",
            }
        ],
        "claim_honesty": {
            "unsupported_claims": 0,
            "interpretations_labeled": True,
            "legal_questions_reserved_for_counsel": True,
            "public_use_approved": False,
        },
        "relay_decision": {
            "allowed": True,
            "conditions": ["Do not share with opposing-side actors."],
        },
    }


def test_evidence_readiness_review_receipt_schema_accepts_valid_receipt():
    schema = json.loads(SCHEMA_PATH.read_text())

    valid, errors = SchemaValidator.validate_dict(_valid_receipt(), schema)

    assert valid is True
    assert errors == []


def test_evidence_readiness_review_receipt_schema_rejects_bad_verdict():
    schema = json.loads(SCHEMA_PATH.read_text())
    receipt = _valid_receipt()
    receipt["verdict"] = "APPROVE"

    valid, errors = SchemaValidator.validate_dict(receipt, schema)

    assert valid is False
    assert errors
