"""Compliance Mapper -- Map governance traces to SOC2, GDPR, OWASP, NIST AI RMF, and EU AI Act controls.

This module parses append-only governance bus JSONL files and extracts
cryptographic evidence to satisfy specific regulatory controls.

SOC2 Controls Mapped:
- CC6.1: Logical Access Security (mapped to DCT tuples)
- CC7.2: Monitoring and Logging (mapped to governance bus integrity)
- CC6.3: Identity & Authentication (mapped to subject/issuer in DCTs)

GDPR Articles Mapped:
- Article 30: Records of Processing (mapped to DCTX/CONTRACT/ATTEST tuples)
- Article 32: Security of Processing (mapped to signed entries)

OWASP Top 10 for Agentic Applications (ASI01-ASI10) Mapped:
- ASI01: Agent Goal Hijack (mapped to INTENT tuples)
- ASI03: Identity & Privilege Abuse (mapped to DCT tuples)
- ASI04: Supply Chain Vulnerabilities (mapped to signed entries)
- ASI07: Insecure Inter-Agent Communication (mapped to DCTX + signed entries)
- ASI08: Cascading Failures (mapped to CIRCUIT_BREAKER/KILLSWITCH tuples)

NIST AI RMF (GOVERN/MAP/MEASURE/MANAGE) Mapped:
- GOVERN 1.1: AI risk management policies (INTENT tuples prove stated objectives)
- GOVERN 1.7: Processes for risk identification (CIRCUIT_BREAKER/KILLSWITCH events)
- MAP 1.1: Organizational context (CONTRACT/DCTX tuples)
- MAP 2.2: Scientific basis for risk assessment (ATTEST/EVIDENCE tuples)
- MEASURE 2.5: Trustworthiness evaluations (signed governance entries)
- MEASURE 2.8: Impact metrics logged (COST_GOVERNOR events)
- MANAGE 1.3: Response plans executed (KILLSWITCH events)
- MANAGE 2.4: Risk treatment applied (CIRCUIT_BREAKER state transitions)

EU AI Act Articles Mapped (High-Risk AI per Annex III):
- Art.9: Risk management system (KILLSWITCH + CIRCUIT_BREAKER evidence)
- Art.10: Data and data governance (ATTEST/EVIDENCE tuples)
- Art.12: Record-keeping and logging (all signed governance entries)
- Art.13: Transparency and information provision (INTENT tuples)
- Art.14: Human oversight (KILLSWITCH tuples with human-initiated state)
- Art.17: Quality management system (DCTX delegation chain integrity)

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ComplianceReport:
    """A structured compliance report containing evidence for multiple controls."""

    generated_at: str
    framework: str
    controls: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize report to JSON."""
        return json.dumps(
            {
                "generated_at": self.generated_at,
                "framework": self.framework,
                "controls": self.controls,
            },
            indent=2,
            sort_keys=True,
        )


