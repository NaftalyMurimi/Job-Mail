import html
import time

from loguru import logger

from app import email_store, settings_store
from app.agent.telegram_client import TelegramError, send_message
from app.config import settings


def _short(text: str | None, limit: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def format_message(row: dict) -> str:
    e = html.escape   # Telegram HTML mode breaks on raw <, > and &
    cv_name = (row.get("cvs") or {}).get("name") or "n/a"
    link = f"https://mail.google.com/mail/u/0/#all/{row['gmail_message_id']}"
    return (
        f"🔔 <b>Match {row['match_score']}/10</b>\n"
        f"<b>{e(_short(row.get('job_title') or 'Job', 120))}</b> "
        f"at {e(_short(row.get('company') or 'unknown company', 80))}\n"
        f"Best CV: {e(cv_name)}\n\n"
        f"{e(_short(row.get('reasoning'), 500))}\n\n"
        f"From: {e(_short(row.get('sender'), 80))}\n"
        f"Subject: {e(_short(row.get('subject'), 120))}\n"
        f'<a href="{link}">Open in Gmail</a>'
    )


def notify_matches(user_id: str) -> dict:
    result = {"sent": 0, "failed": 0, "skipped": None, "error": None}

    user_settings = settings_store.get_settings(user_id)
    chat_id = user_settings["telegram_chat_id"]
    if not chat_id:
        result["skipped"] = "No Telegram chat id saved (use PUT /settings)"
        return result
    if not settings.telegram_bot_token:
        result["skipped"] = "TELEGRAM_BOT_TOKEN is not set"
        return result

    rows = email_store.list_unnotified_matches(
        user_id, user_settings["score_threshold"], settings.notify_limit
    )
    for row in rows:
        try:
            send_message(chat_id, format_message(row))
        except TelegramError as e:
            logger.error(f"Telegram send failed: {e}")
            result["failed"] += 1
            result["error"] = str(e)
            break   # a bad token or chat id fails every time; stop instead of hammering
        email_store.mark_notified(row["id"])   # only after a confirmed send
        result["sent"] += 1
        time.sleep(1.1)   # Telegram allows about one message per second per chat

    logger.info(f"Notifications: {result}")
    return result