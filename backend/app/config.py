from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    # Секреты
    postgres_password: str
    admin_username: str
    admin_password: str
    jwt_secret_key: str

    # Технические параметры (config/app.env), с дефолтами на случай
    # локального запуска без docker compose (например, из-под uv run).
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "element"
    postgres_user: str = "element"

    log_level: str = "info"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    cors_origins: str = "http://localhost:5173"

    max_feed_size_mb: int = 64

    # Telegram-алерты об ошибках (опционально). Пока не заданы — core/alerts.py
    # работает как заглушка и просто логирует событие вместо отправки.
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
