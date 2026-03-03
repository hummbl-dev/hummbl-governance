"""Tests for CircuitBreaker.

Coverage of state transitions, threshold tripping, timeout recovery,
HALF_OPEN probe behavior, callbacks, manual reset, and thread safety.
"""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from hummbl_governance.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpen,
    CircuitBreakerState,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _succeed() -> str:
    return "ok"


def _fail() -> None:
    raise RuntimeError("boom")


def _fail_value_error() -> None:
    raise ValueError("bad value")


# ---------------------------------------------------------------------------
# CircuitBreakerState enum
# ---------------------------------------------------------------------------

class TestCircuitBreakerState:

    def test_state_values_are_unique(self):
        values = [s.value for s in CircuitBreakerState]
        assert len(values) == len(set(values))

    def test_state_names(self):
        assert CircuitBreakerState.CLOSED.name == "CLOSED"
        assert CircuitBreakerState.OPEN.name == "OPEN"
        assert CircuitBreakerState.HALF_OPEN.name == "HALF_OPEN"

    def test_three_states_exist(self):
        assert len(CircuitBreakerState) == 3


# ---------------------------------------------------------------------------
# CircuitBreakerOpen exception
# ---------------------------------------------------------------------------

class TestCircuitBreakerOpen:

    def test_basic_creation(self):
        exc = CircuitBreakerOpen("test message")
        assert str(exc) == "test message"
        assert exc.failure_count == 0
        assert exc.last_failure_time is None
        assert exc.recovery_timeout == 0.0

    def test_creation_with_details(self):
        exc = CircuitBreakerOpen(
            "open",
            failure_count=5,
            last_failure_time=12345.0,
            recovery_timeout=30.0,
        )
        assert exc.failure_count == 5
        assert exc.last_failure_time == 12345.0
        assert exc.recovery_timeout == 30.0

    def test_is_exception(self):
        assert issubclass(CircuitBreakerOpen, Exception)


# ---------------------------------------------------------------------------
# CircuitBreaker construction
# ---------------------------------------------------------------------------

