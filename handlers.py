"""
Command and callback-query handlers for ArchiSMS-Bot.

Scope reminder: this bot only ever deals with account/trial/status
messages. It must never read, receive, store, or forward SMS, OTPs,
banking codes, or any other sensitive content.
"""

from __future__ import annotations

import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

import database
import keyboards
from config import ADMIN_ID, TRIAL_DAYS

logger = logging.getLogger(__name__)


def _format_timedelta_fa(delta_seconds: float) -> str:
    """Formats a duration in seconds as '<days> روز و <hours> ساعت'."""
    if delta_seconds <= 0:
        return "منقضی شده"
    total_hours = int(delta_seconds // 3600)
    days, hours = divmod(total_hours, 24)
    return f"{days} روز و {hours} ساعت"


def _format_datetime_fa(iso_timestamp: str) -> str:
    dt = datetime.fromisoformat(iso_timestamp)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def _account_status_text(user: database.User) -> str:
    status_label = "✅ فعال" if user.is_active else "⛔️ منقضی‌شده"
    remaining = _format_timedelta_fa(user.time_remaining.total_seconds())

    return (
        "📱 <b>وضعیت حساب</b>\n\n"
        f"شناسه تلگرام: <code>{user.telegram_id}</code>\n"
        f"وضعیت: {status_label}\n"
        f"تاریخ شروع: {_format_datetime_fa(user.trial_start)}\n"
        f"تاریخ پایان: {_format_datetime_fa(user.trial_until)}\n"
        f"زمان باقی‌مانده: {remaining}"
    )


def _welcome_text(first_name: str) -> str:
    name = first_name or "کاربر"
    return (
        f"سلام {name} 👋\n\n"
        "به <b>ArchiSMS Bot</b> خوش آمدید.\n"
        f"یک دوره آزمایشی {TRIAL_DAYS} روزه برای شما فعال شد.\n\n"
        "از منوی زیر یکی از گزینه‌ها را انتخاب کنید:"
    )


HELP_TEXT = (
    "ℹ️ <b>راهنما</b>\n\n"
    "این بات به‌صورت مستقل از اپلیکیشن ArchiSMS عمل می‌کند و در حال حاضر فقط برای موارد زیر استفاده می‌شود:\n"
    "• ثبت‌نام کاربر\n"
    "• نمایش وضعیت حساب و دوره آزمایشی\n"
    "• تست اتصال\n\n"
    "این بات هیچ پیامک، رمز یکبار مصرف، کد بانکی یا اطلاعات حساس دیگری را دریافت، ذخیره یا ارسال نمی‌کند."
)

TEST_CONNECTION_TEXT = "✅ اتصال با بات برقرار است."


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    if tg_user is None:
        return

    user = database.add_user(
        telegram_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
    )

    if update.message is not None:
        await update.message.reply_html(
            _welcome_text(user.first_name or ""),
            reply_markup=keyboards.main_menu_keyboard(),
        )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.data is None or query.from_user is None:
        return

    await query.answer()

    if query.data == keyboards.CB_ACCOUNT_STATUS:
        user = database.get_user(query.from_user.id)
        if user is None:
            user = database.add_user(
                telegram_id=query.from_user.id,
                username=query.from_user.username,
                first_name=query.from_user.first_name,
            )
        await query.edit_message_text(
            _account_status_text(user),
            parse_mode="HTML",
            reply_markup=keyboards.back_to_menu_keyboard(),
        )

    elif query.data == keyboards.CB_TEST_CONNECTION:
        await query.edit_message_text(
            TEST_CONNECTION_TEXT,
            reply_markup=keyboards.back_to_menu_keyboard(),
        )

    elif query.data == keyboards.CB_HELP:
        await query.edit_message_text(
            HELP_TEXT,
            parse_mode="HTML",
            reply_markup=keyboards.back_to_menu_keyboard(),
        )

    elif query.data == keyboards.CB_BACK_TO_MENU:
        await query.edit_message_text(
            "منوی اصلی را انتخاب کنید:",
            reply_markup=keyboards.main_menu_keyboard(),
        )


def _is_admin(telegram_id: int) -> bool:
    return telegram_id == ADMIN_ID


def _admin_panel_text() -> str:
    total = database.get_user_count()
    active = database.get_active_count()
    expired = database.get_expired_count()
    return (
        "🛠 <b>پنل مدیریت</b>\n\n"
        f"تعداد کل کاربران: {total}\n"
        f"تعداد کاربران فعال: {active}\n"
        f"تعداد Trialهای منقضی‌شده: {expired}"
    )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    if tg_user is None or update.message is None:
        return

    if not _is_admin(tg_user.id):
        logger.warning("تلاش دسترسی غیرمجاز به پنل ادمین توسط: %s", tg_user.id)
        await update.message.reply_text("⛔️ شما اجازه دسترسی به این بخش را ندارید.")
        return

    await update.message.reply_html(
        _admin_panel_text(),
        reply_markup=keyboards.admin_panel_keyboard(),
    )


async def admin_refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.from_user is None:
        return

    if not _is_admin(query.from_user.id):
        await query.answer("⛔️ شما اجازه دسترسی به این بخش را ندارید.", show_alert=True)
        return

    await query.answer("بروزرسانی شد")
    await query.edit_message_text(
        _admin_panel_text(),
        parse_mode="HTML",
        reply_markup=keyboards.admin_panel_keyboard(),
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("خطای پیش‌بینی‌نشده رخ داد", exc_info=context.error)
