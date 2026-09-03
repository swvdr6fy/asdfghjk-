"""
ArchiSMS-Bot entry point.

Run locally:
    python bot.py

Deployed on Railway via the Procfile's `worker: python bot.py` process.
"""

from __future__ import annotations

import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler

import database
import handlers
import keyboards
from config import BOT_TOKEN, LOG_LEVEL

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)

# Quiet down noisy third-party loggers a bit, keep our own at configured level.
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def build_application() -> Application:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("admin", handlers.admin_command))

    application.add_handler(
        CallbackQueryHandler(handlers.admin_refresh_callback, pattern=f"^{keyboards.CB_ADMIN_REFRESH}$")
    )
    application.add_handler(CallbackQueryHandler(handlers.menu_callback))

    application.add_error_handler(handlers.error_handler)

    return application


def main() -> None:
    database.init_db()

    application = build_application()

    logger.info("ArchiSMS-Bot در حال اجراست...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
