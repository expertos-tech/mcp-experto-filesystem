"""Filesystem helpers for safe path access and content extraction."""

from __future__ import annotations

import hashlib
import mimetypes
import re
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree

from server.config import Settings, settings
from server.exceptions import PathSecurityError, ToolExecutionError, ValidationError

TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".csv",
    ".env.example",
    ".go",
    ".graphql",
    ".h",
    ".hpp",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".log",
    ".lua",
    ".md",
    ".mdx",
    ".php",
    ".pl",
    ".py",
    ".rb",
    ".rs",
    ".rst",
    ".scss",
    ".sh",
    ".sql",
    ".svg",
    ".swift",
    ".tex",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
DOCUMENT_EXTENSIONS = {".doc", ".docx", ".pdf", ".ppt", ".pptx"}
IGNORED_DIRS = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "node_modules",
}
IGNORED_SUFFIXES = {
    ".bin",
    ".class",
    ".dll",
    ".dylib",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".key",
    ".lock",
    ".mp3",
    ".mp4",
    ".o",
    ".otf",
    ".pem",
    ".png",
    ".pyc",
    ".so",
    ".tar",
    ".ttf",
    ".wav",
    ".webp",
    ".zip",
}
WORD_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
DRAWING_NAMESPACE = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


@dataclass(frozen=True)
class ContentSegment:
    """A logical segment extracted from a document."""

    kind: str
    index: int
    text: str


@dataclass(frozen=True)
class ExtractedContent:
    """Normalized content extracted from a file."""

    path: str
    file_kind: str
    extractor: str
    mime_type: str
    content: str
    encoding: str | None = None
    segments: list[ContentSegment] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class WorkspacePathResolver:
    """Resolve and validate paths relative to the project root."""

    def __init__(self, app_settings: Settings | None = None) -> None:
        self._settings = app_settings or settings
        self.root = self._settings.project_root_path
        self.index_dir = self._settings.index_dir_path

    def validate_user_path(self, raw_path: str) -> Path:
        """Resolve a user-provided relative path inside the project root."""
        if not raw_path.strip():
            raise ValidationError("Path cannot be empty.")
        candidate = Path(raw_path)
        if candidate.is_absolute():
            raise PathSecurityError("Absolute paths are not allowed.")
        resolved = (self.root / candidate).resolve()
        self._assert_within_root(resolved)
        if resolved.is_symlink():
            self._assert_within_root(resolved.resolve())
        return resolved

    def to_relative(self, path: Path) -> str:
        """Convert an absolute path to a project-relative POSIX path."""
        return path.resolve().relative_to(self.root).as_posix()

    def is_ignored(self, path: Path) -> bool:
        """Return whether a path should be ignored by default."""
        try:
            relative_parts = path.resolve().relative_to(self.root).parts
        except ValueError:
            return True
        if any(part in IGNORED_DIRS for part in relative_parts):
            return True
        if path.name in {".env"}:
            return True
        if path.suffix.lower() in IGNORED_SUFFIXES:
            return True
        return path.is_file() and self.index_dir in path.resolve().parents

    def iter_files(self, paths: list[str] | None = None) -> Iterable[Path]:
        """Yield indexable files under the workspace or under specific relative paths."""
        if paths:
            for raw_path in paths:
                candidate = self.validate_user_path(raw_path)
                if candidate.is_dir():
                    yield from self._iter_directory(candidate)
                elif candidate.is_file():
                    if not self.is_ignored(candidate):
                        yield candidate
                else:
                    raise ValidationError(f"Path does not exist: {raw_path}")
            return
        yield from self._iter_directory(self.root)

    def _iter_directory(self, directory: Path) -> Iterable[Path]:
        for path in sorted(directory.iterdir(), key=lambda item: item.name):
            if self.is_ignored(path):
                continue
            if path.is_symlink():
                resolved = path.resolve()
                self._assert_within_root(resolved)
            if path.is_dir():
                yield from self._iter_directory(path)
            elif path.is_file():
                yield path

    def _assert_within_root(self, path: Path) -> None:
        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise PathSecurityError("Path escapes the allowed project root.") from exc


