from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Defaults are used if the value is missing from .env
    app_name: str = "Job Mail"
    debug: bool = True

    # Read values from the .env file; ignore keys we haven't defined yet
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# One shared instance imported everywhere else in the app
settings = Settings()