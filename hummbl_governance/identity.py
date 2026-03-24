"""Agent Identity Registry -- Configurable agent identity, aliases, and trust tiers.

Provides a generic agent registry for multi-agent systems. Agents have
canonical names, display names, trust tiers, and status. Aliases map
variant identifiers to canonical names.

Usage:
    from hummbl_governance import AgentRegistry

    registry = AgentRegistry()
    registry.register_agent("orchestrator", display="Orchestrator", trust="high")
    registry.register_agent("worker", display="Worker", trust="medium")
    registry.add_alias("worker-1", "worker")
    registry.add_alias("worker-2", "worker")

    canonical = registry.canonicalize("worker-1")  # -> "worker"
    tier = registry.get_trust_tier("worker-1")      # -> "medium"

Stdlib-only. Zero third-party dependencies.
"""

from __future__ import annotations

from typing import Any


class AgentRegistry:
    """Configurable agent identity registry.

    Manages canonical agent identities, aliases, autonomous services,
    deprecated identities, and retired agents.

    Args:
        agents: Initial dict of canonical agents.
            Format: {"name": {"display": "...", "trust": "...", "status": "..."}}
        aliases: Initial dict of alias -> canonical name mappings.
        services: Initial set of autonomous service names.
        deprecated: Initial set of deprecated/junk identity names.
        retired: Initial dict of retired agent -> reason mappings.
    """

    def __init__(
        self,
        agents: dict[str, dict[str, str]] | None = None,
        aliases: dict[str, str] | None = None,
        services: set[str] | None = None,
        deprecated: set[str] | None = None,
        retired: dict[str, str] | None = None,
    ):
        self._agents: dict[str, dict[str, str]] = dict(agents) if agents else {}
        self._aliases: dict[str, str] = dict(aliases) if aliases else {}
        self._services: set[str] = set(services) if services else set()
        self._deprecated: set[str] = set(deprecated) if deprecated else set()
        self._retired: dict[str, str] = dict(retired) if retired else {}

    def register_agent(
        self,
        name: str,
        display: str | None = None,
        trust: str = "medium",
        status: str = "active",
    ) -> None:
        """Register a canonical agent identity.

        Args:
            name: Canonical agent name (lowercase recommended).
            display: Human-readable display name (defaults to name.title()).
            trust: Trust tier (e.g., "owner", "high", "medium", "low", "system").
            status: Agent status (e.g., "active", "probation", "suspended").
        """
        self._agents[name] = {
            "display": display or name.title(),
            "trust": trust,
            "status": status,
        }

    def unregister_agent(self, name: str) -> None:
        """Remove a canonical agent identity."""
        self._agents.pop(name, None)

    def add_alias(self, alias: str, canonical: str) -> None:
        """Map an alias to a canonical agent name."""
        self._aliases[alias] = canonical

    def remove_alias(self, alias: str) -> None:
        """Remove an alias mapping."""
        self._aliases.pop(alias, None)

    def add_service(self, name: str) -> None:
        """Register an autonomous service as a valid sender."""
        self._services.add(name)

    def remove_service(self, name: str) -> None:
        """Unregister an autonomous service."""
        self._services.discard(name)

    def add_deprecated(self, name: str) -> None:
        """Mark an identity as deprecated/junk."""
        self._deprecated.add(name)

    def retire_agent(self, name: str, reason: str) -> None:
        """Retire an agent with a reason."""
        self._retired[name] = reason

    def canonicalize(self, sender: str) -> str:
        """Map a sender to its canonical identity.

        Resolution order:
        1. Direct alias match (exact, then case-insensitive)
        2. Base name (before parenthetical) alias match
        3. Autonomous service match
        4. Canonical agent match
        5. Returns original sender if unknown
        """
        sender = sender.strip()
        if not sender:
            return sender

        # Base name (strip parenthetical)
        base = sender.split("(", 1)[0].strip() if "(" in sender else sender
        candidates = [sender, base] if base != sender else [sender]

        # 1. Alias lookup
        result = self._lookup_alias(candidates)
        if result is not None:
            return result

        # 2. Set membership lookup (services, then agents)
        result = self._lookup_in_set(candidates, self._services)
        if result is not None:
            return result
        result = self._lookup_in_set(candidates, self._agents)
        if result is not None:
            return result

        return sender

    @staticmethod
    def _lookup_in_set(candidates: list[str], registry: dict | set) -> str | None:
        """Find the first candidate present in a registry (exact or case-insensitive)."""
        for name in candidates:
            if name in registry:
                return name
            if name.lower() in registry:
                return name.lower()
        return None

    def _lookup_alias(self, candidates: list[str]) -> str | None:
        """Find the first candidate that matches an alias (exact or case-insensitive)."""
        for name in candidates:
            if name in self._aliases:
                return self._aliases[name]
            name_lower = name.lower()
            if name_lower in self._aliases:
                return self._aliases[name_lower]
            for alias_key, canonical in self._aliases.items():
                if alias_key.lower() == name_lower:
                    return canonical
        return None

    def is_valid_sender(self, sender: str) -> bool:
        """Check if a sender is a known identity."""
        sender = sender.strip()
        return (
            sender in self._agents
            or sender in self._aliases
            or sender in self._services
            or self.canonicalize(sender) != sender
        )

    def is_deprecated(self, sender: str) -> bool:
        """Check if a sender is a known deprecated/junk identity."""
        return sender.strip() in self._deprecated

    def get_trust_tier(self, sender: str) -> str:
        """Get trust tier for a sender. Returns 'unknown' for unrecognized."""
        canonical = self.canonicalize(sender)
        if canonical in self._agents:
            return self._agents[canonical]["trust"]
        if canonical in self._services:
            return "system"
        return "unknown"

    def get_status(self, sender: str) -> str:
        """Return registry status for a sender."""
        canonical = self.canonicalize(sender)
        if canonical in self._agents:
            return self._agents[canonical]["status"]
        if canonical in self._services:
            return "active"
        stripped = sender.strip()
        if canonical in self._retired or stripped in self._retired:
            return "retired"
        if self.is_deprecated(sender):
            return "deprecated"
        return "unknown"

    def get_known_senders(self) -> set[str]:
        """Return the set of all known sender identifiers."""
        known = set(self._agents)
        known.update(self._aliases)
        known.update(self._services)
        known.update(self._retired)
        return known

    def get_agents(self) -> dict[str, dict[str, str]]:
        """Return a copy of the canonical agents dict."""
        return dict(self._agents)

    def get_aliases(self) -> dict[str, str]:
        """Return a copy of the aliases dict."""
        return dict(self._aliases)

    def to_dict(self) -> dict[str, Any]:
        """Serialize registry to dictionary."""
        return {
            "agents": dict(self._agents),
            "aliases": dict(self._aliases),
            "services": sorted(self._services),
            "deprecated": sorted(self._deprecated),
            "retired": dict(self._retired),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentRegistry:
        """Deserialize registry from dictionary."""
        return cls(
            agents=data.get("agents"),
            aliases=data.get("aliases"),
            services=set(data.get("services", [])),
            deprecated=set(data.get("deprecated", [])),
            retired=data.get("retired"),
        )
