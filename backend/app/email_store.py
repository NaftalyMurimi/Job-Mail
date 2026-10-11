from app.database import supabase


def get_existing_message_ids(user_id: str, ids: list[str]) -> set[str]:
    if not ids:
        return set()
    result = (
        supabase.table("scanned_emails")
        .select("gmail_message_id")
        .eq("user_id", user_id)
        .in_("gmail_message_id", ids)
        .execute()
    )
    return {row["gmail_message_id"] for row in result.data}


def save_scanned_email(user_id: str, email: dict, analysis: dict) -> dict:
    row = {
        "user_id": user_id,
        "gmail_message_id": email["id"],
        "subject": email["subject"],
        "sender": email["sender"],
        "received_at": email["received_at"],
        **analysis,
    }
    return supabase.table("scanned_emails").insert(row).execute().data[0]


def list_scanned(user_id: str, min_score: int | None = None, limit: int = 50) -> list[dict]:
    query = (
        supabase.table("scanned_emails")
        .select("id, subject, sender, received_at, is_job_advert, category, job_title, "
                "company, match_score, best_matching_cv_id, reasoning, notified")
        .eq("user_id", user_id)
    )
    if min_score is not None:
        query = query.gte("match_score", min_score)
    return (
        query.order("match_score", desc=True, nullsfirst=False)
        .order("received_at", desc=True)
        .limit(limit)
        .execute()
        .data
    )