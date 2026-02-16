import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
IG_SESSIONID = os.getenv("INSTAGRAM_SESSIONID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Sheets Configuration
SPREADSHEET_NAME = '50K SCRAPED LEADS IN PHOENIX'
WORKSHEET_NAME = 'Sheet1'
SERVICE_ACCOUNT_FILE = 'credentials.json'
STATUS_COL = 13  # Column M
MSG_NUMBER_COL = 14 # Column N (New for Drip)
LAST_DATE_COL = 15  # Column O (New for Drip)

# Logic Settings
DEFAULT_DM_DELAY = 1200
TEST_MODE = False
DRIP_DELAY_DAYS = 3

DEFAULT_DM_MESSAGE = """Hi! 👋 My name is John... (your full message here)"""