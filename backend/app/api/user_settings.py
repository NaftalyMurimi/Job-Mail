from fastapi import APIRouter, Depends, HTTPException

from app import settings_store
from app.agent.telegram_client import TelegramError, send_message
from app.schemas.user_settings import SettingsResponse, SettingsUpdate
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SettingsResponse)
def read_settings(current_user: dict = Depends(get_current_user)):
    return settings_store.get_settings(current_user["id"])


@router.put("", response_model=SettingsResponse)
def save_settings(data: SettingsUpdate, current_user: dict = Depends(get_current_user)):
    return settings_store.update_settings(
        current_user["id"], data.telegram_chat_id, data.score_threshold
    )


@router.post("/telegram/test")
def send_test_message(current_user: dict = Depends(get_current_user)):
    chat_id = settings_store.get_settings(current_user["id"])["telegram_chat_id"]
    if not chat_id:
        raise HTTPException(status_code=400, detail="Save your telegram_chat_id first (PUT /settings)")
    try:
        send_message(chat_id, "✅ Job Agent is connected. You'll get a message here when a job scores above your threshold.")
    except TelegramError as e:
        raise HTTPException(status_code=400, detail=f"Telegram error: {e}")
    return {"status": "sent"}