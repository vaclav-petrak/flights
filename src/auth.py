# auth.py

from __future__ import print_function
from googleapiclient.discovery import build 
from google.oauth2 import service_account
import os

# Define the required scopes for Google Sheets and Drive API access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Load credentials from the service account file


# Get the absolute path to the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the credentials file
credentials_path = os.path.join(script_dir, '../config/credentials.json')

credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=SCOPES)

# Create a Google Sheets API service object
spreadsheet_service = build('sheets', 'v4', credentials=credentials)

# Create a Google Drive API service object
drive_service = build('drive', 'v3', credentials=credentials)