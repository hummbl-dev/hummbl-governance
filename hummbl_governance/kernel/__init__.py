"""HUMMBL Governance Kernel — Minimal substrate for AI fleet governance.

The Kernel is not a role. It is the operating system of the fleet — the shared
substrate that guarantees every agent action is observable, every observation is
checkable, and every check is against empirical law.

Seven invariants (K1-K7) and seven engines provide the foundation for AI officer
roles, compliance enforcement, and scaling-law governance.

All engines are stdlib-only. No vendor-specific APIs, models, or runtimes.

Usage:
    from hummbl_governance.kernel import Kernel
    kernel = Kernel.boot()
    receipt = kernel.receipt.create(agent_id="devin", ...)
    violations = kernel.law.evaluate(receipt)

__dissect__
-----------
- surface: kernel (governance operating system)
- dependencies: bus_writer_core (for receipt storage), schema_validator (for validation)
- receipts: KERNEL_BOOT, KERNEL_HEALTH, KERNEL_PANIC
- telemetry: engine health, invariant checks, role status
- imports-stdlib: json, hashlib, hmac, os, pathlib, re, datetime, typing
- imports-internal: bus_writer_core (receipt storage), cognition/schema_validator
- imports-third-party: none
- mutable-state: identity registry, role registry, sequence counters
- feature-flags: KERNEL_BOOT_ON_IMPORT (default: False)
- side-effects: writes to _state/kernel/ (receipts, registry, health)
- thread-safe: TBD — engines use file locking via bus_writer patterns
- async: no
"""

from __future__ import annotations

__version__ = "1.0.0"
__spec_version__ = "1.0.0"

from .kernel import Kernel
from .invariants import KernelInvariant, KernelPanic
from .receipt_engine import Receipt, ReceiptEngine
from .law_engine import LawEngine
from .identity_engine import IdentityEngine
from .sequence_engine import SequenceEngine
from .evidence_engine import EvidenceEngine
from .authority_engine import AuthorityEngine
from .schedule_engine import ScheduleEngine

__all__ = [
    "Kernel",
    "KernelInvariant",
    "KernelPanic",
    "Receipt",
    "ReceiptEngine",
    "LawEngine",
    "IdentityEngine",
    "SequenceEngine",
    "EvidenceEngine",
    "AuthorityEngine",
    "ScheduleEngine",
]
