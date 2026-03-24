"""Tests for hummbl_governance.capability_fence."""

import threading

from hummbl_governance.capability_fence import (
    CapabilityAuditEntry,
    CapabilityDenied,
    CapabilityFence,
)
from hummbl_governance.delegation import DelegationToken, DelegationTokenManager, TokenBinding


class TestCapabilityDenied:
    """Test CapabilityDenied exception."""

    def test_exception_attributes(self):
        exc = CapabilityDenied("file:write", frozenset(["api:read"]), frozenset(["file:write"]))
        assert exc.capability == "file:write"
        assert "api:read" in exc.allowed
        assert "file:write" in exc.denied

    def test_exception_message(self):
        exc = CapabilityDenied("shell:execute", frozenset(), frozenset(["shell:execute"]))
        assert "shell:execute" in str(exc)

    def test_exception_is_exception(self):
        assert issubclass(CapabilityDenied, Exception)


class TestCapabilityFenceAllowDeny:
    """Test allow/deny resolution logic."""

    def test_allowed_capability_passes(self):
        fence = CapabilityFence(allowed=["api:read", "bus:write"])
        assert fence.check("api:read") is True

    def test_denied_capability_raises(self):
        fence = CapabilityFence(denied=["file:write"])
        try:
            fence.check("file:write")
            assert False, "Should have raised CapabilityDenied"
        except CapabilityDenied as e:
            assert e.capability == "file:write"

    def test_not_in_allowed_raises(self):
        fence = CapabilityFence(allowed=["api:read"])
        try:
            fence.check("file:write")
            assert False, "Should have raised CapabilityDenied"
        except CapabilityDenied:
            pass

    def test_denied_takes_precedence_over_allowed(self):
        fence = CapabilityFence(allowed=["api:read", "file:write"], denied=["file:write"])
        try:
            fence.check("file:write")
            assert False, "Should have raised CapabilityDenied"
        except CapabilityDenied:
            pass

    def test_no_restrictions_allows_all(self):
        fence = CapabilityFence()
        assert fence.check("anything:goes") is True

    def test_empty_allowed_allows_all(self):
        fence = CapabilityFence(allowed=[])
        assert fence.check("anything:goes") is True

    def test_multiple_allowed(self):
        fence = CapabilityFence(allowed=["a:b", "c:d", "e:f"])
        assert fence.check("a:b") is True
        assert fence.check("c:d") is True
        assert fence.check("e:f") is True

    def test_multiple_denied(self):
        fence = CapabilityFence(denied=["a:b", "c:d"])
        try:
            fence.check("a:b")
            assert False
        except CapabilityDenied:
            pass
        try:
            fence.check("c:d")
            assert False
        except CapabilityDenied:
            pass


class TestCapabilityFenceProperties:
    """Test fence property accessors."""

    def test_allowed_property(self):
        fence = CapabilityFence(allowed=["api:read"])
        assert fence.allowed == frozenset(["api:read"])

    def test_denied_property(self):
        fence = CapabilityFence(denied=["file:write"])
        assert fence.denied == frozenset(["file:write"])

    def test_defaults_are_empty(self):
        fence = CapabilityFence()
        assert fence.allowed == frozenset()
        assert fence.denied == frozenset()


class TestCapabilityFenceGuard:
    """Test guard wrapper."""

    def test_guard_executes_on_allowed(self):
        fence = CapabilityFence(allowed=["compute:run"])
        result = fence.guard(lambda x: x * 2, "compute:run", 5)
        assert result == 10

    def test_guard_raises_on_denied(self):
        fence = CapabilityFence(denied=["compute:run"])
        try:
            fence.guard(lambda x: x * 2, "compute:run", 5)
            assert False, "Should have raised CapabilityDenied"
        except CapabilityDenied:
            pass

    def test_guard_passes_kwargs(self):
        fence = CapabilityFence()

        def add(a, b=0):
            return a + b

        result = fence.guard(add, "math:add", 3, b=7)
        assert result == 10

    def test_guard_does_not_call_fn_on_deny(self):
        called = []
        fence = CapabilityFence(denied=["x:y"])

        def side_effect():
            called.append(True)

        try:
            fence.guard(side_effect, "x:y")
        except CapabilityDenied:
            pass
        assert called == []


class TestCapabilityFenceFromToken:
    """Test from_delegation_token factory."""

    def test_creates_fence_from_token(self):
        mgr = DelegationTokenManager(secret=b"test-secret")
        token = mgr.create_token(
            issuer="orchestrator",
            subject="worker",
            ops_allowed=["api:read", "bus:write"],
            binding=TokenBinding(task_id="t1", contract_id="c1"),
        )
        fence = CapabilityFence.from_delegation_token(token)
        assert fence.check("api:read") is True
        assert fence.check("bus:write") is True
        try:
            fence.check("file:write")
            assert False
        except CapabilityDenied:
            pass

    def test_from_token_with_denied(self):
        mgr = DelegationTokenManager(secret=b"test-secret")
        token = mgr.create_token(
            issuer="orchestrator",
            subject="worker",
            ops_allowed=["api:read", "bus:write"],
            binding=TokenBinding(task_id="t1", contract_id="c1"),
        )
        fence = CapabilityFence.from_delegation_token(token, denied=["bus:write"])
        try:
            fence.check("bus:write")
            assert False
        except CapabilityDenied:
            pass

    def test_from_token_with_audit_log(self):
        mgr = DelegationTokenManager(secret=b"test-secret")
        token = mgr.create_token(
            issuer="o", subject="w",
            ops_allowed=["api:read"],
            binding=TokenBinding(task_id="t1", contract_id="c1"),
        )
        log: list[CapabilityAuditEntry] = []
        fence = CapabilityFence.from_delegation_token(token, audit_log=log)
        fence.check("api:read")
        assert len(log) == 1


class TestAuditLogging:
    """Test audit logging of capability checks."""

    def test_allow_logged(self):
        log: list[CapabilityAuditEntry] = []
        fence = CapabilityFence(allowed=["api:read"], audit_log=log)
        fence.check("api:read")
        assert len(log) == 1
        assert log[0].decision == "allow"
        assert log[0].capability == "api:read"

    def test_deny_logged(self):
        log: list[CapabilityAuditEntry] = []
        fence = CapabilityFence(denied=["file:write"], audit_log=log)
        try:
            fence.check("file:write")
        except CapabilityDenied:
            pass
        assert len(log) == 1
        assert log[0].decision == "deny"

    def test_timestamp_present(self):
        log: list[CapabilityAuditEntry] = []
        fence = CapabilityFence(audit_log=log)
        fence.check("x:y")
        assert log[0].timestamp.endswith("Z")

    def test_no_audit_log_by_default(self):
        # Should not raise even without audit_log
        fence = CapabilityFence(allowed=["x:y"])
        fence.check("x:y")

    def test_multiple_checks_logged(self):
        log: list[CapabilityAuditEntry] = []
        fence = CapabilityFence(audit_log=log)
        fence.check("a:b")
        fence.check("c:d")
        assert len(log) == 2


class TestThreadSafety:
    """Test thread safety of CapabilityFence."""

    def test_concurrent_checks(self):
        log: list[CapabilityAuditEntry] = []
        fence = CapabilityFence(allowed=["api:read"], audit_log=log)
        errors: list[Exception] = []

        def worker():
            try:
                for _ in range(50):
                    fence.check("api:read")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        assert len(log) == 200
