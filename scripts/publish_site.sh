#!/bin/bash
# Commit the price data and generated site (docs/) and push them to GitHub.
# Only these paths are committed, so other local work in progress is left alone.
set -e
cd "$(dirname "$0")/.."

PATHS=(data/flights.csv docs)

git add -- "${PATHS[@]}"
if git diff --cached --quiet -- "${PATHS[@]}"; then
    echo "Site unchanged, nothing to publish."
    exit 0
fi

git commit --quiet -m "Update flight prices $(date +%Y-%m-%d)" -- "${PATHS[@]}"
git push --quiet origin main
echo "Published to GitHub Pages."
