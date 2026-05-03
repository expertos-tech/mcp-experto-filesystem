"""FastMCP tool registrations for filesystem retrieval and indexing."""

from typing import Any

from fastmcp import FastMCP

from server.application.services.executor import universal_response
from server.application.services.workspace_index import get_workspace_service


@universal_response
async def project_overview_handler(max_depth: int = 3) -> dict[str, Any]:
    """Return a compact project structure overview."""
    return get_workspace_service().project_overview(max_depth=max_depth)


@universal_response
async def read_file_excerpt_handler(
    path: str, start_line: int = 1, end_line: int = 50, max_chars: int = 8_000
) -> dict[str, Any]:
    """Return a bounded text excerpt from a workspace file."""
    return get_workspace_service().read_file_excerpt(
        path=path,
        start_line=start_line,
        end_line=end_line,
        max_chars=max_chars,
    )


@universal_response
async def read_document_excerpt_handler(
    path: str, page: int = 1, max_pages: int = 3, max_chars: int = 8_000
) -> dict[str, Any]:
    """Return a bounded excerpt from a supported document."""
    return get_workspace_service().read_document_excerpt(
        path=path,
        page=page,
        max_pages=max_pages,
        max_chars=max_chars,
    )


@universal_response
async def index_workspace_handler(
    force_full: bool = False,
    paths: list[str] | None = None,
    file_types: list[str] | None = None,
) -> dict[str, Any]:
    """Create or update the local workspace index."""
    return get_workspace_service().index_workspace(
        force_full=force_full,
        paths=paths,
        file_types=file_types,
    )


@universal_response
async def search_files_handler(
    query: str,
    mode: str = "hybrid",
    top_k: int = 10,
    file_types: list[str] | None = None,
    path_prefix: str | None = None,
) -> dict[str, Any]:
    """Search indexed workspace content."""
    return get_workspace_service().search_files(
        query=query,
        mode=mode,
        top_k=top_k,
        file_types=file_types,
        path_prefix=path_prefix,
    )


@universal_response
async def find_similar_content_handler(
    path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    top_k: int = 10,
) -> dict[str, Any]:
    """Find semantically similar content for a file or excerpt."""
    return get_workspace_service().find_similar_content(
        path=path,
        start_line=start_line,
        end_line=end_line,
        top_k=top_k,
    )


@universal_response
async def index_status_handler() -> dict[str, Any]:
    """Return index health and watcher status."""
    return get_workspace_service().index_status()


@universal_response
async def index_errors_handler(limit: int = 50) -> dict[str, Any]:
    """Return recent indexing failures."""
    return get_workspace_service().index_errors(limit=limit)


def register_filesystem_tools(mcp: FastMCP) -> None:
    """Register filesystem and indexing tools."""

    @mcp.tool()
    async def project_overview(max_depth: int = 3) -> dict[str, Any]:
        """Returns a token-efficient map of the project structure."""
        return await project_overview_handler(max_depth=max_depth)  # type: ignore[no-any-return]

    @mcp.tool()
    async def read_file_excerpt(
        path: str,
        start_line: int = 1,
        end_line: int = 50,
        max_chars: int = 8_000,
    ) -> dict[str, Any]:
        """Reads a targeted line range from a text-like file."""
        return await read_file_excerpt_handler(  # type: ignore[no-any-return]
            path=path,
            start_line=start_line,
            end_line=end_line,
            max_chars=max_chars,
        )

    @mcp.tool()
    async def read_document_excerpt(
        path: str,
        page: int = 1,
        max_pages: int = 3,
        max_chars: int = 8_000,
    ) -> dict[str, Any]:
        """Reads bounded content from pdf, docx, and pptx files."""
        return await read_document_excerpt_handler(  # type: ignore[no-any-return]
            path=path,
            page=page,
            max_pages=max_pages,
            max_chars=max_chars,
        )

    @mcp.tool()
    async def index_workspace(
        force_full: bool = False,
        paths: list[str] | None = None,
        file_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Builds or updates the local workspace retrieval index."""
        return await index_workspace_handler(  # type: ignore[no-any-return]
            force_full=force_full,
            paths=paths,
            file_types=file_types,
        )

    @mcp.tool()
    async def search_files(
        query: str,
        mode: str = "hybrid",
        top_k: int = 10,
        file_types: list[str] | None = None,
        path_prefix: str | None = None,
    ) -> dict[str, Any]:
        """Searches indexed files by keyword, semantic intent, or both."""
        return await search_files_handler(  # type: ignore[no-any-return]
            query=query,
            mode=mode,
            top_k=top_k,
            file_types=file_types,
            path_prefix=path_prefix,
        )

    @mcp.tool()
    async def find_similar_content(
        path: str,
        start_line: int | None = None,
        end_line: int | None = None,
        top_k: int = 10,
    ) -> dict[str, Any]:
        """Finds semantically similar chunks for a file or excerpt."""
        return await find_similar_content_handler(  # type: ignore[no-any-return]
            path=path,
            start_line=start_line,
            end_line=end_line,
            top_k=top_k,
        )

    @mcp.tool()
    async def index_status() -> dict[str, Any]:
        """Returns local index health, provider, and watcher status."""
        return await index_status_handler()  # type: ignore[no-any-return]

    @mcp.tool()
    async def index_errors(limit: int = 50) -> dict[str, Any]:
        """Returns recent indexing failures and unsupported files."""
        return await index_errors_handler(limit=limit)  # type: ignore[no-any-return]
