from datetime import datetime
from typing import Dict


class DripEngine:
    def __init__(self, delay_days: int, max_sequence: int = 4):
        self.delay_days = delay_days
        self.max_sequence = max_sequence

    def should_send(self, row: Dict) -> bool:
        status = str(row.get("Status", "")).lower()
        msg_number = int(row.get("Message Number") or 0)
        last_date = row.get("Last Message Date")

        if status in ["replied", "completed"]:
            return False

        if msg_number >= self.max_sequence:
            return False

        if msg_number == 0:
            return True  # first message immediately

        if not last_date:
            return True

        last = datetime.strptime(last_date, "%Y-%m-%d")
        delta = (datetime.now() - last).days

        return delta >= self.delay_days

    def next_message_number(self, row: Dict) -> int:
        return int(row.get("Message Number") or 0) + 1

    def mark_completed(self, msg_number: int) -> bool:
        return msg_number >= self.max_sequence
