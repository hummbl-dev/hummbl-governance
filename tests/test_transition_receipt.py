from datetime import datetime, timezone

import pytest



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


def test_context_hash_distinguishes_absent_from_empty_context():
    absent_receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="search_docs",
        tool_input={"query": "x"},
    )
    empty_receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="search_docs",
        tool_input={"query": "x"},
        context={},
    )
    assert absent_receipt.context_hash != empty_receipt.context_hash


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
<<<<<<< HEAD


def test_signature_verification_fails_with_wrong_secret():
    receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="search_docs",
        tool_input={"query": "x"},
        signing_secret=b"secret",
    )

    assert verify_tool_transition_receipt(receipt, signing_secret=b"wrong-secret") is False
=======
>>>>>>> 607e0ce (feat(crewai): add tool transition receipts)
