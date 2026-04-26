import pytest

from server.tools.filesystem import project_overview_handler, read_file_excerpt_handler


@pytest.mark.asyncio
async def test_project_overview_reports_placeholder_status():
    response = await project_overview_handler(max_depth=4)
    assert response["status"] == 200
    assert response["data"]["implementation_status"] == "poc_placeholder"
    assert response["data"]["requested_max_depth"] == 4
    assert "filesystem" in response["data"]["notes"][1].lower()


@pytest.mark.asyncio
async def test_read_file_excerpt_does_not_return_fabricated_content():
    response = await read_file_excerpt_handler(path="README.md", start_line=3, end_line=9)
    assert response["status"] == 200
    assert response["data"]["implementation_status"] == "poc_placeholder"
    assert response["data"]["requested_range"] == {"start_line": 3, "end_line": 9}
    assert "content" not in response["data"]
