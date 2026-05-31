# Gitea Restart Required — Operator Action Needed

**Date**: 2026-05-30
**Created by**: Kimi K2.6
**Blocks**: Gitea push (pre-receive hook 403), Gitea CI runs

---

## Root Cause

`app.ini` line 52 contained an unsubstituted environment variable placeholder:

```ini
INTERNAL_TOKEN = ${GITEA_INTERNAL_TOKEN}
```

`GITEA_INTERNAL_TOKEN` is not set anywhere (machine, user, or process environment). Gitea was
reading the literal string `${GITEA_INTERNAL_TOKEN}` as the token. Every pre-receive hook call
from the Gitea server to its own internal API used this broken token → `403 Forbidden` →
"Internal Server Error Decoding Failed" on every `git push`.

## Fix Applied

`app.ini` line 52 has been updated to a real token:

```ini
INTERNAL_TOKEN = LLixMTrLhVOhW2pLmvILBhtxoIA3EbwHmdl1VVTqK5NC06DYLmd8LILBMN2YtxCKbUcH8Tt_u8E-O_vUKdOH9Q
```

**The fix is already written to disk. It takes effect after Gitea restarts.**

## Operator Action Required

Run the following in an **elevated** PowerShell (Run as Administrator):

```powershell
# 1. Stop the running Gitea server
Stop-Process -Name "gitea" -Force

# 2. Wait for clean exit
Start-Sleep -Seconds 3

# 3. Relaunch Gitea
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\gitea\bin\run-gitea.ps1"

# 4. Wait for startup
Start-Sleep -Seconds 5

# 5. Verify it's running
Get-Process | Where-Object { $_.Name -like "*gitea*" } | Select-Object Id, Name, StartTime
```

## After Restart

Push the pending commits to trigger Gitea CI:

```bash
cd PROJECTS/hummbl-governance
git push gitea main
```

Expected: 2 commits will push, CI run #565+ will start with the `python -m pip` fix.

## CI Local Verification (pre-restart, already confirmed)

Ran all 5 CI job steps locally using the exact toolcache Python path
(`C:\gitea\runner\toolcache\Python\3.13.13\x64`):

| Step | Command | Result |
|------|---------|--------|
| Setup Python | `python -m pip --version` | pip 26.1.1 (python 3.13) ✅ |
| test: install | `python -m pip install -e ".[test]"` | Successfully installed ✅ |
| test: pytest | `python -m pytest tests/ -q --cov-fail-under=80` | 1031 passed, 85.10% coverage ✅ |
| lint: ruff install | `python -m pip install ruff` | Already satisfied ✅ |
| lint: ruff check | `ruff check .` | All checks passed ✅ |

The CI fix is confirmed working. Gitea restart is the only remaining blocker.

## Pending Unpushed Commits

```
ebc953e fix(ci): use python -m pip instead of bare pip in Gitea workflow
85b06a6 docs: remove dead CI badge, update test count 927→1031, mark PRD as superseded
```
