"""Siper settings, read from SIPER_* environment variables or a .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIPER_", env_file=".env", extra="ignore")

    # Where the real LLM server lives (LM Studio's OpenAI-compatible server).
    upstream_base_url: str = "http://localhost:1235"
    # Local models can be slow; seconds to wait for the upstream before giving up.
    upstream_timeout: float = 120.0


def get_settings() -> Settings:
    return Settings()
