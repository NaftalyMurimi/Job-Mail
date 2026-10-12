import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    raise SystemExit("TELEGRAM_BOT_TOKEN missing from backend/.env")

data = httpx.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=15).json()
if not data.get("ok"):
    raise SystemExit(f"Telegram error: {data.get('description')}")

chats = {}
for update in data.get("result", []):
    msg = update.get("message") or update.get("edited_message") or {}
    chat = msg.get("chat")
    if chat:
        chats[chat["id"]] = chat.get("first_name") or chat.get("title") or ""

if not chats:
    print("No messages found. Send /start to your bot in Telegram, then run this again.")
for chat_id, name in chats.items():
    print(f"chat_id = {chat_id}   ({name})")