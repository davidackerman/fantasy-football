#!/usr/bin/env bash
# Publish a new weekly plan: ./new-week.sh 8 ~/Downloads/new-plan.html
# Copies the file to index.html (the live page) and to an archive copy, then pushes.
set -euo pipefail
SEASON=2026
[ $# -eq 2 ] || { echo "Usage: ./new-week.sh <week-number> <path-to-html>"; exit 1; }
cd "$(dirname "$0")"
WEEK="$(printf "%02d" "$1")"
mkdir -p "$SEASON"
cp "$2" "$SEASON/week-$WEEK.html"
cp "$2" index.html
git add -A
git commit -qm "Week $WEEK plan"
git push -q
echo "Published Week $WEEK. Archive: $SEASON/week-$WEEK.html"
