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
=======
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


def test_to_dict_does_not_expose_live_mutable_support_basis():
    receipt = build_tool_transition_receipt(
>>>>>>> c8e0c7e (fix(crewai): harden transition receipt review gaps)
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


def test_budget_warn_remains_allow_with_support_basis():
    receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="moderate_llm_tool",
        tool_input={"prompt": "continue"},
        budget_status={"decision": "WARN", "rationale": "soft cap exceeded"},
    )

    assert receipt.decision == "ALLOW"
    assert receipt.support_basis["budget"]["decision"] == "WARN"
    assert receipt.support_basis["budget"]["rationale"] == "soft cap exceeded"


def test_non_mapping_budget_status_is_preserved_without_decision_crash():
    receipt = build_tool_transition_receipt(
        agent_id="researcher",
        tool_name="custom_budget_tool",
        tool_input={"prompt": "continue"},
        budget_status=["WARN", "soft cap exceeded"],
    )

    assert receipt.decision == "ALLOW"
    assert receipt.support_basis["budget"]["value"] == ("WARN", "soft cap exceeded")


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
<<<<<<< HEAD
=======
>>>>>>> c8e0c7e (fix(crewai): harden transition receipt review gaps)
