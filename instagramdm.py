import os
import time
import logging
from datetime import datetime
from instagrapi import Client
import google.generativeai as genai
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

# ============ Load Environment Variables ============
load_dotenv()
IG_SESSIONID = os.getenv("INSTAGRAM_SESSIONID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ============ Configuration ============
SPREADSHEET_NAME = '50K SCRAPED LEADS IN PHOENIX'
WORKSHEET_NAME = 'Sheet1'
SERVICE_ACCOUNT_FILE = 'credentials.json'
STATUS_COLUMN_INDEX = 13  # Column M
DEFAULT_DM_DELAY_SECONDS = 1200  # 20 minutes
TEST_MODE = False  # Set to True to skip sending DMs

# ============ Setup Folders ============
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ============ Logging Setup ============
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
error_logger = logging.getLogger("errors")
error_handler = logging.FileHandler("logs/errors.log", encoding="utf-8")
error_logger.addHandler(error_handler)

# ============ Instagram Client ============
client = Client()

# ============ Google Sheets ============
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

# ============ Gemini AI ============
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ============ Default DM Message ============
DEFAULT_DM_MESSAGE = """Hi! 👋 My name is John, founder of SB CAIO, a U.S.-based agency specializing in AI-powered systems and automation for small and medium-sized businesses...

We’d love to collaborate and invite your audience to access FREE tools, including a 16-week English Language Learning program and project-based contracts.

If you're interested, I’d be glad to connect!

Warm regards,
John
📧 ceo@sbcaio.com
📱 WhatsApp: +1 (725) 304-6728
🌐 www.sbcaio.com"""

# ============ Helper Functions ============

def extract_username(url):
    if not url:
        return None
    return url.strip().rstrip('/').split("/")[-1]

def login():
    try:
        client.login_by_sessionid(IG_SESSIONID)
        logging.info("✅ Logged in to Instagram")
        return True
    except Exception as e:
        logging.error(f"❌ Instagram login failed: {e}")
        return False

def get_user_info(username):
    try:
        return client.user_info_by_username(username)
    except Exception as e:
        logging.warning(f"⚠️ Failed to fetch user info for {username}: {e}")
        return None

def analyze_bio(bio):
    if not bio:
        return "default"
    bio = bio.lower()
    niches = {
        "business": ["founder", "ceo", "startup", "entrepreneur"],
        "marketing": ["marketing", "branding", "seo", "ads"],
        "creator": ["content", "creator", "youtube", "tiktok"],
        "tech": ["developer", "software", "ai", "app"]
    }
    for niche, keywords in niches.items():
        if any(word in bio for word in keywords):
            return niche
    return "default"

def generate_dm(bio):
    try:
        niche = analyze_bio(bio)
        prompt = f"""Bio: {bio}\nNiche: {niche}\nWrite a friendly Instagram DM for this user, similar in tone and format to:\n{DEFAULT_DM_MESSAGE}"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        return text if text and len(text) < 1000 else DEFAULT_DM_MESSAGE
    except Exception as e:
        error_logger.error(f"Gemini error: {e}")
        return DEFAULT_DM_MESSAGE

def calculate_engagement(user):
    try:
        medias = client.user_medias(user.pk, 10)
        total = sum(m.like_count + m.comment_count for m in medias)
        return round((total / 10) / user.follower_count * 100, 2)
    except:
        return 0

def is_valid_user(user):
    if user.is_private:
        return False
    if not (1000 <= user.follower_count <= 50000):
        return False
    if calculate_engagement(user) < 0.5:
        return False
    return True

def dm_user(user, message):
    try:
        if TEST_MODE:
            logging.info(f"[TEST MODE] Would DM @{user.username}")
            return True
        client.direct_send(message, [user.pk])
        logging.info(f"✅ Sent DM to @{user.username}")
        return True
    except Exception as e:
        error_logger.error(f"DM error for @{user.username}: {e}")
        return False

def dm_from_sheet():
    all_rows = sheet.get_all_records()
    tried_usernames = set()

    for idx, row in enumerate(all_rows, start=2):
        url = row.get("INSTAGRAM URL")
        status = row.get("Status")

        if not url or status == "messaged ✅":
            continue

        username = extract_username(url)
        if not username or username in tried_usernames:
            continue

        user = get_user_info(username)
        if not user or not is_valid_user(user):
            continue

        msg = generate_dm(user.biography)
        success = dm_user(user, msg)

        if success:
            for attempt in range(3):
                try:
                    sheet.update_cell(idx, STATUS_COLUMN_INDEX, "messaged ✅")
                    break
                except Exception as e:
                    error_logger.error(f"Retry {attempt+1} - Failed to update sheet for {username}: {e}")
                    time.sleep(3)
            time.sleep(DEFAULT_DM_DELAY_SECONDS)
        tried_usernames.add(username)

# ============ Entry ============
if __name__ == "__main__":
    if login():
        dm_from_sheet()
        logging.info("✅ All done")
