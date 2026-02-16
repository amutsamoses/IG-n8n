from instagrapi import Client
import logging
from config import IG_SESSIONID, TEST_MODE

client = Client()

def login():
    try:
        client.login_by_sessionid(IG_SESSIONID)
        return True
    except Exception as e:
        logging.error(f"Login failed: {e}")
        return False

def is_valid_user(username):
    try:
        user = client.user_info_by_username(username)
        # Validation logic (Followers, Engagement, etc.)
        if 1000 <= user.follower_count <= 50000 and not user.is_private:
            return user
        return None
    except:
        return None

def send_message(user_id, text):
    if TEST_MODE: return True
    return client.direct_send(text, [user_id])