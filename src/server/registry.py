"""Tool registry: declarative registration and discovery."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from server.exceptions import ConfigurationError


@dataclass
class ToolEntry:
    name: str
    description: str
    handler: Callable[..., Any]
    read_only: bool = True


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolEntry] = {}

    def register(
        self,
        *,
        name: str,
        description: str,
        handler: Callable[..., Any],
        read_only: bool = True,
    ) -> None:
        if name in self._tools:
            raise ConfigurationError(f"Duplicate tool name: '{name}'")
        self._tools[name] = ToolEntry(
            name=name, description=description, handler=handler, read_only=read_only
        )

    def all_tools(self) -> list[ToolEntry]:
        return list(self._tools.values())

    def get(self, name: str) -> ToolEntry:
        if name not in self._tools:
            raise ConfigurationError(f"Unknown tool: '{name}'")
        return self._tools[name]


tool_registry = ToolRegistry()
