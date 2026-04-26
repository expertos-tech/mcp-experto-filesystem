from typing import Any

from fastmcp import FastMCP

from server.application.services.executor import universal_response


@universal_response
async def project_overview_handler(max_depth: int = 3) -> dict[str, Any]:
    """Return the current POC status for project_overview."""
    return {
        "summary": "project_overview is currently exposed as a FastMCP POC placeholder.",
        "implementation_status": "poc_placeholder",
        "requested_max_depth": max_depth,
        "notes": [
            "Repository traversal is not implemented yet.",
            (
                "This response is intentionally non-fabricated and does not claim "
                "to inspect the filesystem."
            ),
        ],
    }


@universal_response
async def read_file_excerpt_handler(
    path: str, start_line: int = 1, end_line: int = 50
) -> dict[str, Any]:
    """Return the current POC status for read_file_excerpt."""
    return {
        "summary": "read_file_excerpt is currently exposed as a FastMCP POC placeholder.",
        "implementation_status": "poc_placeholder",
        "path": path,
        "requested_range": {"start_line": start_line, "end_line": end_line},
        "notes": [
            "File reading is not implemented yet.",
            "This response intentionally does not return fabricated file content.",
        ],
    }


def register_filesystem_tools(mcp: FastMCP) -> None:
    """Register filesystem-related POC tools."""

    @mcp.tool()
    async def project_overview(max_depth: int = 3) -> dict[str, Any]:
        """Returns a token-efficient map of the project structure."""
        return await project_overview_handler(max_depth=max_depth)  # type: ignore[no-any-return]

    @mcp.tool()
    async def read_file_excerpt(
        path: str, start_line: int = 1, end_line: int = 50
    ) -> dict[str, Any]:
        """Reads a targeted line range from a file. Never returns full files."""
        return await read_file_excerpt_handler(  # type: ignore[no-any-return]
            path=path, start_line=start_line, end_line=end_line
        )
