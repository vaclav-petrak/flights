import pytest
from unittest.mock import patch, Mock
import functions 
from datetime import datetime, timedelta  

def test_get_dates_between_basic_range():
    """Test if it generates all days in a small range."""
    start = '2024-01-01'
    end = '2024-01-03'
    result = functions.get_dates_between(start, end)
    
    # We expect 3 days: 1st, 2nd, and 3rd
    assert len(result) == 3
    assert result == ['2024-01-01', '2024-01-02', '2024-01-03']

def test_get_dates_between_filtering():
    """Test if it correctly filters only Mondays (Mo)."""
    start = '2024-07-01' # This is a Monday
    end = '2024-07-10'
    
    # filter for Monday only
    result = functions.get_dates_between(start, end, days_of_week=['Mon'])
    
    # In this 10 day range, there are 2 Mondays (1st and 8th)
    assert result == ['2024-07-01', '2024-07-08']


# --- "Mocked" Test ---

@patch('functions.requests.get')
def test_get_flight_price_success(mock_get):
    """Test that we can parse a correct JSON response."""
    
    # --- BETTER APPROACH: Dynamic Date ---
    future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    # 1. Setup the fake data
    fake_json = {
        "fares": [{
            "outbound": {
                "price": {
                    "value": 127,
                    "currencyCode": "EUR"
                }
            }
        }]
    }
    
    # 2. Teach the mock to return this data
    mock_get.return_value.json.return_value = fake_json

    # 3. Run your function with the SAFE future date
    price = functions.get_flight_price(future_date, "PRG", "JSI")

    # 4. Assertions
    assert price == 127

@patch('functions.requests.get')
def test_get_flight_price_no_flights(mock_get):
    """Test what happens if Ryanair returns no fares (empty list)."""
    
    # Setup fake data with empty fares
    fake_json = {"fares": []}
    mock_get.return_value.json.return_value = fake_json

    price = functions.get_flight_price("2030-01-01")

    # Your code returns None if it catches an IndexError
    assert price is None