import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


# =============================
# Core Configuration Model
# =============================

@dataclass(frozen=True)
class Settings:
    # API Keys
    instagram_session_id: str
    gemini_api_key: str

    # Sheets
    spreadsheet_name: str
    worksheet_name: str
    service_account_file: str

    # Sheet Column Names (Header-based, no indexes)
    col_status: str
    col_message_number: str
    col_last_message_date: str

    # Runtime Logic
    default_dm_delay_seconds: int
    drip_delay_days: int
    test_mode: bool

    # Messaging
    default_dm_message: str
    
    # Rate Limiting
    min_delay_seconds: int
    max_delay_seconds: int
    max_daily_messages: int
    max_sequence: int

    # Drip Templates
    drip_templates: dict


def _get_env(key: str, required: bool = True, default=None):
    value = os.getenv(key, default)

    if required and not value:
        raise ValueError(f"Missing required environment variable: {key}")

    return value


settings = Settings(
    # API
    instagram_session_id=_get_env("INSTAGRAM_SESSIONID"),
    gemini_api_key=_get_env("GEMINI_API_KEY"),

    # Sheets
    spreadsheet_name="50K SCRAPED LEADS IN PHOENIX",
    worksheet_name="Sheet1",
    service_account_file="credentials.json",

    # Header-based column mapping (no magic numbers)
    col_status="Status",
    col_message_number="Message Number",
    col_last_message_date="Last Message Date",

    # Runtime
    default_dm_delay_seconds=1200,
    drip_delay_days=3,
    test_mode=False,

    # Default Message
    default_dm_message="""Hi! 👋 My name is John... (your full message here)""",
    
    # Rate Limiting
    min_delay_seconds=45,
    max_delay_seconds=120,
    max_daily_messages=25,
    max_sequence=4,

    # Drip Templates
    drip_templates={
        1: "Intro message template...",
        2: "Value message template...",
        3: "Social proof template...",
        4: "CTA template..."
    },
    
)
