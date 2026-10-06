from app.database import supabase


def create_cv(user_id: str, name: str, file_name: str | None, content_text: str) -> dict:
    result = (
        supabase.table("cvs")
        .insert({"user_id": user_id, "name": name, "file_name": file_name, "content_text": content_text})
        .execute()
    )
    return result.data[0]


def list_cvs(user_id: str) -> list[dict]:
    result = (
        supabase.table("cvs")
        .select("id, name, file_name, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def get_cvs_with_text(user_id: str) -> list[dict]:
    result = (
        supabase.table("cvs")
        .select("id, name, content_text")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
    )
    return result.data


def delete_cv(user_id: str, cv_id: str) -> None:
    supabase.table("cvs").delete().eq("id", cv_id).eq("user_id", user_id).execute()