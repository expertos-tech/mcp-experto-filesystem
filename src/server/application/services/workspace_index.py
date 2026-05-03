"""Application service for workspace reading, indexing, and search."""

from __future__ import annotations

import json
import logging
import os
import queue
import re
import threading
import unicodedata
from pathlib import Path
from typing import Any

from server.config import Settings, settings
from server.exceptions import ToolExecutionError, ValidationError
from server.infrastructure.filesystem.sqlite_index import (
    DocumentFingerprint,
    SQLiteWorkspaceIndex,
)
from server.infrastructure.filesystem.workspace import ContentExtractor, WorkspacePathResolver
from server.infrastructure.vector.providers import (
    EmbeddingProviderFactory,
    cosine_similarity,
)

logger = logging.getLogger(__name__)


class WorkspaceIndexWatcher:
    """Optional filesystem watcher that keeps the index warm."""

    def __init__(
        self,
        *,
        root: Path,
        callback: Any,
        enabled: bool,
    ) -> None:
        self._root = root
        self._callback = callback
        self._enabled = enabled
        self._observer: Any | None = None
        self._queue: queue.Queue[str] = queue.Queue()
        self._worker: threading.Thread | None = None
        self._available = False
        self._status = "disabled" if not enabled else "unavailable"
        self._start()

    @property
    def status(self) -> str:
        """Return the current watcher status."""
        return self._status

    @property
    def backlog(self) -> int:
        """Return the number of queued filesystem events."""
        return self._queue.qsize()

    def _start(self) -> None:
        if not self._enabled:
            return
        try:
            from watchdog.events import FileSystemEvent, FileSystemEventHandler
            from watchdog.observers import Observer
        except ModuleNotFoundError:
            return

        class Handler(FileSystemEventHandler):
            def __init__(self, target: WorkspaceIndexWatcher) -> None:
                self._target = target

            def on_any_event(self, event: FileSystemEvent) -> None:
                if event.is_directory:
                    return
                try:
                    relative = (
                        Path(os.fsdecode(event.src_path))
                        .resolve()
                        .relative_to(self._target._root)
                        .as_posix()
                    )
                except ValueError:
                    return
                self._target._queue.put(relative)

        self._observer = Observer()
        self._observer.daemon = True
        self._observer.schedule(Handler(self), str(self._root), recursive=True)
        self._observer.start()
        self._worker = threading.Thread(target=self._drain_queue, daemon=True)
        self._worker.start()
        self._available = True
        self._status = "running"

    def _drain_queue(self) -> None:
        while True:
            path = self._queue.get()
            try:
                self._callback(paths=[path], source="watcher")
            except Exception:
                logger.exception("Workspace watcher reindex failed")
            finally:
                self._queue.task_done()


