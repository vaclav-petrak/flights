# Flight Price Tracker

## Overview
This project tracks Ryanair prices between Prague (PRG) and Skiathos (JSI). Every day it records the one-way fare for each flight day in the season, then publishes a static website on GitHub Pages. The site shows round-trip combinations, a season calendar with house occupancy, and price history.

Season 2027: flights on **Tuesday and Saturday**, June to September (`config/config.json`).

## Features
- Daily fares for every flight day, both directions, converted to EUR
- Retries prices that failed to scrape on later runs the same day
- Website (`docs/`) published to GitHub Pages after each run:
  - trip finder: every round trip by length, total price, change since the last check, house free/taken
  - season calendar with fares and house occupancy
  - price history chart per flight day or trip
- House booking kept in a local Excel file. Only the dates are published; names and notes stay local.

## Project Structure
```
flight_price_tracker/
├── src/
│   ├── main.py          # scrape today's prices -> data/flights.csv
│   ├── build_site.py    # data + booking -> docs/ (website)
│   └── functions.py
├── site/index.html      # website template (data is injected by build_site.py)
├── docs/                # generated website, served by GitHub Pages
├── booking/booking.xlsx # local house booking (git-ignored)
├── data/
│   ├── flights.csv      # current season prices
│   └── archive/         # past seasons
├── config/config.json   # season dates and flight days
└── scripts/
    ├── run_flight_tracker.sh  # scrape + build + publish (run hourly by launchd)
    ├── publish_site.sh        # commit data/flights.csv + docs/ and push
    └── com.petrak.flight-price-tracker.plist  # launchd job definition
```

## Setup
1. Install UV (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:

```bash
uv sync
```

3. GitHub Pages: in the repository settings, set **Pages → Build and deployment → Deploy from a branch → `main` / `docs`**.

## House booking
Edit `booking/booking.xlsx`, sheet **Stays**: one row per stay with Name, Arrival, Departure and Note.
Arrival and departure days are changeover days. The nights in between are shown as occupied, and trips that overlap them are marked as taken.

## Usage

```bash
uv run python src/main.py         # scrape today's prices
uv run python src/build_site.py   # rebuild docs/ (open docs/index.html to preview)
scripts/publish_site.sh           # commit and push the site
```

## Automation
`scripts/run_flight_tracker.sh` runs every hour via launchd. Runs before 07:00 exit right away (`START_HOUR` in the script), so each day's check starts at 07:00 Prague time. Each run scrapes, retries any prices that failed earlier, rebuilds the site and pushes it, but only commits when something changed. Unlike cron, launchd runs a missed job as soon as the Mac wakes up, so checks aren't lost while it sleeps.

```bash
# install / reload
cp scripts/com.petrak.flight-price-tracker.plist ~/Library/LaunchAgents/
launchctl bootout gui/$(id -u)/com.petrak.flight-price-tracker 2>/dev/null
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.petrak.flight-price-tracker.plist

# status / run now
launchctl print gui/$(id -u)/com.petrak.flight-price-tracker | grep -E "state|runs|last exit"
launchctl kickstart gui/$(id -u)/com.petrak.flight-price-tracker
```

Output is logged to `data/logs/tracker.log` (launchd's own messages go to `data/logs/launchd.log`). The page shows a warning next to "Last check" when prices are more than a day old. The push uses a passphrase-less deploy key, `~/.ssh/flights_deploy_key`, added with write access under the repo's Settings → Deploy keys. It doesn't use your own SSH key, because ssh-agent and the Keychain aren't reliably available to launchd after a reboot or while the Mac is in a dark wake. Pushes time out instead of hanging, because a stuck run would block all later ones. To set up the key on a new Mac:

```bash
ssh-keygen -q -t ed25519 -N "" -C "flight-price-tracker deploy key" -f ~/.ssh/flights_deploy_key
cat ~/.ssh/flights_deploy_key.pub   # add on GitHub with "Allow write access"
```

## New season
1. Move `data/flights.csv` to `data/archive/flights_<year>.csv` and start a new file with only the header (or an empty file).
2. Update `config/config.json`: `flight_dates_from`, `flight_dates_to`, `flight_days`.
3. Add the stays to `booking/booking.xlsx`.

To preview an archived season: `uv run python src/build_site.py --flights data/archive/flights_2026.csv --season-from 2026-06-01 --season-to 2026-09-30 --days Monday Thursday --out /tmp/preview`, then open `/tmp/preview/index.html?today=2026-05-20`.

## Contributing
Contributions to improve the project are welcome. Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature.
3. Commit your changes.
4. Push to the branch.
5. Create a new Pull Request.

## Contact
[Vaclav B. Petrak] - [vaclav.b.petrak@gmail.com]