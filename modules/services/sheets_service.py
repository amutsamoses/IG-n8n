import logging
from typing import List, Dict
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


class SheetsHandler:
    def __init__(self, service_account_file: str, spreadsheet_name: str, worksheet_name: str):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        self.gc = gspread.authorize(creds)
        self.sheet = self.gc.open(spreadsheet_name).worksheet(worksheet_name)

    def get_all_leads(self) -> List[Dict]:
        try:
            return self.sheet.get_all_records()
        except Exception:
            logger.exception("Failed fetching leads from sheet")
            return []

    def find_row_by_username(self, username: str) -> int:
        """
        Returns row index (1-based) or -1 if not found.
        """
        try:
            cell = self.sheet.find(username)
            return cell.row
        except Exception:
            return -1

    def update_lead_fields(self, row: int, updates: Dict[str, str]) -> bool:
        """
        Updates multiple fields by header name.
        """
        try:
            headers = self.sheet.row_values(1)
            update_cells = []

            for key, value in updates.items():
                if key in headers:
                    col_index = headers.index(key) + 1
                    update_cells.append((row, col_index, value))

            for r, c, v in update_cells:
                self.sheet.update_cell(r, c, v)

            return True

        except Exception:
            logger.exception(f"Failed updating row {row}")
            return False
