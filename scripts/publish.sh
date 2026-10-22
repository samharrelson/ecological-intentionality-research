#!/bin/bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /path/to/Obsidian/vault"
  exit 2
fi

VAULT="$1"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# Only publish from main, and update from the one intended remote branch.
# An implicit "git pull" can fail when local Git has multiple upstream merge
# entries ("Cannot fast-forward to multiple branches"). Using FETCH_HEAD after
# explicitly fetching origin/main avoids that ambiguity without a merge commit.
if [ "$(git branch --show-current)" != "main" ]; then
  echo "Research repository needs attention: switch to the main branch before publishing." >&2
  exit 1
fi

if ! git fetch origin main || ! git merge --ff-only FETCH_HEAD; then
  echo "Research repository needs attention: could not safely fast-forward from origin/main. Resolve divergent or uncommitted changes before publishing." >&2
  exit 1
fi

python3 scripts/sync_public_research.py --vault "$VAULT" --repo "$REPO" --apply
python3 scripts/build_sits_feed.py --vault "$VAULT" --repo "$REPO" --apply
python3 scripts/privacy_guard.py "$REPO"

git add field-notes concepts project method docs

if git diff --cached --quiet; then
  echo "No public research changes to publish."
  exit 0
fi

STAMP="$(date '+%Y-%m-%d %H:%M')"
git commit -m "Update public research layer ${STAMP}"
git push origin HEAD:main

echo "Public research layer published."
