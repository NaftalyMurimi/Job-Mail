# TEMPORARY in-memory user store.
# Phase 2 replaces the bodies of these functions with Supabase calls,
# keeping the same names and return values so nothing else changes.
import uuid
from datetime import datetime, timezone

_users: dict[str, dict] = {}


def create_user(email: str, hashed_password: str, full_name: str | None = None) -> dict:
    user = {
        "id": str(uuid.uuid4()),
        "email": email.lower(),  # store lowercase so lookups are case-insensitive
        "hashed_password": hashed_password,
        "full_name": full_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _users[user["id"]] = user
    return user


def get_user_by_email(email: str) -> dict | None:
    email = email.lower()
    return next((u for u in _users.values() if u["email"] == email), None)


def get_user_by_id(user_id: str) -> dict | None:
    return _users.get(user_id)