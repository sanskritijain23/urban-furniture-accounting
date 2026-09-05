"""
Application configuration, loaded from environment variables.

The shared .env file lives at the repository root, so we resolve its
absolute path instead of depending on the current working directory.
This keeps FastAPI, Alembic, seed scripts and tests consistent.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/app/core/config.py
# parents[0] = core
# parents[1] = app
# parents[2] = backend
# parents[3] = repository root
ROOT_DIR = Path(__file__).resolve().parents[3]

ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/urban_furniture"
    )

    # --- Auth ---
    SECRET_KEY: str = "CHANGE_ME_IN_ENV"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- App ---
    APP_NAME: str = "Urban Furniture Accounting System"
    ENV: str = "development"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        extra="ignore",
    )


settings = Settings()