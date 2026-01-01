import pandas as pd
import os
from datetime import datetime
from functions import get_flight_price, export_to_sheets, get_dates_between 

def main(print_output=True):
    FLIGHT_DATES_FROM = "2026-06-01"
    FLIGHT_DATES_TO = "2026-09-30"
    FLIGHT_DAYS = ['Monday', 'Thursday']

    departure_dates = get_dates_between(FLIGHT_DATES_FROM, FLIGHT_DATES_TO, days_of_week=FLIGHT_DAYS)

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

    # Script is not updated if records already exist
    if today in saved_records.index:
        if print_output: print(f"Data for date {today} are already saved.")

    else:
        current_date_from_prg = {"direction": "From Prague", "offer_date": today}
        current_date_to_prg = {"direction": "To Prague", "offer_date": today}

        if print_output: print("Getting prices from Ryanair between Prague and Skiathos")

        for departure_date in departure_dates:
            price_from_prg = get_flight_price(date=departure_date, departure = "PRG", arrival = "JSI")
            current_date_from_prg[departure_date] = price_from_prg

            price_to_prg = get_flight_price(date=departure_date, departure = "JSI", arrival = "PRG")
            current_date_to_prg[departure_date] = price_to_prg 
            if print_output:
                print(f"    {departure_date} from / to prague: {price_from_prg} / {price_to_prg}")

        df_from_prg = pd.DataFrame([current_date_from_prg]).set_index('offer_date')
        df_to_prg = pd.DataFrame([current_date_to_prg]).set_index('offer_date')
        records = pd.concat([saved_records, df_from_prg, df_to_prg])


        if print_output: print("Price for all flights collected")
        
        # Save to file
        records.to_csv(saved_records_path)

        # Convert index to datetime
        records.index = pd.to_datetime(records.index)

        # Sort the DataFrame by index (offer_date) in descending order
        records = records.sort_index(ascending=False)
        from_prague_records = records[records["direction"] == "From Prague"]
        to_prague_records = records[records["direction"] == "To Prague"]

        export_to_sheets(from_prague_records, sheet='from_prague')
        export_to_sheets(to_prague_records, sheet='to_prague')


if __name__ == "__main__":
    main()