class TestCircuitBreakerInit:

    def test_defaults(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.last_failure_time is None

    def test_custom_params(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
        assert cb._failure_threshold == 3
        assert cb._recovery_timeout == 10.0

    def test_invalid_failure_threshold_zero(self):
        with pytest.raises(ValueError, match="failure_threshold"):
            CircuitBreaker(failure_threshold=0)

    def test_invalid_failure_threshold_negative(self):
        with pytest.raises(ValueError, match="failure_threshold"):
            CircuitBreaker(failure_threshold=-1)

    def test_invalid_recovery_timeout_negative(self):
        with pytest.raises(ValueError, match="recovery_timeout"):
            CircuitBreaker(recovery_timeout=-1.0)

    def test_recovery_timeout_zero_is_allowed(self):
        cb = CircuitBreaker(recovery_timeout=0.0)
        assert cb._recovery_timeout == 0.0

    def test_callback_stored(self):
        cb_fn = MagicMock()
        cb = CircuitBreaker(on_state_change=cb_fn)
        assert cb._on_state_change is cb_fn


# ---------------------------------------------------------------------------
# CLOSED state behavior
# ---------------------------------------------------------------------------

class TestClosedState:

    def test_call_succeeds(self):
        cb = CircuitBreaker(failure_threshold=3)
        result = cb.call(_succeed)
        assert result == "ok"

    def test_call_with_args(self):
        cb = CircuitBreaker()
        result = cb.call(lambda x, y: x + y, 3, 4)
        assert result == 7

    def test_call_with_kwargs(self):
        cb = CircuitBreaker()
        result = cb.call(lambda *, name: f"hello {name}", name="world")
        assert result == "hello world"

    def test_success_increments_count(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.call(_succeed)
        cb.call(_succeed)
        assert cb.success_count == 2

    def test_failure_increments_count(self):
        cb = CircuitBreaker(failure_threshold=3)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb.failure_count == 1
        assert cb.last_failure_time is not None

    def test_failure_reraises_original_exception(self):
        cb = CircuitBreaker(failure_threshold=3)
        with pytest.raises(RuntimeError, match="boom"):
            cb.call(_fail)

    def test_failure_different_exception_types(self):
        cb = CircuitBreaker(failure_threshold=3)
        with pytest.raises(ValueError, match="bad value"):
            cb.call(_fail_value_error)

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(2):
            with pytest.raises(RuntimeError):
                cb.call(_fail)
        assert cb.failure_count == 2
        cb.call(_succeed)
        assert cb.failure_count == 0

    def test_stays_closed_below_threshold(self):
        cb = CircuitBreaker(failure_threshold=5)
        for _ in range(4):
            with pytest.raises(RuntimeError):
                cb.call(_fail)
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 4


# ---------------------------------------------------------------------------
# Threshold tripping: CLOSED -> OPEN
# ---------------------------------------------------------------------------

class TestThresholdTripping:

    def test_trips_at_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            with pytest.raises(RuntimeError):
                cb.call(_fail)
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3

    def test_trips_at_threshold_one(self):
        cb = CircuitBreaker(failure_threshold=1)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb.state == CircuitBreakerState.OPEN

    def test_rejects_after_tripping(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60.0)
        for _ in range(2):
            with pytest.raises(RuntimeError):
                cb.call(_fail)
        with pytest.raises(CircuitBreakerOpen) as exc_info:
            cb.call(_succeed)
        assert exc_info.value.failure_count == 2
        assert exc_info.value.recovery_timeout == 60.0

    def test_open_exception_has_metadata(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=42.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        with pytest.raises(CircuitBreakerOpen) as exc_info:
            cb.call(_succeed)
        exc = exc_info.value
        assert exc.failure_count == 1
        assert exc.last_failure_time is not None
        assert exc.recovery_timeout == 42.0
        assert "open" in str(exc).lower()


# ---------------------------------------------------------------------------
# Timeout recovery: OPEN -> HALF_OPEN
# ---------------------------------------------------------------------------

class TestTimeoutRecovery:

    def test_transitions_to_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb.state == CircuitBreakerState.OPEN
        time.sleep(0.1)
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_stays_open_before_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb.state == CircuitBreakerState.OPEN

    def test_recovery_timeout_zero_transitions_immediately(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb.state == CircuitBreakerState.HALF_OPEN


# ---------------------------------------------------------------------------
# HALF_OPEN probe behavior
# ---------------------------------------------------------------------------

class TestHalfOpenProbe:

    def _make_open_breaker(self, recovery_timeout: float = 0.0) -> CircuitBreaker:
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=recovery_timeout)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        if recovery_timeout > 0:
            time.sleep(recovery_timeout + 0.05)
        return cb

    def test_probe_success_resets_to_closed(self):
        cb = self._make_open_breaker()
        result = cb.call(_succeed)
        assert result == "ok"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_probe_failure_returns_to_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        with patch("hummbl_governance.circuit_breaker.time") as mock_time:
            mock_time.monotonic.return_value = time.monotonic() + 61.0
            assert cb.state == CircuitBreakerState.HALF_OPEN
            mock_time.monotonic.return_value = time.monotonic() + 61.0
            with pytest.raises(RuntimeError):
                cb.call(_fail)
            mock_time.monotonic.return_value = time.monotonic() + 61.0
            assert cb._state == CircuitBreakerState.OPEN

    def test_probe_success_clears_last_failure_time(self):
        cb = self._make_open_breaker()
        cb.call(_succeed)
        assert cb.last_failure_time is None

    def test_probe_success_preserves_total_success_count(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.call(_succeed)
        cb.call(_succeed)
        for _ in range(2):
            with pytest.raises(RuntimeError):
                cb.call(_fail)
        time.sleep(0.01)
        with patch("hummbl_governance.circuit_breaker.time") as mock_time:
            mock_time.monotonic.return_value = time.monotonic() + 31.0
            cb.call(_succeed)
        assert cb.success_count == 3


# ---------------------------------------------------------------------------
# on_state_change callback
# ---------------------------------------------------------------------------

class TestStateChangeCallback:

    def test_callback_on_trip(self):
        transitions = []
        cb = CircuitBreaker(
            failure_threshold=2,
            on_state_change=lambda old, new: transitions.append((old, new)),
        )
        for _ in range(2):
            with pytest.raises(RuntimeError):
                cb.call(_fail)
        assert len(transitions) == 1
        assert transitions[0] == (CircuitBreakerState.CLOSED, CircuitBreakerState.OPEN)

    def test_callback_on_half_open(self):
        transitions = []
        cb = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.0,
            on_state_change=lambda old, new: transitions.append((old, new)),
        )
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert (CircuitBreakerState.CLOSED, CircuitBreakerState.OPEN) in transitions
        cb.call(_succeed)
        assert (CircuitBreakerState.OPEN, CircuitBreakerState.HALF_OPEN) in transitions
        assert (CircuitBreakerState.HALF_OPEN, CircuitBreakerState.CLOSED) in transitions

    def test_callback_on_manual_reset(self):
        transitions = []
        cb = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=60.0,
            on_state_change=lambda old, new: transitions.append((old, new)),
        )
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        transitions.clear()
        cb.reset()
        assert (CircuitBreakerState.OPEN, CircuitBreakerState.CLOSED) in transitions

    def test_callback_error_is_swallowed(self):
        def bad_callback(old, new):
            raise ValueError("callback error")
        cb = CircuitBreaker(failure_threshold=1, on_state_change=bad_callback)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb._state == CircuitBreakerState.OPEN

    def test_no_callback_when_none(self):
        cb = CircuitBreaker(failure_threshold=1, on_state_change=None)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb._state == CircuitBreakerState.OPEN

    def test_callback_not_fired_on_redundant_reset(self):
        transitions = []
        cb = CircuitBreaker(
            on_state_change=lambda old, new: transitions.append((old, new)),
        )
        cb.reset()
        assert len(transitions) == 0


# ---------------------------------------------------------------------------
# Manual reset
# ---------------------------------------------------------------------------

class TestManualReset:

    def test_reset_from_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb.state == CircuitBreakerState.OPEN
        cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.last_failure_time is None

    def test_reset_from_closed(self):
        cb = CircuitBreaker()
        cb.call(_succeed)
        cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.success_count == 0

    def test_reset_allows_calls_again(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        with pytest.raises(CircuitBreakerOpen):
            cb.call(_succeed)
        cb.reset()
        assert cb.call(_succeed) == "ok"

    def test_reset_from_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb.state == CircuitBreakerState.HALF_OPEN
        cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------

class TestThreadSafety:

    def test_concurrent_successes(self):
        cb = CircuitBreaker(failure_threshold=100)
        barrier = threading.Barrier(10)
        errors = []

        def worker():
            try:
                barrier.wait(timeout=5)
                for _ in range(50):
                    cb.call(_succeed)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors
        assert cb.success_count == 500
        assert cb.state == CircuitBreakerState.CLOSED

    def test_concurrent_failures_trip_exactly_once(self):
        transitions = []
        lock = threading.Lock()

        def record_transition(old, new):
            with lock:
                transitions.append((old, new))

        cb = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0,
            on_state_change=record_transition,
        )
        barrier = threading.Barrier(10)
        errors = []

        def worker():
            try:
                barrier.wait(timeout=5)
                for _ in range(5):
                    try:
                        cb.call(_fail)
                    except (RuntimeError, CircuitBreakerOpen):
                        pass
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors
        trip_transitions = [
            t
            for t in transitions
            if t == (CircuitBreakerState.CLOSED, CircuitBreakerState.OPEN)
        ]
        assert len(trip_transitions) == 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_callable_returning_none(self):
        cb = CircuitBreaker()
        result = cb.call(lambda: None)
        assert result is None

    def test_callable_returning_falsy(self):
        cb = CircuitBreaker()
        assert cb.call(lambda: 0) == 0
        assert cb.call(lambda: "") == ""
        assert cb.call(lambda: []) == []

    def test_state_property_reflects_effective_state(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb._state == CircuitBreakerState.OPEN
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_multiple_trips_and_resets(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.0)
        for cycle in range(3):
            for _ in range(2):
                with pytest.raises(RuntimeError):
                    cb.call(_fail)
            assert cb.state in (
                CircuitBreakerState.OPEN,
                CircuitBreakerState.HALF_OPEN,
            ), f"Cycle {cycle}: expected OPEN or HALF_OPEN"
            cb.reset()
            assert cb.state == CircuitBreakerState.CLOSED

    def test_interleaved_success_and_failure(self):
        cb = CircuitBreaker(failure_threshold=3)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        cb.call(_succeed)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        cb.call(_succeed)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        assert cb.state == CircuitBreakerState.CLOSED

    def test_open_breaker_does_not_call_fn(self):
        call_count = 0

        def counting_fn():
            nonlocal call_count
            call_count += 1
            return "ok"

        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        with pytest.raises(CircuitBreakerOpen):
            cb.call(counting_fn)
        assert call_count == 0

    def test_half_open_probe_failure_updates_last_failure_time(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.0)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        first_failure_time = cb.last_failure_time
        time.sleep(0.01)
        with pytest.raises(RuntimeError):
            cb.call(_fail)
        second_failure_time = cb.last_failure_time
        assert second_failure_time is not None
        assert first_failure_time is not None
        assert second_failure_time > first_failure_time


class TestTopLevelImport:
    """Test top-level package imports."""

    def test_import_circuit_breaker(self):
        from hummbl_governance import CircuitBreaker, CircuitBreakerOpen, CircuitBreakerState

        cb = CircuitBreaker(failure_threshold=1)
        assert cb.state == CircuitBreakerState.CLOSED
        assert issubclass(CircuitBreakerOpen, Exception)
