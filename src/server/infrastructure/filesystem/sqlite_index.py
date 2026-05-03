"""SQLite-backed lexical and vector index for workspace retrieval."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class DocumentFingerprint:
    """Persisted fingerprint used for incremental indexing."""

    mtime_ns: int
    size_bytes: int
    sha256: str


class SQLiteWorkspaceIndex:
    """Manage local workspace indexing state inside SQLite."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @property
    def db_path(self) -> Path:
        """Return the database path."""
        return self._db_path

    def replace_document(
        self,
        *,
        path: str,
        fingerprint: DocumentFingerprint,
        mime_type: str,
        file_kind: str,
        extractor: str,
        chunks: list[dict[str, object]],
        embeddings: list[list[float]],
        model_id: str,
    ) -> None:
        """Replace the indexed representation of a single document."""
        with self._connect() as connection:
            connection.execute("BEGIN")
            existing_chunk_rows = connection.execute(
                """
                SELECT chunks.id
                FROM chunks
                JOIN documents ON documents.id = chunks.document_id
                WHERE documents.path = ?
                """,
                (path,),
            ).fetchall()
            for row in existing_chunk_rows:
                connection.execute("DELETE FROM chunks_fts WHERE rowid = ?", (row["id"],))
            connection.execute("DELETE FROM documents WHERE path = ?", (path,))
            cursor = connection.execute(
                """
                INSERT INTO documents (
                    path,
                    mtime_ns,
                    size_bytes,
                    sha256,
                    mime_type,
                    file_kind,
                    extractor,
                    status,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    path,
                    fingerprint.mtime_ns,
                    fingerprint.size_bytes,
                    fingerprint.sha256,
                    mime_type,
                    file_kind,
                    extractor,
                    "indexed",
                    self._now(),
                ),
            )
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to persist document row.")
            document_id = int(cursor.lastrowid)
            for chunk, vector in zip(chunks, embeddings, strict=True):
                chunk_cursor = connection.execute(
                    """
                    INSERT INTO chunks (
                        document_id,
                        chunk_index,
                        content,
                        content_norm,
                        start_line,
                        end_line,
                        page,
                        slide,
                        token_estimate,
                        language_hint
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        document_id,
                        chunk["chunk_index"],
                        chunk["content"],
                        chunk["content_norm"],
                        chunk.get("start_line"),
                        chunk.get("end_line"),
                        chunk.get("page"),
                        chunk.get("slide"),
                        chunk["token_estimate"],
                        chunk.get("language_hint"),
                    ),
                )
                if chunk_cursor.lastrowid is None:
                    raise RuntimeError("Failed to persist chunk row.")
                chunk_id = int(chunk_cursor.lastrowid)
                connection.execute(
                    "INSERT INTO chunks_fts(rowid, content, path) VALUES (?, ?, ?)",
                    (chunk_id, chunk["content"], path),
                )
                connection.execute(
                    """
                    INSERT INTO embeddings (chunk_id, model_id, vector_dim, vector_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (chunk_id, model_id, len(vector), json.dumps(vector)),
                )
            connection.execute("DELETE FROM index_errors WHERE path = ?", (path,))
            connection.commit()

    def record_error(self, path: str, error_code: str, message: str, retryable: bool) -> None:
        """Record an indexing error for a specific path."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO index_errors(path, error_code, message, retryable, last_seen)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    error_code=excluded.error_code,
                    message=excluded.message,
                    retryable=excluded.retryable,
                    last_seen=excluded.last_seen
                """,
                (path, error_code, message, int(retryable), self._now()),
            )

    def record_run(
        self,
        *,
        mode: str,
        indexed_count: int,
        skipped_count: int,
        error_count: int,
        watcher_backlog: int = 0,
    ) -> None:
        """Persist an index run summary."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO index_runs(
                    run_mode,
                    indexed_count,
                    skipped_count,
                    error_count,
                    watcher_backlog,
                    ran_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (mode, indexed_count, skipped_count, error_count, watcher_backlog, self._now()),
            )

    def delete_document(self, path: str) -> None:
        """Delete a document and its indexed chunks."""
        with self._connect() as connection:
            chunk_rows = connection.execute(
                """
                SELECT chunks.id
                FROM chunks
                JOIN documents ON documents.id = chunks.document_id
                WHERE documents.path = ?
                """,
                (path,),
            ).fetchall()
            for row in chunk_rows:
                connection.execute("DELETE FROM chunks_fts WHERE rowid = ?", (row["id"],))
            connection.execute("DELETE FROM documents WHERE path = ?", (path,))

    def clear(self) -> None:
        """Delete all indexed documents and chunks."""
        with self._connect() as connection:
            connection.execute("DELETE FROM embeddings")
            connection.execute("DELETE FROM chunks")
            connection.execute("DELETE FROM documents")
            connection.execute("DELETE FROM chunks_fts")
            connection.execute("DELETE FROM index_errors")

    def get_fingerprint(self, path: str) -> DocumentFingerprint | None:
        """Return the stored fingerprint for a document, if any."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT mtime_ns, size_bytes, sha256 FROM documents WHERE path = ?",
                (path,),
            ).fetchone()
        if row is None:
            return None
        return DocumentFingerprint(
            mtime_ns=int(row["mtime_ns"]),
            size_bytes=int(row["size_bytes"]),
            sha256=str(row["sha256"]),
        )

    def list_document_paths(self) -> list[str]:
        """Return all indexed document paths."""
        with self._connect() as connection:
            rows = connection.execute("SELECT path FROM documents").fetchall()
        return [str(row["path"]) for row in rows]

    def keyword_search(
        self,
        *,
        query: str,
        top_k: int,
        file_types: list[str] | None,
        path_prefix: str | None,
    ) -> list[dict[str, object]]:
        """Run an FTS5 query and return ranked chunk matches."""
        with self._connect() as connection:
            try:
                rows = connection.execute(
                    self._search_sql(query, file_types, path_prefix),
                    self._search_params(query, top_k, file_types, path_prefix),
                ).fetchall()
            except sqlite3.OperationalError:
                fallback_query = " OR ".join(
                    f'"{token}"' for token in query.split() if token.strip()
                ) or f'"{query}"'
                rows = connection.execute(
                    self._search_sql(fallback_query, file_types, path_prefix),
                    self._search_params(fallback_query, top_k, file_types, path_prefix),
                ).fetchall()
        return [dict(row) for row in rows]

    def semantic_candidates(
        self,
        *,
        file_types: list[str] | None,
        path_prefix: str | None,
    ) -> list[dict[str, object]]:
        """Return candidate chunks with stored vectors for semantic ranking."""
        sql = """
            SELECT
                documents.path,
                documents.file_kind,
                chunks.content,
                chunks.start_line,
                chunks.end_line,
                chunks.page,
                chunks.slide,
                embeddings.model_id,
                embeddings.vector_json
            FROM embeddings
            JOIN chunks ON chunks.id = embeddings.chunk_id
            JOIN documents ON documents.id = chunks.document_id
            WHERE 1=1
        """
        params: list[object] = []
        if file_types:
            placeholders = ", ".join("?" for _ in file_types)
            sql += f" AND documents.file_kind IN ({placeholders})"
            params.extend(file_types)
        if path_prefix:
            sql += " AND documents.path LIKE ?"
            params.append(f"{path_prefix}%")
        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def latest_errors(self, limit: int) -> list[dict[str, object]]:
        """Return the most recent indexing errors."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT path, error_code, message, retryable, last_seen
                FROM index_errors
                ORDER BY last_seen DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def stats(self) -> dict[str, object]:
        """Return aggregate index statistics."""
        with self._connect() as connection:
            document_count = connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            chunk_count = connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            error_count = connection.execute("SELECT COUNT(*) FROM index_errors").fetchone()[0]
            latest_run = connection.execute(
                """
                SELECT run_mode, indexed_count, skipped_count, error_count, watcher_backlog, ran_at
                FROM index_runs
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
        return {
            "document_count": int(document_count),
            "chunk_count": int(chunk_count),
            "error_count": int(error_count),
            "latest_run": dict(latest_run) if latest_run is not None else None,
        }

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL UNIQUE,
                    mtime_ns INTEGER NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    sha256 TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    file_kind TEXT NOT NULL,
                    extractor TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    content_norm TEXT NOT NULL,
                    start_line INTEGER,
                    end_line INTEGER,
                    page INTEGER,
                    slide INTEGER,
                    token_estimate INTEGER NOT NULL,
                    language_hint TEXT
                );

                CREATE TABLE IF NOT EXISTS embeddings (
                    chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
                    model_id TEXT NOT NULL,
                    vector_dim INTEGER NOT NULL,
                    vector_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS index_errors (
                    path TEXT PRIMARY KEY,
                    error_code TEXT NOT NULL,
                    message TEXT NOT NULL,
                    retryable INTEGER NOT NULL,
                    last_seen TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS index_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_mode TEXT NOT NULL,
                    indexed_count INTEGER NOT NULL,
                    skipped_count INTEGER NOT NULL,
                    error_count INTEGER NOT NULL,
                    watcher_backlog INTEGER NOT NULL,
                    ran_at TEXT NOT NULL
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    content,
                    path UNINDEXED,
                    tokenize = 'unicode61'
                );
                """
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _search_sql(
        query: str, file_types: list[str] | None, path_prefix: str | None
    ) -> str:
        sql = """
            SELECT
                documents.path,
                documents.file_kind,
                chunks.content,
                chunks.start_line,
                chunks.end_line,
                chunks.page,
                chunks.slide,
                bm25(chunks_fts) AS lexical_rank
            FROM chunks_fts
            JOIN chunks ON chunks.id = chunks_fts.rowid
            JOIN documents ON documents.id = chunks.document_id
            WHERE chunks_fts MATCH ?
        """
        if file_types:
            placeholders = ", ".join("?" for _ in file_types)
            sql += f" AND documents.file_kind IN ({placeholders})"
        if path_prefix:
            sql += " AND documents.path LIKE ?"
        sql += " ORDER BY lexical_rank LIMIT ?"
        return sql

    @staticmethod
    def _search_params(
        query: str, top_k: int, file_types: list[str] | None, path_prefix: str | None
    ) -> list[object]:
        params: list[object] = [query]
        if file_types:
            params.extend(file_types)
        if path_prefix:
            params.append(f"{path_prefix}%")
        params.append(top_k)
        return params
