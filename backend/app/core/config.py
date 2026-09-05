"""
Application configuration, loaded from environment variables.

All values are read via pydantic-settings so nothing is hardcoded.
Never commit real secrets — see .env.example at the repo root.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/urban_furniture"

    # --- Auth ---
    SECRET_KEY: str = "CHANGE_ME_IN_ENV"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- App ---
    APP_NAME: str = "Urban Furniture Accounting System"
    ENV: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
