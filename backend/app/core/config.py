from functools import lru_cache

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.common.enums import Environment

LOCAL_JWT_SECRET = "local-dev-secret-change-me-0123456789abcdef"  # noqa: S105 - rejected outside local/test below


class Settings(BaseSettings):
    """Configuration read from environment variables (and `.env` locally)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Environment = Environment.LOCAL
    app_name: str = "Real Estate Portal API"
    log_level: str = "INFO"

    database_url: str = "mysql+aiomysql://portal:portal@localhost:3306/portal"
    database_echo: bool = False
    # CA bundle for TLS to MySQL (the RDS bundle on AWS, where the server requires TLS). None = no TLS.
    database_ssl_ca: str | None = None
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: SecretStr = SecretStr(LOCAL_JWT_SECRET)
    jwt_algorithm: str = "HS256"
    refresh_cookie_secure: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    @model_validator(mode="after")
    def reject_default_secret_outside_local(self) -> "Settings":
        is_local = self.environment in {Environment.LOCAL, Environment.TEST}
        if not is_local and self.jwt_secret.get_secret_value() == LOCAL_JWT_SECRET:
            raise ValueError("JWT_SECRET must be set outside local/test environments")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
