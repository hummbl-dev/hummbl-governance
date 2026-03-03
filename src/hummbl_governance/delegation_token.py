"""Delegation Capability Token (DCT) -- HMAC-SHA256 signed capability tokens.

Implements signed Delegation Capability Tokens for agent-to-agent delegation
with least-privilege enforcement. All operations are stdlib-only and
feature-flagged behind the ENABLE_IDP environment variable.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

logger = logging.getLogger(__name__)


def _is_idp_enabled() -> bool:
    """Check if IDP feature flag is enabled (runtime check)."""
    return os.environ.get("ENABLE_IDP", "true").lower() == "true"


# Error codes
IDP_E_DCT_VIOLATION = "IDP_E_DCT_VIOLATION"
IDP_E_TOKEN_EXPIRED = "IDP_E_TOKEN_EXPIRED"
IDP_E_TOKEN_INVALID = "IDP_E_TOKEN_INVALID"
IDP_E_BINDING_MISMATCH = "IDP_E_BINDING_MISMATCH"


@dataclass(frozen=True)
class ResourceSelector:
    """Resource selector specifying accessible resources.

    Attributes:
        resource_type: Type of resource (e.g., "file", "database").
        resource_id: Specific resource ID, or "*" for wildcard.
        constraints: Additional constraints on access.
    """

    resource_type: str
    resource_id: str = "*"
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Caveat:
    """Caveat constraining token capability use.

    Attributes:
        caveat_id: Unique identifier for this caveat.
        type: Caveat type (TIME_BOUND, RATE_LIMIT, APPROVAL_REQUIRED, AUDIT_REQUIRED).
        parameters: Type-specific parameters.
    """

    caveat_id: str
    type: Literal["TIME_BOUND", "RATE_LIMIT", "APPROVAL_REQUIRED", "AUDIT_REQUIRED"]
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TokenBinding:
    """Binding linking a token to a specific task and contract.

    Attributes:
        task_id: Task this token is bound to.
        contract_id: Contract this token is bound to.
    """

    task_id: str
    contract_id: str


@dataclass(frozen=True)
class DelegationCapabilityToken:
    """HMAC-SHA256 signed delegation capability token.

    Immutable after creation (frozen dataclass). Binds a set of permitted
    operations to a specific issuer/subject pair with optional expiry,
    resource selectors, and caveats.

    Attributes:
        token_id: Unique UUID for this token.
        issuer: Agent granting the capability.
        subject: Agent receiving the capability.
        resource_selectors: Accessible resource specifications.
        ops_allowed: Permitted operations (e.g., "read", "write").
        caveats: Additional constraints on use.
        expiry: ISO8601 timestamp or None for no expiry.
        binding: Links token to specific task/contract.
        signature: HMAC-SHA256 hex signature for integrity.
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
                {
                    "task_id": self.binding.task_id,
                    "contract_id": self.binding.contract_id,
                }
                if self.binding
                else None
            ),
        }

    def verify_signature(self, secret: bytes) -> bool:
        """Verify HMAC-SHA256 signature matches token content.

        Args:
            secret: Shared secret for HMAC verification.

        Returns:
            True if signature is valid, False otherwise.
        """
        expected = _compute_signature(self.to_dict(), secret)
        return hmac.compare_digest(self.signature, expected)

    def is_expired(self) -> bool:
        """Check if token has expired.

        Returns:
            True if expiry is set and passed, False otherwise.
        """
        if self.expiry is None:
            return False
        try:
            expiry_dt = datetime.fromisoformat(self.expiry.replace("Z", "+00:00"))
            return datetime.now(timezone.utc) > expiry_dt
        except (ValueError, TypeError):
            return True  # Invalid expiry = treat as expired

    def validate_binding(self, task_id: str, contract_id: str, subject: str) -> bool:
        """Validate token is bound to expected task/contract/subject.

        Args:
            task_id: Expected task ID.
            contract_id: Expected contract ID.
            subject: Expected subject (delegatee) ID.

        Returns:
            True if all bindings match, False otherwise.
        """
        if self.binding is None:
            return False
        return (
            self.binding.task_id == task_id
            and self.binding.contract_id == contract_id
            and self.subject == subject
        )


