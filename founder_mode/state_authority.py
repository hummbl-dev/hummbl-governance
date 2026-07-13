"""Authority checks and actor gate definitions for local automation."""

from __future__ import annotations

import os
from typing import Iterable


DEFAULT_AUTHORIZED_ACTORS = {
    "codex",
    "hummbl-governance",
    "codex-governance",
    "founder-mode-bot",
}


def _env_set(env_name: str, fallback: Iterable[str]) -> set[str]:
    value = os.getenv(env_name, "")
    if not value:
        return set(fallback)
    return {item.strip() for item in value.split(",") if item.strip()}


def current_actor() -> str:
    return os.getenv("HUMMBL_ACTOR", os.getenv("GIT_AUTHOR_NAME", "codex"))


def allowed_actors() -> set[str]:
    return _env_set("HUMMBL_ALLOWED_ACTORS", DEFAULT_AUTHORIZED_ACTORS)


def allowed_actions() -> set[str]:
    return _env_set(
        "HUMMBL_ALLOWED_ACTIONS",
        {
            "bus_write",
            "bus_verify",
            "health_check",
            "quality_check",
            "claim_scan",
            "dependency_scan",
        },
    )


def actor_is_allowed(actor: str) -> bool:
    return actor in allowed_actors()


def action_is_allowed(action: str) -> bool:
    return action in allowed_actions()


def require_actor(action: str) -> None:
    actor = current_actor()
    if not actor_is_allowed(actor):
        raise PermissionError(f"actor not authorized: {actor}")
    if not action_is_allowed(action):
        raise PermissionError(f"action not authorized for actor {actor}: {action}")


def require_bus_sender(sender: str) -> None:
    if sender in {"", "unknown", "None"}:
        raise PermissionError("bus sender not provided")
    if not actor_is_allowed(sender):
        raise PermissionError(f"unauthorized bus sender: {sender}")
