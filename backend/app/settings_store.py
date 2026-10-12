from datetime import datetime, timezone

from app.database import supabase

DEFAULTS = {"telegram_chat_id": None, "score_threshold": 7}


def get_settings(user_id: str) -> dict:
    result = (
        supabase.table("user_settings")
        .select("telegram_chat_id, score_threshold")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else dict(DEFAULTS)


def update_settings(user_id: str, telegram_chat_id: str | None = None,
                    score_threshold: int | None = None) -> dict:
    row = {"user_id": user_id, "updated_at": datetime.now(timezone.utc).isoformat()}
    if telegram_chat_id is not None:
        row["telegram_chat_id"] = telegram_chat_id or None   # empty string clears it
    if score_threshold is not None:
        row["score_threshold"] = score_threshold
    supabase.table("user_settings").upsert(row, on_conflict="user_id").execute()
    return get_settings(user_id)