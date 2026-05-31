# CI Post-Mortem: Gitea Runner Setup — 2026-05-30

**Status**: RESOLVED — run 570 green, all 6 jobs passing  
**Duration**: ~8 hours (morning session + afternoon sessions)  
**Commits**: 22 (d76a24f → 6aa2e81) + `app.ini` out-of-band fix  
**Consolidates**: ci-debugging-session, big-pickle-session-review,
session-review-big-pickle-ci-fix, OPERATOR-restart-gitea

---

## Problem Statement

Gitea CI for `hummbl-governance` failed on every run. The repo migrated from GitHub
to a self-hosted Gitea runner (Windows, `anvil-ci`). The GitHub Actions workflow used
`actions/setup-python@v5` — an action that requires registry write access to install
Python. The Gitea Windows runner runs as non-admin user `Owner`, not SYSTEM, so all
Python installation attempts failed.

---

## Timeline & Root Causes

### Phase 1 — Morning session (10 commits, ~d469cc9 → 6fcb909)

**Approach**: Various workarounds for `setup-python@v5`

| Commit | Attempt | Why it failed |
|--------|---------|---------------|
| `d76a24f` | `update-environment: false` on setup-python | setup-python still hits registry |
| `d469cc9` | Download embeddable Python 3.12/3.13 manually | Embeddable Python lacks `venv` module — install-smoke job fails |
| `c111f43` | Simplify PowerShell output syntax | Style fix, not root cause |
| `975923e` | Switch to uv-managed Python (`cpython-3.12.13`, `cpython-3.13.13`) | Works for test/lint; uv Python is "externally managed" (PEP 668) |
| `6fcb909` | Add `--break-system-packages` to all pip installs | `pip install` works; install-smoke fails on other issues |
| `4778834` | Revert to setup-python@v5, remove --break-system-packages | Back to square one — confirms uv was partially working |
| `796b8c2` | Add Gitea runners operations runbook | Documentation |
| `a92b1bd` | Dual-label strategy (`[ubuntu-latest, self-hosted, ...]`) | Labels don't work as AND — job never matched a runner |
| `1fe48c8` | Fix runner labels, add benchmark | Runner picks up job |
| `1d72ffa` | Add `.complete` markers to toolcache | Toolcache has Python 3.12.13/3.13.13 with `.complete`, but runner lacks `RUNNER_TOOL_CACHE` env var |
| `bd881e4` | Pin exact patch versions (3.12.13, 3.13.13) | setup-python still can't find them — env var missing |

**Root cause identified**: Runner processes started without `run-runner.ps1` lack `RUNNER_TOOL_CACHE` env var. `setup-python@v5` cannot find toolcache Python without it.

**Lesson**: Should have checked runner env vars on day 1 before attempting 10+ patching approaches.

---

### Phase 2 — Big Pickle afternoon session (commits a5e06d4, e435da5)

**Agent**: Qwen3.6 Plus ("Big Pickle")  
**Approach**: Abandon `setup-python@v5` entirely; inject system Python via `GITHUB_PATH`

| Commit | Action | Outcome |
|--------|--------|---------|
| `a5e06d4` | Replace setup-python with `AppData\Local\Programs\Python\Python313` | ❌ Broken path — directory exists but has NO `python.exe` |
| `e435da5` | Correct to toolcache path `C:\gitea\runner\toolcache\Python\3.13.13\x64` | ✅ Checkout works; pip install fails |

**Actual failure on run 563**: `pip install -e ".[test]"` → `exit status 1`  
**Root cause**: GITHUB_PATH mechanism unreliable — hermes venv Python 3.11 wins PATH resolution; then `python` not found for pytest step.

**Lesson**: Verify paths exist (`Test-Path`) before committing. Don't end session mid-diagnosis.

---

### Phase 3 — Kimi K2.6 session (commits ebc953e, 85b06a6, 9d886e3, 9c1bdfd, 6aa2e81 + app.ini)

**Agent**: Kimi K2.6 (this model)

#### Fix 1: `python -m pip` everywhere (`ebc953e`)
Replaced bare `pip install` with `python -m pip install` in all 4 affected jobs.  
**Result**: pip still used hermes Python 3.11 (GITHUB_PATH unreliable); `python` not in PATH for pytest.

