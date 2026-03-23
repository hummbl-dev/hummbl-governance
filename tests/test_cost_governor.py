"""Tests for hummbl_governance.cost_governor."""

from datetime import datetime, timezone

import pytest

from hummbl_governance.cost_governor import (
    BudgetStatus,
    CostGovernor,
    UsageRecord,
)


class TestUsageRecord:
    """Test UsageRecord creation."""

    def test_create(self):
        record = UsageRecord.create(
            provider="anthropic",
            model="claude-4",
            tokens_in=1000,
            tokens_out=500,
            cost=0.015,
        )
        assert record.provider == "anthropic"
        assert record.model == "claude-4"
        assert record.cost == 0.015
        assert record.record_id.startswith("usage-")

    def test_create_with_meta(self):
        record = UsageRecord.create(
            provider="openai", model="gpt-4o",
            tokens_in=100, tokens_out=50, cost=0.01,
            meta={"task": "summarize"},
        )
        assert record.meta == {"task": "summarize"}


class TestCostGovernor:
    """Test CostGovernor with in-memory database."""

    def test_record_and_query(self):
        gov = CostGovernor(":memory:")
        gov.record_usage("anthropic", "claude-4", 1000, 500, 0.015)
        assert gov.get_daily_spend() == pytest.approx(0.015)

    def test_multiple_records(self):
        gov = CostGovernor(":memory:")
        gov.record_usage("anthropic", "claude-4", 1000, 500, 10.0)
        gov.record_usage("openai", "gpt-4o", 500, 200, 5.0)
        assert gov.get_daily_spend() == pytest.approx(15.0)

    def test_budget_allow(self):
        gov = CostGovernor(":memory:", soft_cap=50.0, hard_cap=100.0)
        gov.record_usage("anthropic", "claude-4", 1000, 500, 10.0)
        status = gov.check_budget_status()
        assert status.decision == "ALLOW"
        assert status.current_spend == pytest.approx(10.0)

    def test_budget_warn_at_80_percent(self):
        gov = CostGovernor(":memory:", soft_cap=50.0, hard_cap=100.0)
        gov.record_usage("anthropic", "claude-4", 1000, 500, 42.0)
        status = gov.check_budget_status()
        assert status.decision == "WARN"

    def test_budget_warn_over_soft_cap(self):
        gov = CostGovernor(":memory:", soft_cap=50.0, hard_cap=100.0)
        gov.record_usage("anthropic", "claude-4", 1000, 500, 55.0)
        status = gov.check_budget_status()
        assert status.decision == "WARN"

    def test_budget_deny_over_hard_cap(self):
        gov = CostGovernor(":memory:", soft_cap=50.0, hard_cap=100.0)
        gov.record_usage("anthropic", "claude-4", 1000, 500, 110.0)
        status = gov.check_budget_status()
        assert status.decision == "DENY"

    def test_no_hard_cap(self):
        gov = CostGovernor(":memory:", soft_cap=50.0, hard_cap=None)
        gov.record_usage("anthropic", "claude-4", 1000, 500, 200.0)
        status = gov.check_budget_status()
        # Should be WARN, not DENY (no hard cap)
        assert status.decision == "WARN"

    def test_unsafe_path_rejected(self):
        with pytest.raises(ValueError, match="Unsafe"):
            CostGovernor("../../../etc/passwd")


class TestCostGovernorQueries:
    """Test query methods."""

    def test_spend_by_provider(self):
        gov = CostGovernor(":memory:")
        now = datetime.now(timezone.utc)
        gov.record_usage("anthropic", "claude-4", 1000, 500, 10.0, timestamp=now)
        gov.record_usage("openai", "gpt-4o", 500, 200, 5.0, timestamp=now)

        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59)

        result = gov.get_spend_by_provider("anthropic", start, end)
        assert result["total_cost"] == pytest.approx(10.0)
        assert result["request_count"] == 1

    def test_spend_by_model(self):
        gov = CostGovernor(":memory:")
        now = datetime.now(timezone.utc)
        gov.record_usage("anthropic", "claude-4", 1000, 500, 10.0, timestamp=now)
        gov.record_usage("anthropic", "claude-4", 500, 200, 5.0, timestamp=now)

        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59)

        models = gov.get_spend_by_model(start, end)
        assert len(models) == 1
        assert models[0]["total_cost"] == pytest.approx(15.0)
        assert models[0]["request_count"] == 2

    def test_count(self):
        gov = CostGovernor(":memory:")
        gov.record_usage("anthropic", "claude-4", 1000, 500, 10.0)
        gov.record_usage("openai", "gpt-4o", 500, 200, 5.0)
        assert gov.count() == 2


class TestBudgetAlert:
    """Test budget alert callback."""

    def test_alert_callback_called(self):
        alerts = []
        gov = CostGovernor(
            ":memory:", soft_cap=10.0, hard_cap=20.0,
            on_budget_alert=lambda s: alerts.append(s),
        )
        gov.record_usage("anthropic", "claude-4", 1000, 500, 15.0)
        assert len(alerts) == 1
        assert alerts[0].decision == "WARN"

    def test_no_alert_under_threshold(self):
        alerts = []
        gov = CostGovernor(
            ":memory:", soft_cap=100.0, hard_cap=200.0,
            on_budget_alert=lambda s: alerts.append(s),
        )
        gov.record_usage("anthropic", "claude-4", 1000, 500, 1.0)
        assert len(alerts) == 0


class TestBudgetStatusSerialization:
    """Test BudgetStatus serialization."""

    def test_to_dict(self):
        status = BudgetStatus(
            current_spend=42.0, soft_cap=50.0, hard_cap=100.0,
            currency="USD", threshold_percent=84.0,
            decision="WARN", rationale="test",
        )
        d = status.to_dict()
        assert d["decision"] == "WARN"
        assert d["current_spend"] == 42.0
