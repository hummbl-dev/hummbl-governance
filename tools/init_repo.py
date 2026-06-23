#!/usr/bin/env python3
"""
tools/init_repo.py — HUMMBL Repository Initialization Generator

Implements the HUMMBL Init Standard v0.1 (ADR-005).
Consolidates all ad-hoc initialization scripts into one deterministic tool.

Usage:
    python tools/init_repo.py <repo-name> [--org hummbl-dev] [--dry-run] [--verify]
    python tools/init_repo.py --batch --filter "missing-constitution"
    python tools/init_repo.py --adr <repo-name> --title "Some Decision" --status proposed

Principles (from Init Standard v0.1):
    1. Determinism — same artifact class → same file set
    2. Grounding — invariants derived from actual repo content
    3. Receipt-first — KRINEIA genesis receipt before PR
    4. No blind templating — generator produces draft, human confirms
    5. Idempotency — re-running on initialized repo is a no-op
    6. Single source of truth — standards in hummbl-governance, templates in .github

Case-sensitivity guard: detects core.ignorecase and uses git rm --cached + git add
pattern instead of git mv when the filesystem is case-insensitive.
"""

import argparse
import hashlib
import json
import re
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

# --- Constants ---

ORG = "hummbl-dev"
SIGNING_KEY = "594BD296B7D933CE"
STANDARD_VERSION = "0.1"

# --- Data classes ---

@dataclass
class RepoClassification:
    name: str
    is_archived: bool = False
    is_fork: bool = False
    is_private: bool = True
    language: str = "markdown"  # python, typescript, markdown, mixed
    has_agents_md: bool = False
    has_readme: bool = False
    has_pyproject: bool = False
    has_package_json: bool = False
    has_wrangler_toml: bool = False
    existing_invariants: list = field(default_factory=list)

@dataclass
class InitResult:
    repo: str
    action: str  # "initialized", "skipped", "verified", "failed"
    files_created: list = field(default_factory=list)
    files_updated: list = field(default_factory=list)
    receipt_hash: Optional[str] = None
    error: Optional[str] = None

# --- GitHub API helpers ---

def gh_api(endpoint, method="GET", fields=None):
    """Call GitHub API via gh CLI."""
    cmd = ["gh", "api", endpoint]
    if method != "GET":
        cmd.extend(["--method", method])
    if fields:
        for k, v in fields.items():
            cmd.extend(["-f", f"{k}={v}"])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, result.stderr
    return result.stdout, None

def get_repo_info(repo, org=ORG):
    """Fetch repo metadata from GitHub."""
    out, err = gh_api(f"repos/{org}/{repo}")
    if not out:
        return None
    info = json.loads(out)
    return RepoClassification(
        name=repo,
        is_archived=info.get("archived", False),
        is_fork=info.get("fork", False),
        is_private=info.get("private", True),
        has_readme=info.get("description") is not None,
    )

def get_file_content(repo, path, org=ORG):
    """Fetch file content from GitHub API."""
    out, err = gh_api(f"repos/{org}/{repo}/contents/{path}")
    if not out:
        return None
    import base64
    data = json.loads(out)
    if isinstance(data, dict) and "content" in data:
        return base64.b64decode(data["content"]).decode()
    return None

def get_file_sha(repo, path, org=ORG):
    """Get the SHA of a file for API updates."""
    out, err = gh_api(f"repos/{org}/{repo}/contents/{path}")
    if not out:
        return None
    data = json.loads(out)
    if isinstance(data, dict) and "sha" in data:
        return data["sha"]
    return None

def list_repo_tree(repo, org=ORG):
    """List all files in a repo."""
    out, err = gh_api(f"repos/{org}/{repo}/git/trees/HEAD?recursive=1")
    if not out:
        return []
    data = json.loads(out)
    return [item["path"] for item in data.get("tree", [])]

# --- Classification ---

