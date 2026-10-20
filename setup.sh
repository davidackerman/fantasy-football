#!/usr/bin/env bash
# One-time setup: create a public GitHub repo and turn on GitHub Pages.
# Needs git and the GitHub CLI (gh), logged in with `gh auth login`.
set -euo pipefail
REPO="${1:-fantasy-football}"
cd "$(dirname "$0")"
[ -d .git ] || git init -q
git add -A
git commit -qm "Initial fantasy football site" || true
git branch -M main
gh repo create "$REPO" --public --source=. --push
OWNER="$(gh api user -q .login)"
if gh api -X POST "repos/$OWNER/$REPO/pages" -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1; then
  echo "GitHub Pages enabled."
else
  echo "Couldn't enable Pages automatically. Turn it on in the repo's Settings > Pages (branch: main, folder: /)."
fi
echo "Your site: https://$OWNER.github.io/$REPO/ (live in a minute or two)"
