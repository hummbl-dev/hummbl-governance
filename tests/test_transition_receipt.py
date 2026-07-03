from datetime import datetime, timezone

from hummbl_governance import (
    CostGovernor,
    build_tool_transition_receipt,
    verify_tool_transition_receipt,
)
from hummbl_governance.transition_receipt import stable_sha256


def test_stable_sha256_is_order_independent():
    left = {"b": 2, "a": {"z": 3, "y": 4}}
    right = {"a": {"y": 4, "z": 3}, "b": 2}
    assert stable_sha256(left) == stable_sha256(right)


def test_stable_sha256_sorts_sets():
    left = {"tools": {"search", "write", "read"}}
    right = {"tools": {"read", "search", "write"}}
    assert stable_sha256(left) == stable_sha256(right)


def test_stable_sha256_rejects_non_string_dict_keys():
    try:
        stable_sha256({1: "numeric", "1": "string"})
    except TypeError as exc:
        assert "dict keys must be strings" in str(exc)
    else:
        raise AssertionError("non-string dict key should be rejected")


def test_stable_sha256_rejects_non_finite_float():
    try:
        stable_sha256({"cost": float("nan")})
    except ValueError as exc:
        assert "Non-finite floats" in str(exc)
    else:
        raise AssertionError("non-finite float should be rejected")


def test_context_hash_preserves_falsey_values():
    false_receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="search_docs",
        tool_input={"query": "x"},
        context=False,
    )
    empty_receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="search_docs",
        tool_input={"query": "x"},
        context={},
    )
    assert false_receipt.context_hash != empty_receipt.context_hash


def test_to_dict_does_not_expose_live_mutable_support_basis():
    receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="search_docs",
        tool_input={"query": "x"},
        budget_status={"decision": "ALLOW", "rationale": "ok"},
    )
    data = receipt.to_dict()
    data["support_basis"]["budget"]["decision"] = "DENY"
    assert receipt.to_dict()["support_basis"]["budget"]["decision"] == "ALLOW"


def test_build_allow_receipt_with_signature():
    receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="search_docs",
        tool_input={"query": "CrewAI governance"},
        context={"task": "research"},
        signing_secret=b"secret",
        timestamp=datetime(2026, 7, 2, tzinfo=timezone.utc),
    )

    assert receipt.decision == "ALLOW"
    assert receipt.action_hash.startswith("sha256:")
    assert receipt.context_hash.startswith("sha256:")
    assert receipt.decision_hash.startswith("sha256:")
    assert receipt.signature is not None
    assert verify_tool_transition_receipt(receipt, signing_secret=b"secret") is True


def test_kill_switch_denial_becomes_hard_block():
    receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="delete_record",
        tool_input={"record_id": "cust-123"},
        kill_switch_result={
            "allowed": False,
            "action": "block",
            "reason": "Kill switch engaged (HALT_ALL): delete_record blocked",
        },
    )

    assert receipt.decision == "HARD_BLOCK"
    assert "Kill switch engaged" in receipt.reason
    assert verify_tool_transition_receipt(receipt) is True


def test_budget_deny_becomes_hard_block():
    gov = CostGovernor(":memory:", soft_cap=1.0, hard_cap=2.0)
    gov.record_usage("openai", "gpt-4", 100, 50, 3.0)

    receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="expensive_llm_tool",
        tool_input={"prompt": "continue"},
        budget_status=gov.check_budget_status(),
    )

    assert receipt.decision == "HARD_BLOCK"
    assert "hard cap" in receipt.reason


def test_tampering_breaks_verification():
    receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="search_docs",
        tool_input={"query": "x"},
        signing_secret=b"secret",
    )
    data = receipt.to_dict()
    data["decision"] = "HARD_BLOCK"

    assert verify_tool_transition_receipt(data, signing_secret=b"secret") is False