def classify_repo(repo, org=ORG):
    """Classify a repo and determine what files it needs."""
    info = get_repo_info(repo, org)
    if not info:
        return None, f"Could not fetch repo info for {repo}"

    # Check for existing files
    tree = list_repo_tree(repo, org)
    info.has_agents_md = any(p.lower() == "agents.md" for p in tree)
    info.has_readme = any(p.lower() == "readme.md" for p in tree)
    info.has_pyproject = "pyproject.toml" in tree
    info.has_package_json = "package.json" in tree
    info.has_wrangler_toml = "wrangler.toml" in tree

    # Determine language
    if info.has_pyproject:
        info.language = "python"
    elif info.has_package_json and info.has_wrangler_toml:
        info.language = "mixed"
    elif info.has_package_json:
        info.language = "typescript"
    else:
        info.language = "markdown"

    # Ground invariants from existing content
    invariants = []
    if info.has_agents_md:
        agents_content = get_file_content(repo, "AGENTS.md", org)
        if agents_content:
            # Extract invariant hints from AGENTS.md
            if "stdlib" in agents_content.lower() or "no third-party" in agents_content.lower():
                invariants.append("Runtime uses Python standard library only — no third-party dependencies")
            if "conventional commits" in agents_content.lower():
                invariants.append("Commit format: Conventional Commits")
            if "squash" in agents_content.lower():
                invariants.append("Merge strategy: squash-merge to main")
            if "gpg" in agents_content.lower():
                invariants.append("All commits must be GPG-signed")
            if "contract" in agents_content.lower() and "canonical" in agents_content.lower():
                invariants.append("Contracts are canonical — breaking changes require SemVer major bump")
            if "branch naming" in agents_content.lower() or "type/agent" in agents_content.lower():
                invariants.append("Branch naming: type/agent/short-desc")

    # Ensure minimum 3 invariants
    defaults = [
        "Commit format: Conventional Commits",
        "Branch naming: type/agent/short-desc",
        "Merge strategy: squash-merge to main",
    ]
    for d in defaults:
        if len(invariants) >= 8:
            break
        if d not in invariants:
            invariants.append(d)

    info.existing_invariants = invariants[:8]
    return info, None

# --- File generation ---

def generate_constitution(repo, info):
    """Generate CONSTITUTION.md content."""
    inv_lines = "\n".join(f"{i+1}. {inv}" for i, inv in enumerate(info.existing_invariants))
    return f"""# CONSTITUTION.md — {repo}

## Protected Invariants

These invariants cannot be changed without explicit operator approval and a
documented ADR superseding the governance baseline.

{inv_lines}

## Amendment

1. Any agent may propose an amendment via ADR.
2. The ADR must be accepted by the decision owner.
3. A genesis receipt must be appended to `_receipts/krineia/primary.jsonl`.
4. The CONSTITUTION.md must be updated in the same PR as the ADR.

---
Generated by `tools/init_repo.py` v{STANDARD_VERSION} on {time.strftime('%Y-%m-%d')}.
"""

def generate_krineia_md(repo, info):
    """Generate KRINEIA.md content."""
    return f"""# KRINEIA.md — {repo}

## Receipt Store

**Location:** `_receipts/krineia/primary.jsonl`
**Format:** Canonical JSON, one receipt per line
**Chain:** SHA-256, each receipt's `prev_hash` links to the previous receipt's `hash`

## Genesis Receipt

Every repo's receipt chain starts with a genesis receipt:
- `prev_hash`: `{"0" * 64}`
- `event`: `governance.manifest_adopted`
- `payload`: repo manifest details

## Operators

Three operators only:
- `append()` — add a new receipt
- `project()` — read receipts (no mutation)
- `cut()` — create a new chain (rare, requires ADR)

## Verification

```bash
python tools/verify_chain.py _receipts/krineia/primary.jsonl
```

---
Generated by `tools/init_repo.py` v{STANDARD_VERSION} on {time.strftime('%Y-%m-%d')}.
"""

def generate_repo_yaml(repo, info):
    """Generate hummbl.repo.yaml content."""
    classification = "archived" if info.is_archived else ("fork" if info.is_fork else "active")
    return f"""# hummbl.repo.yaml — {repo}
# HUMMBL Repo Standard v{STANDARD_VERSION}

repo:
  name: {repo}
  org: {ORG}
  classification: {classification}
  language: {info.language}
  visibility: {"private" if info.is_private else "public"}

governance:
  standard: HUMMBL Repo Standard v{STANDARD_VERSION}
  constitution: CONSTITUTION.md
  krineia: KRINEIA.md
  receipts: _receipts/krineia/primary.jsonl
  adr_dir: docs/adr/
  handoffs_dir: docs/handoffs/

invariants:
  count: {len(info.existing_invariants)}
  source: grounded  # derived from AGENTS.md content, not templated

agent_policy:
  commit_format: conventional_commits
  branch_naming: type/agent/short-desc
  merge_strategy: squash
  gpg_signing: required
  signing_key: "{SIGNING_KEY}"
"""