class ContentExtractor:
    """Extract normalized text from supported workspace files."""

    def __init__(
        self,
        resolver: WorkspacePathResolver,
        app_settings: Settings | None = None,
    ) -> None:
        self._resolver = resolver
        self._settings = app_settings or settings

    def extract(self, path: Path) -> ExtractedContent:
        """Extract indexed content from a workspace file."""
        relative_path = self._resolver.to_relative(path)
        file_kind = self.classify_file(path)
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if file_kind in {"text", "markdown", "code", "config"}:
            content, encoding = self._read_text_file(path)
            return ExtractedContent(
                path=relative_path,
                file_kind=file_kind,
                extractor="text",
                mime_type=mime_type,
                content=content,
                encoding=encoding,
            )
        if file_kind == "docx":
            return self._extract_docx(path, relative_path, mime_type)
        if file_kind == "pptx":
            return self._extract_pptx(path, relative_path, mime_type)
        if file_kind == "pdf":
            return self._extract_pdf(path, relative_path, mime_type)
        if file_kind == "legacy-office":
            raise ToolExecutionError(
                "Legacy Office documents require an external conversion runtime.",
                operation="extract",
                path=relative_path,
            )
        raise ToolExecutionError(
            "Unsupported file type for extraction.",
            operation="extract",
            path=relative_path,
        )

    def read_text_excerpt(
        self, path: Path, start_line: int, end_line: int, max_chars: int
    ) -> dict[str, object]:
        """Read a bounded excerpt from a text-like file."""
        if start_line < 1:
            raise ValidationError("start_line must be >= 1.")
        if end_line < start_line:
            raise ValidationError("end_line must be >= start_line.")
        extracted = self.extract(path)
        if extracted.file_kind not in {"text", "markdown", "code", "config"}:
            raise ValidationError("read_file_excerpt only supports text-like files.")
        lines = extracted.content.splitlines()
        start_index = start_line - 1
        end_index = min(end_line, len(lines))
        selected = "\n".join(lines[start_index:end_index])
        truncated = selected[:max_chars]
        warnings: list[str] = []
        if len(selected) > max_chars:
            warnings.append("Excerpt truncated to respect max_chars.")
        return {
            "path": extracted.path,
            "file_kind": extracted.file_kind,
            "encoding": extracted.encoding,
            "requested_range": {"start_line": start_line, "end_line": end_line},
            "returned_range": {"start_line": start_line, "end_line": end_index},
            "content": truncated,
            "warnings": warnings,
        }

    def read_document_excerpt(
        self, path: Path, page: int, max_pages: int, max_chars: int
    ) -> dict[str, object]:
        """Read a bounded excerpt from a supported document format."""
        if page < 1:
            raise ValidationError("page must be >= 1.")
        if max_pages < 1:
            raise ValidationError("max_pages must be >= 1.")
        extracted = self.extract(path)
        if extracted.file_kind not in {"docx", "pdf", "pptx"}:
            raise ValidationError("read_document_excerpt only supports pdf, docx, and pptx.")
        segments = extracted.segments or [
            ContentSegment(kind="section", index=1, text=extracted.content)
        ]
        start_index = page - 1
        window = segments[start_index : start_index + max_pages]
        items = []
        for segment in window:
            items.append(
                {
                    "kind": segment.kind,
                    "index": segment.index,
                    "content": segment.text[:max_chars],
                }
            )
        warnings = list(extracted.warnings)
        if extracted.file_kind == "docx":
            warnings.append("DOCX page boundaries are logical, not physical page numbers.")
        return {
            "path": extracted.path,
            "file_kind": extracted.file_kind,
            "extractor": extracted.extractor,
            "requested_page": page,
            "returned_items": items,
            "warnings": warnings,
        }

    def classify_file(self, path: Path) -> str:
        """Classify a file into a retrieval-oriented content family."""
        name = path.name.lower()
        suffix = path.suffix.lower()
        if name.endswith((".md", ".mdx")):
            return "markdown"
        if suffix in {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".rb", ".php"}:
            return "code"
        if suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"}:
            return "config"
        if suffix in {".doc", ".ppt"}:
            return "legacy-office"
        if suffix in DOCUMENT_EXTENSIONS:
            return suffix.lstrip(".")
        if suffix in TEXT_EXTENSIONS or mimetypes.guess_type(path.name)[0] == "text/plain":
            return "text"
        return "unsupported"

    def should_index(self, path: Path) -> bool:
        """Return whether the file should be indexed."""
        if path.stat().st_size > self._settings.max_file_bytes:
            return False
        return self.classify_file(path) != "unsupported"

    @staticmethod
    def file_hash(path: Path) -> str:
        """Compute a stable file hash for change detection."""
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65_536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _read_text_file(self, path: Path) -> tuple[str, str]:
        file_size = path.stat().st_size
        if file_size > self._settings.max_file_bytes:
            raise ToolExecutionError(
                f"File exceeds the configured size limit of {self._settings.max_file_bytes} bytes.",
                operation="read",
                path=self._resolver.to_relative(path),
            )
        raw = path.read_bytes()
        for encoding in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                return raw.decode(encoding), encoding
            except UnicodeDecodeError:
                continue
        raise ToolExecutionError(
            "Unable to decode file with supported text encodings.",
            operation="read",
            path=self._resolver.to_relative(path),
        )

    def _extract_docx(self, path: Path, relative_path: str, mime_type: str) -> ExtractedContent:
        try:
            with zipfile.ZipFile(path) as archive:
                xml_bytes = archive.read("word/document.xml")
        except (KeyError, zipfile.BadZipFile) as exc:
            raise ToolExecutionError(
                "Unable to extract DOCX content.",
                operation="extract",
                path=relative_path,
            ) from exc
        root = ElementTree.fromstring(xml_bytes)
        paragraphs = []
        for paragraph in root.findall(".//w:p", WORD_NAMESPACE):
            texts = [node.text or "" for node in paragraph.findall(".//w:t", WORD_NAMESPACE)]
            joined = "".join(texts).strip()
            if joined:
                paragraphs.append(joined)
        text = "\n".join(paragraphs)
        return ExtractedContent(
            path=relative_path,
            file_kind="docx",
            extractor="ooxml",
            mime_type=mime_type,
            content=text,
            segments=[ContentSegment(kind="section", index=1, text=text)],
        )

    def _extract_pptx(self, path: Path, relative_path: str, mime_type: str) -> ExtractedContent:
        try:
            with zipfile.ZipFile(path) as archive:
                slide_names = sorted(
                    name
                    for name in archive.namelist()
                    if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
                )
                slides = []
                for slide_number, slide_name in enumerate(slide_names, start=1):
                    root = ElementTree.fromstring(archive.read(slide_name))
                    texts = [node.text or "" for node in root.findall(".//a:t", DRAWING_NAMESPACE)]
                    joined = "\n".join(part.strip() for part in texts if part.strip())
                    if joined:
                        slides.append(ContentSegment(kind="slide", index=slide_number, text=joined))
        except zipfile.BadZipFile as exc:
            raise ToolExecutionError(
                "Unable to extract PPTX content.",
                operation="extract",
                path=relative_path,
            ) from exc
        content = "\n\n".join(segment.text for segment in slides)
        return ExtractedContent(
            path=relative_path,
            file_kind="pptx",
            extractor="ooxml",
            mime_type=mime_type,
            content=content,
            segments=slides,
        )

    def _extract_pdf(self, path: Path, relative_path: str, mime_type: str) -> ExtractedContent:
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError as exc:
            raise ToolExecutionError(
                "PDF extraction requires the optional pypdf dependency.",
                operation="extract",
                path=relative_path,
            ) from exc
        try:
            reader = PdfReader(str(path))
        except Exception as exc:
            raise ToolExecutionError(
                "Unable to open PDF document.",
                operation="extract",
                path=relative_path,
            ) from exc
        pages = []
        warnings: list[str] = []
        for page_number, pdf_page in enumerate(reader.pages, start=1):
            extracted = (pdf_page.extract_text() or "").strip()
            if extracted:
                pages.append(ContentSegment(kind="page", index=page_number, text=extracted))
        if not pages:
            warnings.append("No extractable PDF text was found. The file may require OCR.")
        content = "\n\n".join(segment.text for segment in pages)
        return ExtractedContent(
            path=relative_path,
            file_kind="pdf",
            extractor="pypdf",
            mime_type=mime_type,
            content=content,
            segments=pages,
            warnings=warnings,
        )
