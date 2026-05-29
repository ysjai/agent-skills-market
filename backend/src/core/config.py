"""Configuration settings for the application."""

import secrets
import warnings
from functools import lru_cache
from typing import Annotated
from urllib.parse import unquote, urlparse

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "agent_skills_user"
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str = "agent_skills"

    ENVIRONMENT: str = "development"

    SECRET_KEY: str | None = None

    ALLOWED_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003",
        ]
    )
    ALLOWED_ORIGIN_REGEX: str | None = None

    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def empty_secret_key_to_none(cls, v: str | None) -> str | None:
        """Treat empty SECRET_KEY as unset so development auto-generation still works."""
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("ALLOWED_ORIGIN_REGEX", mode="before")
    @classmethod
    def empty_allowed_origin_regex_to_none(cls, v: str | None) -> str | None:
        """Treat empty ALLOWED_ORIGIN_REGEX as unset."""
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @model_validator(mode="after")
    def populate_postgres_settings_from_database_url(self) -> "Settings":
        """Populate POSTGRES_* fields from DATABASE_URL when they are omitted."""
        parsed = urlparse(self.DATABASE_URL)

        if parsed.hostname and self.POSTGRES_HOST == "localhost":
            object.__setattr__(self, "POSTGRES_HOST", parsed.hostname)

        if parsed.port and self.POSTGRES_PORT == 5432:
            object.__setattr__(self, "POSTGRES_PORT", parsed.port)

        if parsed.username and self.POSTGRES_USER == "agent_skills_user":
            object.__setattr__(self, "POSTGRES_USER", unquote(parsed.username))

        if parsed.password and self.POSTGRES_PASSWORD is None:
            object.__setattr__(self, "POSTGRES_PASSWORD", unquote(parsed.password))

        database_name = parsed.path.lstrip("/")
        if database_name and self.POSTGRES_DB == "agent_skills":
            object.__setattr__(self, "POSTGRES_DB", database_name)

        return self

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        """Validate SECRET_KEY and auto-generate for development."""
        if self.SECRET_KEY is None:
            if self.ENVIRONMENT == "production":
                raise ValueError(
                    "SECRET_KEY must be set in production environment.\n"
                    + "Generate one with:\n"
                    + "  openssl rand -hex 32\n"
                    + '  python -c "import secrets; print(secrets.token_hex(32))"'
                )

            object.__setattr__(self, "SECRET_KEY", secrets.token_hex(32))
            warnings.warn(
                "Development mode: Auto-generated SECRET_KEY. "
                + "Sessions will not persist across restarts. "
                + "Set SECRET_KEY in .env for persistent sessions.",
                UserWarning,
                stacklevel=2,
            )
        else:
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    f"SECRET_KEY is too short ({len(self.SECRET_KEY)} characters). "
                    + "It must be at least 32 characters.\n"
                    + "Generate a secure key with:\n"
                    + "  openssl rand -hex 32\n"
                    + '  python -c "import secrets; print(secrets.token_hex(32))"'
                )

        return self

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list[str]) -> list[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string or list."""
        if isinstance(v, list):
            return v
        return [origin.strip() for origin in v.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()  # type: ignore[call-arg]
