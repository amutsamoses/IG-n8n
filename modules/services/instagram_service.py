import logging
from typing import Optional
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

logger = logging.getLogger(__name__)


class InstagramClient:
    def __init__(self, session_id: str, test_mode: bool = False):
        self._client = Client()
        self._session_id = session_id
        self._test_mode = test_mode
        self._is_logged_in = False

    def login(self) -> bool:
        try:
            self._client.login_by_sessionid(self._session_id)
            self._is_logged_in = True
            logger.info("Instagram login successful")
            return True
        except Exception as e:
            logger.exception("Instagram login failed")
            return False

    def ensure_login(self):
        if not self._is_logged_in:
            raise LoginRequired("Instagram client not authenticated")

    def get_valid_user(self, username: str) -> Optional[dict]:
        """
        Returns user object dict if valid.
        Validation rules:
        - Followers between 1k and 50k
        - Account must be public
        """
        try:
            self.ensure_login()
            user = self._client.user_info_by_username(username)

            if (
                1000 <= user.follower_count <= 50000
                and not user.is_private
            ):
                return user.dict()

            return None

        except Exception:
            logger.exception(f"Failed validating user: {username}")
            return None

    def send_message(self, user_id: int, text: str) -> bool:
        try:
            if self._test_mode:
                logger.info(f"[TEST MODE] Message to {user_id}: {text}")
                return True

            self.ensure_login()
            self._client.direct_send(text, [user_id])
            logger.info(f"Message sent to {user_id}")
            return True

        except Exception:
            logger.exception(f"Failed sending message to {user_id}")
            return False
