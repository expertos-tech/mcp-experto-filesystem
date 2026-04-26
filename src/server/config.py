"""Project-wide configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables (prefix: MCP_)."""

    project_root: str = "."
    max_file_bytes: int = 1_048_576   # 1 MB
    max_tokens_per_response: int = 8_000
    log_level: str = "INFO"

    model_config = {"env_prefix": "MCP_"}


settings = Settings()
