# config.py
# ──────────────────────────────────────────────────────────────
# Central configuration — all env vars loaded in one place.
# Uses pydantic-settings so missing required vars fail fast
# with a clear error message, not a confusing KeyError later.
# ──────────────────────────────────────────────────────────────

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file so the path is correct no matter
# which directory the user runs the script or pytest from.
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # LLM provider — only OpenAI for this video.
    # Azure OpenAI and Anthropic added in later videos.
    openai_api_key: str = ""
    openai_model: str = ""

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")


# Module-level singleton — import this everywhere instead of
# re-reading env vars in each file.
settings = Settings()
