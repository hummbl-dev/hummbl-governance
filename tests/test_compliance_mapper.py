"""Tests for hummbl_governance.compliance_mapper."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


from hummbl_governance.compliance_mapper import (
    ComplianceMapper,
    ComplianceReport,
    main,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _days_ago_str(n: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=n)
    return dt.strftime("%Y-%m-%d")


def _write_governance_file(directory: Path, date_str: str, entries: list[dict]) -> Path:
    """Write a governance JSONL file with the given entries."""
    fp = directory / f"governance-{date_str}.jsonl"
    with open(fp, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    return fp


def _dct_entry(entry_id: str = "e1", signed: bool = True) -> dict:
    return {
        "entry_id": entry_id,
        "timestamp": "2026-03-23T10:00:00Z",
        "task_id": "t1",
        "intent_id": "i1",
        "signature": "sig123" if signed else None,
        "tuple_type": "DCT",
        "tuple_data": {
            "issuer": "system",
            "subject": "agent-1",
            "resource_selectors": ["res:*"],
            "ops_allowed": ["read"],
        },
    }


def _dctx_entry(entry_id: str = "e2") -> dict:
    return {
        "entry_id": entry_id,
        "timestamp": "2026-03-23T10:01:00Z",
        "task_id": "t1",
        "intent_id": "i1",
        "signature": "sig456",
        "tuple_type": "DCTX",
        "tuple_data": {
            "delegator": "agent-1",
            "delegatee": "agent-2",
            "event": "task_delegated",
        },
    }


def _intent_entry(entry_id: str = "e3") -> dict:
    return {
        "entry_id": entry_id,
        "timestamp": "2026-03-23T10:02:00Z",
        "task_id": "t2",
        "intent_id": "i2",
        "signature": "sig789",
        "tuple_type": "INTENT",
        "tuple_data": {
            "agent": "claude",
            "objective": "generate briefing",
            "phase": "SPECIFICATION",
        },
    }


def _contract_entry(entry_id: str = "e4") -> dict:
    return {
        "entry_id": entry_id,
        "timestamp": "2026-03-23T10:03:00Z",
        "task_id": "t3",
        "intent_id": "i3",
        "signature": None,
        "tuple_type": "CONTRACT",
        "tuple_data": {
            "delegator": "system",
            "delegatee": "agent-1",
            "event": "contract_created",
        },
    }


def _circuit_breaker_entry(entry_id: str = "e5") -> dict:
    return {
        "entry_id": entry_id,
        "timestamp": "2026-03-23T10:04:00Z",
        "task_id": "t4",
        "intent_id": "i4",
        "signature": "sigabc",
        "tuple_type": "CIRCUIT_BREAKER",
        "tuple_data": {
            "state": "OPEN",
            "adapter": "github",
        },
    }


def _killswitch_entry(entry_id: str = "e6") -> dict:
    return {
        "entry_id": entry_id,
        "timestamp": "2026-03-23T10:05:00Z",
        "task_id": "t5",
        "intent_id": "i5",
        "signature": "sigdef",
        "tuple_type": "KILLSWITCH",
        "tuple_data": {
            "state": "HALT_ALL",
            "adapter": None,
        },
    }


# ---------------------------------------------------------------------------
# TestComplianceReport
# ---------------------------------------------------------------------------

class TestComplianceReport:
    def test_creation(self):
        report = ComplianceReport(
            generated_at="2026-03-23T10:00:00Z",
            framework="SOC2",
        )
        assert report.generated_at == "2026-03-23T10:00:00Z"
        assert report.framework == "SOC2"
        assert report.controls == {}

    def test_to_json_roundtrip(self):
        report = ComplianceReport(
            generated_at="2026-03-23T10:00:00Z",
            framework="GDPR",
            controls={"Art.30": [{"entry_id": "e1"}]},
        )
        json_str = report.to_json()
        parsed = json.loads(json_str)
        assert parsed["framework"] == "GDPR"
        assert parsed["generated_at"] == "2026-03-23T10:00:00Z"
        assert len(parsed["controls"]["Art.30"]) == 1
        assert parsed["controls"]["Art.30"][0]["entry_id"] == "e1"

    def test_empty_controls(self):
        report = ComplianceReport(
            generated_at="2026-03-23T10:00:00Z",
            framework="SOC2",
            controls={"CC6.1": [], "CC7.2": []},
        )
        parsed = json.loads(report.to_json())
        assert parsed["controls"]["CC6.1"] == []
        assert parsed["controls"]["CC7.2"] == []

    def test_to_json_sorted_keys(self):
        report = ComplianceReport(
            generated_at="2026-03-23T10:00:00Z",
            framework="SOC2",
            controls={"z_control": [], "a_control": []},
        )
        json_str = report.to_json()
        # Keys should be sorted
        assert json_str.index('"controls"') < json_str.index('"framework"')
        assert json_str.index('"framework"') < json_str.index('"generated_at"')


# ---------------------------------------------------------------------------
# TestComplianceMapperSOC2
# ---------------------------------------------------------------------------

class TestComplianceMapperSOC2:
    def test_generates_report(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert report.framework == "SOC2"
        assert "CC6.1" in report.controls
        assert "CC7.2" in report.controls
        assert "CC6.3" in report.controls

    def test_dct_maps_to_cc61(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert len(report.controls["CC6.1"]) == 1
        evidence = report.controls["CC6.1"][0]
        assert evidence["issuer"] == "system"
        assert evidence["subject"] == "agent-1"
        assert evidence["resources"] == ["res:*"]
        assert evidence["ops"] == ["read"]

    def test_dct_maps_to_cc63(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert len(report.controls["CC6.3"]) == 1
        evidence = report.controls["CC6.3"][0]
        assert evidence["subject"] == "agent-1"
        assert evidence["issuer"] == "system"

    def test_signed_maps_to_cc72(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry(signed=True)])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert len(report.controls["CC7.2"]) == 1

    def test_unsigned_skips_cc72(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry(signed=False)])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert len(report.controls["CC7.2"]) == 0

    def test_date_filter_excludes_old(self, tmp_path):
        _write_governance_file(tmp_path, _days_ago_str(30), [_dct_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert len(report.controls["CC6.1"]) == 0

    def test_date_filter_includes_recent(self, tmp_path):
        _write_governance_file(tmp_path, _days_ago_str(3), [_dct_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert len(report.controls["CC6.1"]) == 1


# ---------------------------------------------------------------------------
# TestComplianceMapperGDPR
# ---------------------------------------------------------------------------

class TestComplianceMapperGDPR:
    def test_dctx_maps_to_art30(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dctx_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_gdpr_report(days=30)
        assert len(report.controls["Art.30"]) == 1
        evidence = report.controls["Art.30"][0]
        assert evidence["tuple_type"] == "DCTX"
        assert evidence["delegator"] == "agent-1"

    def test_contract_maps_to_art30(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_contract_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_gdpr_report(days=30)
        assert len(report.controls["Art.30"]) == 1

    def test_signed_maps_to_art32(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dctx_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_gdpr_report(days=30)
        # dctx_entry has signature="sig456"
        assert len(report.controls["Art.32"]) == 1
        evidence = report.controls["Art.32"][0]
        assert evidence["tuple_type"] == "DCTX"

    def test_unsigned_skips_art32(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_contract_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_gdpr_report(days=30)
        # contract_entry has signature=None
        assert len(report.controls["Art.32"]) == 0


# ---------------------------------------------------------------------------
# TestComplianceMapperOWASP
# ---------------------------------------------------------------------------

class TestComplianceMapperOWASP:
    def test_all_10_controls_initialized(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_owasp_report(days=7)
        expected = {f"ASI{str(i).zfill(2)}" for i in range(1, 11)}
        assert set(report.controls.keys()) == expected

    def test_intent_maps_to_asi01(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_intent_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_owasp_report(days=7)
        assert len(report.controls["ASI01"]) == 1
        evidence = report.controls["ASI01"][0]
        assert evidence["agent"] == "claude"
        assert evidence["objective"] == "generate briefing"
        assert evidence["phase"] == "SPECIFICATION"

    def test_dct_maps_to_asi03(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_owasp_report(days=7)
        assert len(report.controls["ASI03"]) == 1
        evidence = report.controls["ASI03"][0]
        assert evidence["issuer"] == "system"
        assert evidence["subject"] == "agent-1"

    def test_signed_maps_to_asi04(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry(signed=True)])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_owasp_report(days=7)
        assert len(report.controls["ASI04"]) == 1

    def test_unsigned_skips_asi04(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry(signed=False)])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_owasp_report(days=7)
        assert len(report.controls["ASI04"]) == 0

    def test_dctx_maps_to_asi07(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dctx_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_owasp_report(days=7)
        assert len(report.controls["ASI07"]) == 1
        evidence = report.controls["ASI07"][0]
        assert evidence["delegator"] == "agent-1"
        assert evidence["delegatee"] == "agent-2"

    def test_circuit_breaker_maps_to_asi08(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_circuit_breaker_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_owasp_report(days=7)
        assert len(report.controls["ASI08"]) == 1
        evidence = report.controls["ASI08"][0]
        assert evidence["tuple_type"] == "CIRCUIT_BREAKER"
        assert evidence["state"] == "OPEN"

    def test_killswitch_maps_to_asi08(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_killswitch_entry()])
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_owasp_report(days=7)
        assert len(report.controls["ASI08"]) == 1
        evidence = report.controls["ASI08"][0]
        assert evidence["tuple_type"] == "KILLSWITCH"
        assert evidence["state"] == "HALT_ALL"


# ---------------------------------------------------------------------------
# TestParseRobustness
# ---------------------------------------------------------------------------

class TestParseRobustness:
    def test_malformed_jsonl_line_skipped(self, tmp_path):
        fp = tmp_path / f"governance-{_today_str()}.jsonl"
        with open(fp, "w") as f:
            f.write("NOT VALID JSON\n")
            f.write(json.dumps(_dct_entry()) + "\n")
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert len(report.controls["CC6.1"]) == 1

    def test_bad_filename_skipped(self, tmp_path):
        fp = tmp_path / "governance-not-a-date.jsonl"
        with open(fp, "w") as f:
            f.write(json.dumps(_dct_entry()) + "\n")
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert len(report.controls["CC6.1"]) == 0

    def test_empty_governance_dir(self, tmp_path):
        mapper = ComplianceMapper(governance_dir=tmp_path)
        report = mapper.generate_soc2_report(days=7)
        assert report.controls["CC6.1"] == []


# ---------------------------------------------------------------------------
# TestDefaultDir
# ---------------------------------------------------------------------------

class TestDefaultDir:
    def test_default_governance_dir(self):
        mapper = ComplianceMapper()
        assert mapper.governance_dir == Path("governance")

    def test_custom_governance_dir(self, tmp_path):
        mapper = ComplianceMapper(governance_dir=tmp_path)
        assert mapper.governance_dir == tmp_path

    def test_string_governance_dir(self, tmp_path):
        mapper = ComplianceMapper(governance_dir=str(tmp_path))
        assert mapper.governance_dir == tmp_path


# ---------------------------------------------------------------------------
# TestCLI
# ---------------------------------------------------------------------------

class TestCLI:
    def test_framework_soc2(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry()])
        rc = main(["--framework", "soc2", "--dir", str(tmp_path)])
        assert rc == 0

    def test_framework_gdpr(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dctx_entry()])
        rc = main(["--framework", "gdpr", "--dir", str(tmp_path)])
        assert rc == 0

    def test_framework_owasp(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_intent_entry()])
        rc = main(["--framework", "owasp", "--dir", str(tmp_path)])
        assert rc == 0

    def test_output_file(self, tmp_path):
        _write_governance_file(tmp_path, _today_str(), [_dct_entry()])
        output_path = tmp_path / "report.json"
        rc = main(["--dir", str(tmp_path), "--output", str(output_path)])
        assert rc == 0
        assert output_path.exists()
        parsed = json.loads(output_path.read_text())
        assert parsed["framework"] == "SOC2"

    def test_days_arg(self, tmp_path):
        _write_governance_file(tmp_path, _days_ago_str(10), [_dct_entry()])
        # days=5 should exclude 10-day-old file
        output_path = tmp_path / "report.json"
        rc = main(["--dir", str(tmp_path), "--days", "5", "--output", str(output_path)])
        assert rc == 0
        parsed = json.loads(output_path.read_text())
        assert len(parsed["controls"]["CC6.1"]) == 0
