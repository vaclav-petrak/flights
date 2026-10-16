# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Tracks daily Ryanair one-way fares Prague (PRG) ⇄ Skiathos (JSI) for one summer season and publishes a static website (GitHub Pages from `main` / `docs/`). The site replaced an older Google Sheets workflow; its four tabs mirror the old spreadsheet tabs (`trips`, `from_prague`, `to_prague`, `calendar`). Season dates and flight weekdays live in `config/config.json`.

## Commands

```bash
uv sync                                   # install deps (Python 3.12)
uv run python src/main.py                 # scrape today's prices -> data/flights.csv
uv run python src/build_site.py           # data + booking -> docs/index.html, docs/data.json
scripts/publish_site.sh                   # commit data/flights.csv + docs/ and push main

# tests (pytest is not a project dependency; run from src/ because modules import each other flatly)
cd src && uv run --with pytest python -m pytest -q
cd src && uv run --with pytest python -m pytest -q test_functions.py::test_get_dates_between_filtering

# preview an archived season (open with ?today=YYYY-MM-DD to fake "today")
uv run python src/build_site.py --flights data/archive/flights_2026.csv \
  --season-from 2026-06-01 --season-to 2026-09-30 --days Monday Thursday --out /tmp/preview
```

Check page changes visually with headless Chrome, e.g.
`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --window-size=1440,1000 --screenshot=out.png "file://$PWD/docs/index.html#trips"` (tabs: `#trips`, `#out`, `#back`, `#house`). Headless Chrome has a ~500px minimum window width, so test phone layouts inside a 390px-wide iframe.

## Architecture

Pipeline: `src/main.py` (scrape) → `data/flights.csv` → `src/build_site.py` → `docs/` (published).

- **Scraping** (`src/functions.py`): `get_flight_price` calls Ryanair's `farfnd/3/oneWayFares` API and converts to EUR via the Frankfurter API. It returns `None` both for "not on sale / sold out" and for request failures. `main.py` re-scrapes any missing cell for today on every run, so hourly runs fill gaps. `src/` modules import each other without a package (`from functions import ...`), so run them as scripts or from inside `src/`.
- **`data/flights.csv` format**: wide table. Each row is one `offer_date` (check day) × `direction` (`From Prague` / `To Prague`); columns are the flight dates from the config. Past seasons go to `data/archive/flights_<year>.csv`.
- **House booking**: `booking/booking.xlsx`, sheet `Stays` (Name, Arrival, Departure, Note). It is git-ignored on purpose because it holds guest names. `build_site.py` publishes only arrival/departure dates. A stay occupies the nights `[arrival, departure)`, so arrival and departure days count as changeover days. The page's JS implements the same rule (`clashes`, `dayState`).
- **Site**: `site/index.html` is the single template: CSS + vanilla JS, no build step or libraries. `build_site.py` replaces the placeholder `/*__FLIGHT_DATA__*/null` with the JSON payload and writes `docs/`. All rendering happens client-side, including "today", past-flight hiding and the stale-data warning (`?today=` overrides it). Never edit `docs/` by hand; edit the template and rebuild.
  - Round trips: one row per departure, one column per trip length, where column *k* returns on the *k*-th following flight day (`MAX_SLOTS = 6`). Cards link to Ryanair's flight-select page only when both legs had a fare at the last check and departure hasn't passed.
  - Colour scale copies the old spreadsheet: green `#57BB8A` → white at the median → red `#E67C73`. The price grids use fixed €20 / median / €200 ends, as the Excel conditional formatting did. Round trips use the 5th / median / 95th percentile.
  - "When to buy" tab (`#buy`): a buy window per flight and leg (`BUY_FROM`/`BUY_TO`/`CHEAP` in the JS, taken from a backtest of the 2025–26 seasons), plus a heatmap of median fares by days before departure. `build_site.py` `load_history` computes the heatmap from `data/archive/` seasons before the current one, skipping seasons tracked from less than 180 days out (2024).
  - The page is intentionally light-only (dark mode was removed at the owner's request).

## Automation

`scripts/run_flight_tracker.sh` runs hourly through launchd (`scripts/com.petrak.flight-price-tracker.plist`, installed in `~/Library/LaunchAgents`; launchd, unlike cron, catches up after sleep). Each run does scrape → build → `publish_site.sh`. Logs go to `data/logs/tracker.log`.

`publish_site.sh` commits only `data/flights.csv` and `docs/`, and only when they changed, then pushes `origin main`. Consequences:
- Work happens on `main`. On another branch, the hourly job would commit there and push a stale `main`.
- Any local commits on `main` are pushed by the next hourly run.

Never commit `sheets/` (the old spreadsheet export contains guest names) or `booking/`.

## New season

Move `data/flights.csv` to `data/archive/flights_<year>.csv` and start a header-only file. Update `config/config.json` (`flight_dates_from`, `flight_dates_to`, `flight_days`), then add the stays to `booking/booking.xlsx`.
