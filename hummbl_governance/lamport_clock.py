"""Lamport Clock -- Logical clock for causal ordering of distributed events.

Implements Lamport's (1978) logical clock algorithm for establishing
total causal ordering of events in a distributed multi-agent system
where wall clocks may disagree or have insufficient resolution.

Each message gets a monotonically increasing sequence number. When an
agent receives a message, it advances its clock to max(local, received) + 1.
This guarantees: if event A happened-before event B, then clock(A) < clock(B).

Usage::

    from hummbl_governance.lamport_clock import LamportClock

    clock = LamportClock()
    t1 = clock.tick()        # Local event: 1
    t2 = clock.tick()        # Local event: 2
    t3 = clock.receive(10)   # Received msg with ts=10: max(2,10)+1 = 11
    t4 = clock.tick()        # Local event: 12

Stdlib-only. Thread-safe.

Reference:
    Lamport, L. (1978). Time, Clocks, and the Ordering of Events in a
    Distributed System. Communications of the ACM, 21(7), 558-565.
    DOI: 10.1145/359545.359563
"""

from __future__ import annotations

import threading


class LamportClock:
    """Thread-safe Lamport logical clock.

    Args:
        initial: Starting value for the clock (default 0).
        agent_id: Optional identifier for tie-breaking when two events
            have the same logical timestamp. Lamport's algorithm uses
            process IDs for total ordering.
    """

    def __init__(self, initial: int = 0, agent_id: str = "") -> None:
        self._counter = initial
        self._agent_id = agent_id
        self._lock = threading.Lock()

    @property
    def value(self) -> int:
        """Current clock value (read without advancing)."""
        with self._lock:
            return self._counter

    @property
    def agent_id(self) -> str:
        """Agent identifier used for tie-breaking."""
        return self._agent_id

    def tick(self) -> int:
        """Record a local event. Increments and returns the new clock value."""
        with self._lock:
            self._counter += 1
            return self._counter

    def receive(self, remote_timestamp: int) -> int:
        """Update clock on receiving a message from another agent.

        Sets local clock to max(local, remote) + 1.

        Args:
            remote_timestamp: The logical timestamp from the received message.

        Returns:
            The updated local clock value.
        """
        with self._lock:
            self._counter = max(self._counter, remote_timestamp) + 1
            return self._counter

    def stamp(self) -> tuple[int, str]:
        """Generate a (timestamp, agent_id) pair for total ordering.

        Two events with the same Lamport timestamp are concurrent.
        The agent_id breaks ties for a total order.

        Returns:
            Tuple of (logical_timestamp, agent_id).
        """
        ts = self.tick()
        return (ts, self._agent_id)

    @staticmethod
    def happened_before(
        a: tuple[int, str], b: tuple[int, str]
    ) -> bool | None:
        """Compare two stamped events for causal ordering.

        Args:
            a: (timestamp, agent_id) from event A.
            b: (timestamp, agent_id) from event B.

        Returns:
            True if A happened before B, False if B happened before A,
            None if events are concurrent (same timestamp, different agents).
        """
        ts_a, id_a = a
        ts_b, id_b = b
        if ts_a < ts_b:
            return True
        if ts_a > ts_b:
            return False
        # Same timestamp: use agent_id for total ordering
        if id_a == id_b:
            return None  # Same agent, same timestamp — should not happen
        return id_a < id_b
