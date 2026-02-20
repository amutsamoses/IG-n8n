class ReplyDetector:
    def __init__(self, instagram_client, sheets_handler, settings):
        self.instagram = instagram_client
        self.sheets = sheets_handler
        self.settings = settings

    def detect_replies(self):
        threads = self.instagram.get_unread_threads()

        for thread in threads:
            for user in thread.users:
                username = user.username

                # Mark lead as replied
                self.sheets.mark_replied_by_username(username)