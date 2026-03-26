#!/usr/bin/env python3
"""MCP Server for Agent Sandboxing.

Combines kill switch, circuit breaker, capability fence, and output validator
into a unified sandboxing service. "Run any agent inside HUMMBL guardrails."

Inspired by Cloudflare Dynamic Workers + NVIDIA OpenShell patterns.

Tools:
    sandbox_create    - Create a sandbox with policy constraints
    sandbox_check     - Check if an action is allowed within a sandbox
    sandbox_validate  - Validate agent output against rules
    sandbox_status    - Get sandbox state (all primitives)
    sandbox_destroy   - Tear down a sandbox and emit audit receipt
"""

import json
import os
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hummbl_governance import (
    KillSwitch,
    CircuitBreaker,
)

try:
    from hummbl_governance.capability_fence import CapabilityFence
except ImportError:
    CapabilityFence = None

try:
    from hummbl_governance.output_validator import OutputValidator
except ImportError:
    OutputValidator = None

from hummbl_governance import AuditLog

SERVER_NAME = "agent-sandbox"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2024-11-05"

STATE_DIR = Path(os.environ.get("SANDBOX_STATE_DIR", "/tmp/hummbl-sandbox"))

# Active sandboxes
_sandboxes = {}


class Sandbox:
    """An isolated governance context for an agent."""

    def __init__(self, sandbox_id, agent_name, allowed_tools=None,
                 blocked_paths=None, max_cost=10.0, timeout_sec=300):
        self.id = sandbox_id
        self.agent = agent_name
        self.allowed_tools = set(allowed_tools or [])
        self.blocked_paths = set(blocked_paths or [])
        self.max_cost = max_cost
        self.timeout_sec = timeout_sec
        self.created_at = datetime.now(timezone.utc)
        self.actions = []
        self.cost_spent = 0.0

        state_dir = STATE_DIR / sandbox_id
        state_dir.mkdir(parents=True, exist_ok=True)

        self.kill_switch = KillSwitch(state_dir=state_dir)
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
        self.audit = AuditLog(base_dir=str(state_dir / "audit"))

    def check_action(self, tool, path=None, cost=0.0):
        """Check if an action is allowed."""
        reasons = []

        # Kill switch
        if self.kill_switch.engaged:
            return {"allowed": False, "reason": f"Kill switch engaged: {self.kill_switch.mode}"}

        # Circuit breaker
        if hasattr(self.circuit_breaker, 'state') and self.circuit_breaker.state.name == "OPEN":
            return {"allowed": False, "reason": "Circuit breaker OPEN — too many failures"}

        # Tool allowlist
        if self.allowed_tools and tool not in self.allowed_tools:
            reasons.append(f"Tool '{tool}' not in allowed set: {sorted(self.allowed_tools)}")

        # Path blocklist
        if path:
            for bp in self.blocked_paths:
                if path.startswith(bp):
                    reasons.append(f"Path '{path}' is in blocked scope: {bp}")

        # Cost cap
        if self.cost_spent + cost > self.max_cost:
            reasons.append(f"Cost ${self.cost_spent + cost:.2f} would exceed cap ${self.max_cost:.2f}")

        if reasons:
            return {"allowed": False, "reasons": reasons}

        self.cost_spent += cost
        self.actions.append({
            "tool": tool, "path": path, "cost": cost,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return {"allowed": True, "cost_remaining": round(self.max_cost - self.cost_spent, 2)}

    def to_dict(self):
        return {
            "id": self.id,
            "agent": self.agent,
            "created_at": self.created_at.isoformat(),
            "allowed_tools": sorted(self.allowed_tools) if self.allowed_tools else "all",
            "blocked_paths": sorted(self.blocked_paths),
            "max_cost": self.max_cost,
            "cost_spent": round(self.cost_spent, 2),
            "actions_count": len(self.actions),
            "kill_switch": (
                self.kill_switch.mode.name
                if hasattr(self.kill_switch.mode, "name")
                else str(self.kill_switch.mode)
            ),
            "circuit_breaker": (
                self.circuit_breaker.state.name
                if hasattr(self.circuit_breaker.state, "name")
                else str(self.circuit_breaker.state)
            ),
        }


TOOLS = [
    {
        "name": "sandbox_create",
        "description": (
            "Create an isolated sandbox for an agent with policy constraints"
            " (tool allowlist, path blocklist, cost cap)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_name": {"type": "string", "description": "Agent identity"},
                "allowed_tools": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Allowlist of tools (empty = all allowed)",
                },
                "blocked_paths": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Paths the agent cannot access",
                },
                "max_cost": {"type": "number", "description": "Maximum cost in USD (default: 10.0)", "default": 10.0},
                "timeout_sec": {"type": "integer", "description": "Timeout in seconds (default: 300)", "default": 300},
            },
            "required": ["agent_name"],
        },
    },
    {
        "name": "sandbox_check",
        "description": "Check if an action is allowed within a sandbox.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sandbox_id": {"type": "string", "description": "Sandbox ID"},
                "tool": {"type": "string", "description": "Tool name being invoked"},
                "path": {"type": "string", "description": "File path being accessed (optional)"},
                "cost": {"type": "number", "description": "Estimated cost of this action (default: 0)", "default": 0},
            },
            "required": ["sandbox_id", "tool"],
        },
    },
    {
        "name": "sandbox_validate_output",
        "description": "Validate agent output against sandbox rules (no secrets, no blocked content).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sandbox_id": {"type": "string", "description": "Sandbox ID"},
                "output": {"type": "string", "description": "Agent output text to validate"},
            },
            "required": ["sandbox_id", "output"],
        },
    },
    {
        "name": "sandbox_status",
        "description": "Get full sandbox state: kill switch, circuit breaker, cost, actions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sandbox_id": {"type": "string", "description": "Sandbox ID (omit for all sandboxes)"},
            },
            "required": [],
        },
    },
    {
        "name": "sandbox_destroy",
        "description": "Tear down a sandbox and emit an audit receipt.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sandbox_id": {"type": "string", "description": "Sandbox ID"},
            },
            "required": ["sandbox_id"],
        },
    },
]


