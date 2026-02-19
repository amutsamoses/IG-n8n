class Metrics:
    def __init__(self):
        self.total_attempts = 0
        self.successful_sends = 0
        self.failed_sends = 0
        self.replies_received = 0
    
    def record_attempt(self, success: bool):
        self.total_attempts += 1
        if success:
            self.successful_sends += 1
        else:
            self.failed_sends += 1
            
    def record_reply(self):
        self.replies_received += 1
        
    def report(self):
        return {
            "total_attempts": self.total_attempts,
            "successful_sends": self.successful_sends,
            "failed_sends": self.failed_sends,
            "replies_received": self.replies_received,
            "reply_rate": (self.replies_received / self.successful_sends * 100) if self.successful_sends > 0 else 0
        }