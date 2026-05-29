"""Tests for configuration settings."""

import warnings

import pytest

from src.core.config import Settings, get_settings


class TestSettingsValidation:
    """Test configuration settings validation."""

    def test_settings_production_without_secret_key_raises_error(self):
        """Test production environment requires SECRET_KEY (L47-53)."""
        with pytest.raises(ValueError, match="SECRET_KEY must be set in production"):
            Settings(
                DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
                POSTGRES_PASSWORD="test",
                ENVIRONMENT="production",
                SECRET_KEY=None,
            )

    def test_settings_short_secret_key_raises_error(self):
        """Test SECRET_KEY must be at least 32 characters (L64-71)."""
        with pytest.raises(ValueError, match="SECRET_KEY is too short"):
            Settings(
                DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
                POSTGRES_PASSWORD="test",
                ENVIRONMENT="development",
                SECRET_KEY="short",
            )

    def test_settings_short_secret_key_includes_generation_instructions(self):
        """Test short SECRET_KEY error includes generation instructions."""
        with pytest.raises(ValueError) as exc_info:
            Settings(
                DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
                POSTGRES_PASSWORD="test",
                ENVIRONMENT="development",
                SECRET_KEY="short",
            )

        error_msg = str(exc_info.value)
        assert "openssl rand -hex 32" in error_msg
        assert "secrets.token_hex" in error_msg

    def test_settings_auto_generates_secret_key_in_development(self):
        """Test development mode auto-generates SECRET_KEY (L55-62)."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings(
                DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
                POSTGRES_PASSWORD="test",
                ENVIRONMENT="development",
                SECRET_KEY=None,
            )

            # Verify SECRET_KEY was auto-generated
            assert settings.SECRET_KEY is not None
            assert len(settings.SECRET_KEY) >= 32

            # Verify warning was issued
            assert len(w) == 1
            assert "Development mode: Auto-generated SECRET_KEY" in str(w[0].message)

    def test_settings_empty_secret_key_auto_generates_in_development(self):
        """Test empty SECRET_KEY is treated as unset in development."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings(
                DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
                POSTGRES_PASSWORD="test",
                ENVIRONMENT="development",
                SECRET_KEY="",
            )

            assert settings.SECRET_KEY is not None
            assert len(settings.SECRET_KEY) >= 32
            assert len(w) == 1
            assert "Development mode: Auto-generated SECRET_KEY" in str(w[0].message)

    def test_settings_valid_secret_key_no_warning(self):
        """Test valid SECRET_KEY does not generate warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings(
                DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
                POSTGRES_PASSWORD="test",
                ENVIRONMENT="development",
                SECRET_KEY="a" * 32,  # 32 character key
            )

            assert settings.SECRET_KEY == "a" * 32
            # Should not have auto-generation warning
            assert not any("Auto-generated" in str(warning.message) for warning in w)


class TestAllowedOriginsParsing:
    """Test ALLOWED_ORIGINS parsing."""

    def test_allowed_origins_from_list(self):
        """Test ALLOWED_ORIGINS from list (L79-80)."""
        origins = ["http://localhost:3000", "http://localhost:3001"]
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            ALLOWED_ORIGINS=origins,
            SECRET_KEY="a" * 32,
        )

        assert settings.ALLOWED_ORIGINS == origins

    def test_allowed_origins_from_string(self):
        """Test ALLOWED_ORIGINS from comma-separated string (L81)."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            ALLOWED_ORIGINS="http://localhost:3000,http://localhost:3001",
            SECRET_KEY="a" * 32,
        )

        assert settings.ALLOWED_ORIGINS == ["http://localhost:3000", "http://localhost:3001"]

    def test_allowed_origins_from_string_with_spaces(self):
        """Test ALLOWED_ORIGINS from string with spaces (L81)."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            ALLOWED_ORIGINS="http://localhost:3000, http://localhost:3001 , http://localhost:3002",
            SECRET_KEY="a" * 32,
        )

        assert settings.ALLOWED_ORIGINS == [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
        ]

    def test_allowed_origins_from_string_with_empty_values(self):
        """Test ALLOWED_ORIGINS filters empty values (L81)."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            ALLOWED_ORIGINS="http://localhost:3000,,http://localhost:3001,",
            SECRET_KEY="a" * 32,
        )

        assert settings.ALLOWED_ORIGINS == ["http://localhost:3000", "http://localhost:3001"]

    def test_allowed_origins_from_env_string(self, monkeypatch: pytest.MonkeyPatch):
        """Test ALLOWED_ORIGINS from env keeps comma-separated support."""
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
        monkeypatch.setenv("POSTGRES_PASSWORD", "test")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:3001",
        )

        settings = Settings(_env_file=None)

        assert settings.ALLOWED_ORIGINS == [
            "http://localhost:3000",
            "http://localhost:3001",
        ]

    def test_empty_allowed_origin_regex_from_env_becomes_none(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """Test empty ALLOWED_ORIGIN_REGEX does not remain an empty string."""
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
        monkeypatch.setenv("POSTGRES_PASSWORD", "test")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ALLOWED_ORIGIN_REGEX", "")

        settings = Settings(_env_file=None)

        assert settings.ALLOWED_ORIGIN_REGEX is None


class TestDatabaseUrlParsing:
    """Test DATABASE_URL-derived Postgres settings."""

    def test_postgres_fields_derive_from_database_url(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("POSTGRES_HOST", raising=False)
        monkeypatch.delenv("POSTGRES_PORT", raising=False)
        monkeypatch.delenv("POSTGRES_USER", raising=False)
        monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
        monkeypatch.delenv("POSTGRES_DB", raising=False)

        settings = Settings(
            DATABASE_URL=(
                "postgresql+asyncpg://postgres.abpkobhfnmcqqzqeeqss:super-secret"
                "@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres?ssl=require"
            ),
            SECRET_KEY="a" * 32,
            _env_file=None,
        )

        assert settings.POSTGRES_HOST == "aws-0-ap-southeast-1.pooler.supabase.com"
        assert settings.POSTGRES_PORT == 5432
        assert settings.POSTGRES_USER == "postgres.abpkobhfnmcqqzqeeqss"
        assert settings.POSTGRES_PASSWORD == "super-secret"
        assert settings.POSTGRES_DB == "postgres"

    def test_explicit_postgres_fields_are_not_overridden(self):
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://derived-user:derived-pass@derived-host:6543/derived-db",
            POSTGRES_HOST="custom-host",
            POSTGRES_PORT=6000,
            POSTGRES_USER="custom-user",
            POSTGRES_PASSWORD="custom-pass",
            POSTGRES_DB="custom-db",
            SECRET_KEY="a" * 32,
            _env_file=None,
        )

        assert settings.POSTGRES_HOST == "custom-host"
        assert settings.POSTGRES_PORT == 6000
        assert settings.POSTGRES_USER == "custom-user"
        assert settings.POSTGRES_PASSWORD == "custom-pass"
        assert settings.POSTGRES_DB == "custom-db"


class TestSettingsDefaults:
    """Test settings default values."""

    def test_default_postgres_host(self):
        """Test default POSTGRES_HOST."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            SECRET_KEY="a" * 32,
            _env_file=None,
        )

        assert settings.POSTGRES_HOST == "localhost"

    def test_default_postgres_port(self):
        """Test default POSTGRES_PORT."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            SECRET_KEY="a" * 32,
            _env_file=None,
        )

        assert settings.POSTGRES_PORT == 5432

    def test_default_postgres_user(self, monkeypatch: pytest.MonkeyPatch):
        """Test POSTGRES_USER derives from DATABASE_URL when omitted."""
        monkeypatch.delenv("POSTGRES_USER", raising=False)

        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            SECRET_KEY="a" * 32,
            _env_file=None,
        )

        assert settings.POSTGRES_USER == "user"

    def test_default_environment(self):
        """Test default ENVIRONMENT."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            SECRET_KEY="a" * 32,
            _env_file=None,
        )

        assert settings.ENVIRONMENT == "development"

    def test_default_max_file_size(self):
        """Test default MAX_FILE_SIZE (10MB)."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            SECRET_KEY="a" * 32,
            _env_file=None,
        )

        assert settings.MAX_FILE_SIZE == 10 * 1024 * 1024

    def test_default_allowed_origins(self):
        """Test default ALLOWED_ORIGINS."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            POSTGRES_PASSWORD="test",
            SECRET_KEY="a" * 32,
            _env_file=None,
        )

        assert settings.ALLOWED_ORIGINS == [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003",
        ]


class TestGetSettingsCaching:
    """Test get_settings caching."""

    def test_get_settings_returns_cached_instance(self):
        """Test get_settings returns cached instance (L84-87)."""
        # Clear cache first
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the same instance
        assert settings1 is settings2

    def test_get_settings_uses_lru_cache(self):
        """Test get_settings uses lru_cache decorator."""
        # The function should have cache_info and cache_clear methods
        assert hasattr(get_settings, "cache_info")
        assert hasattr(get_settings, "cache_clear")
