#!/bin/bash
# Scrape today's prices, rebuild the website and publish it to GitHub Pages.
# Run hourly by launchd (see README). Output goes to data/logs/tracker.log.
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"
set -e

# Push with a passphrase-less deploy key for this repo only, so publishing doesn't
# depend on ssh-agent or the Keychain (unavailable after a reboot or in a dark
# wake). Never wait for a prompt or a dead connection (e.g. the Mac fell asleep
# mid-push): a hung run blocks all later ones, since launchd doesn't start a job
# that is still running.
export GIT_SSH_COMMAND="ssh -F /dev/null -i $HOME/.ssh/flights_deploy_key -o IdentitiesOnly=yes -o IdentityAgent=none -o BatchMode=yes -o ConnectTimeout=30 -o ServerAliveInterval=15 -o ServerAliveCountMax=4"

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
