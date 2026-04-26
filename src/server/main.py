"""MCP server startup via FastMCP."""

import logging
from pathlib import Path

from fastmcp import FastMCP

from server.tools.filesystem import register_filesystem_tools
from server.tools.help import register_help_tool

logger = logging.getLogger(__name__)
DOCS_DIR = Path(__file__).parent / "docs"


def load_server_instructions() -> str:
    """Load onboarding guidance for the MCP lifecycle initialize response."""
    return (DOCS_DIR / "server_instructions.md").read_text(encoding="utf-8")


mcp = FastMCP(
    name="mcp-experto-filesystem",
    instructions=load_server_instructions(),
)

# Register tool groups
register_help_tool(mcp)
register_filesystem_tools(mcp)


def run() -> None:
    """Entrypoint to start the server."""
    logging.basicConfig(level="INFO")
    logger.info("mcp-experto-filesystem (FastMCP) starting...")
    mcp.run()
