#!/usr/bin/env python3
"""Canonical bus write surface for local founder-mode tooling."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import importlib.util
import sys
from pathlib import Path

try:
    from .. import state_authority
except Exception:  # pragma: no cover - direct script execution
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.append(str(repo_root))
    authority_path = repo_root / "founder_mode" / "state_authority.py"
    authority_spec = importlib.util.spec_from_file_location("founder_mode.state_authority", authority_path)
    if authority_spec is None or authority_spec.loader is None:
        raise
    state_authority = importlib.util.module_from_spec(authority_spec)
    sys.modules["founder_mode.state_authority"] = state_authority
    authority_spec.loader.exec_module(state_authority)


def fallback_bus_line(
    sender: str,
    recipient: str,
    msg_type: str,
    message: str,
) -> str:
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    safe_message = (message or "").replace("\r\n", "\\n").replace("\n", "\\n").replace("\t", " ")
    return f"{ts}\t{sender}\t{recipient}\t{msg_type}\t{safe_message}\n"


def read_body() -> str:
    import sys

    stdin = sys.stdin.read().strip()
    return stdin


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post a canonical bus message")
    parser.add_argument("--sender", required=True, help="Identity posting on the bus")
    parser.add_argument("--to", default="all", help="Recipient")
    parser.add_argument("--type", default="STATUS", help="Message type")
    parser.add_argument("--message", default="", help="Payload message")
    parser.add_argument("--bus-path", default=None, help="Output TSV bus path")
    parser.add_argument("--json", action="store_true", help="Emit JSON receipt")
    parser.add_argument("--dry-run", action="store_true", help="Do not write")
    return parser.parse_args()


def resolve_bus_path(cli_path: str | None) -> Path:
    if cli_path:
        return Path(cli_path)
    env_path = os.getenv("HUMMBL_BUS_PATH") or os.getenv("AGENT_TOOLSET_BUS_PATH")
    if env_path:
        return Path(env_path)
    return Path("_receipts") / "bus.tsv"


def post_bus_line(line: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fp:
        fp.write(line)


def main() -> int:
    args = parse_args()
    state_authority.require_bus_sender(args.sender)
    state_authority.require_actor("bus_write")
    message = args.message or read_body()
    if not message:
        message = "(no message)"
    try:
        from hummbl_governance.coordination_bus import BusWriter

        writer = BusWriter(resolve_bus_path(args.bus_path))
        writer.post(
            from_id=args.sender,
            to_id=args.to,
            msg_type=args.type,
            message=message,
        )
        line = None
    except Exception:
        line = fallback_bus_line(args.sender, args.to, args.type, message)

    if args.dry_run:
        if args.json:
            print(json.dumps({"dry_run": True, "line": line}))
        else:
            print("DRY RUN:")
            print(line or "bus writer call only")
        return 0

    if line is not None:
        bus_path = resolve_bus_path(args.bus_path)
        post_bus_line(line, bus_path)
    if args.json:
        print(json.dumps({"status": "posted", "bus_path": str(resolve_bus_path(args.bus_path))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
