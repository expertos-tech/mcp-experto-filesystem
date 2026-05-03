import pytest
from fastmcp import FastMCP

from server.tools import help as help_module
from server.tools.help import get_help_handler


@pytest.mark.asyncio
async def test_get_help_no_topic_returns_docs_and_tool_list(mocker):
    mcp = FastMCP("test")

    @mcp.tool()
    def dummy_tool():
        """Dummy tool."""

    mocker.patch.object(help_module, "_load_doc", return_value="# get_help")

    response = await get_help_handler(topic=None, mcp=mcp)

    assert response["status"] == 200
    assert response["data"]["documentation"] == "# get_help"
    assert any(
        tool["name"] == "dummy_tool"
        and tool["more_info"] == 'call get_help(topic="dummy_tool")'
        for tool in response["data"]["available_tools"]
    )


@pytest.mark.asyncio
async def test_get_help_standards_returns_schema_and_snippet():
    mcp = FastMCP("test")

    response = await get_help_handler(topic="standards", mcp=mcp)

    assert response["status"] == 200
    assert response["data"]["schema"]["status"].startswith("int")
    assert "response['status']" in response["data"]["python_parse_snippet"]


@pytest.mark.asyncio
async def test_get_help_specific_tool_returns_doc(mocker):
    mcp = FastMCP("test")
    mocker.patch.object(help_module, "_load_doc", return_value="# project_overview")

    response = await get_help_handler(topic="project_overview", mcp=mcp)

    assert response["status"] == 200
    assert response["data"]["tool"] == "project_overview"
    assert response["data"]["documentation"] == "# project_overview"
    assert response["data"]["implementation_status"] == "implemented"


@pytest.mark.asyncio
async def test_get_help_unknown_returns_validation_error(mocker):
    mcp = FastMCP("test")
    mocker.patch.object(
        help_module,
        "_load_doc",
        side_effect=help_module.ToolExecutionError("missing"),
    )

    response = await get_help_handler(topic="missing", mcp=mcp)

    assert response["status"] == 400
    assert response["error"]["error_code"] == "VALIDATION_ERROR"
    assert "Unknown topic" in response["error"]["message"]


@pytest.mark.asyncio
async def test_get_help_no_mcp_returns_tool_execution_error():
    response = await get_help_handler(topic=None, mcp=None)

    assert response["status"] == 500
    assert response["data"] is None
    assert response["error"]["error_code"] == "TOOL_EXECUTION_ERROR"
