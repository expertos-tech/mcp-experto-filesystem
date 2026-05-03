"""Project-wide configuration via pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables (prefix: MCP_)."""

    project_root: str = "."
    max_file_bytes: int = 1_048_576  # 1 MB
    max_tokens_per_response: int = 8_000
    index_dir_name: str = ".mcp-experto/index"
    chunk_max_chars: int = 1_200
    chunk_max_lines: int = 40
    search_default_top_k: int = 10
    enable_index_watcher: bool = True
    embedding_provider: str = "auto"
    sentence_transformer_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    log_level: str = "INFO"

    model_config = {"env_prefix": "MCP_"}

    @property
    def project_root_path(self) -> Path:
        """Return the configured project root as a resolved path."""
        return Path(self.project_root).resolve()

    @property
    def index_dir_path(self) -> Path:
        """Return the local index directory path."""
        return self.project_root_path / self.index_dir_name

    @property
    def index_db_path(self) -> Path:
        """Return the SQLite database path used by the workspace index."""
        return self.index_dir_path / "index.db"


settings = Settings()
