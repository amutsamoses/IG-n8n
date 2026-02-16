import time
from datetime import datetime
from modules.sheets import SheetsHandler
from modules.instagram import login, is_valid_user, send_message
from modules.ai_engine import generate_custom_dm
import config

def run_bot():
    if not login(): return
    
    db = SheetsHandler()
    leads = db.get_all_leads()

    for idx, row in enumerate(leads, start=2):
        # 1. Extract and Check Status
        url = row.get("INSTAGRAM URL")
        if not url or row.get("Status") == "completed": continue

        # 2. Extract Username
        username = url.strip().rstrip('/').split("/")[-1]
        
        # 3. Validate User
        user = is_valid_user(username)
        if user:
            # 4. Generate & Send
            msg = generate_custom_dm(user.biography)
            if send_message(user.pk, msg):
                db.update_lead(idx, config.STATUS_COL, "messaged ✅")
                # Update timestamp for drip logic
                db.update_lead(idx, config.LAST_DATE_COL, datetime.now().strftime("%Y-%m-%d"))
            
            time.sleep(config.DEFAULT_DM_DELAY)

if __name__ == "__main__":
    run_bot()