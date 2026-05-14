"""Translate founder-mode-style paths to hummbl-governance package paths.

The 12 coverage matrices were authored citing founder_mode primitives
(`services/kill_switch_core.py`, `cognition/ledger_writer.py`, etc.) — those
paths do not resolve in the hummbl-governance package, whose layout is
`hummbl_governance/*`. Per ADR-001 the evidence column must point to a
resolvable artifact OR be explicitly labeled planned/external.

This script applies a verified translation map for primitives that exist
under both names, and prefixes `[DRAFT — planned per ADR-001] ` to anything
unresolvable.

Stdlib-only. Idempotent (skips already-translated and already-drafted refs).
Implements hummbl-governance#31 (path-resolution against actual package).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Verified mapping: founder-mode-style path -> hummbl-governance package path.
# Each target was confirmed to exist in hummbl_governance/ with semantically
# equivalent functionality (kill_switch, circuit_breaker, delegation token +
# context, audit log via append-only ledger, cost governor, coordination bus).
TRANSLATION_MAP: dict[str, str] = {
    "services/kill_switch_core.py": "hummbl_governance/kill_switch.py",
    "services/circuit_breaker.py": "hummbl_governance/circuit_breaker.py",
    "services/delegation_token.py": "hummbl_governance/delegation.py",
    "services/delegation_context.py": "hummbl_governance/delegation.py",
    "services/governance_bus.py": "hummbl_governance/coordination_bus.py",
    "cognition/ledger_writer.py": "hummbl_governance/audit_log.py",
    "integrations/cost_tracker.py": "hummbl_governance/cost_governor.py",
}

# Founder-mode paths that have no current package equivalent — relabel
# as planned/external rather than translate.
RELABEL_AS_PLANNED = (
    "services/c2pa_mcp",
    "services/incident_reporting",
)

DRAFT_PREFIX = "[DRAFT — planned per ADR-001] "

BACKTICK_RE = re.compile(r"`([^`\n]+)`")


def already_drafted(prefix_context: str) -> bool:
    return "[DRAFT" in prefix_context or "DRAFT —" in prefix_context


def translate_file(path: Path, dry_run: bool = False) -> tuple[int, int]:
    """Translate paths in a single matrix file.

    Returns (translated_count, relabeled_count).
    """
    text = path.read_text(encoding="utf-8")
    original = text
    translated = 0
    relabeled = 0

    def replace(m: re.Match) -> str:
        nonlocal translated, relabeled
        ref = m.group(1)

        # Direct translation
        if ref in TRANSLATION_MAP:
            translated += 1
            return f"`{TRANSLATION_MAP[ref]}`"

        # Planned-relabel for unmapped founder-mode paths
        if any(ref.startswith(p) for p in RELABEL_AS_PLANNED):
            start = m.start()
            prefix_window = text[max(0, start - 60):start]
            if already_drafted(prefix_window):
                return m.group(0)
            relabeled += 1
            return f"`{DRAFT_PREFIX}{ref}`"

        return m.group(0)

    new_text = BACKTICK_RE.sub(replace, text)
    if not dry_run and new_text != original:
        path.write_text(new_text, encoding="utf-8")
    return translated, relabeled


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--matrix-dir", type=Path, default=Path("docs/coverage"))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    files = sorted(
        f for f in args.matrix_dir.glob("*.md") if f.name != "README.md"
    )
    total_translated = 0
    total_relabeled = 0
    for f in files:
        t, r = translate_file(f, dry_run=args.dry_run)
        if t or r:
            print(f"{f.name}: translated={t} relabeled={r}")
        total_translated += t
        total_relabeled += r

    print()
    print(f"TOTAL translated: {total_translated}")
    print(f"TOTAL relabeled (planned): {total_relabeled}")
    if args.dry_run:
        print("(dry-run; no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
