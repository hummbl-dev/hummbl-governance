"""Compliance Mapper -- Map governance traces to SOC2, GDPR, and OWASP controls.

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
        choices=["soc2", "gdpr", "owasp"],
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
