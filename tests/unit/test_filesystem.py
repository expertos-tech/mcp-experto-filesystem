import zipfile

import pytest

from server import config
from server.application.services import workspace_index
from server.tools.filesystem import (
    find_similar_content_handler,
    index_errors_handler,
    index_status_handler,
    index_workspace_handler,
    project_overview_handler,
    read_document_excerpt_handler,
    read_file_excerpt_handler,
    search_files_handler,
)


@pytest.fixture()
def workspace_root(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "src").mkdir()
    (root / "docs").mkdir()
    (root / ".git").mkdir()
    monkeypatch.setattr(config.settings, "project_root", str(root))
    monkeypatch.setattr(config.settings, "enable_index_watcher", False)
    monkeypatch.setattr(config.settings, "embedding_provider", "hashing")
    workspace_index._workspace_service = None
    return root


def _write_basic_docx(path, text):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "word/document.xml",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                f"<w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body></w:document>"
            ),
        )


@pytest.mark.asyncio
async def test_project_overview_returns_real_tree(workspace_root):
    (workspace_root / "README.md").write_text("# Title\n", encoding="utf-8")
    (workspace_root / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")

    response = await project_overview_handler(max_depth=3)

    assert response["status"] == 200
    assert response["data"]["max_depth"] == 3
    assert any(node["path"] == "README.md" for node in response["data"]["tree"])
    assert response["data"]["counts"]["indexed_candidate_files"] >= 2


@pytest.mark.asyncio
async def test_read_file_excerpt_returns_content(workspace_root):
    (workspace_root / "README.md").write_text("line1\nline2\nline3\nline4\n", encoding="utf-8")

    response = await read_file_excerpt_handler(path="README.md", start_line=2, end_line=3)

    assert response["status"] == 200
    assert response["data"]["requested_range"] == {"start_line": 2, "end_line": 3}
    assert response["data"]["content"] == "line2\nline3"


@pytest.mark.asyncio
async def test_read_file_excerpt_blocks_traversal(workspace_root):
    response = await read_file_excerpt_handler(path="../secret.txt")

    assert response["status"] == 403
    assert response["error"]["error_code"] == "PATH_SECURITY_ERROR"


@pytest.mark.asyncio
async def test_read_document_excerpt_supports_docx(workspace_root):
    _write_basic_docx(workspace_root / "docs" / "guide.docx", "hello document")

    response = await read_document_excerpt_handler(path="docs/guide.docx")

    assert response["status"] == 200
    assert response["data"]["file_kind"] == "docx"
    assert response["data"]["returned_items"][0]["content"] == "hello document"


@pytest.mark.asyncio
async def test_index_workspace_and_search_files(workspace_root):
    (workspace_root / "src" / "auth.py").write_text(
        "def authenticate_user():\n    return 'ok'\n",
        encoding="utf-8",
    )
    (workspace_root / "docs" / "auth.md").write_text(
        "Authentication flow and token refresh.\n",
        encoding="utf-8",
    )

    index_response = await index_workspace_handler()
    search_response = await search_files_handler(query="authenticate_user", mode="keyword")

    assert index_response["status"] == 200
    assert index_response["data"]["indexed_count"] >= 2
    assert search_response["status"] == 200
    assert search_response["data"]["matches"][0]["path"] == "src/auth.py"


@pytest.mark.asyncio
async def test_search_files_hybrid_works_with_fallback_provider(workspace_root):
    (workspace_root / "docs" / "billing.md").write_text(
        "The billing workflow validates invoices and payment status.\n",
        encoding="utf-8",
    )

    await index_workspace_handler()
    response = await search_files_handler(query="billing workflow", mode="hybrid")

    assert response["status"] == 200
    assert response["data"]["matches"]
    assert response["data"]["embedding_provider"]


@pytest.mark.asyncio
async def test_find_similar_content_returns_related_match(workspace_root):
    (workspace_root / "src" / "payments.py").write_text(
        "def process_invoice():\n    return 'paid'\n",
        encoding="utf-8",
    )
    (workspace_root / "src" / "billing.py").write_text(
        "def invoice_payment_status():\n    return 'paid'\n",
        encoding="utf-8",
    )

    await index_workspace_handler()
    response = await find_similar_content_handler(path="src/payments.py")

    assert response["status"] == 200
    assert any(match["path"] == "src/billing.py" for match in response["data"]["matches"])


@pytest.mark.asyncio
async def test_index_status_reports_database(workspace_root):
    (workspace_root / "README.md").write_text("hello\n", encoding="utf-8")
    await index_workspace_handler()

    response = await index_status_handler()

    assert response["status"] == 200
    assert response["data"]["database_path"].endswith("index.db")
    assert response["data"]["document_count"] >= 1


@pytest.mark.asyncio
async def test_index_errors_reports_failed_pdf_extraction(workspace_root):
    (workspace_root / "docs" / "scan.pdf").write_bytes(b"%PDF-1.4 fake pdf")

    await index_workspace_handler()
    response = await index_errors_handler()

    assert response["status"] == 200
    assert any(error["path"] == "docs/scan.pdf" for error in response["data"]["errors"])
