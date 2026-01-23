from __future__ import print_function
from auth import spreadsheet_service
from auth import drive_service
import requests
import time
import pandas as pd
import json
from datetime import datetime
import os

def load_config(config_path = "'./config/config.json"):
    with open(config_path, 'r') as f:
        return json.load(f)

def create_spreadsheet(title):
    """ Creates new Google spreadsheet spreadsheet """
    spreadsheet_details = {
        'properties': {
            'title': title
        }
    }
    sheet = spreadsheet_service.spreadsheets().create(body=spreadsheet_details,
                                    fields='spreadsheetId').execute()
    sheetId = sheet.get('spreadsheetId')
    print('Spreadsheet ID: {0}'.format(sheetId))
    permission1 = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'vaclavp@gmail.com'
    }
    drive_service.permissions().create(fileId=sheetId, body=permission1).execute()
    return sheetId

def export_to_sheets(df, sheet = 'data', spreadsheet_id = '1UpjPSDufq4DkDN0cQdRGuMNBtHMSoitT5QnytD8HVjo'):
    """ Exports data to Google sheets """
    spreadsheet_id = spreadsheet_id
    
    df = df.fillna("-").infer_objects(copy=False)
    
    # Convert index to datetime strings
    df.index = df.index.strftime('%Y-%m-%d')
    
    # Reset the index to make it a column
    df_reset = df.reset_index()
    
    # Add the index name as the first element in the column list
    columns = [df.index.name] + df.columns.tolist()
    
    # Convert all values to strings
    values = [[str(cell) for cell in row] for row in df_reset.values.tolist()]
    
    body = {
        'values': [columns] + values
    }
    
    result = spreadsheet_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, 
        range= sheet + '!A1', 
        valueInputOption='USER_ENTERED', 
        body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

def convert_currency(amount, from_curr, to_curr="EUR"):
    """
    Converts amount dynamically using the free Frankfurter API.
    """
    if from_curr == to_curr:
        return amount
    
    try:
        # Request exchange rate
        url = f"https://api.frankfurter.app/latest"
        params = {"amount": amount, "from": from_curr, "to": to_curr}
        
        response = requests.get(url, params=params)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        
        return data["rates"][to_curr]
        
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Conversion failed ({from_curr} to {to_curr}): {e}")
        return None

def get_flight_price(date, departure="PRG", arrival="JSI", target_currency="EUR"):
    """ Gets data from Ryanair website and converts currency dynamically """
    
    url = "https://services-api.ryanair.com/farfnd/3/oneWayFares"
    
    params = {
        "departureAirportIataCode": departure,
        "arrivalAirportIataCode": arrival,
        "outboundDepartureDateFrom": date,
        "outboundDepartureDateTo": date
    }

    current_date = datetime.now().date()
    search_date = datetime.strptime(date, "%Y-%m-%d").date()

    price = None # Default initialization

    if search_date >= current_date:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extracting relevant information
            fare = data["fares"][0]
            raw_price = fare["outbound"]["price"]["value"]
            currency_code = fare["outbound"]["price"]["currencyCode"]
            
            # Dynamic Conversion
            price = convert_currency(raw_price, currency_code, target_currency)

        except (IndexError, KeyError):
            # No fares found
            price = None
        except requests.RequestException as e:
            print(f"Ryanair API Request failed: {e}")
            price = None

        if price is not None:
            price = round(price, 0)
            
        time.sleep(1) # Be polite to the API
    
    return price





def get_dates_between(start_date, end_date, days_of_week=None):
    """
    Generate a list of dates between two dates, optionally filtered by specific days of the week.

    Parameters:
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.
        days_of_week (list of str, optional): List of day names to include.
            Day names can be full or abbreviated and are case-insensitive.
            Examples: ['Monday', 'Thu', 'friday', 'sa'].

    Returns:
        list of str: A list of date strings in 'YYYY-MM-DD' format that fall between
        the start and end dates (inclusive) and match the specified days of the week.

    Examples:
        >>> get_dates_between('2024-07-01', '2024-07-31', days_of_week=['Mon', 'THURSDAY'])
        ['2024-07-01', '2024-07-04', '2024-07-08', '2024-07-11', '2024-07-15', '2024-07-18', '2024-07-22', '2024-07-25', '2024-07-29']

    Notes:
        - If 'days_of_week' is None, all dates between the start and end dates are returned.
        - The function accepts day names in various formats; it standardizes them by converting
        to lowercase and taking the first two letters.
        - Valid day abbreviations include any case-insensitive version of the day name or its first
        few letters (e.g., 'Mon', 'monday', 'MO', 'mo', 'Mo').
        - The function does not perform validation on the input date strings; ensure they are in
        the correct format.
    """
    from datetime import datetime, timedelta

    day_name_to_int = {
        'mo': 0,
        'tu': 1,
        'we': 2,
        'th': 3,
        'fr': 4,
        'sa': 5,
        'su': 6
    }

    # If days_of_week is provided, process it
    if days_of_week is not None:
        # Standardize day names to two-letter lowercase abbreviations
        days_of_week = [day.lower()[:2] for day in days_of_week]
        # Convert the day abbreviations to their corresponding weekday numbers
        days_of_week_int = [day_name_to_int[day] for day in days_of_week]
    else:
        days_of_week_int = None  # Include all days if not specified

    # Parse the input date strings into datetime objects
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    # Calculate the difference between the dates
    delta = end_date_dt - start_date_dt

    # Generate a list of dates between the start and end dates, inclusive
    dates = []
    for i in range(delta.days + 1):
        current_date = start_date_dt + timedelta(days=i)
        if days_of_week_int is None or current_date.weekday() in days_of_week_int:
            dates.append(current_date.strftime('%Y-%m-%d'))

    return dates

