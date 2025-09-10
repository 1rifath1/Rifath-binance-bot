# src/logger_config.py
import logging
import json
from logging.handlers import RotatingFileHandler

def setup_logger(name="bot", log_file="bot.log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(log_file, maxBytes=2*1024*1024, backupCount=3)

    def json_formatter(record):
        log_entry = {
            "ts": record.created,
            "level": record.levelname,
            "module": record.module,
            "event": record.getMessage()
        }
        return json.dumps(log_entry)

    handler.setFormatter(logging.Formatter(fmt="%(message)s"))
    logger.addHandler(handler)
    return logger

logger = setup_logger()
