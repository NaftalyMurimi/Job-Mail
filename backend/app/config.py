from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Job Mail"
    debug: bool = True

    # No default on purpose: the app refuses to start if SECRET_KEY is missing
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # tokens last 24 hours

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    supabase_url: str
    supabase_service_key: str

        # OpenAI + Gmail (Phase 3)
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    gmail_query: str = "newer_than:3d"
    notify_threshold: int = 7

settings = Settings()