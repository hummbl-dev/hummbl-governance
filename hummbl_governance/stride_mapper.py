"""STRIDE Threat Mapper -- Map agent interactions to STRIDE threat categories.

Decomposes agent-to-agent and agent-to-tool interactions into the six STRIDE
threat categories, mapping each to the hummbl-governance module that mitigates it.

STRIDE categories (Shostack, 2014):
- Spoofing:                identity.py (AgentRegistry, trust tiers)
- Tampering:               audit_log.py (append-only, HMAC signatures)
- Repudiation:             audit_log.py (immutable entries, amendment chains)
- Information Disclosure:  delegation.py (least-privilege tokens, caveats)
- Denial of Service:       circuit_breaker.py, cost_governor.py, kill_switch.py
- Elevation of Privilege:  delegation.py (time-bound, caveat-constrained tokens)

Usage::

    from hummbl_governance.stride_mapper import StrideMapper, ThreatFinding

    mapper = StrideMapper()
    findings = mapper.analyze_interaction(
        source="worker-1",
        target="database",
        action="write",
        trust_boundary=True,
    )
    for f in findings:
        print(f.category, f.risk_level, f.mitigation_module)

    report = mapper.generate_report(interactions)

Stdlib-only.

Reference:
    Shostack, A. (2014). Threat Modeling: Designing for Security.
    John Wiley & Sons. ISBN: 978-1-118-80999-0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class StrideCategory(Enum):
    """The six STRIDE threat categories."""

    SPOOFING = "Spoofing"
    TAMPERING = "Tampering"
    REPUDIATION = "Repudiation"
    INFORMATION_DISCLOSURE = "Information Disclosure"
    DENIAL_OF_SERVICE = "Denial of Service"
    ELEVATION_OF_PRIVILEGE = "Elevation of Privilege"


class RiskLevel(Enum):
    """Risk severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Mapping from STRIDE category to hummbl-governance mitigation modules
_MITIGATIONS: dict[StrideCategory, dict[str, str]] = {
    StrideCategory.SPOOFING: {
        "module": "identity.py",
        "class": "AgentRegistry",
        "mechanism": "Trust tiers, alias resolution, sender validation",
    },
    StrideCategory.TAMPERING: {
        "module": "audit_log.py",
        "class": "AuditLog",
        "mechanism": "Append-only JSONL, HMAC-SHA256 signatures, entry immutability",
    },
    StrideCategory.REPUDIATION: {
        "module": "audit_log.py",
        "class": "AuditLog",
        "mechanism": "Immutable entries with UUID IDs, amendment chains, HMAC signatures",
    },
    StrideCategory.INFORMATION_DISCLOSURE: {
        "module": "delegation.py",
        "class": "DelegationTokenManager",
        "mechanism": "Least-privilege tokens, resource selectors, caveat constraints",
    },
    StrideCategory.DENIAL_OF_SERVICE: {
        "module": "circuit_breaker.py + cost_governor.py + kill_switch.py",
        "class": "CircuitBreaker + CostGovernor + KillSwitch",
        "mechanism": "Fast-fail on OPEN, budget DENY on hard cap, graduated halt modes",
    },
    StrideCategory.ELEVATION_OF_PRIVILEGE: {
        "module": "delegation.py",
        "class": "DelegationTokenManager",
        "mechanism": "Time-bound tokens, HMAC signature verification, caveat enforcement",
    },
}


@dataclass(frozen=True)
class ThreatFinding:
    """A single STRIDE threat finding for an interaction."""

    category: StrideCategory
    risk_level: RiskLevel
    description: str
    mitigation_module: str
    mitigation_class: str
    mitigation_mechanism: str
    source: str
    target: str
    action: str
    trust_boundary: bool


@dataclass
class Interaction:
    """An agent-to-agent or agent-to-resource interaction to analyze."""

    source: str
    target: str
    action: str
    trust_boundary: bool = False
    authenticated: bool = False
    encrypted: bool = False
    has_delegation_token: bool = False
    has_audit_trail: bool = False
    has_rate_limit: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StrideReport:
    """Aggregated STRIDE analysis report."""

    generated_at: str
    interactions_analyzed: int
    findings: list[ThreatFinding]
    summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "generated_at": self.generated_at,
            "interactions_analyzed": self.interactions_analyzed,
            "findings_count": len(self.findings),
            "by_category": self.summary,
            "findings": [
                {
                    "category": f.category.value,
                    "risk_level": f.risk_level.value,
                    "description": f.description,
                    "mitigation_module": f.mitigation_module,
                    "source": f.source,
                    "target": f.target,
                    "action": f.action,
                    "trust_boundary": f.trust_boundary,
                }
                for f in self.findings
            ],
        }


