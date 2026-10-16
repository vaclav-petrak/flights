#!/bin/bash
# Commit the price data and generated site (docs/) and push them to GitHub.
# Only these paths are committed, so other local work in progress is left alone.
# Also pushes earlier commits that a previous run failed to push (e.g. no network right after wake).
set -e
cd "$(dirname "$0")/.."

PATHS=(data/flights.csv docs)

git add -- "${PATHS[@]}"
if ! git diff --cached --quiet -- "${PATHS[@]}"; then
    git commit --quiet -m "Update flight prices $(date +%Y-%m-%d)" -- "${PATHS[@]}"
fi

if [ -z "$(git log origin/main..main --oneline)" ]; then
    echo "Site unchanged, nothing to publish."
    exit 0
fi

# The network may not be up yet right after the Mac wakes; retry once
if ! git push --quiet origin main; then
    sleep 30
    git push --quiet origin main
fi
echo "Published to GitHub Pages."
