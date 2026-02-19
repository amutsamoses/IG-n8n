from email import message
import time
import logging
from datetime import datetime
from typing import Dict

from modules.services.sheets_service import SheetsHandler
from modules.services.instagram_service import InstagramClient
from modules.services.ai_engine_service import AIEngine
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
            session_id=settings.instagram_session_id,
            test_mode=settings.test_mode
        )

        self.sheets = SheetsHandler(
            service_account_file=settings.service_account_file,
            spreadsheet_name=settings.spreadsheet_name,
            worksheet_name=settings.worksheet_name
        )

        self.ai = AIEngine(
            api_key=settings.gemini_api_key,
            default_message=settings.default_dm_message
        )
        
        self.drip_engine = DripEngine(
            delay_days=settings.drip_delay_days,
            max_sequence=settings.max_sequence
        )

        self.rate_limiter = RateLimiter(
            min_delay_seconds=settings.min_delay_seconds,
            max_delay_seconds=settings.max_delay_seconds
        )

        self.metrics = Metrics()
        self.sent_today = 0


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
        if self.sent_today >= settings.max_daily_messages:
            logger.info("Daily message cap reached.")
            return False  # stop processing

        if not self.drip_engine.should_send(row):
            self.metrics.skipped += 1
            return True

        url = row.get("INSTAGRAM URL")
        username = self.extract_username(url)

        user = self.instagram.get_valid_user(username)
        if not user:
            self.metrics.failed += 1
            return True

        msg_number = self.drip_engine.next_message_number(row)
        template = settings.drip_templates.get(msg_number)

        message = self.ai.generate_custom_dm(user.get("biography"), template)

    # Mark as sending (crash safety)
        self.sheets.update_lead_fields(row_index, {
            settings.col_status: "sending..."
    })

        success = self.instagram.send_message(user.get("pk"), message)

        if success:
            self.sent_today += 1
            self.metrics.sent += 1

            updates = {
                settings.col_status: "completed" 
                if self.drip_engine.mark_completed(msg_number)
                else "messaged",
                settings.col_message_number: msg_number,    
                settings.col_last_message_date: datetime.now().strftime("%Y-%m-%d"),
        }

            self.sheets.update_lead_fields(row_index, updates)

            self.rate_limiter.wait()
        else:
            self.metrics.failed += 1

        return True


    def run(self):
        if not self.instagram.login():
            logger.error("Login failed. Bot aborted.")
            return

        leads = self.sheets.get_all_leads()

        for idx, row in enumerate(leads, start=2):  # Start at row 2 (skip headers)
            try:
                if self.should_skip(row):
                    continue
                
                should_continue = self.process_lead(row, idx)
                if not should_continue:
                    logger.info("Stopping further processing for today.")
                    break

            except Exception:
                logger.exception(f"Error processing row {idx}")
                
        logger.info(f"Run complete: {self.metrics.report()}")



if __name__ == "__main__":
    DripOrchestrator().run()
