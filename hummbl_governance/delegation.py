"""Delegation Token -- HMAC-SHA256 signed capability tokens for agent delegation.

Implements delegation capability tokens with cryptographic integrity,
expiry, binding to tasks/contracts, and least-privilege enforcement.

Usage:
    from hummbl_governance import DelegationToken, DelegationTokenManager
    from hummbl_governance.delegation import TokenBinding

    mgr = DelegationTokenManager(secret=b"my-secret")
    token = mgr.create_token(
        issuer="orchestrator",
        subject="worker-agent",
        ops_allowed=["read_data", "write_results"],
        binding=TokenBinding(task_id="task-1", contract_id="contract-1"),
    )

    valid, error = mgr.validate_token(token)

Stdlib-only. Zero third-party dependencies.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from hummbl_governance.errors import HummblError

logger = logging.getLogger(__name__)


try:
    from hummbl_library.governance.types import (
        Caveat,
        DelegationToken,
        ResourceSelector,
        TokenBinding,
    )
except ImportError:
    # Fallback for environments without hummbl-library installed

    @dataclass(frozen=True)
    class ResourceSelector:
        """Resource selector specifying accessible resources."""

        resource_type: str
        resource_id: str = "*"
        constraints: dict[str, Any] = field(default_factory=dict)

    @dataclass(frozen=True)
    class Caveat:
        """Caveat constraining capability use."""

        caveat_id: str
        type: Literal["TIME_BOUND", "RATE_LIMIT", "APPROVAL_REQUIRED", "AUDIT_REQUIRED"]
        parameters: dict[str, Any] = field(default_factory=dict)

    @dataclass(frozen=True)
    class TokenBinding:
        """Binding linking a token to a specific task and contract."""

        task_id: str
        contract_id: str

    @dataclass(frozen=True)
    class DelegationToken:
        """HMAC-SHA256 signed delegation capability token.

        Immutable after creation (frozen dataclass).
        """

        token_id: str
        issuer: str
        subject: str
        resource_selectors: tuple[ResourceSelector, ...] = field(default_factory=tuple)
        ops_allowed: tuple[str, ...] = field(default_factory=tuple)
        caveats: tuple[Caveat, ...] = field(default_factory=tuple)
        expiry: str | None = None
        binding: TokenBinding | None = None
        signature: str = ""

        def to_dict(self) -> dict[str, Any]:
            """Serialize token to dictionary (excluding signature for signing)."""
            return {
                "token_id": self.token_id,
                "issuer": self.issuer,
                "subject": self.subject,
                "resource_selectors": [
                    {
                        "resource_type": r.resource_type,
                        "resource_id": r.resource_id,
                        "constraints": r.constraints,
                    }
                    for r in self.resource_selectors
                ],
                "ops_allowed": list(self.ops_allowed),
                "caveats": [
                    {"caveat_id": c.caveat_id, "type": c.type, "parameters": c.parameters}
                    for c in self.caveats
                ],
                "expiry": self.expiry,
                "binding": (
                    {"task_id": self.binding.task_id, "contract_id": self.binding.contract_id}
                    if self.binding
                    else None
                ),
            }

        def verify_signature(self, secret: bytes) -> bool:
            """Verify HMAC-SHA256 signature matches token content."""
            expected = _compute_signature(self.to_dict(), secret)
            return hmac.compare_digest(self.signature, expected)

        def is_expired(self) -> bool:
            """Check if token has expired."""
            if self.expiry is None:
                return False
            try:
                expiry_dt = datetime.fromisoformat(self.expiry.replace("Z", "+00:00"))
                return datetime.now(timezone.utc) > expiry_dt
            except (ValueError, TypeError):
                return True

        def validate_binding(self, task_id: str, contract_id: str, subject: str) -> bool:
            """Validate token is bound to expected task/contract/subject."""
            if self.binding is None:
                return False
            return (
                self.binding.task_id == task_id
                and self.binding.contract_id == contract_id
                and self.subject == subject
            )


# Error code shorthands — resolved from the unified HummblError enum.
E_TOKEN_INVALID = HummblError.TOKEN_INVALID.value
E_TOKEN_EXPIRED = HummblError.TOKEN_EXPIRED.value
E_BINDING_MISMATCH = HummblError.BINDING_MISMATCH.value
E_DCT_VIOLATION = HummblError.DCT_VIOLATION.value


class DelegationTokenManager:
    """Manager for creating and validating delegation tokens.

    Args:
        secret: HMAC secret bytes. If None, reads from HUMMBL_SIGNING_SECRET
            or DCT_SECRET env vars, or generates an ephemeral key.
    """

    def __init__(self, secret: bytes | None = None):
        if secret is None:
            for var in ("HUMMBL_SIGNING_SECRET", "DCT_SECRET"):
                secret_str = os.environ.get(var)
                if secret_str:
                    secret = secret_str.encode("utf-8")
                    break
            if secret is None:
                logger.warning(
                    "No signing secret configured, using ephemeral key. "
                    "Tokens will be invalid after process restart."
                )
                secret = os.urandom(32)
        self._secret = secret

    def create_token(
        self,
        issuer: str,
        subject: str,
        ops_allowed: list[str],
        binding: TokenBinding,
        resource_selectors: list[ResourceSelector] | None = None,
        caveats: list[Caveat] | None = None,
        expiry_minutes: int | None = 120,
    ) -> DelegationToken:
        """Create a new signed delegation token.

        Args:
            issuer: Agent granting the capability.
            subject: Agent receiving the capability.
            ops_allowed: Permitted operations.
            binding: Task/contract binding.
            resource_selectors: Accessible resources (default: all).
            caveats: Constraints on use.
            expiry_minutes: Minutes until expiry (None = no expiry).

        Returns:
            Signed DelegationToken.
        """
        expiry = None
        if expiry_minutes is not None:
            expiry_dt = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            expiry = expiry_dt.isoformat().replace("+00:00", "Z")

        token = DelegationToken(
            token_id=str(uuid.uuid4()),
            issuer=issuer,
            subject=subject,
            resource_selectors=tuple(resource_selectors or []),
            ops_allowed=tuple(ops_allowed),
            caveats=tuple(caveats or []),
            expiry=expiry,
            binding=binding,
            signature="",
        )

        sig = _compute_signature(token.to_dict(), self._secret)

        return DelegationToken(
            token_id=token.token_id,
            issuer=token.issuer,
            subject=token.subject,
            resource_selectors=token.resource_selectors,
            ops_allowed=token.ops_allowed,
            caveats=token.caveats,
            expiry=token.expiry,
            binding=token.binding,
            signature=sig,
        )

    def validate_token(
        self,
        token: DelegationToken,
        expected_task_id: str | None = None,
        expected_contract_id: str | None = None,
        expected_subject: str | None = None,
    ) -> tuple[bool, str | None]:
        """Validate a delegation token.

        Returns:
            Tuple of (is_valid, error_code).
        """
        if not token.verify_signature(self._secret):
            return False, E_TOKEN_INVALID
        if token.is_expired():
            return False, E_TOKEN_EXPIRED
        if expected_task_id or expected_contract_id or expected_subject:
            return self._validate_binding(token, expected_task_id, expected_contract_id, expected_subject)
        return True, None

    @staticmethod
    def _validate_binding(
        token: DelegationToken,
        expected_task_id: str | None,
        expected_contract_id: str | None,
        expected_subject: str | None,
    ) -> tuple[bool, str | None]:
        """Validate token binding against expected values."""
        task_id = expected_task_id or (token.binding.task_id if token.binding else "")
        contract_id = expected_contract_id or (token.binding.contract_id if token.binding else "")
        subject = expected_subject or token.subject
        if not token.validate_binding(task_id, contract_id, subject):
            return False, E_BINDING_MISMATCH
        return True, None

    def check_least_privilege(
        self,
        token: DelegationToken,
        requested_op: str,
        allowed_tools: list[str] | None = None,
        denied_tools: list[str] | None = None,
    ) -> tuple[bool, str | None]:
        """Check if requested operation complies with least privilege.

        Returns:
            Tuple of (is_allowed, error_code).
        """
        if requested_op not in token.ops_allowed:
            return False, E_DCT_VIOLATION
        if allowed_tools is not None and requested_op not in allowed_tools:
            return False, E_DCT_VIOLATION
        if denied_tools is not None and requested_op in denied_tools:
            return False, E_DCT_VIOLATION
        return True, None


def _compute_signature(data: dict[str, Any], secret: bytes) -> str:
    """Compute HMAC-SHA256 signature for token data."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
