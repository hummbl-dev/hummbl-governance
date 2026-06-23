# Copyright 2024-2026 HUMMBL, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""Internal type definitions for hummbl-governance.

Vendored from hummbl-library to eliminate the supply-chain risk of
fallback imports.  All types here are stdlib-only and frozen.

This module is not part of the public API;  consumers should import
types from the sub-modules that expose them (e.g.
``from hummbl_governance import KillSwitchMode``).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Literal


# ---------------------------------------------------------------------------
# Kill switch
# ---------------------------------------------------------------------------

class KillSwitchMode(Enum):
    """Kill switch engagement modes."""

    DISENGAGED = auto()
    HALT_NONCRITICAL = auto()
    HALT_ALL = auto()
    EMERGENCY = auto()


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------

class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


# ---------------------------------------------------------------------------
# Coordination bus
# ---------------------------------------------------------------------------

class PolicyLevel(Enum):
    """Security policy levels for bus message validation.

    Levels are ordered by strictness: PERMISSIVE < WARN < STRICT.
    """

    PERMISSIVE = 1  # Accept all messages, no validation
    WARN = 2  # Accept all, log warnings for unsigned
    STRICT = 3  # Reject unsigned messages

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, PolicyLevel):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other: object) -> bool:
        if not isinstance(other, PolicyLevel):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, PolicyLevel):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, PolicyLevel):
            return NotImplemented
        return self.value >= other.value


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AuditEntry:
    """Single entry in the governance audit log."""

    timestamp: str
    entry_id: str
    intent_id: str
    task_id: str
    tuple_type: str
    tuple_data: dict[str, Any]
    signature: str | None = None
    contract_id: str | None = None
    capability_token_id: str | None = None
    verification_id: str | None = None
    amendment_of: str | None = None

    def to_jsonl(self) -> str:
        """Serialize to JSONL line."""
        data: dict[str, Any] = {
            "timestamp": self.timestamp,
            "entry_id": self.entry_id,
            "intent_id": self.intent_id,
            "task_id": self.task_id,
            "tuple_type": self.tuple_type,
            "tuple_data": self.tuple_data,
            "signature": self.signature,
        }
        if self.contract_id is not None:
            data["contract_id"] = self.contract_id
        if self.capability_token_id is not None:
            data["capability_token_id"] = self.capability_token_id
        if self.verification_id is not None:
            data["verification_id"] = self.verification_id
        if self.amendment_of is not None:
            data["amendment_of"] = self.amendment_of
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditEntry":
        """Deserialize from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            entry_id=data["entry_id"],
            intent_id=data["intent_id"],
            task_id=data["task_id"],
            tuple_type=data["tuple_type"],
            tuple_data=data["tuple_data"],
            signature=data.get("signature"),
            contract_id=data.get("contract_id"),
            capability_token_id=data.get("capability_token_id"),
            verification_id=data.get("verification_id"),
            amendment_of=data.get("amendment_of"),
        )


# ---------------------------------------------------------------------------
# Delegation tokens
# ---------------------------------------------------------------------------

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
        canonical = json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)
        mac = hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256)
        expected = mac.hexdigest()
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


# ---------------------------------------------------------------------------
# Cost governor
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class UsageRecord:
    """A single API usage record."""

    record_id: str
    timestamp: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    cost: float
    meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        provider: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost: float,
        timestamp: datetime | None = None,
        meta: dict[str, Any] | None = None,
    ) -> "UsageRecord":
        """Factory method with auto-generated IDs."""
        ts = timestamp or datetime.now(timezone.utc)
        return cls(
            record_id=f"usage-{uuid.uuid4().hex[:12]}",
            timestamp=ts.isoformat().replace("+00:00", "Z"),
            provider=provider,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            meta=meta or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "provider": self.provider,
            "model": self.model,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost": self.cost,
            "meta": self.meta,
        }


@dataclass(frozen=True, slots=True)
class BudgetStatus:
    """Budget status report with governance decision."""

    current_spend: float
    soft_cap: float
    hard_cap: float | None
    currency: str
    threshold_percent: float
    decision: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_spend": self.current_spend,
            "soft_cap": self.soft_cap,
            "hard_cap": self.hard_cap,
            "currency": self.currency,
            "threshold_percent": self.threshold_percent,
            "decision": self.decision,
            "rationale": self.rationale,
        }
