"""Coverage matrix evidence-cell validator.

Inspects every code-reference in matrix Evidence cells and classifies as:
  - VALID — resolves against known CLI / file system / spec-doc set
  - DRAFT — already explicitly marked [DRAFT] or "planned"
  - UNRESOLVABLE — claims a CLI flag or path that does not exist

Stdlib-only. Implements hummbl-governance#29 (CLI surface) and
hummbl-governance#31 (path-resolution against actual hummbl_governance package).

Two classes of unresolvable references the validator catches:

1. CLI invocations with flags or framework values outside the real
   compliance_mapper argparse surface.
2. Python file paths under founder_mode/, services/, cognition/, integrations/
   that do not exist in the hummbl-governance package layout. The
   hummbl-governance package uses `hummbl_governance/*` paths
   (kill_switch.py, delegation.py, coordination_bus.py, audit_log.py, ...);
   founder-mode-style paths are package-context errors that must be
   translated or labeled planned/external.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Actual compliance_mapper CLI surface (parsed from main() argparse).
# These are the only flags that resolve. Anything else cited is unresolvable.
COMPLIANCE_MAPPER_FLAGS = {"--days", "--framework", "--dir", "--output"}
COMPLIANCE_MAPPER_FRAMEWORKS = {
    "soc2", "gdpr", "owasp", "nist-rmf", "eu-ai-act", "iso27001", "nist-csf"
}

# Patterns to extract code references from matrix files.
BACKTICK_RE = re.compile(r"`([^`\n]+)`")

# Patterns identifying claim types within backticks.
RE_COMPLIANCE_MAPPER = re.compile(r"^compliance_mapper\b")
RE_FILE_PATH = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_./-]*\.(py|md|json|toml|yaml|yml|tsv|jsonl)$")
RE_PYTHON_MODULE_PATH = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_/.]*\.py$")
RE_FOUNDER_MODE_PATH = re.compile(r"^founder_mode/[a-zA-Z0-9_/.-]+$")
RE_DOCS_PATH = re.compile(r"^.*docs?/[a-zA-Z0-9_/.\-]+$")
RE_ENVVAR_OR_FLAG = re.compile(r"^[A-Z_]+_TOKEN$|^\[[a-z-]+\]$|^--[a-z][a-z0-9-]+$")
RE_DRAFT_MARKER = re.compile(r"\[DRAFT(?::[^\]]*)?\]|planned|not yet shipped", re.IGNORECASE)


def classify_compliance_mapper_invocation(text: str) -> tuple[str, str]:
    """Classify a compliance_mapper CLI invocation.

    Returns (status, reason). Status is one of "valid", "unresolvable".
    """
    # Extract --flag tokens from the invocation
    tokens = text.split()
    flags_in_text = {t for t in tokens if t.startswith("--")}
    # Any unknown flag → unresolvable
    unknown = flags_in_text - COMPLIANCE_MAPPER_FLAGS
    if unknown:
        return "unresolvable", f"unknown flag(s): {sorted(unknown)}"

    # If --framework is given, check the value
    fw_match = re.search(r"--framework\s+([a-z0-9-]+)", text)
    if fw_match:
        fw = fw_match.group(1)
        if fw not in COMPLIANCE_MAPPER_FRAMEWORKS and not fw.startswith("<"):
            return "unresolvable", f"unknown framework: {fw}"

    return "valid", "matches CLI surface"


def classify_reference(ref: str) -> tuple[str, str]:
    """Classify a backtick-quoted reference. Returns (kind, status)."""
    # Strip wrapping whitespace
    ref = ref.strip()

    # Skip pure-prose backticks (e.g., `[DRAFT]`)
    if RE_DRAFT_MARKER.search(ref):
        return "draft-marker", "draft"

    # Compliance mapper invocations
    if RE_COMPLIANCE_MAPPER.match(ref):
        status, reason = classify_compliance_mapper_invocation(ref)
        return "compliance-mapper-cli", status

    # Python file paths
    if RE_PYTHON_MODULE_PATH.match(ref):
        # Check actual hummbl-governance package layout (#31).
        # Paths under hummbl_governance/* are resolvable; founder-mode-style
        # paths (services/, cognition/, integrations/) do not exist in this
        # package and must be translated or labeled planned/external.
        if ref.startswith("hummbl_governance/"):
            pkg_path = Path(__file__).resolve().parent.parent / ref
            if pkg_path.exists():
                return "file-path", "valid"
            return "file-path", "unresolvable"

        # founder-mode-style paths in a hummbl-governance matrix
        if ref.startswith(("services/", "cognition/", "integrations/", "bus/")):
            return "file-path", "unresolvable"

        return "file-path", "unknown-path"

    # Founder-mode paths — file references to the founder-mode repo cited
    # from hummbl-governance matrices need to be labeled external: or
    # planned: rather than presented as if they resolve in-package.
    if RE_FOUNDER_MODE_PATH.match(ref):
        # Spec/doc paths are legitimate external references.
        if "/docs/" in ref or ref.endswith(".md"):
            return "founder-mode-path", "external-ref"
        # Python module paths under founder_mode are unresolvable in-package.
        return "founder-mode-path", "unresolvable"

    # Docs path
    if RE_DOCS_PATH.match(ref):
        return "docs-path", "external-ref"

    # Env var or pip extra
    if RE_ENVVAR_OR_FLAG.match(ref):
        return "config-token", "valid"

    return "other", "uncategorized"


def scan_matrix(path: Path) -> dict:
    """Scan a matrix file and return reference classification."""
    text = path.read_text(encoding="utf-8")
    refs: list[dict] = []

    for match in BACKTICK_RE.finditer(text):
        ref = match.group(1)
        kind, status = classify_reference(ref)
        # Skip uninteresting categories
        if kind in ("draft-marker", "config-token"):
            continue
        if kind == "other" and len(ref) < 5:
            # Skip noise like `id`, `N/A`
            continue
        refs.append({
            "ref": ref,
            "kind": kind,
            "status": status,
        })

    return {
        "path": str(path),
        "refs": refs,
        "by_status": dict(Counter(r["status"] for r in refs)),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--matrix-dir", type=Path, default=Path("docs/coverage"))
    p.add_argument("--format", choices=("human", "json"), default="human")
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 if any unresolvable refs found")
    args = p.parse_args(argv)

    files = sorted(
        f for f in args.matrix_dir.glob("*.md") if f.name != "README.md"
    )
    fleet_unresolvable = 0
    results = []
    for f in files:
        r = scan_matrix(f)
        results.append(r)
        fleet_unresolvable += r["by_status"].get("unresolvable", 0)

    if args.format == "json":
        print(json.dumps({"matrices": results, "fleet_unresolvable": fleet_unresolvable}, indent=2))
    else:
        for r in results:
            name = Path(r["path"]).name
            unresolvable = [x for x in r["refs"] if x["status"] == "unresolvable"]
            ok_count = sum(1 for x in r["refs"] if x["status"] == "valid")
            print(f"\n=== {name} (refs total={len(r['refs'])}, valid={ok_count}, unresolvable={len(unresolvable)}) ===")
            if unresolvable:
                for u in unresolvable[:30]:
                    print(f"  ✗ [{u['kind']}] {u['ref']}")
        print()
        print(f"FLEET UNRESOLVABLE: {fleet_unresolvable}")

    return 1 if (args.strict and fleet_unresolvable > 0) else 0


if __name__ == "__main__":
    sys.exit(main())