class StrideMapper:
    """Analyzes interactions for STRIDE threats and maps to governance modules."""

    def analyze_interaction(self, interaction: Interaction) -> list[ThreatFinding]:
        """Analyze a single interaction for all six STRIDE threat categories.

        Returns findings only for categories where the interaction has
        insufficient mitigation.
        """
        findings: list[ThreatFinding] = []

        src = interaction.source
        tgt = interaction.target
        act = interaction.action
        tb = interaction.trust_boundary

        # Spoofing: higher risk at trust boundaries without authentication
        if not interaction.authenticated:
            risk = RiskLevel.HIGH if tb else RiskLevel.MEDIUM
            findings.append(self._finding(
                StrideCategory.SPOOFING, risk, src, tgt, act, tb,
                f"{'Cross-boundary i' if tb else 'I'}nteraction without authentication. "
                f"Source '{src}' identity is not verified.",
            ))

        # Tampering: any write action without audit trail
        if act in ("write", "modify", "delete", "execute") and not interaction.has_audit_trail:
            risk = RiskLevel.HIGH if tb else RiskLevel.MEDIUM
            findings.append(self._finding(
                StrideCategory.TAMPERING, risk, src, tgt, act, tb,
                f"Mutation action '{act}' from '{src}' to '{tgt}' without audit trail. "
                f"Changes cannot be detected or attributed.",
            ))

        # Repudiation: actions without audit trail
        if not interaction.has_audit_trail:
            risk = RiskLevel.MEDIUM if tb else RiskLevel.LOW
            findings.append(self._finding(
                StrideCategory.REPUDIATION, risk, src, tgt, act, tb,
                f"Action '{act}' from '{src}' has no audit record. "
                f"Source could deny performing this action.",
            ))

        # Information Disclosure: cross-boundary reads without delegation token
        if tb and not interaction.has_delegation_token:
            risk = RiskLevel.HIGH if act in ("read", "query", "export") else RiskLevel.MEDIUM
            findings.append(self._finding(
                StrideCategory.INFORMATION_DISCLOSURE, risk, src, tgt, act, tb,
                f"Cross-boundary access from '{src}' to '{tgt}' without delegation token. "
                f"No least-privilege enforcement on data access.",
            ))

        # Denial of Service: actions without rate limiting
        if not interaction.has_rate_limit:
            risk = RiskLevel.HIGH if tb else RiskLevel.LOW
            findings.append(self._finding(
                StrideCategory.DENIAL_OF_SERVICE, risk, src, tgt, act, tb,
                f"Action '{act}' from '{src}' to '{tgt}' has no rate limiting. "
                f"Source could exhaust target resources.",
            ))

        # Elevation of Privilege: cross-boundary mutations without delegation
        if tb and act in ("write", "modify", "delete", "execute", "admin"):
            if not interaction.has_delegation_token:
                findings.append(self._finding(
                    StrideCategory.ELEVATION_OF_PRIVILEGE, RiskLevel.CRITICAL,
                    src, tgt, act, tb,
                    f"Cross-boundary mutation '{act}' from '{src}' to '{tgt}' "
                    f"without delegation token. Agent may exceed intended privileges.",
                ))

        return findings

    def generate_report(self, interactions: list[Interaction]) -> StrideReport:
        """Analyze multiple interactions and produce an aggregated report."""
        all_findings: list[ThreatFinding] = []
        for interaction in interactions:
            all_findings.extend(self.analyze_interaction(interaction))

        summary: dict[str, int] = {}
        for cat in StrideCategory:
            count = sum(1 for f in all_findings if f.category == cat)
            if count > 0:
                summary[cat.value] = count

        return StrideReport(
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            interactions_analyzed=len(interactions),
            findings=all_findings,
            summary=summary,
        )

    @staticmethod
    def _finding(
        category: StrideCategory,
        risk: RiskLevel,
        src: str,
        tgt: str,
        act: str,
        tb: bool,
        desc: str,
    ) -> ThreatFinding:
        mitigation = _MITIGATIONS[category]
        return ThreatFinding(
            category=category,
            risk_level=risk,
            description=desc,
            mitigation_module=mitigation["module"],
            mitigation_class=mitigation["class"],
            mitigation_mechanism=mitigation["mechanism"],
            source=src,
            target=tgt,
            action=act,
            trust_boundary=tb,
        )