class WorkspaceIndexService:
    """Coordinate safe reading, indexing, and retrieval for the workspace."""

    def __init__(self, app_settings: Settings | None = None) -> None:
        self._settings = app_settings or settings
        self._resolver = WorkspacePathResolver(self._settings)
        self._extractor = ContentExtractor(self._resolver, self._settings)
        self._repository = SQLiteWorkspaceIndex(self._settings.index_db_path)
        self._provider, self._provider_status = EmbeddingProviderFactory(self._settings).create()
        self._watcher = WorkspaceIndexWatcher(
            root=self._settings.project_root_path,
            callback=self._index_from_watcher,
            enabled=self._settings.enable_index_watcher,
        )

    def project_overview(self, max_depth: int = 3) -> dict[str, Any]:
        """Return a token-efficient project map."""
        if max_depth < 1:
            raise ValidationError("max_depth must be >= 1.")
        root = self._settings.project_root_path
        tree = self._build_tree(root, depth=1, max_depth=max_depth)
        counts = {"indexed_candidate_files": 0, "ignored_entries": 0}
        for path in self._resolver.iter_files():
            counts["indexed_candidate_files"] += int(self._extractor.should_index(path))
        for path in root.rglob("*"):
            if self._resolver.is_ignored(path):
                counts["ignored_entries"] += 1
        return {
            "summary": f"Mapped the workspace up to depth {max_depth}.",
            "root": root.as_posix(),
            "max_depth": max_depth,
            "tree": tree,
            "counts": counts,
            "index_location": self._repository.db_path.as_posix(),
            "watcher_status": self._watcher.status,
        }

    def read_file_excerpt(
        self, path: str, start_line: int = 1, end_line: int = 50, max_chars: int | None = None
    ) -> dict[str, Any]:
        """Read a bounded text excerpt from the workspace."""
        resolved = self._resolver.validate_user_path(path)
        return {
            "summary": f"Read lines {start_line}-{end_line} from {path}.",
            **self._extractor.read_text_excerpt(
                resolved,
                start_line=start_line,
                end_line=end_line,
                max_chars=max_chars or self._settings.max_tokens_per_response,
            ),
        }

    def read_document_excerpt(
        self, path: str, page: int = 1, max_pages: int = 3, max_chars: int | None = None
    ) -> dict[str, Any]:
        """Read a bounded excerpt from a supported document file."""
        resolved = self._resolver.validate_user_path(path)
        return {
            "summary": f"Read document content from {path}.",
            **self._extractor.read_document_excerpt(
                resolved,
                page=page,
                max_pages=max_pages,
                max_chars=max_chars or self._settings.max_tokens_per_response,
            ),
        }

    def index_workspace(
        self,
        *,
        force_full: bool = False,
        paths: list[str] | None = None,
        file_types: list[str] | None = None,
        source: str = "manual",
    ) -> dict[str, Any]:
        """Create or update the local workspace index."""
        indexed = 0
        skipped = 0
        errors = 0
        candidates = list(self._resolver.iter_files(paths=paths))
        if force_full and paths is None:
            self._repository.clear()
        indexed_paths: set[str] = set()
        for path in candidates:
            relative_path = self._resolver.to_relative(path)
            indexed_paths.add(relative_path)
            if file_types and self._extractor.classify_file(path) not in file_types:
                skipped += 1
                continue
            if not self._extractor.should_index(path):
                skipped += 1
                continue
            fingerprint = DocumentFingerprint(
                mtime_ns=path.stat().st_mtime_ns,
                size_bytes=path.stat().st_size,
                sha256=self._extractor.file_hash(path),
            )
            stored = self._repository.get_fingerprint(relative_path)
            if not force_full and stored == fingerprint:
                skipped += 1
                continue
            try:
                extracted = self._extractor.extract(path)
                chunks = self._chunk_content(extracted)
                embeddings = self._provider.embed_texts([chunk["content"] for chunk in chunks])
                self._repository.replace_document(
                    path=relative_path,
                    fingerprint=fingerprint,
                    mime_type=extracted.mime_type,
                    file_kind=extracted.file_kind,
                    extractor=extracted.extractor,
                    chunks=chunks,
                    embeddings=embeddings,
                    model_id=self._provider.provider_id,
                )
                indexed += 1
            except ToolExecutionError as exc:
                errors += 1
                self._repository.record_error(
                    relative_path,
                    error_code=self._error_code_for(exc),
                    message=str(exc),
                    retryable="requires" in str(exc).lower(),
                )
        if paths is None:
            for stale_path in set(self._repository.list_document_paths()) - indexed_paths:
                self._repository.delete_document(stale_path)
        self._repository.record_run(
            mode="full" if force_full and paths is None else source,
            indexed_count=indexed,
            skipped_count=skipped,
            error_count=errors,
            watcher_backlog=self._watcher.backlog,
        )
        return {
            "summary": f"Workspace indexing finished with {indexed} updated files.",
            "indexed_count": indexed,
            "skipped_count": skipped,
            "error_count": errors,
            "paths_scanned": len(candidates),
            "embedding_provider": self._provider.provider_id,
            "embedding_warnings": self._provider_status.warnings,
            "watcher_status": self._watcher.status,
        }

    def search_files(
        self,
        *,
        query: str,
        mode: str = "hybrid",
        top_k: int | None = None,
        file_types: list[str] | None = None,
        path_prefix: str | None = None,
    ) -> dict[str, Any]:
        """Search indexed files by keyword, semantic intent, or both."""
        if not query.strip():
            raise ValidationError("query cannot be empty.")
        if mode not in {"keyword", "semantic", "hybrid"}:
            raise ValidationError("mode must be one of: keyword, semantic, hybrid.")
        if top_k is not None and top_k < 1:
            raise ValidationError("top_k must be >= 1.")
        if self._repository.stats()["document_count"] == 0:
            raise ToolExecutionError(
                "Index is empty. Run index_workspace first.",
                operation="search",
            )
        requested_top_k = top_k or self._settings.search_default_top_k
        normalized_prefix = self._normalize_path_prefix(path_prefix)
        keyword_matches = []
        semantic_matches = []
        if mode in {"keyword", "hybrid"}:
            keyword_matches = self._repository.keyword_search(
                query=query,
                top_k=requested_top_k * 3,
                file_types=file_types,
                path_prefix=normalized_prefix,
            )
        if mode in {"semantic", "hybrid"}:
            semantic_matches = self._semantic_search(
                query=query,
                top_k=requested_top_k * 3,
                file_types=file_types,
                path_prefix=normalized_prefix,
            )
        merged = self._merge_rankings(keyword_matches, semantic_matches, requested_top_k)
        warnings = list(self._provider_status.warnings)
        if not merged:
            warnings.append("No matches were found for the given query.")
        return {
            "summary": f"Found {len(merged)} matches for '{query}'.",
            "query": query,
            "mode": mode,
            "matches": merged,
            "warnings": warnings,
            "embedding_provider": self._provider.provider_id,
        }

    def find_similar_content(
        self,
        *,
        path: str,
        start_line: int | None = None,
        end_line: int | None = None,
        top_k: int = 10,
    ) -> dict[str, Any]:
        """Find semantically similar content to a file or file excerpt."""
        if top_k < 1:
            raise ValidationError("top_k must be >= 1.")
        resolved = self._resolver.validate_user_path(path)
        if start_line is not None or end_line is not None:
            excerpt = self._extractor.read_text_excerpt(
                resolved,
                start_line=start_line or 1,
                end_line=end_line or ((start_line or 1) + self._settings.chunk_max_lines),
                max_chars=self._settings.chunk_max_chars,
            )["content"]
            if not isinstance(excerpt, str):
                raise ToolExecutionError(
                    "Unable to derive excerpt content.",
                    operation="find_similar_content",
                )
            query = excerpt
        else:
            extracted = self._extractor.extract(resolved)
            query = extracted.content[: self._settings.chunk_max_chars]
        matches = self._semantic_search(
            query=query,
            top_k=top_k + 3,
            file_types=None,
            path_prefix=None,
        )
        relative_path = self._resolver.to_relative(resolved)
        filtered = [match for match in matches if match["path"] != relative_path][:top_k]
        return {
            "summary": f"Found {len(filtered)} similar matches for {path}.",
            "path": relative_path,
            "matches": filtered,
            "embedding_provider": self._provider.provider_id,
            "warnings": list(self._provider_status.warnings),
        }

    def index_status(self) -> dict[str, Any]:
        """Return local index health and provider status."""
        stats = self._repository.stats()
        return {
            "summary": "Returned local index status.",
            "database_path": self._repository.db_path.as_posix(),
            "embedding_provider_requested": self._provider_status.requested,
            "embedding_provider_active": self._provider_status.active,
            "embedding_warnings": self._provider_status.warnings,
            "watcher_status": self._watcher.status,
            "watcher_backlog": self._watcher.backlog,
            **stats,
        }

    def index_errors(self, limit: int = 50) -> dict[str, Any]:
        """Return the most recent indexing failures."""
        if limit < 1:
            raise ValidationError("limit must be >= 1.")
        errors = self._repository.latest_errors(limit)
        return {
            "summary": f"Returned {len(errors)} indexing errors.",
            "errors": errors,
        }

    def _chunk_content(self, extracted: Any) -> list[dict[str, Any]]:
        if extracted.segments:
            chunks: list[dict[str, Any]] = []
            chunk_index = 0
            for segment in extracted.segments:
                for offset in range(0, len(segment.text), self._settings.chunk_max_chars):
                    text = segment.text[offset : offset + self._settings.chunk_max_chars].strip()
                    if not text:
                        continue
                    chunks.append(
                        {
                            "chunk_index": chunk_index,
                            "content": text,
                            "content_norm": self._normalize_text(text),
                            "page": segment.index if segment.kind == "page" else None,
                            "slide": segment.index if segment.kind == "slide" else None,
                            "start_line": None,
                            "end_line": None,
                            "token_estimate": max(1, len(text) // 4),
                            "language_hint": None,
                        }
                    )
                    chunk_index += 1
            return chunks or [
                {
                    "chunk_index": 0,
                    "content": extracted.content,
                    "content_norm": self._normalize_text(extracted.content),
                    "page": None,
                    "slide": None,
                    "start_line": None,
                    "end_line": None,
                    "token_estimate": max(1, len(extracted.content) // 4),
                    "language_hint": None,
                }
            ]
        lines = extracted.content.splitlines()
        chunks = []
        chunk_index = 0
        current_lines: list[str] = []
        current_start_line = 1
        current_chars = 0
        for line_number, line in enumerate(lines, start=1):
            prospective_chars = current_chars + len(line) + 1
            if current_lines and (
                len(current_lines) >= self._settings.chunk_max_lines
                or prospective_chars > self._settings.chunk_max_chars
            ):
                content = "\n".join(current_lines)
                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "content": content,
                        "content_norm": self._normalize_text(content),
                        "start_line": current_start_line,
                        "end_line": line_number - 1,
                        "page": None,
                        "slide": None,
                        "token_estimate": max(1, len(content) // 4),
                        "language_hint": None,
                    }
                )
                chunk_index += 1
                current_lines = []
                current_start_line = line_number
                current_chars = 0
            current_lines.append(line)
            current_chars += len(line) + 1
        if current_lines:
            content = "\n".join(current_lines)
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "content": content,
                    "content_norm": self._normalize_text(content),
                    "start_line": current_start_line,
                    "end_line": len(lines),
                    "page": None,
                    "slide": None,
                    "token_estimate": max(1, len(content) // 4),
                    "language_hint": None,
                }
            )
        return chunks

    def _semantic_search(
        self,
        *,
        query: str,
        top_k: int,
        file_types: list[str] | None,
        path_prefix: str | None,
    ) -> list[dict[str, Any]]:
        query_vector = self._provider.embed_text(query)
        candidates = self._repository.semantic_candidates(
            file_types=file_types,
            path_prefix=path_prefix,
        )
        ranked = []
        for candidate in candidates:
            vector = json.loads(str(candidate["vector_json"]))
            score = cosine_similarity(query_vector, list(map(float, vector)))
            if score <= 0:
                continue
            ranked.append(
                {
                    "path": candidate["path"],
                    "file_kind": candidate["file_kind"],
                    "content": candidate["content"],
                    "start_line": candidate["start_line"],
                    "end_line": candidate["end_line"],
                    "page": candidate["page"],
                    "slide": candidate["slide"],
                    "semantic_score": round(score, 4),
                }
            )
        ranked.sort(key=self._semantic_score_value, reverse=True)
        return ranked[:top_k]

    def _merge_rankings(
        self,
        keyword_matches: list[dict[str, Any]],
        semantic_matches: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        merged: dict[tuple[str, str], dict[str, Any]] = {}
        for rank, match in enumerate(keyword_matches, start=1):
            key = (str(match["path"]), str(match["content"]))
            lexical_score = 1 / (50 + rank)
            entry = merged.setdefault(
                key,
                {
                    "path": match["path"],
                    "file_kind": match["file_kind"],
                    "excerpt": self._truncate_excerpt(str(match["content"])),
                    "line_range": self._line_range(match),
                    "page": match["page"],
                    "slide": match["slide"],
                    "score": 0.0,
                    "match_types": [],
                },
            )
            entry["score"] += lexical_score
            entry["match_types"].append("keyword")
        for rank, match in enumerate(semantic_matches, start=1):
            key = (str(match["path"]), str(match["content"]))
            semantic_score = 1 / (50 + rank)
            entry = merged.setdefault(
                key,
                {
                    "path": match["path"],
                    "file_kind": match["file_kind"],
                    "excerpt": self._truncate_excerpt(str(match["content"])),
                    "line_range": self._line_range(match),
                    "page": match["page"],
                    "slide": match["slide"],
                    "score": 0.0,
                    "match_types": [],
                },
            )
            entry["score"] += semantic_score
            entry["match_types"].append("semantic")
        ordered = sorted(merged.values(), key=self._score_value, reverse=True)
        for item in ordered:
            score = float(item.get("score", 0.0))
            item["score"] = round(score, 4)
            item["match_type"] = (
                "hybrid" if len(set(item["match_types"])) > 1 else item["match_types"][0]
            )
            item["reason"] = self._reason_for(item)
            item.pop("match_types", None)
        return ordered[:top_k]

    def _build_tree(self, directory: Path, *, depth: int, max_depth: int) -> list[dict[str, Any]]:
        nodes = []
        for child in sorted(
            directory.iterdir(),
            key=lambda item: (item.is_file(), item.name.lower()),
        ):
            if self._resolver.is_ignored(child):
                continue
            node: dict[str, Any] = {
                "name": child.name,
                "path": child.relative_to(self._settings.project_root_path).as_posix(),
                "kind": "directory" if child.is_dir() else "file",
            }
            if child.is_file():
                node["file_kind"] = self._extractor.classify_file(child)
            if child.is_dir() and depth < max_depth:
                node["children"] = self._build_tree(child, depth=depth + 1, max_depth=max_depth)
            nodes.append(node)
        return nodes

    def _normalize_path_prefix(self, path_prefix: str | None) -> str | None:
        if path_prefix is None:
            return None
        resolved = self._resolver.validate_user_path(path_prefix)
        if resolved.is_file():
            return self._resolver.to_relative(resolved)
        return f"{self._resolver.to_relative(resolved).rstrip('/')}/"

    def _index_from_watcher(self, *, paths: list[str], source: str) -> None:
        valid_paths = []
        for raw_path in paths:
            try:
                resolved = self._resolver.validate_user_path(raw_path)
            except Exception:
                continue
            if not resolved.exists() or self._resolver.is_ignored(resolved):
                continue
            valid_paths.append(raw_path)
        if valid_paths:
            self.index_workspace(force_full=False, paths=valid_paths, source=source)

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKC", text.casefold())
        return re.sub(r"\s+", " ", normalized).strip()

    @staticmethod
    def _truncate_excerpt(text: str, limit: int = 280) -> str:
        return text if len(text) <= limit else f"{text[: limit - 3]}..."

    @staticmethod
    def _score_value(item: dict[str, Any]) -> float:
        return float(item.get("score", 0.0))

    @staticmethod
    def _semantic_score_value(item: dict[str, Any]) -> float:
        return float(item.get("semantic_score", 0.0))

    @staticmethod
    def _line_range(match: dict[str, Any]) -> dict[str, int] | None:
        start_line = match.get("start_line")
        end_line = match.get("end_line")
        if start_line is None or end_line is None:
            return None
        return {"start_line": int(start_line), "end_line": int(end_line)}

    @staticmethod
    def _error_code_for(exc: ToolExecutionError) -> str:
        message = str(exc).lower()
        if "unsupported" in message:
            return "UNSUPPORTED_FILE_TYPE"
        if "requires" in message:
            return "EXTRACTION_RUNTIME_REQUIRED"
        return "EXTRACTION_FAILED"

    @staticmethod
    def _reason_for(item: dict[str, Any]) -> str:
        if item["match_type"] == "hybrid":
            return "Matched both lexical and semantic ranking."
        if item["match_type"] == "keyword":
            return "Matched exact or near-exact query terms."
        return "Matched semantic similarity."


_workspace_service: WorkspaceIndexService | None = None


def get_workspace_service() -> WorkspaceIndexService:
    """Return the shared workspace service singleton."""
    global _workspace_service
    if _workspace_service is None:
        _workspace_service = WorkspaceIndexService()
    return _workspace_service
