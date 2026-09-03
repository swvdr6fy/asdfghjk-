"""
Configuration loader for ArchiSMS-Bot.

All secrets (BOT_TOKEN, ADMIN_ID) are read exclusively from environment
variables. Nothing sensitive is hard-coded here or anywhere else in
this project.
"""

from __future__ import annotations

import os
import sys
import logging

from dotenv import load_dotenv

load_dotenv()  # Loads .env for local development; harmless no-op on Railway.

logger = logging.getLogger(__name__)


def _get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        logger.critical("متغیر محیطی ضروری «%s» تنظیم نشده است.", name)
        sys.exit(1)
    return value


def _get_required_int_env(name: str) -> int:
    raw = _get_required_env(name)
    try:
        return int(raw)
    except ValueError:
        logger.critical("متغیر محیطی «%s» باید عددی باشد. مقدار فعلی: %s", name, raw)
        sys.exit(1)


# --- Required secrets (no defaults, no hard-coded fallbacks) ---
BOT_TOKEN: str = _get_required_env("BOT_TOKEN")
ADMIN_ID: int = _get_required_int_env("ADMIN_ID")

# --- Optional configuration with sane defaults ---
DB_PATH: str = os.environ.get("DB_PATH", "archisms_bot.db")
TRIAL_DAYS: int = int(os.environ.get("TRIAL_DAYS", "7"))
LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO").upper()
