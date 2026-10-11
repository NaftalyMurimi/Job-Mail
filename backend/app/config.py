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

        # LLM provider (Phase 3), any OpenAI-compatible API
    llm_api_key: str
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_delay_seconds: float = 2.0

    # Gmail scan (Phase 3)
    gmail_query: str = "newer_than:3d"
    notify_threshold: int = 7

settings = Settings()