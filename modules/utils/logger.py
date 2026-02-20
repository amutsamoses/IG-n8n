import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "logs/bot.log",
    maxBytes=5_000_000,
    backupCount=3
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)