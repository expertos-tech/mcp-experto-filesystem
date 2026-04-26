import functools
import inspect
import json
import logging
import time
from collections.abc import Callable
from typing import Any

from server.exceptions import MCPError, PathSecurityError, ToolExecutionError, ValidationError
from server.share.responses import MCPErrorDetail, MCPMetrics, MCPResponse

logger = logging.getLogger(__name__)


def universal_response(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that wraps any tool handler in the Universal Response Contract."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        start = time.perf_counter()
        # Estimate input size safely
        try:
            input_bytes = len(json.dumps(kwargs, default=str).encode())
        except Exception:
            input_bytes = 0
        input_tokens = input_bytes // 4

        status, message, data, error = 200, "Success", None, None

        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                data = await result
            else:
                data = result
        except ValidationError as exc:
            status, message = 400, "Validation Error"
            logger.warning("Validation error in tool handler %s", func.__name__, exc_info=exc)
            error = MCPErrorDetail(
                error_code="VALIDATION_ERROR",
                message=str(exc),
                category="CLIENT_ERROR",
                context={"input_fields": sorted(kwargs.keys())},
            )
        except PathSecurityError as exc:
            status, message = 403, "Security Violation"
            logger.warning("Path security error in tool handler %s", func.__name__, exc_info=exc)
            error = MCPErrorDetail(
                error_code="PATH_SECURITY_ERROR",
                message=str(exc),
                category="CLIENT_ERROR",
            )
        except ToolExecutionError as exc:
            status, message = 500, "Tool Execution Failed"
            logger.error("Tool execution error in tool handler %s", func.__name__, exc_info=exc)
            error = MCPErrorDetail(
                error_code="TOOL_EXECUTION_ERROR",
                message=str(exc),
                category="SERVER_ERROR",
                context={"operation": exc.operation, "path": exc.path},
            )
        except MCPError as exc:
            status, message = 500, "Internal Server Error"
            logger.error("Unhandled MCP error in tool handler %s", func.__name__, exc_info=exc)
            error = MCPErrorDetail(
                error_code="INTERNAL_ERROR",
                message=str(exc),
                category="SERVER_ERROR",
            )
        except Exception as exc:
            status, message = 500, "Unexpected Error"
            logger.error("Unexpected error in tool handler %s", func.__name__, exc_info=exc)
            error = MCPErrorDetail(
                error_code="UNEXPECTED_ERROR",
                message="An unexpected error occurred.",
                category="SERVER_ERROR",
            )

        elapsed = (time.perf_counter() - start) * 1000
        
        # Estimate output size safely
        try:
            output_bytes = len(json.dumps(data, default=str).encode()) if data else 0
        except Exception:
            output_bytes = 0

        return MCPResponse(
            status=status,
            message=message,
            data=data if error is None else None,
            error=error,
            metrics=MCPMetrics(
                execution_time_ms=round(elapsed, 2),
                approx_input_tokens=input_tokens,
                approx_output_tokens=output_bytes // 4,
                input_bytes=input_bytes,
                output_bytes=output_bytes,
            ),
        ).model_dump()

    return wrapper
