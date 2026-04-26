"""Domain-specific exception hierarchy for mcp-experto-filesystem."""


class MCPError(Exception):
    """Base exception for all mcp-experto-filesystem errors."""


class ValidationError(MCPError):
    """Raised when caller input fails schema or semantic validation."""


class PathSecurityError(MCPError):
    """Raised when a path escapes the allowed project root."""


class ToolExecutionError(MCPError):
    """Raised when a tool fails at runtime."""

    def __init__(self, message: str, *, operation: str = "", path: str = "") -> None:
        super().__init__(message)
        self.operation = operation
        self.path = path


class ConfigurationError(MCPError):
    """Raised when server or environment configuration is invalid."""
