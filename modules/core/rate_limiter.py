import time
import random

class RateLimiter:
    def __init__(self, min_seconds: int, max_seconds: int):
        """
        sleep for a random interval between `min_seconds` and max_seconds
        """

        # validation
        if min_seconds < 0 or max_seconds < 0:
            raise ValueError("Seconds must be non-negative")
        if min_seconds > max_seconds:
            raise ValueError("min_seconds cannot be greater than max_seconds")
        
        
        self.min_seconds = min_seconds
        self.max_seconds = max_seconds
        
    def wait(self):
        delay = random.randint(self.min_seconds, self.max_seconds)
        time.sleep(delay)
        
        