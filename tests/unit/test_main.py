from server.main import load_server_instructions


def test_load_server_instructions_returns_markdown_content():
    instructions = load_server_instructions()

    assert instructions.startswith("<!-- AGENTS SUMMARY")
    assert "# Server Instructions" in instructions
    assert "get_help(topic=\"standards\")" in instructions
