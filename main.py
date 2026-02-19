import time
import logging
from datetime import datetime
from typing import Dict

from modules.sheets_service import SheetsHandler
from modules.instagram_service import InstagramClient
from modules.ai_engine_service import AIEngine
from modules.core.drip_engine import DripEngine
from modules.core.rate_limiter import RateLimiter
from modules.metrics import Metrics
import config as settings
import config


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DripOrchestrator:
    def __init__(self):
        self.instagram = InstagramClient(
            session_id=config.IG_SESSIONID,
            test_mode=config.TEST_MODE
        )

        self.sheets = SheetsHandler(
            service_account_file=config.SERVICE_ACCOUNT_FILE,
            spreadsheet_name=config.SPREADSHEET_NAME,
            worksheet_name=config.WORKSHEET_NAME
        )

        self.ai = AIEngine(
            api_key=config.GEMINI_API_KEY,
            default_message=config.DEFAULT_DM_MESSAGE
        )

    def extract_username(self, url: str) -> str:
        return url.strip().rstrip("/").split("/")[-1]

    def should_skip(self, row: Dict) -> bool:
        if not row.get("INSTAGRAM URL"):
            return True

        status = str(row.get("Status", "")).lower()
        if status in ["completed", "replied", "messaged ✅"]:
            return True

        return False

    def process_lead(self, row: Dict, row_index: int):
        url = row.get("INSTAGRAM URL")
        username = self.extract_username(url)

        user = self.instagram.get_valid_user(username)
        if not user:
            logger.info(f"User not valid: {username}")
            return

        message = self.ai.generate_custom_dm(user.get("biography"))

        success = self.instagram.send_message(user.get("pk"), message)

        if success:
            updates = {
                "Status": "messaged ✅",
                "Last Message Date": datetime.now().strftime("%Y-%m-%d"),
            }

            self.sheets.update_lead_fields(row_index, updates)
            logger.info(f"Message sent & sheet updated: {username}")

            time.sleep(config.DEFAULT_DM_DELAY)

    def run(self):
        if not self.instagram.login():
            logger.error("Login failed. Bot aborted.")
            return

        leads = self.sheets.get_all_leads()

        for idx, row in enumerate(leads, start=2):  # Start at row 2 (skip headers)
            try:
                if self.should_skip(row):
                    continue

                self.process_lead(row, idx)

            except Exception:
                logger.exception(f"Error processing row {idx}")


if __name__ == "__main__":
    DripOrchestrator().run()
