# CI Debugging Session — 2026-05-30

## Problem
CI failures on hummbl-governance repo Windows runner (anvil-windows-general). Root cause: `actions/setup-python@v5` action requires admin privileges to modify Windows registry, but runner runs as non-admin user "Owner" instead of SYSTEM.

Error: `Remove-Item : Requested registry access is not allowed` during Python installation at `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall`

## Failed Approaches

### 1. Registry Permission Bypass with Embeddable Python
- Downloaded Python 3.12.10 and 3.13.0 embeddable distributions
- Extracted to `C:\Python312\` and `C:\Python313\`
- Modified `python312._pth` and `python313._pth` to enable site modules
- Installed pip using get-pip.py
- **Result**: Test jobs passed, but install-smoke jobs failed due to missing `venv` module in embeddable distributions

### 2. Full Python Installation (POP-UPS)
- Attempted to install full Python 3.12.10 and 3.13.0 installers
- **Result**: Caused annoying pop-up windows for user, highly disruptive
- **Grade**: D- performance - should have checked existing installations first

## Successful Solution

### Step 1: Use Existing uv-Managed Python
Found uv-managed Python installations at:
- `C:\Users\Owner\AppData\Roaming\uv\python\cpython-3.12.13-windows-x86_64-none\python.exe`
- `C:\Users\Owner\AppData\Roaming\uv\python\cpython-3.13.13-windows-x86_64-none\python.exe`

Verified these installations include the `venv` module (required for build isolation in install-smoke jobs).

### Step 2: Update CI Workflow
Updated `.gitea/workflows/ci.yml` to use uv Python paths instead of embeddable Python:
- Matrix jobs (test, install-smoke): conditional logic for 3.12/3.13
- Non-matrix jobs (lint, arbiter-governance, coverage-matrix-validate, ci-aggregate): hardcoded to 3.12

### Step 3: Handle Externally-Managed Environment
uv Python installations are externally managed (PEP 668) and block `pip install` by default. Added `--break-system-packages` flag to all pip install commands:
- `pip install --upgrade pip --break-system-packages`
- `pip install -e ".[test]" --break-system-packages`
- `pip install build --break-system-packages`
- `pip install ruff --break-system-packages`
- `pip install "arbiter-dev[analyzers]" --break-system-packages`

## Commits
1. `d469cc9` - fix(ci): bypass setup-python registry permission issue with manual Python installs
2. `c111f43` - fix(ci): simplify PowerShell output syntax for python-path
3. `975923e` - fix(ci): use uv Python installations with venv support
4. `6fcb909` - fix(ci): add --break-system-packages to pip install for uv Python

## Current State
- CI run 552 (commit 6fcb909) in progress
- Test jobs (py3.12, py3.13): passed
- Install-smoke jobs: pending verification with --break-system-packages fix
- Other jobs: pending verification

## Lessons Learned

### What Went Wrong
- Caused disruptive pop-ups by running Python installers interactively
- Did not systematically check for existing Python installations first
- Went down wrong path (embeddable Python) before checking alternatives
- Multiple failed attempts before finding working solution
- User feedback: "this is the worst performance i have ever seen" - justified

### Correct Approach (for future)
1. Check existing Python installations (`where python`, `py --list`)
2. Test venv availability in existing installations
3. Use working installation in CI workflow
4. Handle externally-managed restriction if needed
5. Avoid interactive installers - use silent/quiet modes only

### Root Cause
Lack of systematic investigation. Should have started with "what Python installations already exist and do they have venv?" rather than immediately trying to install new distributions.

## Fleet Software Inventory Context
From AGENTS.md:
- Anvil: Python 3.11.15 (stable)
- Nodezero: Python 3.14.3 (development/alpha)
- Huxley: Python 3.14.5 (development/alpha)

uv provides Python 3.10, 3.11, 3.12, 3.13, 3.14 via `py.cmd` wrapper at `C:\Users\Owner\bin\py.cmd`.
