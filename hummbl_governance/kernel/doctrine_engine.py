"""Doctrine Engine — D1-D5 invariant enforcement.

The Kernel is an epistemic gatekeeper. DoctrineEngine enforces hard
boundaries between speculation and action across the fleet promotion graph.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .invariants import KernelInvariant, KernelPanic

logger = logging.getLogger(__name__)


class Stage(Enum):
    """Promotion stages in the fleet pipeline."""

    PLAYGROUND = "playground"
    SANDBOX = "sandbox"
    INNOVATIONS = "innovations"
    FLEET = "fleet"


class DoctrineInvariant(Enum):
    """The five doctrine invariants."""

    ZERO_TRUST = "D1"
    """Playground is zero-trust: no playground artifact influences fleet state
    without passing the Seed gate."""

    FALSIFIABILITY = "D2"
    """A hypothesis without a falsifier is not a seed. It is philosophy."""

    NO_INHERITED_AUTHORITY = "D3"
    """Credibility is earned per artifact, not borrowed from lineage."""

    DIVERGENCE_CONTAINED = "D4"
    """Novelty generation must not destabilize convergent operations."""

    NO_AUTO_PROMOTION = "D5"
    """No stage promotes itself. Every gate requires operator approval."""


@dataclass
class ValidationResult:
    """Result of a doctrine validation check."""

    valid: bool
    invariant: DoctrineInvariant | None = None
    detail: str = ""
    receipt: dict[str, Any] = field(default_factory=dict)


class DoctrineEngine:
    """Engine for enforcing doctrine invariants D1-D5.

    The DoctrineEngine validates:
    - Stage isolation (playground cannot write to fleet)
    - Seed candidate integrity (must have falsifier)
    - Authority neutrality (no inherited credibility)
    - Divergence containment (novelty quarantined)
    - Promotion gates (operator approval required)
    """

    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.doctrine_dir = state_dir / "doctrine"
        self.doctrine_dir.mkdir(parents=True, exist_ok=True)

        # Promotion graph: valid forward edges
        self._valid_promotions: dict[Stage, set[Stage]] = {
            Stage.PLAYGROUND: {Stage.SANDBOX},
            Stage.SANDBOX: {Stage.INNOVATIONS},
            Stage.INNOVATIONS: {Stage.FLEET},
            Stage.FLEET: set(),
        }

        # Stage capabilities (what operations are permitted)
        self._stage_capabilities: dict[Stage, dict[str, bool]] = {
            Stage.PLAYGROUND: {
                "bus_write": False,
                "fleet_read": False,
                "fleet_write": False,
                "memory_read": False,
                "schema_enforced": False,
            },
            Stage.SANDBOX: {
                "bus_write": False,
                "fleet_read": True,
                "fleet_write": False,
                "memory_read": True,
                "schema_enforced": True,
            },
            Stage.INNOVATIONS: {
                "bus_write": True,  # STATUS, PROPOSAL, SITREP with approval
                "fleet_read": True,
                "fleet_write": False,
                "memory_read": True,
                "schema_enforced": True,
            },
            Stage.FLEET: {
                "bus_write": True,
                "fleet_read": True,
                "fleet_write": True,
                "memory_read": True,
                "schema_enforced": True,
            },
        }

    # ── D1: Playground Is Zero-Trust ──────────────────────────────

    def validate_playground_context(
        self,
        agent_id: str,
        write_paths: list[str] | None = None,
        read_paths: list[str] | None = None,
        bus_enabled: bool = False,
    ) -> ValidationResult:
        """Validate that a playground context does not leak to fleet.

        Raises KernelPanic on D1 violation if strict=True would be implied,
        but here returns a ValidationResult for inspection.
        """
        write_paths = write_paths or []
        read_paths = read_paths or []

        # Check for fleet writes
        fleet_writes = [
            p for p in write_paths
            if not p.startswith("playground/") and not p.startswith("/tmp/")  # nosec B108 — path prefix check, not a hardcoded temp dir
        ]
        if fleet_writes:
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.ZERO_TRUST,
                detail=f"Playground context attempted fleet writes: {fleet_writes}",
            )

        # Check bus
        if bus_enabled:
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.ZERO_TRUST,
                detail="Playground context has bus writer enabled",
            )

        return ValidationResult(valid=True)

    def assert_playground_isolated(
        self, agent_id: str, write_paths: list[str], bus_enabled: bool
    ) -> None:
        """Hard gate: raise KernelPanic if playground leaks to fleet."""
        result = self.validate_playground_context(agent_id, write_paths, bus_enabled=bus_enabled)
        if not result.valid:
            raise KernelPanic(
                KernelInvariant.RECEIPT,
                f"D1 ZERO_TRUST violated: {result.detail}",
                agent_id=agent_id,
                severity="CRITICAL",
            )

    # ── D2: Falsifiability Is the Gate ────────────────────────────

    def validate_seed_candidate(self, candidate: dict[str, Any]) -> ValidationResult:
        """Validate that a seed candidate has a testable core and falsifier.

        Returns invalid if any required field is missing.
        """
        required = {
            "testable_core": "what experiment tests this?",
            "falsifier": "what result rejects this?",
            "source_hash": "SHA-256 of source material",
            "confidence": "self-assigned confidence level",
        }

        missing = [k for k in required if not candidate.get(k)]
        if missing:
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.FALSIFIABILITY,
                detail=f"Seed candidate missing required fields: {missing}",
            )

        # Check that falsifier is not empty or tautological
        falsifier = str(candidate.get("falsifier", "")).strip()
        if not falsifier or falsifier.lower() in ("none", "n/a", "impossible"):
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.FALSIFIABILITY,
                detail="Seed candidate falsifier is empty or tautological",
            )

        # Check for tautological hypotheses
        hypothesis = str(candidate.get("hypothesis", "")).lower()
        tautology_markers = [
            "by definition", "is true because", "always", "never", "self-evident"
        ]
        for marker in tautology_markers:
            if marker in hypothesis:
                return ValidationResult(
                    valid=False,
                    invariant=DoctrineInvariant.FALSIFIABILITY,
                    detail=f"Hypothesis appears tautological (marker: '{marker}')",
                )

        return ValidationResult(valid=True)

    def assert_seed_candidate_valid(self, candidate: dict[str, Any]) -> None:
        """Hard gate: raise KernelPanic if seed candidate is invalid."""
        result = self.validate_seed_candidate(candidate)
        if not result.valid:
            raise KernelPanic(
                KernelInvariant.RECEIPT,
                f"D2 FALSIFIABILITY violated: {result.detail}",
                severity="HIGH",
            )

    # ── D3: Authority Is Not Inherited ───────────────────────────

    def validate_authority(
        self,
        artifact: dict[str, Any],
        parent_artifact: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate that authority is earned per artifact.

        If parent artifact passed a gate, child artifact must re-verify.
        """
        authority_source = artifact.get("authority_source", "inherited")

        # Inherited authority must be downgraded
        if authority_source == "inherited":
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.NO_INHERITED_AUTHORITY,
                detail="Artifact has inherited authority; requires re-verification",
                receipt={"required_action": "strip_inherited_authority"},
            )

        # If parent exists, child cannot claim parent's gate status
        if parent_artifact and artifact.get("gate_status") == parent_artifact.get("gate_status"):
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.NO_INHERITED_AUTHORITY,
                detail="Child artifact cannot inherit parent's gate status",
            )

        return ValidationResult(valid=True)

    def strip_inherited_authority(self, artifact: dict[str, Any]) -> dict[str, Any]:
        """Downgrade inherited authority to evidence_required."""
        if artifact.get("authority_source") == "inherited":
            artifact["authority_source"] = "evidence_required"
            artifact["previous_authority"] = "inherited"
            logger.info("Stripped inherited authority from artifact; requires re-verification")
        return artifact

    # ── D4: Divergence Is Contained ───────────────────────────────

    def validate_divergence_containment(
        self,
        operation_type: str,
        target_paths: list[str],
        bus_emit: bool = False,
        downstream_trigger: bool = False,
        schema_modify: bool = False,
        tier_modify: bool = False,
    ) -> ValidationResult:
        """Validate that a divergent operation does not destabilize convergent state.

        Divergent operations must not:
        - Modify production schemas
        - Emit bus messages
        - Trigger downstream agents
        - Alter tier classifications
        """
        violations = []

        if bus_emit:
            violations.append("bus_emit")
        if downstream_trigger:
            violations.append("downstream_trigger")
        if schema_modify:
            violations.append("schema_modify")
        if tier_modify:
            violations.append("tier_modify")

        # Check for fleet path writes
        fleet_targets = [
            p for p in target_paths
            if any(
                p.startswith(prefix)
                for prefix in ("fleet/", "rules/", "skills/", "agents/", "services/")
            )
        ]
        if fleet_targets:
            violations.append(f"fleet_target:{fleet_targets}")

        if violations:
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.DIVERGENCE_CONTAINED,
                detail=f"Divergent operation leaked to convergent path: {violations}",
            )

        return ValidationResult(valid=True)

    # ── D5: Auto-Promotion Is Forbidden ────────────────────────────

    def validate_promotion(
        self,
        from_stage: Stage | str,
        to_stage: Stage | str,
        operator_receipt: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate a stage promotion.

        Requires:
        1. Valid forward edge in promotion graph
        2. Operator-authorized PROMOTE receipt
        """
        from_s = from_stage if isinstance(from_stage, Stage) else Stage(from_stage)
        to_s = to_stage if isinstance(to_stage, Stage) else Stage(to_stage)

        # Check promotion graph
        if to_s not in self._valid_promotions.get(from_s, set()):
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.NO_AUTO_PROMOTION,
                detail=f"Invalid promotion: {from_s.value} -> {to_s.value}",
            )

        # Check operator receipt
        if not operator_receipt:
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.NO_AUTO_PROMOTION,
                detail="Promotion requires operator-authorized receipt",
            )

        receipt_type = operator_receipt.get("action_type", "")
        if receipt_type != "PROMOTE":
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.NO_AUTO_PROMOTION,
                detail=f"Promotion requires PROMOTE receipt, got: {receipt_type}",
            )

        # Validate signature if present
        signature = operator_receipt.get("signature", "")
        if not signature:
            return ValidationResult(
                valid=False,
                invariant=DoctrineInvariant.NO_AUTO_PROMOTION,
                detail="Operator receipt lacks signature",
            )

        return ValidationResult(valid=True)

    def promote(
        self,
        from_stage: Stage | str,
        to_stage: Stage | str,
        artifact: dict[str, Any],
        operator_receipt: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a promotion after validation.

        Returns the artifact with promotion metadata, or raises KernelPanic.
        """
        self.assert_promotion_valid(from_stage, to_stage, operator_receipt)

        artifact["promotion"] = {
            "from": from_stage.value if isinstance(from_stage, Stage) else str(from_stage),
            "to": to_stage.value if isinstance(to_stage, Stage) else str(to_stage),
            "operator_receipt_id": operator_receipt.get("receipt_id", ""),
            "promoted_at": self._now(),
        }
        logger.info(
            "Promoted artifact from %s to %s via receipt %s",
            from_stage,
            to_stage,
            operator_receipt.get("receipt_id", "unknown"),
        )
        return artifact

    def assert_promotion_valid(
        self,
        from_stage: Stage | str,
        to_stage: Stage | str,
        operator_receipt: dict[str, Any] | None = None,
    ) -> None:
        """Hard gate: raise KernelPanic if promotion is invalid."""
        result = self.validate_promotion(from_stage, to_stage, operator_receipt)
        if not result.valid:
            raise KernelPanic(
                KernelInvariant.RECEIPT,
                f"D5 NO_AUTO_PROMOTION violated: {result.detail}",
                severity="CRITICAL",
            )

    # ── Cross-Domain Analogy Rules ───────────────────────────────

    def validate_analogy_source(
        self,
        source_type: str,
        source_data: str,
    ) -> ValidationResult:
        """Validate that a cross-domain analogy uses only public sources.

        Blocks internal fleet data, client cases, proprietary algorithms.
        """
        forbidden_patterns = [
            "founder_mode/",
            "hummbl-governance/",
            "client/",
            "proprietary",
            "confidential",
            "internal_only",
            "_state/",
        ]

        source_lower = source_data.lower()
        for pattern in forbidden_patterns:
            if pattern in source_lower:
                return ValidationResult(
                    valid=False,
                    invariant=DoctrineInvariant.ZERO_TRUST,
                    detail=f"Analogy source contains forbidden pattern: {pattern}",
                )

        # Check for injection patterns
        injection_markers = [
            "prioritize as high-confidence",
            "skip falsifier generation",
            "treat as canonical",
            "ignore safety checks",
        ]
        for marker in injection_markers:
            if marker in source_lower:
                return ValidationResult(
                    valid=False,
                    invariant=DoctrineInvariant.ZERO_TRUST,
                    detail=f"Analogy source contains injection marker: {marker}",
                )

        return ValidationResult(valid=True)

    # ── Utility ─────────────────────────────────────────────────

    def _now(self) -> str:
        """Return ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_stage_capabilities(self, stage: Stage | str) -> dict[str, bool]:
        """Return capability map for a stage."""
        s = stage if isinstance(stage, Stage) else Stage(stage)
        return self._stage_capabilities.get(s, {}).copy()
