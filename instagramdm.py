import os
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List

from dotenv import load_dotenv
from instagrapi import Client
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials


# =============================
# Logging
# =============================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =============================
# Services
# =============================

class InstagramService:
    def __init__(self, session_id: str, test_mode: bool = False):
        self.client = Client()
        self.session_id = session_id
        self.test_mode = test_mode

    def login(self) -> bool:
        try:
            self.client.login_by_sessionid(self.session_id)
            logger.info("Instagram login successful")
            return True
        except Exception:
            logger.exception("Instagram login failed")
            return False

    def get_user(self, username: str):
        try:
            return self.client.user_info_by_username(username)
        except Exception:
            logger.warning(f"Failed fetching user {username}")
            return None

    def calculate_engagement(self, user) -> float:
        try:
            medias = self.client.user_medias(user.pk, 10)
            total = sum(m.like_count + m.comment_count for m in medias)
            return round((total / 10) / user.follower_count * 100, 2)
        except Exception:
            return 0

    def is_valid_user(self, user) -> bool:
        if user.is_private:
            return False
        if not (1000 <= user.follower_count <= 50000):
            return False
        if self.calculate_engagement(user) < 0.5:
            return False
        return True

    def send_dm(self, user, message: str) -> bool:
        try:
            if self.test_mode:
                logger.info(f"[TEST MODE] Would DM @{user.username}")
                return True

            self.client.direct_send(message, [user.pk])
            logger.info(f"Sent DM to @{user.username}")
            return True

        except Exception:
            logger.exception(f"DM failed for @{user.username}")
            return False


class AIService:
    DEFAULT_MESSAGE = """Hi! 👋 My name is John..."""

    NICHE_KEYWORDS = {
        "business": ["founder", "ceo", "startup", "entrepreneur"],
        "marketing": ["marketing", "branding", "seo", "ads"],
        "creator": ["content", "creator", "youtube", "tiktok"],
        "tech": ["developer", "software", "ai", "app"],
    }

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def analyze_niche(self, bio: str) -> str:
        if not bio:
            return "default"

        bio = bio.lower()

        for niche, keywords in self.NICHE_KEYWORDS.items():
            if any(k in bio for k in keywords):
                return niche

        return "default"

    def generate_dm(self, bio: str) -> str:
        try:
            niche = self.analyze_niche(bio)
            prompt = f"""
Bio: {bio}
Niche: {niche}
Write a concise, friendly Instagram DM similar to:
{self.DEFAULT_MESSAGE}
"""

            response = self.model.generate_content(prompt)
            text = response.text.strip()

            if not text or len(text) > 1000:
                return self.DEFAULT_MESSAGE

            return text

        except Exception:
            logger.exception("AI generation failed")
            return self.DEFAULT_MESSAGE


class SheetsService:
    def __init__(self, credentials_file: str, spreadsheet: str, worksheet: str):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        self.gc = gspread.authorize(creds)
        self.sheet = self.gc.open(spreadsheet).worksheet(worksheet)

    def get_rows(self) -> List[Dict]:
        return self.sheet.get_all_records()

    def update_status(self, row_index: int, status: str):
        headers = self.sheet.row_values(1)
        if "Status" not in headers:
            return

        col = headers.index("Status") + 1
        self.sheet.update_cell(row_index, col, status)


# =============================
# Orchestrator
# =============================

class InstagramDMBot:
    def __init__(self):
        load_dotenv()

        self.instagram = InstagramService(
            session_id=os.getenv("INSTAGRAM_SESSIONID"),
            test_mode=False
        )

        self.ai = AIService(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.sheets = SheetsService(
            credentials_file="credentials.json",
            spreadsheet="50K SCRAPED LEADS IN PHOENIX",
            worksheet="Sheet1"
        )

        self.delay = 1200  # 20 min

    @staticmethod
    def extract_username(url: str) -> Optional[str]:
        if not url:
            return None
        return url.strip().rstrip("/").split("/")[-1]

    def run(self):
        if not self.instagram.login():
            return

        rows = self.sheets.get_rows()
        processed = set()

        for idx, row in enumerate(rows, start=2):

            url = row.get("INSTAGRAM URL")
            status = row.get("Status")

            if not url or status == "messaged ✅":
                continue

            username = self.extract_username(url)

            if not username or username in processed:
                continue

            user = self.instagram.get_user(username)

            if not user or not self.instagram.is_valid_user(user):
                continue

            message = self.ai.generate_dm(user.biography)

            if self.instagram.send_dm(user, message):
                self.sheets.update_status(idx, "messaged ✅")
                time.sleep(self.delay)

            processed.add(username)


# =============================
# Entry
# =============================

if __name__ == "__main__":
    InstagramDMBot().run()
