#!/usr/bin/env python3
"""hummbl-governance REST API server.

Lightweight HTTP API wrapping governance primitives. Uses only stdlib
(http.server). Deploy behind a reverse proxy for production.

Endpoints:
    GET  /api/v1/status              - Governance overview
    GET  /api/v1/kill-switch         - Kill switch state
    POST /api/v1/kill-switch/engage  - Engage kill switch
    POST /api/v1/kill-switch/disengage - Disengage
    GET  /api/v1/circuit-breaker     - Circuit breaker state
    GET  /api/v1/cost/check          - Budget status
    POST /api/v1/cost/record         - Record usage
    GET  /api/v1/audit               - Query audit log
    GET  /api/v1/health              - Health check
    GET  /api/v1/score               - Governance score

Usage:
    python3 api_server.py [--port 8090] [--host 127.0.0.1]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hummbl_governance import (
    KillSwitch,
    KillSwitchMode,
    CircuitBreaker,
    CostGovernor,
    AuditLog,
)

STATE_DIR = Path(os.environ.get("GOVERNANCE_STATE_DIR", ".governance"))
DB_PATH = STATE_DIR / "costs.db"

# Singletons
_ks = None
_cb = None
_cg = None
_al = None


def init_services():
    global _ks, _cb, _cg, _al
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "audit").mkdir(exist_ok=True)
    _ks = KillSwitch(state_dir=STATE_DIR)
    _cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
    _cg = CostGovernor(db_path=str(DB_PATH))
    _al = AuditLog(base_dir=str(STATE_DIR / "audit"))


class GovernanceHandler(BaseHTTPRequestHandler):
    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)

        if path == "/api/v1/status":
            budget = _cg.check_budget_status()
            self._json_response({
                "kill_switch": {"mode": _ks.mode.name, "engaged": _ks.engaged},
                "circuit_breaker": {"state": _cb.state.name, "failure_count": _cb.failure_count},
                "cost_governor": {
                    "daily_spend": getattr(budget, "current_spend", 0),
                    "decision": (
                        getattr(budget, "decision", "UNKNOWN").name
                        if hasattr(getattr(budget, "decision", None), "name")
                        else str(getattr(budget, "decision", "UNKNOWN"))
                    ),
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        elif path == "/api/v1/kill-switch":
            status = _ks.get_status()
            self._json_response(status)

        elif path == "/api/v1/circuit-breaker":
            self._json_response({
                "state": _cb.state.name,
                "failure_count": _cb.failure_count,
                "success_count": getattr(_cb, "success_count", 0),
            })

        elif path == "/api/v1/cost/check":
            budget = _cg.check_budget_status()
            result = {}
            for attr in ("current_spend", "soft_cap", "hard_cap", "decision", "rationale", "utilization"):
                val = getattr(budget, attr, None)
                if val is not None:
                    result[attr] = val.name if hasattr(val, "name") else val
            self._json_response(result)

        elif path == "/api/v1/audit":
            intent_id = params.get("intent_id", [None])[0]
            task_id = params.get("task_id", [None])[0]
            entries = []
            if intent_id:
                entries = list(_al.query_by_intent(intent_id))
            elif task_id:
                entries = list(_al.query_by_task(task_id))
            self._json_response({
                "count": len(entries),
                "entries": [
                    {k: str(v) for k, v in (e.__dict__ if hasattr(e, "__dict__") else {"data": str(e)}).items()}
                    for e in entries[:50]
                ],
            })

        elif path == "/api/v1/health":
            self._json_response({
                "healthy": not _ks.engaged and _cb.state.name == "CLOSED",
                "kill_switch": _ks.mode.name,
                "circuit_breaker": _cb.state.name,
            })

        elif path == "/api/v1/score":
            score = 0
            if not _ks.engaged:
                score += 25
            if _cb.state.name == "CLOSED":
                score += 25
            budget = _cg.check_budget_status()
            decision = getattr(budget, "decision", None)
            if hasattr(decision, "name") and decision.name == "ALLOW":
                score += 25
            if (STATE_DIR / "policy.json").exists():
                score += 25
            grade = "A+" if score >= 95 else "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "F"
            self._json_response({"score": score, "grade": grade})

        else:
            self._json_response({"error": f"Not found: {path}"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/api/v1/kill-switch/engage":
            body = self._read_body()
            mode_name = body.get("mode", "HALT_NONCRITICAL")
            mode_map = {
                "HALT_NONCRITICAL": KillSwitchMode.HALT_NONCRITICAL,
                "HALT_ALL": KillSwitchMode.HALT_ALL,
                "EMERGENCY": KillSwitchMode.EMERGENCY,
            }
            mode = mode_map.get(mode_name)
            if not mode:
                self._json_response({"error": f"Invalid mode: {mode_name}"}, 400)
                return
            if not body.get("confirm"):
                self._json_response({"error": "Must set confirm=true"}, 400)
                return
            _ks.engage(mode=mode, reason=body.get("reason", "API"), triggered_by=body.get("triggered_by", "api-client"))
            self._json_response({"engaged": True, "mode": mode_name})

        elif path == "/api/v1/kill-switch/disengage":
            body = self._read_body()
            _ks.disengage(reason=body.get("reason", "API"), triggered_by=body.get("triggered_by", "api-client"))
            self._json_response({"disengaged": True})

        elif path == "/api/v1/cost/record":
            body = self._read_body()
            required = ["provider", "model", "tokens_in", "tokens_out", "cost"]
            missing = [f for f in required if f not in body]
            if missing:
                self._json_response({"error": f"Missing fields: {missing}"}, 400)
                return
            _cg.record_usage(**{k: body[k] for k in required})
            self._json_response({"recorded": True})

        else:
            self._json_response({"error": f"Not found: {path}"}, 404)

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    init_services()
    server = HTTPServer((args.host, args.port), GovernanceHandler)
    print(f"hummbl-governance API | http://{args.host}:{args.port}/api/v1/status")
    print(f"State: {STATE_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown.")


if __name__ == "__main__":
    main()
