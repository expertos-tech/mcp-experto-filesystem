"""MCP server startup via FastMCP."""

import logging

from fastmcp import FastMCP

from server.tools.filesystem import register_filesystem_tools
from server.tools.help import register_help_tool

logger = logging.getLogger(__name__)

mcp = FastMCP("mcp-experto-filesystem")

# Register tool groups
register_help_tool(mcp)
register_filesystem_tools(mcp)


def run() -> None:
    """Entrypoint to start the server."""
    logging.basicConfig(level="INFO")
    logger.info("mcp-experto-filesystem (FastMCP) starting...")
    mcp.run()
