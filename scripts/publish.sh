#!/bin/bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /path/to/Obsidian/vault"
  exit 2
fi

VAULT="$1"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# Pick up remote changes before exporting, without creating merge commits.
# A failed fast-forward stops publication rather than trying a risky merge.
if ! git pull --ff-only; then
  echo "Research repository needs attention: could not safely fast-forward. Resolve local Git changes before publishing." >&2
  exit 1
fi

python3 scripts/sync_public_research.py --vault "$VAULT" --repo "$REPO" --apply
python3 scripts/privacy_guard.py "$REPO"

git add field-notes concepts project method

if git diff --cached --quiet; then
  echo "No public research changes to publish."
  exit 0
fi

STAMP="$(date '+%Y-%m-%d %H:%M')"
git commit -m "Update public research layer ${STAMP}"
git push

echo "Public research layer published."
