from pydantic import BaseModel, Field


class SettingsUpdate(BaseModel):
    telegram_chat_id: str | None = None
    score_threshold: int | None = Field(default=None, ge=1, le=9)


class SettingsResponse(BaseModel):
    telegram_chat_id: str | None = None
    score_threshold: int = 7