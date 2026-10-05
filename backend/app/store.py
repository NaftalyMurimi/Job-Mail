from app.database import supabase


def create_user(email: str, hashed_password: str, full_name: str | None = None) -> dict:
    result = (
        supabase.table("users")
        .insert({
            "email": email.lower(),
            "hashed_password": hashed_password,
            "full_name": full_name,
        })
        .execute()
    )
    return result.data[0]


def get_user_by_email(email: str) -> dict | None:
    result = (
        supabase.table("users")
        .select("*")
        .eq("email", email.lower())
        .execute()
    )
    return result.data[0] if result.data else None


def get_user_by_id(user_id: str) -> dict | None:
    result = (
        supabase.table("users")
        .select("*")
        .eq("id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None