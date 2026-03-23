"""Tests for hummbl_governance.circuit_breaker."""

import time

import pytest

from hummbl_governance.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpen,
    CircuitBreakerState,
)


def _failing_fn():
    raise RuntimeError("service down")


class TestCircuitBreakerBasic:
    def test_starts_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_successful_call(self):
        cb = CircuitBreaker()
        result = cb.call(lambda: 42)
        assert result == 42
        assert cb.success_count == 1
        assert cb.failure_count == 0

    def test_call_with_args(self):
        cb = CircuitBreaker()
        result = cb.call(lambda x, y: x + y, 3, 4)
        assert result == 7

    def test_call_with_kwargs(self):
        cb = CircuitBreaker()
        result = cb.call(lambda x, y=10: x + y, 5, y=20)
        assert result == 25

    def test_invalid_threshold(self):
        with pytest.raises(ValueError):
            CircuitBreaker(failure_threshold=0)

    def test_invalid_timeout(self):
        with pytest.raises(ValueError):
            CircuitBreaker(recovery_timeout=-1)


class TestStateTransitions:
    def test_trips_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            with pytest.raises(RuntimeError):
                cb.call(_failing_fn)
        assert cb.state == CircuitBreakerState.OPEN

    def test_open_rejects_calls(self):
        cb = CircuitBreaker(failure_threshold=1)
        with pytest.raises(RuntimeError):
            cb.call(_failing_fn)
        with pytest.raises(CircuitBreakerOpen):
            cb.call(lambda: 42)

    def test_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        with pytest.raises(RuntimeError):
            cb.call(_failing_fn)
        assert cb.state == CircuitBreakerState.OPEN
        time.sleep(0.02)
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_half_open_success_closes(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        with pytest.raises(RuntimeError):
            cb.call(_failing_fn)
        time.sleep(0.02)
        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.state == CircuitBreakerState.CLOSED

    def test_half_open_failure_reopens(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        with pytest.raises(RuntimeError):
            cb.call(_failing_fn)
        time.sleep(0.02)
        with pytest.raises(RuntimeError):
            cb.call(_failing_fn)
        assert cb.state == CircuitBreakerState.OPEN

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=1)
        with pytest.raises(RuntimeError):
            cb.call(_failing_fn)
        assert cb.state == CircuitBreakerState.OPEN
        cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(2):
            with pytest.raises(RuntimeError):
                cb.call(_failing_fn)
        assert cb.failure_count == 2
        cb.call(lambda: "ok")
        assert cb.failure_count == 0


class TestStateChangeCallback:
    def test_callback_on_open(self):
        transitions = []
        cb = CircuitBreaker(
            failure_threshold=1,
            on_state_change=lambda old, new: transitions.append((old, new)),
        )
        with pytest.raises(RuntimeError):
            cb.call(_failing_fn)
        assert len(transitions) == 1
        assert transitions[0] == (CircuitBreakerState.CLOSED, CircuitBreakerState.OPEN)

    def test_callback_error_swallowed(self):
        def bad_callback(old, new):
            raise RuntimeError("callback error")
        cb = CircuitBreaker(failure_threshold=1, on_state_change=bad_callback)
        with pytest.raises(RuntimeError, match="service down"):
            cb.call(_failing_fn)
        assert cb.state == CircuitBreakerState.OPEN

    def test_callback_on_reset(self):
        transitions = []
        cb = CircuitBreaker(
            failure_threshold=1,
            on_state_change=lambda old, new: transitions.append((old, new)),
        )
        with pytest.raises(RuntimeError):
            cb.call(_failing_fn)
        transitions.clear()
        cb.reset()
        assert (CircuitBreakerState.OPEN, CircuitBreakerState.CLOSED) in transitions


class TestCircuitBreakerOpenException:
    def test_attributes(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=30.0)
        with pytest.raises(RuntimeError):
            cb.call(_failing_fn)
        with pytest.raises(CircuitBreakerOpen) as exc_info:
            cb.call(lambda: 42)
        assert exc_info.value.failure_count == 1
        assert exc_info.value.recovery_timeout == 30.0
        assert exc_info.value.last_failure_time is not None