class ComplianceMapper:
    """Maps governance entries to regulatory controls."""

    def __init__(self, governance_dir: Path | str | None = None):
        if governance_dir is None:
            self.governance_dir = Path("governance")
        else:
            self.governance_dir = Path(governance_dir)

    def _parse_line(self, line: str) -> dict[str, Any] | None:
        """Safely parse a single JSONL line."""
        try:
            return json.loads(line.strip())
        except json.JSONDecodeError:
            logger.warning("Failed to parse governance line: %s", line[:100])
            return None

    def _collect_files(self, days: int) -> list[Path]:
        """Collect governance JSONL files within the date window."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days)

        files = sorted(self.governance_dir.glob("governance-*.jsonl"), reverse=True)
        result = []

        for file_path in files:
            try:
                file_date_str = file_path.stem.split("governance-")[-1]
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
                if file_date < cutoff.replace(hour=0, minute=0, second=0, microsecond=0):
                    continue
            except (ValueError, IndexError):
                continue
            result.append(file_path)

        return result

    def _read_entries(self, files: list[Path]) -> list[dict[str, Any]]:
        """Read and parse all entries from governance files."""
        entries: list[dict[str, Any]] = []
        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    entry = self._parse_line(line)
                    if entry:
                        entries.append(entry)
        return entries

    @staticmethod
    def _base_evidence(entry: dict[str, Any]) -> dict[str, Any]:
        """Extract common evidence fields from an entry."""
        return {
            "entry_id": entry.get("entry_id"),
            "timestamp": entry.get("timestamp"),
            "task_id": entry.get("task_id"),
            "intent_id": entry.get("intent_id"),
            "signature": entry.get("signature"),
        }

    def generate_soc2_report(self, days: int = 7) -> ComplianceReport:
        """Generate a SOC2 compliance report from recent governance traces."""
        now = datetime.now(timezone.utc)

        report = ComplianceReport(
            generated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            framework="SOC2",
        )

        report.controls["CC6.1"] = []  # Logical Access
        report.controls["CC7.2"] = []  # Monitoring
        report.controls["CC6.3"] = []  # Identity

        files = self._collect_files(days)
        entries = self._read_entries(files)

        for entry in entries:
            evidence = self._base_evidence(entry)
            tuple_type = entry.get("tuple_type")
            tuple_data = entry.get("tuple_data", {})

            # CC7.2: Monitoring and Logging -- signed entries prove monitoring
            if entry.get("signature"):
                report.controls["CC7.2"].append(evidence)

            # CC6.1 & CC6.3: Logical Access and Identity
            if tuple_type == "DCT":
                access_evidence = evidence.copy()
                access_evidence.update({
                    "issuer": tuple_data.get("issuer"),
                    "subject": tuple_data.get("subject"),
                    "resources": tuple_data.get("resource_selectors"),
                    "ops": tuple_data.get("ops_allowed"),
                })
                report.controls["CC6.1"].append(access_evidence)

                identity_evidence = evidence.copy()
                identity_evidence.update({
                    "subject": tuple_data.get("subject"),
                    "issuer": tuple_data.get("issuer"),
                })
                report.controls["CC6.3"].append(identity_evidence)

        return report

    def generate_gdpr_report(self, days: int = 30) -> ComplianceReport:
        """Generate a GDPR compliance report from recent governance traces."""
        now = datetime.now(timezone.utc)

        report = ComplianceReport(
            generated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            framework="GDPR",
        )

        report.controls["Art.30"] = []  # Records of Processing
        report.controls["Art.32"] = []  # Security of Processing

        files = self._collect_files(days)
        entries = self._read_entries(files)

        for entry in entries:
            evidence = self._base_evidence(entry)
            tuple_type = entry.get("tuple_type")
            tuple_data = entry.get("tuple_data", {})

            # Art.30: Records of Processing
            if tuple_type in ("DCTX", "CONTRACT", "ATTEST", "EVIDENCE"):
                processing_evidence = evidence.copy()
                processing_evidence.update({
                    "tuple_type": tuple_type,
                    "delegator": tuple_data.get("delegator"),
                    "delegatee": tuple_data.get("delegatee"),
                    "event": tuple_data.get("event"),
                })
                report.controls["Art.30"].append(processing_evidence)

            # Art.32: Security of Processing (signed entries prove integrity)
            if entry.get("signature"):
                security_evidence = evidence.copy()
                security_evidence["tuple_type"] = tuple_type
                report.controls["Art.32"].append(security_evidence)

        return report

    def generate_owasp_report(self, days: int = 7) -> ComplianceReport:
        """Generate an OWASP Agentic Top 10 compliance report from governance traces.

        Maps governance entries to OWASP ASI01-ASI10 controls. Controls that
        lack runtime governance traces (ASI02, ASI05, ASI06, ASI09, ASI10) are
        initialized empty -- they are evidenced by code audit, not runtime logs.
        """
        now = datetime.now(timezone.utc)

        report = ComplianceReport(
            generated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            framework="OWASP_AGENTIC",
        )

        # Controls with governance-trace evidence
        report.controls["ASI01"] = []  # Agent Goal Hijack (INTENT tuples)
        report.controls["ASI03"] = []  # Identity & Privilege Abuse (DCT tuples)
        report.controls["ASI04"] = []  # Supply Chain (signed entries)
        report.controls["ASI07"] = []  # Insecure Inter-Agent Comms (DCTX + signed)
        report.controls["ASI08"] = []  # Cascading Failures (CIRCUIT_BREAKER/KILLSWITCH)

        # Controls evidenced by code audit (no runtime trace)
        report.controls["ASI02"] = []  # Tool Misuse
        report.controls["ASI05"] = []  # Unexpected Code Execution
        report.controls["ASI06"] = []  # Memory & Context Poisoning
        report.controls["ASI09"] = []  # Human-Agent Trust Exploitation
        report.controls["ASI10"] = []  # Rogue Agents

        files = self._collect_files(days)
        entries = self._read_entries(files)

        for entry in entries:
            evidence = self._base_evidence(entry)
            tuple_type = entry.get("tuple_type")
            tuple_data = entry.get("tuple_data", {})

            # ASI01: Agent Goal Hijack -- INTENT tuples prove lifecycle
            if tuple_type == "INTENT":
                intent_evidence = evidence.copy()
                intent_evidence.update({
                    "agent": tuple_data.get("agent"),
                    "objective": tuple_data.get("objective"),
                    "phase": tuple_data.get("phase"),
                })
                report.controls["ASI01"].append(intent_evidence)

            # ASI03: Identity & Privilege Abuse -- DCT tuples prove delegation
            if tuple_type == "DCT":
                dct_evidence = evidence.copy()
                dct_evidence.update({
                    "issuer": tuple_data.get("issuer"),
                    "subject": tuple_data.get("subject"),
                    "resources": tuple_data.get("resource_selectors"),
                    "ops": tuple_data.get("ops_allowed"),
                })
                report.controls["ASI03"].append(dct_evidence)

            # ASI04: Supply Chain -- signed entries prove integrity
            if entry.get("signature"):
                report.controls["ASI04"].append(evidence)

            # ASI07: Inter-Agent Comms -- DCTX entries
            if tuple_type == "DCTX":
                dctx_evidence = evidence.copy()
                dctx_evidence.update({
                    "delegator": tuple_data.get("delegator"),
                    "delegatee": tuple_data.get("delegatee"),
                    "event": tuple_data.get("event"),
                })
                report.controls["ASI07"].append(dctx_evidence)

            # ASI08: Cascading Failures -- circuit breaker + kill switch
            if tuple_type in ("CIRCUIT_BREAKER", "KILLSWITCH"):
                failure_evidence = evidence.copy()
                failure_evidence.update({
                    "tuple_type": tuple_type,
                    "state": tuple_data.get("state"),
                    "adapter": tuple_data.get("adapter"),
                })
                report.controls["ASI08"].append(failure_evidence)

        return report


    def generate_nist_rmf_report(self, days: int = 30) -> ComplianceReport:
        """Generate a NIST AI Risk Management Framework compliance report.

        Maps governance traces to the four NIST AI RMF core functions:
        GOVERN, MAP, MEASURE, and MANAGE. Controls with no runtime evidence
        (e.g. policy documents) are initialised empty — they are satisfied by
        artefact review, not runtime logs.

        Reference: NIST AI 100-1 (2023), AI RMF Playbook.
        """
        now = datetime.now(timezone.utc)

        report = ComplianceReport(
            generated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            framework="NIST_AI_RMF",
        )

        # GOVERN function
        report.controls["GOVERN-1.1"] = []   # AI risk policies — INTENT tuples prove declared objectives
        report.controls["GOVERN-1.7"] = []   # Risk identification processes — CB/KS events
        # MAP function
        report.controls["MAP-1.1"] = []      # Organisational context — CONTRACT/DCTX
        report.controls["MAP-2.2"] = []      # Risk assessment basis — ATTEST/EVIDENCE
        # MEASURE function
        report.controls["MEASURE-2.5"] = []  # Trustworthiness evaluations — signed entries
        report.controls["MEASURE-2.8"] = []  # Impact metrics — COST_GOVERNOR events
        # MANAGE function
        report.controls["MANAGE-1.3"] = []   # Response plans executed — KILLSWITCH events
        report.controls["MANAGE-2.4"] = []   # Risk treatment applied — CB state transitions

        files = self._collect_files(days)
        entries = self._read_entries(files)

        for entry in entries:
            evidence = self._base_evidence(entry)
            tuple_type = entry.get("tuple_type")
            tuple_data = entry.get("tuple_data", {})

            # GOVERN-1.1: Policies — INTENT tuples capture declared objectives
            if tuple_type == "INTENT":
                intent_evidence = evidence.copy()
                intent_evidence.update({
                    "agent": tuple_data.get("agent"),
                    "objective": tuple_data.get("objective"),
                    "phase": tuple_data.get("phase"),
                })
                report.controls["GOVERN-1.1"].append(intent_evidence)

            # GOVERN-1.7 & MANAGE-1.3 & MANAGE-2.4: Risk/response — CB + KS events
            if tuple_type in ("CIRCUIT_BREAKER", "KILLSWITCH"):
                failure_evidence = evidence.copy()
                failure_evidence.update({
                    "tuple_type": tuple_type,
                    "state": tuple_data.get("state"),
                    "adapter": tuple_data.get("adapter"),
                })
                report.controls["GOVERN-1.7"].append(failure_evidence)
                if tuple_type == "KILLSWITCH":
                    report.controls["MANAGE-1.3"].append(failure_evidence)
                if tuple_type == "CIRCUIT_BREAKER":
                    report.controls["MANAGE-2.4"].append(failure_evidence)

            # MAP-1.1: Organisational context — delegation and contract records
            if tuple_type in ("CONTRACT", "DCTX", "DCT"):
                context_evidence = evidence.copy()
                context_evidence.update({
                    "tuple_type": tuple_type,
                    "delegator": tuple_data.get("delegator") or tuple_data.get("issuer"),
                    "delegatee": tuple_data.get("delegatee") or tuple_data.get("subject"),
                })
                report.controls["MAP-1.1"].append(context_evidence)

            # MAP-2.2: Risk assessment basis — attested evidence entries
            if tuple_type in ("ATTEST", "EVIDENCE"):
                attest_evidence = evidence.copy()
                attest_evidence.update({
                    "tuple_type": tuple_type,
                    "claim": tuple_data.get("claim"),
                    "outcome": tuple_data.get("outcome"),
                })
                report.controls["MAP-2.2"].append(attest_evidence)

            # MEASURE-2.5: Trustworthiness — any signed entry proves integrity
            if entry.get("signature"):
                signed_evidence = evidence.copy()
                signed_evidence["tuple_type"] = tuple_type
                report.controls["MEASURE-2.5"].append(signed_evidence)

            # MEASURE-2.8: Impact metrics — cost governor events
            if tuple_type == "COST_GOVERNOR":
                cost_evidence = evidence.copy()
                cost_evidence.update({
                    "agent": tuple_data.get("agent"),
                    "decision": tuple_data.get("decision"),
                    "spend": tuple_data.get("spend"),
                    "budget": tuple_data.get("budget"),
                })
                report.controls["MEASURE-2.8"].append(cost_evidence)

        return report

    def generate_eu_ai_act_report(self, days: int = 30) -> ComplianceReport:
        """Generate an EU AI Act compliance report (High-Risk AI, Annex III).

        Maps governance traces to Articles 9, 10, 12, 13, 14, and 17.
        These are the core operational obligations for high-risk AI systems.

        Controls with no runtime evidence are initialised empty; they are
        satisfied by design documentation and human review artefacts.

        Reference: Regulation (EU) 2024/1689 (AI Act), in force 2024-08-01.
        """
        now = datetime.now(timezone.utc)

        report = ComplianceReport(
            generated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            framework="EU_AI_ACT",
        )

        report.controls["Art.9"] = []   # Risk management system
        report.controls["Art.10"] = []  # Data and data governance
        report.controls["Art.12"] = []  # Record-keeping and logging
        report.controls["Art.13"] = []  # Transparency and information provision
        report.controls["Art.14"] = []  # Human oversight
        report.controls["Art.17"] = []  # Quality management system

        files = self._collect_files(days)
        entries = self._read_entries(files)

        for entry in entries:
            evidence = self._base_evidence(entry)
            tuple_type = entry.get("tuple_type")
            tuple_data = entry.get("tuple_data", {})

            # Art.9: Risk management system — CB and KS events show residual risk controls
            if tuple_type in ("CIRCUIT_BREAKER", "KILLSWITCH"):
                risk_evidence = evidence.copy()
                risk_evidence.update({
                    "tuple_type": tuple_type,
                    "state": tuple_data.get("state"),
                    "adapter": tuple_data.get("adapter"),
                })
                report.controls["Art.9"].append(risk_evidence)

            # Art.10: Data governance — attested/evidence entries
            if tuple_type in ("ATTEST", "EVIDENCE"):
                data_evidence = evidence.copy()
                data_evidence.update({
                    "tuple_type": tuple_type,
                    "claim": tuple_data.get("claim"),
                    "outcome": tuple_data.get("outcome"),
                })
                report.controls["Art.10"].append(data_evidence)

            # Art.12: Record-keeping — every signed entry is a tamper-evident log record
            if entry.get("signature"):
                log_evidence = evidence.copy()
                log_evidence["tuple_type"] = tuple_type
                report.controls["Art.12"].append(log_evidence)

            # Art.13: Transparency — INTENT tuples capture purpose and objectives
            if tuple_type == "INTENT":
                transparency_evidence = evidence.copy()
                transparency_evidence.update({
                    "agent": tuple_data.get("agent"),
                    "objective": tuple_data.get("objective"),
                    "phase": tuple_data.get("phase"),
                })
                report.controls["Art.13"].append(transparency_evidence)

            # Art.14: Human oversight — KILLSWITCH with human-initiated halt state
            if tuple_type == "KILLSWITCH":
                ks_state = tuple_data.get("state", "")
                oversight_evidence = evidence.copy()
                oversight_evidence.update({
                    "state": ks_state,
                    "human_initiated": ks_state in ("HALT_ALL", "EMERGENCY"),
                })
                report.controls["Art.14"].append(oversight_evidence)

            # Art.17: Quality management — delegation chain integrity (DCTX entries)
            if tuple_type == "DCTX":
                qms_evidence = evidence.copy()
                qms_evidence.update({
                    "delegator": tuple_data.get("delegator"),
                    "delegatee": tuple_data.get("delegatee"),
                    "event": tuple_data.get("event"),
                })
                report.controls["Art.17"].append(qms_evidence)

        return report


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Map governance traces to compliance controls."
    )
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days to include in report"
    )
    parser.add_argument(
        "--framework",
        choices=["soc2", "gdpr", "owasp", "nist-rmf", "eu-ai-act"],
        default="soc2",
        help="Compliance framework",
    )
    parser.add_argument(
        "--dir", type=str, default="governance", help="Governance directory"
    )
    parser.add_argument("--output", type=str, help="Output JSON file path")

    args = parser.parse_args(argv)

    mapper = ComplianceMapper(governance_dir=Path(args.dir))
    if args.framework == "gdpr":
        report = mapper.generate_gdpr_report(days=args.days)
    elif args.framework == "owasp":
        report = mapper.generate_owasp_report(days=args.days)
    elif args.framework == "nist-rmf":
        report = mapper.generate_nist_rmf_report(days=args.days)
    elif args.framework == "eu-ai-act":
        report = mapper.generate_eu_ai_act_report(days=args.days)
    else:
        report = mapper.generate_soc2_report(days=args.days)

    json_output = report.to_json()

    if args.output:
        Path(args.output).write_text(json_output, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(json_output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