def handle_tool(name, arguments):
    if name == "sandbox_create":
        sid = f"sbx-{uuid.uuid4().hex[:8]}"
        sb = Sandbox(
            sandbox_id=sid,
            agent_name=arguments["agent_name"],
            allowed_tools=arguments.get("allowed_tools"),
            blocked_paths=arguments.get("blocked_paths"),
            max_cost=arguments.get("max_cost", 10.0),
            timeout_sec=arguments.get("timeout_sec", 300),
        )
        _sandboxes[sid] = sb
        return {"created": True, "sandbox": sb.to_dict()}

    elif name == "sandbox_check":
        sid = arguments["sandbox_id"]
        sb = _sandboxes.get(sid)
        if not sb:
            return {"error": f"Sandbox {sid} not found"}
        return sb.check_action(
            tool=arguments["tool"],
            path=arguments.get("path"),
            cost=arguments.get("cost", 0),
        )

    elif name == "sandbox_validate_output":
        sid = arguments["sandbox_id"]
        sb = _sandboxes.get(sid)
        if not sb:
            return {"error": f"Sandbox {sid} not found"}
        output = arguments["output"]
        issues = []
        # Check for common secret patterns
        import re
        secret_patterns = [
            (r'sk-[a-zA-Z0-9_-]{10,}', "API key (sk-...)"),
            (r'ghp_[a-zA-Z0-9]{36}', "GitHub PAT"),
            (r'AKIA[A-Z0-9]{16}', "AWS access key"),
            (r'-----BEGIN.*PRIVATE KEY-----', "Private key"),
        ]
        for pattern, desc in secret_patterns:
            if re.search(pattern, output):
                issues.append({"type": "secret_leak", "pattern": desc})
        # Check output length
        if len(output) > 100000:
            issues.append({"type": "excessive_output", "length": len(output)})
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "output_length": len(output),
        }

    elif name == "sandbox_status":
        sid = arguments.get("sandbox_id")
        if sid:
            sb = _sandboxes.get(sid)
            if not sb:
                return {"error": f"Sandbox {sid} not found"}
            return {"sandbox": sb.to_dict()}
        return {
            "active_sandboxes": len(_sandboxes),
            "sandboxes": [sb.to_dict() for sb in _sandboxes.values()],
        }

    elif name == "sandbox_destroy":
        sid = arguments["sandbox_id"]
        sb = _sandboxes.pop(sid, None)
        if not sb:
            return {"error": f"Sandbox {sid} not found"}
        receipt = {
            "destroyed": True,
            "sandbox_id": sid,
            "agent": sb.agent,
            "duration_sec": (datetime.now(timezone.utc) - sb.created_at).total_seconds(),
            "total_actions": len(sb.actions),
            "total_cost": round(sb.cost_spent, 2),
            "kill_switch_engaged": sb.kill_switch.engaged,
        }
        return receipt

    return {"error": f"Unknown tool: {name}"}


def send_response(msg_id, result):
    response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def send_error(msg_id, code, message):
    response = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def main():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params", {})

        try:
            if method == "initialize":
                send_response(msg_id, {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                })
            elif method == "notifications/initialized":
                pass
            elif method == "tools/list":
                send_response(msg_id, {"tools": TOOLS})
            elif method == "tools/call":
                result = handle_tool(params.get("name", ""), params.get("arguments", {}))
                send_response(msg_id, {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}],
                })
            elif method == "ping":
                send_response(msg_id, {})
            else:
                send_error(msg_id, -32601, f"Method not found: {method}")
        except Exception as e:
            send_error(msg_id, -32603, f"Internal error: {e}\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
