"""MCP server startup via stdio transport."""

import logging

logger = logging.getLogger(__name__)


def run() -> None:
    """Start the MCP server on stdio."""
    logging.basicConfig(level="INFO")
    logger.info("mcp-experto-filesystem starting...")
    # TODO: initialize MCP server, register tools, start stdio transport
