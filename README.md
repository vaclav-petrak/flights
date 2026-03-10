# Flight Price Tracker

## Overview
This project is a flight price tracker that monitors and records prices for flights between Prague (PRG) and Skiathos (JSI). It automatically fetches prices for specified dates, saves the data, and can export it to Google Sheets for easy analysis.

## Features
- Fetches flight prices for multiple dates
- Tracks prices for both directions (PRG to JSI and JSI to PRG)
- Saves data locally in a CSV file
- Exports data to Google Sheets (optional)
- Avoids duplicate data collection for the same date

## Project Structure
```
flight_price_tracker/
│
├── src/
│   ├── main.py
│   ├── functions.py
│   └── auth.py
│
├── data/
│   └── flights.csv
│
├── config/
│   └── credentials.json
│
├── requirements.txt
└── README.md
```

## Setup
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/flight_price_tracker.git
   cd flight_price_tracker
   ```

2. Install UV (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies with UV:

```bash
uv sync
```

4. Set up your Google Sheets API credentials:
   - Follow the [Google Sheets API Python Quickstart](https://developers.google.com/sheets/api/quickstart/python) to obtain your `credentials.json` file.
   - Place the `credentials.json` file in the `config/` directory.

## Usage

Run the main script to fetch and save flight prices:

```bash
uv run python src/main.py
```

For automated execution, you can set up a cron job:

```bash
# Edit crontab
crontab -e

# Add line to run every hour
0 * * * * /Users/vaclav/Code/flight_price_tracker/scripts/run_flight_tracker.sh
```

I run the script from command line using conda enviroment

```bash
/opt/homebrew/anaconda3/bin/python /Users/vaclav/OneDrive/personal/sw/flight_price_tracker/src/main.py
```

The script will:
1. Check if data for the current date has already been collected.
2. If not, it will fetch prices for all specified dates.
3. Save the new data to `data/flights.csv`.
4. Optionally export the data to Google Sheets (uncomment the relevant lines in `main.py` to enable this feature).

## Customization
- To change the date range or days of the week for price checking, modify the parameters in the `generate_dates()` function call in `src/main.py`.
- To track different routes, update the airport codes (PRG and JSI) in `src/main.py`.

## Contributing
Contributions to improve the project are welcome. Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature.
3. Commit your changes.
4. Push to the branch.
5. Create a new Pull Request.

## Contact
[Vaclav B. Petrak] - [vaclav.b.petrak@gmail.com]