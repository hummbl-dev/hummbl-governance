#!/bin/bash
# Sync Gitea → GitHub for hummbl-governance
# This script should be run on a schedule (e.g., every 8 hours via cron/launchd)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting Gitea → GitHub sync"

# Fetch from Gitea (source of truth)
echo "Fetching from Gitea..."
git fetch gitea main

# Fetch from GitHub to get current state
echo "Fetching from GitHub..."
git fetch github main

# Check if there are new commits on Gitea
GITEA_SHA=$(git rev-parse gitea/main)
GITHUB_SHA=$(git rev-parse github/main)

if [ "$GITEA_SHA" = "$GITHUB_SHA" ]; then
    echo "Gitea and GitHub are already in sync ($GITEA_SHA)"
    exit 0
fi

echo "Gitea is ahead: $GITEA_SHA vs $GITHUB_SHA"

# Push to GitHub (marketing/distribution surface)
echo "Pushing to GitHub..."
git push github main:main --force-with-lease

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Sync complete: $GITEA_SHA → GitHub"