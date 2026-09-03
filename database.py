"""
Database access layer for ArchiSMS-Bot.

Uses the standard library sqlite3 module. Each function opens and
closes its own short-lived connection, which is simple and safe for
a bot at this scale (SQLite handles concurrent readers fine; writes
are serialized by SQLite itself).

Table: users
    telegram_id  INTEGER PRIMARY KEY  - Telegram user ID
    username     TEXT                 - Telegram @username (nullable)
    first_name   TEXT                 - Telegram first name
    created_at   TEXT                 - ISO timestamp of registration
    trial_start  TEXT                 - ISO timestamp of trial start
    trial_until  TEXT                 - ISO timestamp of trial end
"""

from __future__ import annotations

import sqlite3
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterator, Optional

from config import DB_PATH, TRIAL_DAYS

logger = logging.getLogger(__name__)


@dataclass
class User:
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    created_at: str
    trial_start: str
    trial_until: str

    @property
    def trial_until_dt(self) -> datetime:
        return datetime.fromisoformat(self.trial_until)

    @property
    def is_active(self) -> bool:
        return datetime.now(timezone.utc) < self.trial_until_dt

    @property
    def time_remaining(self) -> timedelta:
        remaining = self.trial_until_dt - datetime.now(timezone.utc)
        return remaining if remaining.total_seconds() > 0 else timedelta(0)


@contextmanager
def _get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    """Creates the users table if it does not already exist."""
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                created_at  TEXT NOT NULL,
                trial_start TEXT NOT NULL,
                trial_until TEXT NOT NULL
            )
            """
        )
    logger.info("پایگاه داده با موفقیت مقداردهی اولیه شد. (%s)", DB_PATH)


def add_user(telegram_id: int, username: Optional[str], first_name: Optional[str]) -> User:
    """
    Registers a new user with a fresh trial period, or returns the
    existing user unchanged if they are already registered.
    """
    existing = get_user(telegram_id)
    if existing is not None:
        return existing

    now = datetime.now(timezone.utc)
    trial_until = now + timedelta(days=TRIAL_DAYS)

    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, created_at, trial_start, trial_until)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                username,
                first_name,
                now.isoformat(),
                now.isoformat(),
                trial_until.isoformat(),
            ),
        )

    logger.info("کاربر جدید ثبت شد: %s", telegram_id)

    user = get_user(telegram_id)
    assert user is not None  # just inserted, must exist
    return user


def get_user(telegram_id: int) -> Optional[User]:
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()

    if row is None:
        return None

    return User(
        telegram_id=row["telegram_id"],
        username=row["username"],
        first_name=row["first_name"],
        created_at=row["created_at"],
        trial_start=row["trial_start"],
        trial_until=row["trial_until"],
    )


def get_user_count() -> int:
    with _get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()
    return int(row["cnt"])


def get_active_count() -> int:
    now_iso = datetime.now(timezone.utc).isoformat()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM users WHERE trial_until > ?",
            (now_iso,),
        ).fetchone()
    return int(row["cnt"])


def get_expired_count() -> int:
    now_iso = datetime.now(timezone.utc).isoformat()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM users WHERE trial_until <= ?",
            (now_iso,),
        ).fetchone()
    return int(row["cnt"])
