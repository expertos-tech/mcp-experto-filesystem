# Usage Guide

Learn how to interact with the MCP Experto Filesystem server and its specialized tools.

## Running the Server

To start the server locally:

```bash
python -m src.server
```

## Available Tools

### Filesystem Operations
- **read_file:** Read contents of a file with line-range support.
- **write_file:** Create or overwrite files.
- **replace:** Perform surgical text replacements.
- **list_directory:** List contents of a directory.
- **grep_search:** Search for patterns within files.

### Help & Documentation
- **get_help:** Retrieve information about available tools and workflows.

## Strategic Workflows

The server is designed to support a **Research -> Strategy -> Execution** lifecycle:

1. **Research:** Use `grep_search` and `list_directory` to map the codebase.
2. **Strategy:** Formulate a plan based on empirical evidence.
3. **Execution:** Apply changes using `replace` or `write_file` and validate with tests.

## Local Telemetry

If you have Docker installed, you can start the telemetry stack:

```bash
cd local-telemetry
docker-compose up -d
```
Access Grafana at `http://localhost:3000` to monitor operations.