class DelegationTokenManager:
    """Manager for creating and validating delegation tokens.

    Implements token lifecycle with HMAC-SHA256 signing.
    All operations are feature-flagged via ENABLE_IDP.

    Args:
        secret: HMAC secret key. If None, reads from DCT_SECRET env var
                or generates an ephemeral key (not recommended for production).
    """

    def __init__(self, secret: bytes | None = None):
        if secret is None:
            secret_str = os.environ.get("DCT_SECRET")
            if secret_str:
                secret = secret_str.encode("utf-8")
            else:
                logger.warning(
                    "DCT_SECRET not set, using ephemeral key. "
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
    ) -> DelegationCapabilityToken:
        """Create a new HMAC-SHA256 signed delegation token.

        Args:
            issuer: Agent granting the capability.
            subject: Agent receiving the capability.
            ops_allowed: List of permitted operations.
            binding: Task/contract binding for the token.
            resource_selectors: Accessible resources (default: all).
            caveats: Constraints on use (default: none).
            expiry_minutes: Minutes until expiry (None = no expiry, default: 120).

        Returns:
            Signed DelegationCapabilityToken.

        Raises:
            RuntimeError: If ENABLE_IDP is False.
        """
        if not _is_idp_enabled():
            raise RuntimeError("IDP is disabled. Set ENABLE_IDP=true to create tokens.")

        expiry = None
        if expiry_minutes is not None:
            expiry_dt = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            expiry = expiry_dt.isoformat().replace("+00:00", "Z")

        token = DelegationCapabilityToken(
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

        return DelegationCapabilityToken(
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
        token: DelegationCapabilityToken,
        expected_task_id: str | None = None,
        expected_contract_id: str | None = None,
        expected_subject: str | None = None,
    ) -> tuple[bool, str | None]:
        """Validate a delegation token for use.

        Performs signature verification, expiry check, and optional
        binding validation.

        Args:
            token: The token to validate.
            expected_task_id: If provided, validate binding to this task.
            expected_contract_id: If provided, validate binding to this contract.
            expected_subject: If provided, validate token subject matches.

        Returns:
            Tuple of (is_valid, error_code). Error codes:
            - IDP_E_TOKEN_INVALID: Signature verification failed.
            - IDP_E_TOKEN_EXPIRED: Token has expired.
            - IDP_E_BINDING_MISMATCH: Task/contract/subject binding mismatch.
        """
        if not _is_idp_enabled():
            return True, None

        if not token.verify_signature(self._secret):
            return False, IDP_E_TOKEN_INVALID

        if token.is_expired():
            return False, IDP_E_TOKEN_EXPIRED

        if expected_task_id or expected_contract_id or expected_subject:
            task_id = expected_task_id or token.binding.task_id if token.binding else ""
            contract_id = (
                expected_contract_id or token.binding.contract_id
                if token.binding
                else ""
            )
            subject = expected_subject or token.subject

            if not token.validate_binding(task_id, contract_id, subject):
                return False, IDP_E_BINDING_MISMATCH

        return True, None

    def check_least_privilege(
        self,
        token: DelegationCapabilityToken,
        requested_op: str,
        allowed_tools: list[str] | None = None,
        denied_tools: list[str] | None = None,
    ) -> tuple[bool, str | None]:
        """Check if a requested operation complies with least privilege.

        Args:
            token: The token authorizing the operation.
            requested_op: Operation being requested (e.g., "write_file").
            allowed_tools: Allowed operations list (None = any allowed).
            denied_tools: Denied operations list (None = none denied).

        Returns:
            Tuple of (is_allowed, error_code). Error codes:
            - IDP_E_DCT_VIOLATION: Operation not permitted.
        """
        if not _is_idp_enabled():
            return True, None

        if requested_op not in token.ops_allowed:
            return False, IDP_E_DCT_VIOLATION

        if allowed_tools is not None and requested_op not in allowed_tools:
            return False, IDP_E_DCT_VIOLATION

        if denied_tools is not None and requested_op in denied_tools:
            return False, IDP_E_DCT_VIOLATION

        return True, None


def _compute_signature(data: dict[str, Any], secret: bytes) -> str:
    """Compute HMAC-SHA256 signature for token data.

    Args:
        data: Token dictionary (excluding signature field).
        secret: HMAC secret key.

    Returns:
        Hex-encoded HMAC-SHA256 signature.
    """
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256).hexdigest()


# Module-level singleton for convenience
_default_manager: DelegationTokenManager | None = None
_default_manager_lock = threading.Lock()


def get_token_manager() -> DelegationTokenManager:
    """Get default token manager instance (singleton).

    Returns:
        Shared DelegationTokenManager instance.
    """
    global _default_manager
    if _default_manager is None:
        with _default_manager_lock:
            if _default_manager is None:
                _default_manager = DelegationTokenManager()
    return _default_manager


def create_token(
    issuer: str, subject: str, ops_allowed: list[str], binding: TokenBinding, **kwargs
) -> DelegationCapabilityToken:
    """Convenience function to create token via default manager."""
    return get_token_manager().create_token(
        issuer=issuer,
        subject=subject,
        ops_allowed=ops_allowed,
        binding=binding,
        **kwargs,
    )


def validate_token(
    token: DelegationCapabilityToken, **kwargs
) -> tuple[bool, str | None]:
    """Convenience function to validate token via default manager."""
    return get_token_manager().validate_token(token, **kwargs)
