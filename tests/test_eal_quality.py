import pytest
from hummbl_governance.eal import evaluate_validation

def test_eal_validates_code_quality_success():
    contract = {
        "contract_id": "c1",
        "contract_hash": "h1",
        "action_space": ["act1"]
    }
    receipt = {
        "receipt_id": "r1",
        "contract_id": "c1",
        "contract_hash": "h1",
        "signature": {"status": "valid"},
        "evidence": [{}],
        "receipt_hash": "rh1",
        "actions": [{"action_id": "act1"}],
        "min_arbiter_score": 80.0,
        "actual_arbiter_score": 85.0
    }
    report = evaluate_validation(contract, receipt)
    assert report["classification"] == "VALID"
    assert "E_OK_VALID" in report["reason_codes"]

def test_eal_validates_code_quality_failure():
    contract = {
        "contract_id": "c1",
        "contract_hash": "h1",
        "action_space": ["act1"]
    }
    receipt = {
        "receipt_id": "r1",
        "contract_id": "c1",
        "contract_hash": "h1",
        "signature": {"status": "valid"},
        "evidence": [{}],
        "receipt_hash": "rh1",
        "actions": [{"action_id": "act1"}],
        "min_arbiter_score": 80.0,
        "actual_arbiter_score": 75.0
    }
    report = evaluate_validation(contract, receipt)
    assert report["classification"] == "INVALID"
    assert "E_CODE_QUALITY_FAIL" in report["reason_codes"]

def test_eal_handles_missing_quality_metadata():
    contract = {
        "contract_id": "c1",
        "contract_hash": "h1",
        "action_space": ["act1"]
    }
    receipt = {
        "receipt_id": "r1",
        "contract_id": "c1",
        "contract_hash": "h1",
        "signature": {"status": "valid"},
        "evidence": [{}],
        "receipt_hash": "rh1",
        "actions": [{"action_id": "act1"}]
    }
    report = evaluate_validation(contract, receipt)
    assert report["classification"] == "VALID"
