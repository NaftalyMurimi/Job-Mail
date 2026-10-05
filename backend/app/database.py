from supabase import create_client, Client

from app.config import settings

# One shared client, created once and reused everywhere
supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)