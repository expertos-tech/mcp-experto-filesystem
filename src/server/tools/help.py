from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from server.application.services.executor import universal_response
from server.exceptions import ToolExecutionError, ValidationError

DOCS_DIR = Path(__file__).parent.parent / "docs"
POC_TOOL_NAMES: set[str] = set()


def _load_doc(doc_name: str) -> str:
    """Read a runtime markdown document by name."""
    doc_path = DOCS_DIR / f"{doc_name}.md"
    if not doc_path.is_file():
        raise ToolExecutionError(
            f"Documentation file not found: {doc_name}.md",
            operation="get_help",
            path=str(doc_path),
        )
    return doc_path.read_text(encoding="utf-8")


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

    if topic is None:
        tools = await mcp.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "implementation_status": _tool_status(tool.name),
                "more_info": f'call get_help(topic="{tool.name}")',
            }
            for tool in tools
        ]
        return {
            "documentation": _load_doc("get_help"),
            "available_tools": available_tools,
        }

    if topic.lower() == "standards":
        python_parse_snippet = "\n".join(
            [
                "import json",
                "response = json.loads(raw_json)",
                "if response['status'] >= 400:",
                "    err = response['error']",
                "    print(err['error_code'], err['message'])",
                "    if err['retryable']:",
                "        pass",
                "else:",
                "    data = response['data']",
                "    warnings = response['meta']['warnings']",
                "    exec_ms = response['metrics']['execution_time_ms']",
            ]
        )
        return {
            "title": "Universal Response Envelope",
            "schema": {
                "status": "int - HTTP-style status code (200=success, 4xx/5xx=error)",
                "message": "str - Human-readable summary",
                "data": "any | null - Tool payload on success; null on error",
                "error": {
                    "error_code": (
                        "str - VALIDATION_ERROR | PATH_SECURITY_ERROR | "
                        "TOOL_EXECUTION_ERROR | INTERNAL_ERROR | UNEXPECTED_ERROR"
                    ),
                    "message": "str - Error detail",
                    "category": "CLIENT_ERROR | SERVER_ERROR | EXTERNAL_ERROR",
                    "retryable": "bool",
                    "context": "dict - Operation-specific debug context",
                },
                "meta": {
                    "warnings": "list[str] - Non-fatal warnings",
                    "next_steps": "list[str] - Suggested follow-up actions",
                },
                "metrics": {
                    "execution_time_ms": "float",
                    "approx_input_tokens": "int",
                    "approx_output_tokens": "int",
                    "input_bytes": "int",
                    "output_bytes": "int",
                },
            },
            "python_parse_snippet": python_parse_snippet,
        }

    try:
        return {
            "tool": topic,
            "documentation": _load_doc(topic),
            "implementation_status": _tool_status(topic),
        }
    except ToolExecutionError:
        tools = await mcp.list_tools()
        match = next((tool for tool in tools if tool.name == topic), None)
        if match:
            return {
                "tool": match.name,
                "description": match.description,
                "implementation_status": _tool_status(match.name),
                "input_schema": _extract_tool_input_schema(match),
                "note": (
                    "No dedicated doc file found under src/server/docs. "
                    "Use src/server/templates/tool_help_template.md when adding one."
                ),
            }

    raise ValidationError(
        f"Unknown topic: '{topic}'. Call get_help() without arguments to see available tools."
    )


def register_help_tool(mcp: FastMCP) -> None:
    """Register the help tool."""

    @mcp.tool()
    async def get_help(topic: str | None = None) -> dict[str, Any]:
        """Returns documentation for the MCP server and its tools."""
        return await get_help_handler(topic=topic, mcp=mcp)  # type: ignore[no-any-return]
