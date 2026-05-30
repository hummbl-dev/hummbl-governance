# Gitea Migration Playbook

## Purpose

This playbook documents the pattern for migrating HUMMBL repos from GitHub Actions to Gitea Actions, establishing Gitea as the canonical CI/CD surface and GitHub as the marketing/distribution surface.

## Policy

- **Gitea = Source of Truth**: All development, CI/CD, and automation happens on Gitea
- **GitHub = Marketing/Distribution**: GitHub serves public distribution, external collaboration, and marketing
- **Sync Direction**: Gitea → GitHub (never GitHub → Gitea unless one-time catch-up)
- **Cost Goal**: Eliminate GitHub Actions minutes consumption for HUMMBL repos

## Migration Pattern

### 1. Git Remote Configuration

```bash
# Add Gitea remote (source of truth)
git remote add gitea https://anvil.tail0ff7b3.ts.net/HUMMBL/<repo>.git

# Add GitHub remote (marketing/distribution)
git remote add github git@github.com:hummbl-dev/<repo>.git

# Remove origin to prevent accidental GitHub pushes
git remote remove origin

# Configure Gitea as fetch/push default
git remote set-head origin gitea main
git branch --set-upstream-to=gitea/main main
```

### 2. One-Time Sync (if Gitea is behind GitHub)

```bash
# Fetch latest from GitHub
git fetch github main

# Force update Gitea to match GitHub
git push gitea github/main:main --force-with-lease
```

### 3. Create Gitea Actions Workflow

Create `.gitea/workflows/ci.yml` with self-hosted runner configuration:

```yaml
jobs:
  test:
    runs-on: [self-hosted, linux, x64, anvil, wsl, <repo-specific-label]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python -m pytest tests/ -v
```

**Key changes from GitHub Actions**:
- Replace `ubuntu-latest` with `[self-hosted, linux, x64, anvil, wsl, <repo-label>]`
- Add `shell: bash` to all steps for Windows compatibility
- Use platform-specific runner labels (e.g., `windows, anvil` for Windows jobs)

### 4. Port GitHub Actions Jobs

Migrate essential jobs from `.github/workflows/` to `.gitea/workflows/`:

**Essential (must port)**:
- `ci.yml` (main test suite)
- `security.yml` (Bandit + Semgrep scans)
- `pr-guardrails.yml` (size checks, unsigned commit detection)

**Nice-to-have (port if feasible)**:
- `lint-and-schema.yml` (code quality)
- `coverage-matrix-validate.yml` (evidence validation)

**GitHub-specific (skip)**:
- Workflows using GitHub-specific features not available in Gitea
- External integrations that require GitHub API tokens

### 5. Create Sync Script

Create `scripts/sync-gitea-to-github.sh`:

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting Gitea → GitHub sync"

git fetch gitea main
git fetch github main

GITEA_SHA=$(git rev-parse gitea/main)
GITHUB_SHA=$(git rev-parse github/main)

if [ "$GITEA_SHA" = "$GITHUB_SHA" ]; then
    echo "Gitea and GitHub are already in sync ($GITEA_SHA)"
    exit 0
fi

echo "Gitea is ahead: $GITEA_SHA vs $GITHUB_SHA"
git push github main:main --force-with-lease

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Sync complete: $GITEA_SHA → GitHub"
```

### 6. Schedule Sync Script

**macOS (launchd)**: Create `~/Library/LaunchAgents/com.hummbl.sync-gitea-to-github.plist`

**Linux (cron)**: Add to crontab:
```
0 */8 * * * /path/to/scripts/sync-gitea-to-github.sh >> /var/log/gitea-sync.log 2>&1
```

**Windows (Task Scheduler)**: Create scheduled task to run script every 8 hours

### 7. Verify Gitea Actions

1. Push to Gitea main branch
2. Check Gitea Actions tab: https://anvil.tail0ff7b3.ts.net/HUMMBL/<repo>/actions
3. Verify workflow runs on self-hosted runner
4. Check that all jobs pass

### 8. Disable GitHub Actions (Optional)

Once Gitea Actions is validated, disable GitHub Actions to prevent cost bleed:

- Go to repo Settings → Actions → General
- Disable "Allow all actions and reusable workflows"
- Or add `on: []` to `.github/workflows/ci.yml` to disable all triggers

## Validation Checklist

- [ ] Gitea remote configured as source of truth
- [ ] GitHub remote configured for marketing/distribution
- [ ] Origin remote removed
- [ ] `.gitea/workflows/ci.yml` created with self-hosted runner labels
- [ ] Essential GitHub Actions jobs ported to Gitea
- [ ] Sync script created and tested
- [ ] Sync script scheduled (cron/launchd/Task Scheduler)
- [ ] Gitea Actions runs successfully on self-hosted runner
- [ ] GitHub Actions disabled (optional but recommended)

## Rollback Plan

If Gitea Actions fails:

1. Re-enable GitHub Actions
2. Push to GitHub main branch
3. Delete `.gitea/workflows/` directory
4. Reconfigure git remotes (origin = GitHub)

## Notes

- Gitea Actions API mirror configuration did not work via API; use sync script instead
- GitHub Actions status checks are bypassed when pushing from Gitea (expected)
- Self-hosted runner labels: `[self-hosted, linux, x64, anvil, wsl, <repo-label>]`
- Windows runner labels: `[self-hosted, windows, anvil, <repo-label>]`
- macOS runner labels: `[self-hosted, macos, nodezero, <repo-label>]