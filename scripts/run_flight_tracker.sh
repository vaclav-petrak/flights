#!/bin/bash
# Scrape today's prices, rebuild the website and publish it to GitHub Pages.
# Run hourly by launchd (see README). Output goes to data/logs/tracker.log.
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"
set -e

REPO="/Users/vaclav/Code/flight_price_tracker"
PYTHON="$REPO/.venv/bin/python"
LOG="$REPO/data/logs/tracker.log"
mkdir -p "$(dirname "$LOG")"

# The day's check starts at 07:00 (Ryanair doesn't update fares at midnight
# Prague time); earlier hourly runs do nothing.
START_HOUR=7
[ "$(date +%-H)" -ge "$START_HOUR" ] || exit 0

{
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
    "$PYTHON" "$REPO/src/main.py"
    "$PYTHON" "$REPO/src/build_site.py"
    "$REPO/scripts/publish_site.sh"
} >> "$LOG" 2>&1