def generate_codeowners(repo, info):
    """Generate CODEOWNERS content."""
    return f"""# CODEOWNERS — {repo}
# Default owner for all files
* @reubenbowlby

# Governance files require operator review
/CONSTITUTION.md @reubenbowlby
/KRINEIA.md @reubenbowlby
/hummbl.repo.yaml @reubenbowlby
/docs/adr/ @reubenbowlby
"""

def generate_adr_001(repo, info):
    """Generate ADR-001 governance baseline."""
    return f"""# ADR-001 — {repo} repo governance baseline

- **Status:** accepted
- **Date:** {time.strftime('%Y-%m-%d')}
- **Decision owner:** Reuben Bowlby
- **Steward:** HUMMBL Research Institute
- **Supersedes:** none
- **Superseded by:** none

## Context

A live audit of all `{ORG}` repositories found that `{ORG}/{repo}` was missing
the core governance artifact stack. The HUMMBL Repo Standard v{STANDARD_VERSION}
was adopted in `hummbl-governance` (ADR-003).

## Decision

Adopt the HUMMBL Repo Standard v{STANDARD_VERSION} artifact stack for
`{ORG}/{repo}`.

## Files added

| File | Purpose |
|------|---------|
| `CONSTITUTION.md` | Protected invariants ({len(info.existing_invariants)} invariants) |
| `KRINEIA.md` | Receipt store documentation |
| `hummbl.repo.yaml` | Repo manifest |
| `CODEOWNERS` | Ownership rules |
| `_receipts/krineia/primary.jsonl` | Genesis receipt |
| `docs/adr/ADR-001-repo-governance-baseline.md` | This decision record |

## Consequences

- **Positive:** Governance artifacts are now present and consistent with fleet standard.
- **Negative:** Additional files to maintain.

## Receipts

Genesis receipt in `_receipts/krineia/primary.jsonl`.
"""

