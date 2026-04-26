from typing import Any

from fastmcp import FastMCP

from server.application.services.executor import universal_response
from server.exceptions import ToolExecutionError, ValidationError

POC_TOOL_NAMES = {"project_overview", "read_file_excerpt"}


def _extract_tool_input_schema(tool: Any) -> dict[str, Any] | None:
    """Return the FastMCP tool input schema when available."""
    schema = getattr(tool, "inputSchema", None)
    if schema is None:
        schema = getattr(tool, "input_schema", None)
    return schema if isinstance(schema, dict) else None


def _tool_status(tool_name: str) -> str:
    """Return the documented implementation status for a tool."""
    if tool_name in POC_TOOL_NAMES:
        return "poc_placeholder"
    return "implemented"


@universal_response
async def get_help_handler(topic: str | None = None, mcp: Any = None) -> dict[str, Any]:
    """Return runtime-aware help for the MCP server and its registered tools."""
    if mcp is None:
        raise ToolExecutionError(
            "FastMCP instance not provided to help handler.",
            operation="get_help",
        )

    tools = await mcp.list_tools()
    available_tools = [
        {
            "name": t.name,
            "description": t.description,
            "implementation_status": _tool_status(t.name),
        }
        for t in tools
    ]

    if topic is None:
        return {
            "title": "mcp-experto-filesystem - Getting Started",
            "architecture": "FastMCP-based MCP server with a universal response decorator.",
            "available_tools": available_tools,
            "response_contract": {
                "success": "status 200-299 with data populated and error set to null.",
                "error": "status 400-599 with data set to null and error populated.",
            },
            "usage": "Call 'get_help(topic=\"[Tool Name]\")' for per-tool details.",
        }

    if topic.lower() == "standards":
        return {
            "title": "Universal Response Payload Standards",
            "schema_info": {
                "fields": ["status", "message", "data", "error", "meta", "metrics"],
                "error_rule": "Errors must return data as null and populate the error object.",
            },
        }

    match = next((t for t in tools if t.name == topic), None)
    if match:
        return {
            "tool": match.name,
            "description": match.description,
            "implementation_status": _tool_status(match.name),
            "input_schema": _extract_tool_input_schema(match),
            "notes": (
                "This tool is currently exposed as a POC placeholder."
                if match.name in POC_TOOL_NAMES
                else "This tool is implemented in the current FastMCP runtime."
            ),
        }

    raise ValidationError(f"Unknown topic: '{topic}'")


def register_help_tool(mcp: FastMCP) -> None:
    """Register the help tool."""

    @mcp.tool()
    async def get_help(topic: str | None = None) -> dict[str, Any]:
        """Returns documentation for the MCP server and its tools."""
        return await get_help_handler(topic=topic, mcp=mcp)  # type: ignore[no-any-return]
