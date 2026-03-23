"""
Configuration management for the LMS bot.

Loads secrets from environment variables (or .env.bot.secret file).
Uses pydantic-settings for validation and type safety.

This pattern:
- Keeps secrets out of code
- Validates required variables at startup
- Provides clear error messages when config is missing
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    # Telegram
    bot_token: str | None = None

    # LMS Backend API
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str | None = None

    # LLM API
    llm_api_base_url: str | None = None
    llm_api_key: str | None = None
    llm_api_model: str | None = None

    model_config = SettingsConfigDict(
        # Load from .env.bot.secret in the bot directory
        env_file=Path(__file__).parent / ".env.bot.secret",
        # Environment variable names (uppercase with underscores)
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Map env vars to fields
        extra="ignore",
    )

    @property
    def is_test_mode(self) -> bool:
        """Check if running in test mode (no Telegram connection)."""
        return self.bot_token is None or self.bot_token == "test"


@lru_cache
def get_settings() -> BotSettings:
    """
    Get cached bot settings.
    
    Using lru_cache means settings are loaded once and reused,
    which is efficient and ensures consistent config across the app.
    
    Returns:
        BotSettings with loaded configuration.
    """
    return BotSettings()


# Convenience function for quick access
def get_config() -> BotSettings:
    """Get bot configuration."""
    return get_settings()