#### Fix 2: Gitea INTERNAL_TOKEN (`app.ini`, out-of-band)
**Discovery**: `git push gitea main` rejected with "Internal Server Error Decoding Failed".  
**Root cause**: `app.ini` line 52 contained literal `${GITEA_INTERNAL_TOKEN}` — env var was never set anywhere (machine, user, or process). Gitea's pre-receive hook called its own internal API with this broken token → 403 Forbidden on every push attempt.  
**Fix**: Replaced placeholder with a real `secrets.token_urlsafe(64)` token.  
**Required**: Operator to restart Gitea as elevated user (Gitea PID 17516 ran as SYSTEM).

#### Fix 3: Explicit Python path via workflow env var (`9c1bdfd`)
**Root cause confirmed**: `GITHUB_PATH` PATH injection unreliable in Gitea act runner on Windows — hermes venv Python 3.11 was intercepting `python` calls; PATH state didn't carry reliably between steps.  
**Fix**: Removed all `Setup Python` steps. Added workflow-level `env: PYTHON: C:\gitea\runner\toolcache\Python\3.13.13\x64\python.exe`. All `run:` steps use `& "$env:PYTHON"` with `shell: powershell`.  
**Result**: Run 569 — test ✅, install-smoke ✅, lint ✅, coverage-matrix ✅. Arbiter ❌.

#### Fix 4: `sys.executable -m arbiter` in arbiter_audit.py (`6aa2e81`)
**Root cause**: `scripts/arbiter_audit.py` called `["arbiter", "score", ...]` as a bare subprocess. `arbiter` CLI is installed in `C:\gitea\runner\toolcache\Python\3.13.13\x64\Scripts\` but that directory is not in PATH inside the subprocess environment.  
**Fix**: One-line change — `[sys.executable, "-m", "arbiter", "score", ...]`.  
**Result**: Run 570 — **6/6 jobs green** ✅

---

## Final State

**Run 570** — commit `6aa2e81` — all 6 jobs passing:

| Job | Result |
|-----|--------|
| test | ✅ 1031 passed, 85.10% coverage |
| install-smoke | ✅ sdist → wheel → install → smoke |
| lint | ✅ ruff all checks passed |
| arbiter-governance | ✅ Arbiter score ≥ 90.0 |
| coverage-matrix-validate | ✅ advisory |
| ci-aggregate | ✅ |

---

## Defect Catalog

| # | Defect | Root Cause | Fix |
|---|--------|-----------|-----|
| 1 | `setup-python@v5` requires admin registry access | Windows runner runs as non-admin `Owner` | Replaced with explicit toolcache Python path |
| 2 | Toolcache Python not found even when present | Runner lacked `RUNNER_TOOL_CACHE` env var | Moot — moved away from setup-python entirely |
| 3 | `GITHUB_PATH` PATH injection unreliable | Gitea act runner on Windows; hermes venv Python intercepted | Switched to `& "$env:PYTHON"` explicit invocation |
| 4 | `AppData\Python313` has no `python.exe` | Path used without verification | Replaced with verified toolcache path |
| 5 | Gitea push blocked by 403 pre-receive | `INTERNAL_TOKEN = ${GITEA_INTERNAL_TOKEN}` unsubstituted placeholder | Replaced with real token in app.ini; restarted Gitea |
| 6 | `arbiter` CLI not found in subprocess | Scripts/ not in subprocess PATH | `sys.executable -m arbiter` |

---

## Lessons Learned

1. **Verify paths before committing** — `Test-Path` before any hardcoded file path in a workflow
2. **Test locally before pushing to main** — all 3 final fixes were verified locally first
3. **Check env vars on the runner** — `RUNNER_TOOL_CACHE` absence was the original root cause; discovering it early would have saved 10 commits
4. **Use `sys.executable` for subprocess calls to Python tools** — bare CLI names depend on PATH; `sys.executable -m tool` does not
5. **GITHUB_PATH is unreliable in Gitea act runner on Windows** — don't use it; prefer explicit full paths
6. **Config placeholders must be verified** — `${ENV_VAR}` in config files that don't support shell interpolation will be read literally
7. **Don't end a session mid-diagnosis** — the pip install failure was identified but not resolved, adding a full session of overhead

---

## Archived Files

The following files are superseded by this post-mortem:
- `ci-debugging-session-2026-05-30.md` — morning session notes
- `big-pickle-session-review-2026-05-30.md` — Big Pickle grading
- `session-review-big-pickle-ci-fix-2026-05-30.md` — independent review
- `OPERATOR-restart-gitea-2026-05-30.md` — Gitea restart runbook (completed)
