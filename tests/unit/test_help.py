import pytest
from fastmcp import FastMCP

from server.tools.help import get_help_handler


@pytest.mark.asyncio
async def test_get_help_no_args():
    mcp = FastMCP("test")

    @mcp.tool()
    def dummy():
        pass

    response = await get_help_handler(topic=None, mcp=mcp)
    assert "Getting Started" in response["data"]["title"]
    assert response["data"]["architecture"].startswith("FastMCP-based")
    assert any(t["name"] == "dummy" for t in response["data"]["available_tools"])


@pytest.mark.asyncio
async def test_get_help_standards():
    mcp = FastMCP("test")
    response = await get_help_handler(topic="standards", mcp=mcp)
    assert "Universal Response Payload" in response["data"]["title"]
    assert response["data"]["schema_info"]["fields"] == [
        "status",
        "message",
        "data",
        "error",
        "meta",
        "metrics",
    ]


@pytest.mark.asyncio
async def test_get_help_specific_tool():
    mcp = FastMCP("test")

    @mcp.tool()
    def my_tool():
        """Special tool."""
        pass

    response = await get_help_handler(topic="my_tool", mcp=mcp)
    assert response["data"]["tool"] == "my_tool"
    assert response["data"]["description"] == "Special tool."
    assert response["data"]["implementation_status"] == "implemented"


@pytest.mark.asyncio
async def test_get_help_unknown():
    mcp = FastMCP("test")
    response = await get_help_handler(topic="missing", mcp=mcp)
    assert response["status"] == 400
    assert "Unknown topic" in response["error"]["message"]


@pytest.mark.asyncio
async def test_get_help_no_mcp():
    response = await get_help_handler(topic=None, mcp=None)
    assert response["status"] == 500
    assert response["data"] is None
    assert response["error"]["error_code"] == "TOOL_EXECUTION_ERROR"
