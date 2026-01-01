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

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Google Sheets API credentials:
   - Follow the [Google Sheets API Python Quickstart](https://developers.google.com/sheets/api/quickstart/python) to obtain your `credentials.json` file.
   - Place the `credentials.json` file in the `config/` directory.

## Usage
Run the main script to fetch and save flight prices:
```
python src/main.py
```

I run the script from command line using conda enviroment
```
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

## License
[Specify your license here, e.g., MIT, GPL, etc.]

## Contact
[Vaclav B. Petrak] - [vaclav.b.petrak@gmail.com]