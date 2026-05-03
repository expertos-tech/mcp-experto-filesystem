<!-- AGENTS SUMMARY
Architectural boundaries, communication protocols, and standardized contracts for the MCP server.
Sessions:
- TLDR: Fast summary of the architectural contract.
- PROTOCOL-DISTRIBUTION: Rules for stdio usage and local security.
- INITIALIZATION-DISCOVERY: How the server handles the initialize hook and self-discovery tools.
- TOOL-REGISTRATION: How tools are registered, discovered, and exposed via the initialize hook.
- STANDARD-PAYLOAD: Schema and field definitions for the Universal Response Payload.
- ERROR-PAYLOAD: Schema and field definitions for error responses (status >= 400).
- PERFORMANCE-SLAS: Latency targets per tool class.
- DESIGN-PHILOSOPHY: Rationale behind the structured communication approach.
-->

# System Architecture and Protocol Contracts

## Table of Contents

* [Protocol and Distribution](#protocol-and-distribution)
* [Initialization and Self-Discovery](#initialization-and-self-discovery)
* [Tool Registration Flow](#tool-registration-flow)
* [Standard Response Payload (The Universal Contract)](#standard-response-payload-the-universal-contract)
* [Error Response Schema](#error-response-schema)
* [Performance SLAs](#performance-slas)
* [Design Philosophy](#design-philosophy)

---

<!-- START TLDR -->
## TL;DR

* The MCP server is designed for local stdio execution, FastMCP-based tool exposure, and a shared structured response envelope.
* This document defines the response contract, initialization flow, and performance expectations for the server.
* Use it whenever you change tool behavior, runtime composition, or payload structure.
<!-- END TLDR -->

---

<!-- START PROTOCOL-DISTRIBUTION -->
## 1. Protocol and Distribution

### 1.1 Local Execution via stdio

Given its nature as a filesystem automation tool, the MCP server must always operate via stdio.
This ensures:

* **Security:** No network ports are opened on the host machine.
* **Locality:** The agent executing the commands runs in the same environment as the codebase.
* **Simplicity:** No complex authentication or network routing is required.
<!-- END PROTOCOL-DISTRIBUTION -->

---

<!-- START INITIALIZATION-DISCOVERY -->
## 2. Initialization and Self-Discovery

To prevent LLMs from guessing how to use the server, the system provides self-discovery mechanisms that
fit the current `FastMCP` runtime.

### 2.1 FastMCP Initialization

The current server delegates MCP lifecycle management and tool exposure to `FastMCP`.

On startup:

* `src/server/main.py` creates a shared `FastMCP("mcp-experto-filesystem")` instance.
* The server loads `src/server/docs/server_instructions.md` and passes it to the FastMCP
  `instructions` parameter.
* Tool modules register themselves against that shared application instance.
* MCP clients discover tools through the standard MCP tool listing flow exposed by `FastMCP`.

The MCP lifecycle `initialize` response now carries lightweight onboarding instructions through
FastMCP's native `instructions` field. Richer runtime guidance remains available through `get_help()`.

### 2.2 The get_help Tool

A dedicated `get_help` tool provides runtime-aware documentation without introducing a separate
registry. It reads markdown files from `src/server/docs/` to serve tool help on demand,
keeping documentation co-located with the code and eliminating drift between docs and runtime.
<!-- END INITIALIZATION-DISCOVERY -->

---

<!-- START TOOL-REGISTRATION -->
## 3. Tool Registration Flow

### 3.1 Current FastMCP Composition Model

Tools are registered directly with the shared `FastMCP` instance through `@mcp.tool()`.
The current architecture separates runtime registration from handler logic:

| Layer | Responsibility |
| :--- | :--- |
| `src/server/main.py` | Creates the shared `FastMCP` application and composes tool groups |
| `src/server/tools/*.py` | Declares MCP tool functions and binds them to handlers |
| `src/server/application/services/executor.py` | Applies the Universal Response contract through a decorator |
| `src/server/share/responses.py` | Defines the shared response payload models |

### 3.2 Registration Lifecycle

1. `main.py` creates a single `FastMCP("mcp-experto-filesystem")` instance.
2. Each tool module exports a registration function such as `register_help_tool(mcp)`.
3. Registration functions declare public MCP tools with `@mcp.tool()`.
4. Each public tool delegates to a handler that is already wrapped by the universal response decorator.

### 3.3 Tool Discovery by Agents

Agents discover tools through:

1. The MCP tool listing exposed by the `FastMCP` runtime.
2. `get_help()` queries for current runtime details and project-specific implementation notes.

### 3.4 Future Metadata Expansion

Richer metadata such as read-only flags, curated examples, or capability tiers may be added later.
If introduced, that metadata must complement the `FastMCP` composition model.
<!-- END TOOL-REGISTRATION -->

---

<!-- START STANDARD-PAYLOAD -->
## 4. Standard Response Payload (The Universal Contract)

Every tool exposed by this MCP server must return a strictly typed JSON response. This ensures the AI agent
can parse responses predictably, regardless of the tool used.

### 4.1 Success Payload Schema (status 200-299)

```json
{
  "status": 200,
  "message": "Operation completed successfully.",
  "data": {},
  "error": null,
  "meta": {
    "warnings": [],
    "next_steps": []
  },
  "metrics": {
    "execution_time_ms": 120.5,
    "approx_input_tokens": 45,
    "approx_output_tokens": 300,
    "input_bytes": 150,
    "output_bytes": 1200
  }
}
```

### 4.2 Field Definitions

* **status (integer):** HTTP-like status codes (200, 400, 403, 404, 500).
* **message (string):** A brief, human-readable summary of the operation result.
* **data (object | array):** The actual tool payload. Must be `null` when status >= 400.
* **error (object | null):** Present only when status >= 400. Contains structured failure details.
* **meta (object):** Contains `warnings` (non-fatal issues) and `next_steps` (agent guidance).
* **metrics (object):** Telemetry data to monitor token economy and performance.

In the current implementation, tool-specific content lives inside `data`, while the outer MCP envelope is produced
by the universal response decorator.
<!-- END STANDARD-PAYLOAD -->

---

<!-- START ERROR-PAYLOAD -->
## 5. Error Response Schema

When a tool fails, `data` must be `null` and `error` must be populated. This allows the LLM to see
and react to failure details rather than receiving an opaque empty response.

### 5.1 Error Payload Schema (status 400-599)

```json
{
  "status": 404,
  "message": "Target path not found.",
  "data": null,
  "error": {
    "error_code": "PATH_NOT_FOUND",
    "message": "The path 'src/missing.py' does not exist under the project root.",
    "category": "CLIENT_ERROR",
    "retryable": false,
    "context": {
      "path": "src/missing.py",
      "operation": "read_file_excerpt"
    }
  },
  "meta": {
    "warnings": [],
    "next_steps": [
      "Use project_overview to list available files.",
      "Check spelling of the path and retry."
    ]
  },
  "metrics": {
    "execution_time_ms": 3.2,
    "approx_input_tokens": 20,
    "approx_output_tokens": 80,
    "input_bytes": 40,
    "output_bytes": 320
  }
}
```

### 5.2 Error Field Definitions

* **error_code (string):** Machine-readable identifier. Use `UPPER_SNAKE_CASE`.
* **message (string):** Human-readable description of the failure.
* **category (string):** One of `CLIENT_ERROR`, `SERVER_ERROR`, or `EXTERNAL_ERROR`.
* **retryable (bool):** `true` if the same request may succeed after a transient condition clears.
* **context (object):** Optional key-value pairs relevant to the failure (path, operation, value).

### 5.3 Status Code Mapping

| Status | Category | When to Use |
| :--- | :--- | :--- |
| 400 | CLIENT_ERROR | Bad input, schema validation failure |
| 403 | CLIENT_ERROR | Path security violation (traversal attempt) |
| 404 | CLIENT_ERROR | File or resource not found |
| 422 | CLIENT_ERROR | Semantically invalid input (e.g., directory passed where file expected) |
| 500 | SERVER_ERROR | Unexpected internal failure |
| 503 | EXTERNAL_ERROR | Filesystem, subprocess, or index unavailable |
<!-- END ERROR-PAYLOAD -->

---

<!-- START PERFORMANCE-SLAS -->
## 6. Performance SLAs

| Tool Class | Target Latency | Hard Limit |
| :--- | :--- | :--- |
| File read (up to 1 MB) | < 200 ms | 500 ms |
| Directory traversal (up to 1000 files) | < 500 ms | 2 s |
| Semantic search query | < 1 s | 3 s |
| Write / patch operations | < 300 ms | 1 s |
| get_help() | < 10 ms | 50 ms |

* All tools must include `execution_time_ms` in the `metrics` block.

Caching of help payloads is a future optimization, not a current implementation detail.
<!-- END PERFORMANCE-SLAS -->

---

<!-- START DESIGN-PHILOSOPHY -->
## 7. Design Philosophy

By routing all tools through the Universal Contract, we ensure that:

1. The LLM never has to parse unstructured text dumps.
2. Token consumption is transparent and observable via `metrics`.
3. Errors carry enough context for the agent to self-correct without human intervention.
4. Performance is measurable and enforceable without external instrumentation.
<!-- END DESIGN-PHILOSOPHY -->
