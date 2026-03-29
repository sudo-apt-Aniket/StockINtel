"""Configuration settings for the stock intelligence backend."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings with environment variable support."""

    app_name: str = "Stock Intelligence API"
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    default_timeframe: str = Field(default="1d")
    market_data_provider: str = Field(default="nse_yahoo_finance")
    news_provider: str = Field(default="nse_yahoo_finance")
    news_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)
    database_path: Path = Field(default=Path("data/stock_intelligence.db"))
    alert_confidence_threshold: float = Field(default=0.7)
    context_dir: Path = Field(default=Path("context"))
    prompts_dir: Path = Field(default=Path("prompts"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="STOCK_INTEL_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings object for app-wide reuse."""
    return Settings()
