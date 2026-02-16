import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SPREADSHEET_NAME, WORKSHEET_NAME

class SheetsHandler:
    def __init__(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
        self.gc = gspread.authorize(creds)
        self.sheet = self.gc.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

    def get_all_leads(self):
        return self.sheet.get_all_records()

    def update_lead(self, row_idx, col_idx, value):
        self.sheet.update_cell(row_idx, col_idx, value)