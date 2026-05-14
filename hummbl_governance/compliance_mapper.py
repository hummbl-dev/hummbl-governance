"""Compliance Mapper -- Map governance traces to common security and AI controls.

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
import re
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
        """Generate a GDPR compliance report from recent governance traces.

        Maps governance entries to Articles 5, 6, 25, 28, 30, and 32.
        These are the articles with direct technical evidence addressable
        by code-level governance primitives.
        """
        now = datetime.now(timezone.utc)

        report = ComplianceReport(
            generated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            framework="GDPR",
        )

        report.controls["Art.5"] = []   # Principles — lawfulness, fairness, transparency
        report.controls["Art.6"] = []   # Lawfulness of processing
        report.controls["Art.25"] = []  # Data protection by design and by default
        report.controls["Art.28"] = []  # Processor obligations
        report.controls["Art.30"] = []  # Records of Processing
        report.controls["Art.32"] = []  # Security of Processing

        files = self._collect_files(days)
        entries = self._read_entries(files)

        for entry in entries:
            evidence = self._base_evidence(entry)
            tuple_type = entry.get("tuple_type")
            tuple_data = entry.get("tuple_data", {})

            # Art.5: Principles — INTENT captures purpose (transparency, purpose limitation)
            if tuple_type == "INTENT":
                princ_evidence = evidence.copy()
                princ_evidence.update({
                    "objective": tuple_data.get("objective"),
                    "agent": tuple_data.get("agent"),
                })
                report.controls["Art.5"].append(princ_evidence)

            # Art.6: Lawfulness — CONTRACT tuples prove consent/contract/legitimate interest basis
            if tuple_type == "CONTRACT":
                law_evidence = evidence.copy()
                law_evidence.update({
                    "issuer": tuple_data.get("issuer"),
                    "operations": tuple_data.get("operations"),
                })
                report.controls["Art.6"].append(law_evidence)

            # Art.25: Data protection by design — DCT ops_allowed + CapabilityFence restrict scope
            if tuple_type == "DCT":
                design_evidence = evidence.copy()
                design_evidence.update({
                    "ops_allowed": tuple_data.get("ops_allowed"),
                    "resources": tuple_data.get("resource_selectors"),
                })
                report.controls["Art.25"].append(design_evidence)
            if tuple_type == "CAPABILITY_FENCE":
                design_evidence = evidence.copy()
                design_evidence["action"] = tuple_data.get("action")
                report.controls["Art.25"].append(design_evidence)

            # Art.28: Processor obligations — DCTX delegation chains prove processor binding
            if tuple_type == "DCTX":
                proc_evidence = evidence.copy()
                proc_evidence.update({
                    "delegator": tuple_data.get("delegator"),
                    "delegatee": tuple_data.get("delegatee"),
                })
                report.controls["Art.28"].append(proc_evidence)

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

        Maps governance traces to Articles 9, 10, 11, 12, 13, 14, 15, 16, 17, and 19.
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
        report.controls["Art.11"] = []  # Technical documentation
        report.controls["Art.12"] = []  # Record-keeping and logging
        report.controls["Art.13"] = []  # Transparency and information provision
        report.controls["Art.14"] = []  # Human oversight
        report.controls["Art.15"] = []  # Accuracy, robustness, cybersecurity
        report.controls["Art.16"] = []  # Obligations of providers
        report.controls["Art.17"] = []  # Quality management system
        report.controls["Art.19"] = []  # Automatically generated logs

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

            # Art.11: Technical documentation — CONTRACT + ATTEST entries prove documented specs
            if tuple_type in ("CONTRACT", "ATTEST"):
                doc_evidence = evidence.copy()
                doc_evidence["tuple_type"] = tuple_type
                report.controls["Art.11"].append(doc_evidence)

            # Art.15: Accuracy, robustness, cybersecurity — CB + KS events prove residual risk
            if tuple_type in ("CIRCUIT_BREAKER", "KILLSWITCH"):
                robust_evidence = evidence.copy()
                robust_evidence.update({
                    "tuple_type": tuple_type,
                    "state": tuple_data.get("state"),
                })
                report.controls["Art.15"].append(robust_evidence)

            # Art.16: Obligations of providers — DCTX delegation integrity + signed entries
            if tuple_type == "DCTX" or entry.get("signature"):
                prov_evidence = evidence.copy()
                prov_evidence["tuple_type"] = tuple_type
                report.controls["Art.16"].append(prov_evidence)

            # Art.19: Automatically generated logs — ALL signed entries are auto-generated
            if entry.get("signature"):
                log_evidence = evidence.copy()
                log_evidence["tuple_type"] = tuple_type
                log_evidence["auto_generated"] = True
                report.controls["Art.19"].append(log_evidence)

        return report


    def generate_iso27001_report(self, days: int = 30) -> ComplianceReport:
        """Generate an ISO/IEC 27001:2022 compliance report from governance traces.

        Maps governance entries to Annex A organizational controls (A.5–A.9, A.12).
        These are the control families most directly addressable by code-level
        governance primitives for AI agent orchestration.

        Controls with no runtime evidence are initialised empty; they are
        satisfied by organizational process documentation outside the library.

        Reference: ISO/IEC 27001:2022, Annex A.
        """
        now = datetime.now(timezone.utc)

        report = ComplianceReport(
            generated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            framework="ISO27001",
        )

        report.controls["A.5"] = []   # Information security policies
        report.controls["A.6"] = []   # Organization of information security
        report.controls["A.7"] = []   # Human resource security
        report.controls["A.8"] = []   # Asset management
        report.controls["A.9"] = []   # Access control
        report.controls["A.12"] = []  # Operations security — logging

        files = self._collect_files(days)
        entries = self._read_entries(files)

        for entry in entries:
            evidence = self._base_evidence(entry)
            tuple_type = entry.get("tuple_type")
            tuple_data = entry.get("tuple_data", {})

            # A.5: Information security policies — INTENT tuples prove stated objectives
            if tuple_type == "INTENT":
                pol_evidence = evidence.copy()
                pol_evidence.update({
                    "agent": tuple_data.get("agent"),
                    "objective": tuple_data.get("objective"),
                })
                report.controls["A.5"].append(pol_evidence)

            # A.6: Organization — DCTX delegation chains show organizational structure
            if tuple_type == "DCTX":
                org_evidence = evidence.copy()
                org_evidence.update({
                    "delegator": tuple_data.get("delegator"),
                    "delegatee": tuple_data.get("delegatee"),
                    "event": tuple_data.get("event"),
                })
                report.controls["A.6"].append(org_evidence)

            # A.7: Human resource security — identity validation and contract binding
            if tuple_type in ("DCT", "CONTRACT"):
                hr_evidence = evidence.copy()
                hr_evidence.update({
                    "issuer": tuple_data.get("issuer"),
                    "subject": tuple_data.get("subject"),
                    "ops": tuple_data.get("ops_allowed") or tuple_data.get("operations"),
                })
                report.controls["A.7"].append(hr_evidence)

            # A.8: Asset management — DCT resource ownership and ATTEST evidence
            if tuple_type in ("DCT", "ATTEST"):
                asset_evidence = evidence.copy()
                asset_evidence.update({
                    "resources": tuple_data.get("resource_selectors") or tuple_data.get("resources"),
                    "tuple_type": tuple_type,
                })
                report.controls["A.8"].append(asset_evidence)

            # A.9: Access control — DCT ops_allowed and delegation binding
            if tuple_type == "DCT":
                access_evidence = evidence.copy()
                access_evidence.update({
                    "issuer": tuple_data.get("issuer"),
                    "subject": tuple_data.get("subject"),
                    "ops_allowed": tuple_data.get("ops_allowed"),
                    "resources": tuple_data.get("resource_selectors"),
                })
                report.controls["A.9"].append(access_evidence)

            # A.12: Operations security — signed entries prove logging and monitoring
            if entry.get("signature"):
                ops_evidence = evidence.copy()
                ops_evidence["tuple_type"] = tuple_type
                report.controls["A.12"].append(ops_evidence)

        return report

    def generate_nist_csf_report(self, days: int = 30) -> ComplianceReport:
        """Generate a NIST Cybersecurity Framework 2.0 compliance report.

        Maps governance traces to the six CSF Functions: GOVERN, IDENTIFY,
        PROTECT, DETECT, RESPOND, RECOVER. Each function is mapped to the
        governance primitives that produce technical evidence for that
        function's outcomes.

        Reference: NIST CSF 2.0 (2024).
        """
        now = datetime.now(timezone.utc)

        report = ComplianceReport(
            generated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            framework="NIST_CSF",
        )

        report.controls["GOVERN"] = []    # Organizational context and risk strategy
        report.controls["IDENTIFY"] = []  # Asset and risk identification
        report.controls["PROTECT"] = []   # Safeguards and access controls
        report.controls["DETECT"] = []    # Continuous monitoring and anomaly detection
        report.controls["RESPOND"] = []   # Incident response
        report.controls["RECOVER"] = []   # Restoration and improvement

        files = self._collect_files(days)
        entries = self._read_entries(files)

        for entry in entries:
            evidence = self._base_evidence(entry)
            tuple_type = entry.get("tuple_type")
            tuple_data = entry.get("tuple_data", {})

            # GOVERN: INTENT tuples and DCTX chains show organizational context
            if tuple_type in ("INTENT", "DCTX"):
                gov_evidence = evidence.copy()
                gov_evidence["tuple_type"] = tuple_type
                if tuple_type == "INTENT":
                    gov_evidence["objective"] = tuple_data.get("objective")
                else:
                    gov_evidence["event"] = tuple_data.get("event")
                report.controls["GOVERN"].append(gov_evidence)

            # IDENTIFY: AgentRegistry identity and DCT asset binding
            if tuple_type in ("DCT", "ATTEST"):
                id_evidence = evidence.copy()
                id_evidence.update({
                    "issuer": tuple_data.get("issuer"),
                    "subject": tuple_data.get("subject"),
                    "tuple_type": tuple_type,
                })
                report.controls["IDENTIFY"].append(id_evidence)

            # PROTECT: KillSwitch, CapabilityFence, DCT ops restrictions
            if tuple_type in ("KILLSWITCH", "CAPABILITY_FENCE", "DCT"):
                prot_evidence = evidence.copy()
                prot_evidence["tuple_type"] = tuple_type
                if tuple_type == "KILLSWITCH":
                    prot_evidence["state"] = tuple_data.get("state")
                elif tuple_type == "CAPABILITY_FENCE":
                    prot_evidence["action"] = tuple_data.get("action")
                else:
                    prot_evidence["ops_allowed"] = tuple_data.get("ops_allowed")
                report.controls["PROTECT"].append(prot_evidence)

            # DETECT: CircuitBreaker, HealthProbe, BehaviorMonitor events
            if tuple_type in ("CIRCUIT_BREAKER", "HEALTH_PROBE", "BEHAVIOR_MONITOR"):
                detect_evidence = evidence.copy()
                detect_evidence["tuple_type"] = tuple_type
                if tuple_type == "CIRCUIT_BREAKER":
                    detect_evidence["state"] = tuple_data.get("state")
                report.controls["DETECT"].append(detect_evidence)

            # RESPOND: KillSwitch HALT/EMERGENCY, CircuitBreaker OPEN
            if tuple_type == "KILLSWITCH" and tuple_data.get("state") in ("HALT_ALL", "EMERGENCY"):
                resp_evidence = evidence.copy()
                resp_evidence["state"] = tuple_data.get("state")
                report.controls["RESPOND"].append(resp_evidence)
            if tuple_type == "CIRCUIT_BREAKER" and tuple_data.get("state") == "OPEN":
                resp_evidence = evidence.copy()
                resp_evidence["state"] = "OPEN"
                report.controls["RESPOND"].append(resp_evidence)

            # RECOVER: CircuitBreaker HALF_OPEN, CostGovernor budget decisions
            if tuple_type == "CIRCUIT_BREAKER" and tuple_data.get("state") == "HALF_OPEN":
                rec_evidence = evidence.copy()
                rec_evidence["state"] = "HALF_OPEN"
                report.controls["RECOVER"].append(rec_evidence)
            if tuple_type == "COST_GOVERNOR":
                rec_evidence = evidence.copy()
                rec_evidence["decision"] = tuple_data.get("decision")
                report.controls["RECOVER"].append(rec_evidence)

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
        choices=["soc2", "gdpr", "owasp", "nist-rmf", "eu-ai-act", "iso27001", "nist-csf"],
        default="soc2",
        help="Compliance framework",
    )
    parser.add_argument(
        "--dir", type=str, default="governance", help="Governance directory"
    )
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument(
        "--validate", type=str, metavar="MATRIX.md",
        help="Validate a coverage matrix .md file and report pass/fail per cell",
    )
    parser.add_argument(
        "--repo-root", type=str, default=".",
        help="Repository root for resolving relative evidence paths (default: CWD). "
             "Use --evidence-roots for cross-repo resolution.",
    )
    parser.add_argument(
        "--evidence-roots", type=str, nargs="*", default=None,
        help="Additional repository roots for cross-repo evidence resolution. "
             "Use when matrices reference paths in multiple repos (e.g. founder-mode).",
    )
    parser.add_argument(
        "--validate-json", action="store_true",
        help="Output validation results as JSON instead of terminal table",
    )

    args = parser.parse_args(argv)

    if args.validate:
        return _validate_matrix(
            args.validate,
            repo_root=args.repo_root,
            evidence_roots=args.evidence_roots or [],
            json_output=args.validate_json,
        )

    mapper = ComplianceMapper(governance_dir=Path(args.dir))
    if args.framework == "gdpr":
        report = mapper.generate_gdpr_report(days=args.days)
    elif args.framework == "owasp":
        report = mapper.generate_owasp_report(days=args.days)
    elif args.framework == "nist-rmf":
        report = mapper.generate_nist_rmf_report(days=args.days)
    elif args.framework == "eu-ai-act":
        report = mapper.generate_eu_ai_act_report(days=args.days)
    elif args.framework == "iso27001":
        report = mapper.generate_iso27001_report(days=args.days)
    elif args.framework == "nist-csf":
        report = mapper.generate_nist_csf_report(days=args.days)
    else:
        report = mapper.generate_soc2_report(days=args.days)

    json_output = report.to_json()

    if args.output:
        Path(args.output).write_text(json_output, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(json_output)

    return 0


def _validate_matrix(matrix_path: str, *, repo_root: str = ".", evidence_roots: list[str] | None = None, json_output: bool = False) -> int:
    """Validate a coverage matrix .md file.

    Parses evidence cells, resolves file references against repo_root and
    optional additional evidence_roots (for cross-repo resolution), and
    checks file existence. Reports pass/fail per evidence cell.

    Returns 0 if all evidence cells pass, 1 if any fail.
    """
    path = Path(matrix_path)
    if not path.exists():
        print(f"ERROR: Matrix file not found: {matrix_path}", file=sys.stderr)
        return 2

    root = Path(repo_root).resolve()
    extra_roots = [Path(r).resolve() for r in (evidence_roots or [])]
    text = path.read_text(encoding="utf-8")

    # Match backtick-quoted file references. Use non-greedy matching
    # and anchor to avoid cross-cell pulls.
    file_ref = re.compile(r"`([^`]*?(?:[^`\s]*/|[^`\s]*\.(?:py|md|ts|tsv|jsonl))[^`]*)`")

    results: list[dict] = []
    passed = 0
    failed = 0

    for match in file_ref.finditer(text):
        ref = match.group(1).strip()
        # Skip markdown formatting, URLs, non-ASCII, or very long refs
        if ref.startswith("http") or len(ref) > 200:
            continue
        if not ref.isascii():
            continue
        if "/" not in ref and "." not in ref:
            continue
        resolved = _resolve_evidence(ref, root, extra_roots)
        cell = {"evidence": ref, "resolved": resolved["path"], "status": resolved["status"], "detail": resolved["detail"]}
        results.append(cell)
        if resolved["status"] == "pass":
            passed += 1
        else:
            failed += 1

    if json_output:
        import json as _json
        print(_json.dumps({"total": passed + failed, "passed": passed, "failed": failed, "results": results}, indent=2))
    else:
        print(f"Matrix validation: {passed + failed} evidence cells")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        for r in results:
            icon = "PASS" if r["status"] == "pass" else "FAIL"
            print(f"  [{icon}] {r['evidence']} -> {r['resolved']} ({r['detail']})")

    return 0 if failed == 0 else 1


def _resolve_evidence(ref: str, repo_root: Path, extra_roots: list[Path] | None = None) -> dict:
    """Resolve an evidence reference to a file path and check existence across multiple roots."""
    all_roots = [repo_root] + (extra_roots or [])

    for root in all_roots:
        candidates = [
            root / ref,
            root / "hummbl_governance" / ref,
            root / "tests" / ref,
            root / "founder_mode" / ref,
            root / "founder_mode" / "services" / ref,
            root / "founder_mode" / "cognition" / ref,
            root / "services" / ref,
        ]
        for candidate in candidates:
            if candidate.exists():
                return {"path": str(candidate), "status": "pass", "detail": f"file exists (via {root.name})"}

        # Try with .py extension
        if not ref.endswith(".py"):
            for candidate in candidates[:4]:
                py_candidate = candidate.with_suffix(".py")
                if py_candidate.exists():
                    return {"path": str(py_candidate), "status": "pass", "detail": f"file exists (.py via {root.name})"}

    return {"path": f"Tried {len(all_roots)} root(s)", "status": "fail", "detail": "file not found in any root"}


if __name__ == "__main__":
    sys.exit(main())
