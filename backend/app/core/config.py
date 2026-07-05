from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables (.env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    DEV_AUTH_BYPASS: bool = False

    DATABASE_URL: str = "postgresql+psycopg2://preorder:preorder@db:5432/preorder"

    LINE_CLIENT_ID: str = ""
    LINE_CLIENT_SECRET: str = ""
    LINE_REDIRECT_URI: str = ""

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""

    JWT_SECRET: str = "dev-only-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    FRONTEND_URL: str = "http://localhost:5173"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
