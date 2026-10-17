import pandas as pd
import os
from datetime import datetime
from functions import get_flight_price, get_dates_between, load_config

def is_missing(value):
    """A cell counts as missing if it was never scraped or stored as a dash."""
    return value is None or value == "-" or pd.isna(value)

def main(print_output=True):

    # Load config
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '../config/config.json')
    config = load_config(config_path=config_path)

    departure_dates = get_dates_between(
        start_date = config['flight_dates_from'],
        end_date = config['flight_dates_to'],
        days_of_week =  config['flight_days'])

    # Get the absolute path to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the credentials file
    saved_records_path = os.path.join(script_dir, '../data/flights.csv')

    # Load saved records
    saved_records = pd.read_csv(saved_records_path, index_col='offer_date')
    
    if len(saved_records.index) == 0:
        saved_records = pd.DataFrame(columns=['offer_date', 'direction'] + departure_dates)
        saved_records.set_index('offer_date', inplace=True)

    # Get the current date
    current_date = datetime.now().date()
    today = current_date.strftime("%Y-%m-%d")

    # Existing rows for today (if any), so we only re-scrape the missing cells.
    # A previous run may have failed to scrape some prices (stored as missing / "-");
    # those are retried on each subsequent run until a value is found.
    todays_records = saved_records[saved_records.index == today]

    def existing_prices(direction):
        rows = todays_records[todays_records["direction"] == direction]
        return rows.iloc[0].to_dict() if len(rows) else {}

    existing_from = existing_prices("From Prague")
    existing_to = existing_prices("To Prague")

    current_date_from_prg = {"direction": "From Prague", "offer_date": today}
    current_date_to_prg = {"direction": "To Prague", "offer_date": today}

    if print_output:
        if len(todays_records):
            print("Retrying missing prices from Ryanair between Prague and Skiathos")
        else:
            print("Getting prices from Ryanair between Prague and Skiathos")

    scraped_count = 0
    for departure_date in departure_dates:
        from_val = existing_from.get(departure_date)
        if is_missing(from_val):
            price_from_prg = get_flight_price(date=departure_date, departure="PRG", arrival="JSI")
            scraped_count += 1
        else:
            price_from_prg = from_val
        current_date_from_prg[departure_date] = price_from_prg

        to_val = existing_to.get(departure_date)
        if is_missing(to_val):
            price_to_prg = get_flight_price(date=departure_date, departure="JSI", arrival="PRG")
            scraped_count += 1
        else:
            price_to_prg = to_val
        current_date_to_prg[departure_date] = price_to_prg

        if print_output:
            print(f"    {departure_date} from / to Prague: {price_from_prg} / {price_to_prg}")

    # Nothing to do if today's data already exists and no cell was missing
    if len(todays_records) and scraped_count == 0:
        if print_output: print(f"Data for date {today} are already complete.")
        return

    # Drop any existing rows for today; they are replaced by the refreshed values
    saved_records = saved_records[saved_records.index != today]

    df_from_prg = pd.DataFrame([current_date_from_prg]).set_index('offer_date')
    df_to_prg = pd.DataFrame([current_date_to_prg]).set_index('offer_date')
    # Skip the empty frame of a fresh season (pandas warns on concatenating it)
    records = pd.concat([df for df in (saved_records, df_from_prg, df_to_prg) if len(df)])
    # Keep flight columns in date order when the season is extended (concat appends new ones)
    records = records[['direction'] + sorted(c for c in records.columns if c != 'direction')]

    if print_output: print("Price for all flights collected")

    # Save to file
    records.to_csv(saved_records_path)


if __name__ == "__main__":
    main()