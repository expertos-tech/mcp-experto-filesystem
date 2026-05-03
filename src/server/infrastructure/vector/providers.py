"""Local vector providers for semantic retrieval."""

from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Protocol

from server.config import Settings, settings
from server.exceptions import ToolExecutionError


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    provider_id: str

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text payload."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text payloads."""


@dataclass(frozen=True)
class ProviderStatus:
    """Metadata about the active embedding provider."""

    requested: str
    active: str
    warnings: list[str]


class HashingEmbeddingProvider:
    """Deterministic local fallback provider based on hashed token features."""

    provider_id = "hashing-384-v1"

    def __init__(self, dimensions: int = 384) -> None:
        self._dimensions = dimensions

    def embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        normalized = unicodedata.normalize("NFKC", text.casefold())
        tokens = re.findall(r"\w+", normalized, flags=re.UNICODE)
        grams = [normalized[index : index + 3] for index in range(max(0, len(normalized) - 2))]
        for token in tokens + grams:
            if not token.strip():
                continue
            index = int(hashlib.sha1(token.encode("utf-8")).hexdigest(), 16) % self._dimensions
            vector[index] += 1.0
        magnitude = math.sqrt(sum(component * component for component in vector))
        if magnitude == 0:
            return vector
        return [component / magnitude for component in vector]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]


class SentenceTransformerEmbeddingProvider:
    """SentenceTransformers-based local provider."""

    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ModuleNotFoundError as exc:
            raise ToolExecutionError(
                "sentence-transformers is not installed.",
                operation="embeddings",
            ) from exc
        self._model = SentenceTransformer(model_name)
        self.provider_id = f"sentence-transformers:{model_name}"

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [list(map(float, vector)) for vector in vectors]


class EmbeddingProviderFactory:
    """Create the preferred local embedding provider with safe fallback."""

    def __init__(self, app_settings: Settings | None = None) -> None:
        self._settings = app_settings or settings

    def create(self) -> tuple[EmbeddingProvider, ProviderStatus]:
        requested = self._settings.embedding_provider
        warnings: list[str] = []
        provider: EmbeddingProvider
        if requested in {"auto", "sentence-transformers"}:
            try:
                provider = SentenceTransformerEmbeddingProvider(
                    self._settings.sentence_transformer_model
                )
                return provider, ProviderStatus(
                    requested=requested,
                    active=provider.provider_id,
                    warnings=warnings,
                )
            except ToolExecutionError:
                warnings.append(
                    "sentence-transformers is unavailable. Falling back to hashing embeddings."
                )
        provider = HashingEmbeddingProvider()
        return provider, ProviderStatus(
            requested=requested,
            active=provider.provider_id,
            warnings=warnings,
        )


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Return cosine similarity between normalized vectors."""
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True))
