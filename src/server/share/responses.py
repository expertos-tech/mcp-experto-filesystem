"""Universal Response Payload models - the MCP contract."""

from typing import Any

from pydantic import BaseModel, Field


class MCPMetrics(BaseModel):
    execution_time_ms: float = 0.0
    approx_input_tokens: int = 0
    approx_output_tokens: int = 0
    input_bytes: int = 0
    output_bytes: int = 0


class MCPMeta(BaseModel):
    warnings: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class MCPErrorDetail(BaseModel):
    error_code: str
    message: str
    category: str  # CLIENT_ERROR | SERVER_ERROR | EXTERNAL_ERROR
    retryable: bool = False
    context: dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    status: int
    message: str
    data: Any = None
    error: MCPErrorDetail | None = None
    meta: MCPMeta = Field(default_factory=MCPMeta)
    metrics: MCPMetrics = Field(default_factory=MCPMetrics)
