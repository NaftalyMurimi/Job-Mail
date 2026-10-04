from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Job Mail"
    debug: bool = True

    # No default on purpose: the app refuses to start if SECRET_KEY is missing
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # tokens last 24 hours

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()