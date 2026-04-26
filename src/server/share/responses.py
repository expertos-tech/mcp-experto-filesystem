"""Universal Response Payload models - the MCP contract."""

from typing import Any

from pydantic import BaseModel


class MCPMetrics(BaseModel):
    execution_time_ms: float = 0.0
    approx_input_tokens: int = 0
    approx_output_tokens: int = 0
    input_bytes: int = 0
    output_bytes: int = 0


class MCPMeta(BaseModel):
    warnings: list[str] = []
    next_steps: list[str] = []


class MCPErrorDetail(BaseModel):
    error_code: str
    message: str
    category: str  # CLIENT_ERROR | SERVER_ERROR | EXTERNAL_ERROR
    retryable: bool = False
    context: dict[str, Any] = {}


class MCPResponse(BaseModel):
    status: int
    message: str
    data: Any = None
    error: MCPErrorDetail | None = None
    meta: MCPMeta = MCPMeta()
    metrics: MCPMetrics = MCPMetrics()