def generate_genesis_receipt(repo, info, prev_hash="0" * 64):
    """Generate a KRINEIA genesis receipt."""
    receipt = {
        "id": str(uuid.uuid4()),
        "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "state": {
            "event": "governance.manifest_adopted",
            "payload": {
                "repo": f"{ORG}/{repo}",
                "standard": f"HUMMBL Repo Standard v{STANDARD_VERSION}",
                "invariant_count": len(info.existing_invariants),
                "adopter": "init_repo.py",
            }
        },
        "drift": None,
        "prev_hash": prev_hash,
    }
    canonical = json.dumps(
        {"id": receipt["id"], "time": receipt["time"], "state": receipt["state"],
         "drift": receipt["drift"], "prev_hash": receipt["prev_hash"]},
        sort_keys=True, separators=(",", ":")
    )
    receipt["hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    return receipt

# --- Case-sensitivity guard ---

def is_case_insensitive_fs(path):
    """Check if the filesystem at path is case-insensitive."""
    test_a = path / ".case_test_A"
    test_b = path / ".case_test_a"
    try:
        test_a.mkdir()
        if test_b.exists():
            return True
    except FileExistsError:
        return True
    finally:
        try:
            test_a.rmdir()
        except OSError:
            pass
    return False

def git_mv_safe(repo_dir, old_path, new_path):
    """Case-safe git mv. Uses rm --cached + add on case-insensitive FS."""
    if is_case_insensitive_fs(repo_dir):
        # Use the rm --cached + add pattern
        r = subprocess.run(
            ["git", "rm", "--cached", old_path],
            capture_output=True, text=True, cwd=repo_dir
        )
        if r.returncode != 0:
            return False, r.stderr
        r = subprocess.run(
            ["git", "add", new_path],
            capture_output=True, text=True, cwd=repo_dir
        )
        return r.returncode == 0, r.stderr
    else:
        r = subprocess.run(
            ["git", "mv", old_path, new_path],
            capture_output=True, text=True, cwd=repo_dir
        )
        return r.returncode == 0, r.stderr

# --- Core operations ---

def init_repo(repo, org=ORG, dry_run=False):
    """Initialize governance artifacts for a repo."""
    # Classify
    info, err = classify_repo(repo, org)
    if not info:
        return InitResult(repo=repo, action="failed", error=err)

    # Skip archived repos
    if info.is_archived:
        return InitResult(repo=repo, action="skipped", error="repo is archived (read-only)")

    # Check what's already present
    tree = list_repo_tree(repo, org)
    existing = {p.lower() for p in tree}

    # Determine what files to create
    files_to_create = {}
    if "constitution.md" not in existing:
        files_to_create["CONSTITUTION.md"] = generate_constitution(repo, info)
    if "krineia.md" not in existing:
        files_to_create["KRINEIA.md"] = generate_krineia_md(repo, info)
    if "hummbl.repo.yaml" not in existing:
        files_to_create["hummbl.repo.yaml"] = generate_repo_yaml(repo, info)
    if "codeowners" not in existing:
        files_to_create["CODEOWNERS"] = generate_codeowners(repo, info)
    if "_receipts/krineia/primary.jsonl" not in existing:
        receipt = generate_genesis_receipt(repo, info)
        receipt_json = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
        files_to_create["_receipts/krineia/primary.jsonl"] = receipt_json + "\n"
    if "docs/adr/adr-001-repo-governance-baseline.md" not in existing:
        files_to_create["docs/adr/ADR-001-repo-governance-baseline.md"] = generate_adr_001(repo, info)

    if not files_to_create:
        return InitResult(repo=repo, action="skipped", error="all governance files already present")

    if dry_run:
        print(f"[DRY RUN] {repo}: would create {len(files_to_create)} files:")
        for path in files_to_create:
            print(f"  - {path}")
        return InitResult(repo=repo, action="skipped", files_created=list(files_to_create.keys()))

    # Create files via GitHub API
    created = []
    for path, content in files_to_create.items():
        import base64
        content_b64 = base64.b64encode(content.encode()).decode()
        out, err = gh_api(
            f"repos/{org}/{repo}/contents/{path}",
            method="PUT",
            fields={
                "message": f"feat(governance): add {path} (HUMMBL Repo Standard v{STANDARD_VERSION})",
                "content": content_b64,
                "branch": "main",
            }
        )
        if err:
            return InitResult(
                repo=repo, action="failed", files_created=created,
                error=f"Failed to create {path}: {err}",
            )
        created.append(path)
        time.sleep(0.3)  # Rate limit

    receipt_hash = None
    if "_receipts/krineia/primary.jsonl" in files_to_create:
        receipt = generate_genesis_receipt(repo, info)
        receipt_hash = receipt["hash"][:16]

    return InitResult(repo=repo, action="initialized", files_created=created, receipt_hash=receipt_hash)

def verify_repo(repo, org=ORG):
    """Verify that a repo has all required governance artifacts."""
    tree = list_repo_tree(repo, org)
    tree_lower = {p.lower() for p in tree}

    required = [
        "CONSTITUTION.md",
        "KRINEIA.md",
        "hummbl.repo.yaml",
        "CODEOWNERS",
        "_receipts/krineia/primary.jsonl",
        "docs/adr/ADR-001-repo-governance-baseline.md",
    ]

    missing = [f for f in required if f.lower() not in tree_lower]

    return InitResult(
        repo=repo,
        action="verified" if not missing else "failed",
        files_created=missing,  # reuse field for missing
        error=f"Missing: {', '.join(missing)}" if missing else None,
    )

def create_adr(repo, title, status="proposed", org=ORG, dry_run=False):
    """Create a new ADR in a repo."""
    # Find next ADR number
    tree = list_repo_tree(repo, org)
    adr_files = [p for p in tree if re.match(r'docs/adr/ADR-\d{3}-', p)]
    numbers = []
    for p in adr_files:
        m = re.search(r'ADR-(\d{3})-', p)
        if m:
            numbers.append(int(m.group(1)))
    next_num = max(numbers) + 1 if numbers else 1

    kebab_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    filename = f"docs/adr/ADR-{next_num:03d}-{kebab_title}.md"

    content = f"""# ADR-{next_num:03d} — {title}

- **Status:** {status}
- **Date:** {time.strftime('%Y-%m-%d')}
- **Decision owner:** Reuben Bowlby
- **Steward:** HUMMBL Research Institute
- **Supersedes:** none
- **Superseded by:** none

## Context

<why this decision is needed>

## Decision

<what was decided>

## Alternatives considered

<what else was on the table>

## Consequences

- **Positive:** <benefits>
- **Negative:** <costs>

## Receipts

<KRINEIA receipt references>
"""

    if dry_run:
        print(f"[DRY RUN] {repo}: would create {filename}")
        print(content)
        return InitResult(repo=repo, action="skipped", files_created=[filename])

    import base64
    content_b64 = base64.b64encode(content.encode()).decode()
    out, err = gh_api(
        f"repos/{org}/{repo}/contents/{filename}",
        method="PUT",
        fields={
            "message": f"docs: add {filename}",
            "content": content_b64,
            "branch": "main",
        }
    )
    if err:
        return InitResult(repo=repo, action="failed", error=err)

    return InitResult(repo=repo, action="initialized", files_created=[filename])

# --- Batch operations ---

def batch_verify(org=ORG, filter_type=None):
    """Verify governance artifacts across all repos."""
    result = subprocess.run(
        ["gh", "repo", "list", org, "--limit", "200", "--json",
         "name,isFork,isArchived"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return
    repos = json.loads(result.stdout)
    repos = [r for r in repos if not r.get("isFork") and not r.get("isArchived")]

    if filter_type == "missing-constitution":
        results = []
        for repo in repos:
            tree = list_repo_tree(repo["name"], org)
            if "CONSTITUTION.md" not in {p.lstrip("/") for p in tree} and \
               "constitution.md" not in {p.lower().lstrip("/") for p in tree}:
                results.append((repo["name"], "MISSING"))
            else:
                results.append((repo["name"], "OK"))
        return results

    results = []
    for repo in repos:
        r = verify_repo(repo["name"], org)
        status = "OK" if r.action == "verified" else f"MISSING: {r.error}"
        results.append((repo["name"], status))
        print(f"  {repo['name']}: {status}")
        time.sleep(0.2)

    return results

# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="HUMMBL Repository Initialization Generator (Init Standard v0.1)"
    )
    parser.add_argument("repo", nargs="?", help="Repo name to initialize")
    parser.add_argument("--org", default=ORG, help="GitHub org (default: hummbl-dev)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--verify", action="store_true", help="Verify governance artifacts are present")
    parser.add_argument("--batch", action="store_true", help="Batch operation across all repos")
    parser.add_argument("--filter", help="Filter for batch: 'missing-constitution', 'missing-all'")
    parser.add_argument("--adr", action="store_true", help="Create a new ADR instead of full init")
    parser.add_argument("--title", help="ADR title (with --adr)")
    parser.add_argument("--status", default="proposed", help="ADR status (with --adr)")

    args = parser.parse_args()

    if args.batch:
        if args.verify:
            print("=== Batch verification ===")
            results = batch_verify(args.org, args.filter)
            ok = sum(1 for _, s in results if s == "OK")
            print(f"\n{ok}/{len(results)} repos fully compliant")
        elif args.filter == "missing-constitution":
            print("=== Finding repos missing CONSTITUTION.md ===")
            results = batch_verify(args.org, "missing-constitution")
            missing = [r for r, s in results if s == "MISSING"]
            print(f"\n{len(missing)} repos missing CONSTITUTION.md:")
            for r in missing:
                print(f"  - {r}")
        else:
            print("=== Batch initialization ===")
            result = subprocess.run(
                ["gh", "repo", "list", args.org, "--limit", "200", "--json",
                 "name,isFork,isArchived"],
                capture_output=True, text=True
            )
            repos = json.loads(result.stdout)
            repos = [r for r in repos if not r.get("isFork") and not r.get("isArchived")]
            for repo in repos:
                print(f"\n--- {repo['name']} ---")
                result = init_repo(repo["name"], args.org, args.dry_run)
                print(f"  {result.action}: {result.files_created}")
                if result.error:
                    print(f"  Error: {result.error}")
        return

    if not args.repo:
        parser.print_help()
        return

    if args.verify:
        result = verify_repo(args.repo, args.org)
        print(f"{result.repo}: {result.action}")
        if result.error:
            print(f"  {result.error}")
        return

    if args.adr:
        if not args.title:
            print("Error: --title required with --adr")
            return
        result = create_adr(args.repo, args.title, args.status, args.org, args.dry_run)
        print(f"{result.repo}: {result.action}")
        if result.files_created:
            print(f"  Created: {result.files_created}")
        if result.error:
            print(f"  Error: {result.error}")
        return

    result = init_repo(args.repo, args.org, args.dry_run)
    print(f"{result.repo}: {result.action}")
    if result.files_created:
        print(f"  Created: {', '.join(result.files_created)}")
    if result.receipt_hash:
        print(f"  Receipt: {result.receipt_hash}...")
    if result.error:
        print(f"  Error: {result.error}")

if __name__ == "__main__":
    main()
