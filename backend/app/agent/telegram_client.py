import httpx

from app.config import settings


class TelegramError(Exception):
    pass


def send_message(chat_id: str, text: str) -> None:
    """Send one HTML-formatted message. Never log the URL: it contains the bot token."""
    if not settings.telegram_bot_token:
        raise TelegramError("TELEGRAM_BOT_TOKEN is not set")

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        resp = httpx.post(url, json=payload, timeout=15)
    except httpx.HTTPError as e:
        raise TelegramError(f"Could not reach Telegram: {type(e).__name__}")

    try:
        data = resp.json()
    except ValueError:
        data = {}
    if resp.status_code != 200 or not data.get("ok"):
        raise TelegramError(data.get("description", f"HTTP {resp.status_code}"))