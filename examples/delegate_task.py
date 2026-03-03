#!/usr/bin/env python3
"""Delegation Token: Create and verify a signed capability token.

Demonstrates HMAC-SHA256 signed tokens for agent-to-agent delegation
with least-privilege enforcement.
"""

from hummbl_governance import (
    DelegationToken,
    ResourceSelector,
    Caveat,
    TokenBinding,
    create_token,
    validate_token,
)

# Create a token: agent-orchestrator delegates to agent-worker
token = create_token(
    issuer="agent-orchestrator",
    subject="agent-worker",
    resource_selectors=[ResourceSelector(resource_type="file", pattern="/data/*.csv")],
    ops_allowed=["read", "summarize"],
    caveats=[Caveat(caveat_type="TIME_BOUND")],
    binding=TokenBinding(task_id="task-001", contract_id="contract-001"),
)

print(f"Token ID:  {token.token_id}")
print(f"Issuer:    {token.issuer}")
print(f"Subject:   {token.subject}")
print(f"Ops:       {token.ops_allowed}")
print(f"Signed:    {token.signature[:16]}...")

# Verify the token
result = validate_token(token)
print(f"Valid:     {result}")
