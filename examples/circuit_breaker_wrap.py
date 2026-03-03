#!/usr/bin/env python3
"""Circuit Breaker: Wrap an unreliable service with automatic failure detection.

Demonstrates the three-state circuit breaker pattern:
CLOSED (normal) -> OPEN (tripped) -> HALF_OPEN (testing) -> CLOSED (recovered).
"""

import random
from hummbl_governance import CircuitBreaker, CircuitBreakerOpen, CircuitBreakerState


def unreliable_api_call() -> str:
    """Simulates an API that fails 60% of the time."""
    if random.random() < 0.6:
        raise ConnectionError("Service unavailable")
    return "OK"


# Create breaker: trips after 3 failures, recovers after 2 seconds
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2.0)

print(f"Initial state: {breaker.state.name}")

for i in range(10):
    try:
        result = breaker.call(unreliable_api_call)
        print(f"  Call {i+1}: {result} (failures={breaker.failure_count})")
    except CircuitBreakerOpen as e:
        print(f"  Call {i+1}: BLOCKED - breaker is {breaker.state.name}")
    except ConnectionError:
        print(f"  Call {i+1}: FAILED  (failures={breaker.failure_count}, state={breaker.state.name})")

print(f"\nFinal state: {breaker.state.name}")
print(f"Total failures: {breaker.failure_count}")
