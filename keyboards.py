"""
Inline keyboard builders for ArchiSMS-Bot.
"""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Callback data constants (kept in one place to avoid typos/duplication)
CB_ACCOUNT_STATUS = "account_status"
CB_TEST_CONNECTION = "test_connection"
CB_HELP = "help"
CB_BACK_TO_MENU = "back_to_menu"
CB_ADMIN_REFRESH = "admin_refresh"


def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📱 وضعیت حساب", callback_data=CB_ACCOUNT_STATUS)],
        [InlineKeyboardButton("🧪 تست اتصال", callback_data=CB_TEST_CONNECTION)],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data=CB_HELP)],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data=CB_BACK_TO_MENU)]]
    return InlineKeyboardMarkup(keyboard)


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data=CB_ADMIN_REFRESH)]]
    return InlineKeyboardMarkup(keyboard)
