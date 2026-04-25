<!-- AGENTS SUMMARY
Architectural boundaries, communication protocols, and standardized contracts for the MCP server.
Sessions:
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

To prevent LLMs from guessing how to use the server, the system provides aggressive self-discovery mechanisms.

### 2.1 The initialize Hook

Upon connection, the server must return a Getting Started payload that includes:

* A brief description of every registered tool (name, purpose, required parameters).
* The standard response payload schema, so the agent knows how to parse all future responses.
* Safety rules: which operations are read-only by default, which require explicit confirmation.

### 2.2 The get_help Tool

A dedicated `get_help` tool must be exposed to allow agents to query documentation dynamically.

* **get_help()** (no arguments): Returns the full initialization documentation.
* **get_help(topic="standards")**: Returns strict instructions on how to parse the standard response payload.
* **get_help(topic="[Tool Name]")**: Returns detailed instructions for a specific tool, including its
  full input schema, output schema, and usage examples.
<!-- END INITIALIZATION-DISCOVERY -->

---

<!-- START TOOL-REGISTRATION -->
## 3. Tool Registration Flow

### 3.1 Registration Requirements

Every tool must be registered with the following fields before the server starts accepting connections:

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | Unique, snake_case identifier |
| `description` | `str` | One sentence summary for LLM discovery (max 200 tokens) |
| `input_model` | `pydantic.BaseModel` | Validated input schema |
| `output_model` | `pydantic.BaseModel` | Validated output schema |
| `handler` | `Callable` | Pure function that implements the tool logic |
| `read_only` | `bool` | Whether the tool mutates filesystem state |

### 3.2 Registration Lifecycle

1. All tools are registered at module import time via `tool_registry.register(...)`.
2. On `initialize`, the registry introspects all registered tools and builds the Getting Started payload.
3. `get_help(topic="[Tool Name]")` queries the registry at runtime; no separate documentation file is needed.
4. The registry validates that no two tools share the same `name` on startup; duplicate names raise `ConfigurationError`.

### 3.3 Tool Discovery by Agents

Agents discover tools exclusively through:

1. The `initialize` response (full list at connection time).
2. `get_help()` queries (on demand, cheaper than re-reading the full init payload).

Agents must never infer tool names or parameters by pattern-matching; they must use the registry.
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
| get_help() (cached) | < 10 ms | 50 ms |

* All tools must include `execution_time_ms` in the `metrics` block.
* Tools that exceed the hard limit must return a `SERVER_ERROR` with `retryable: true`
  and a suggestion to reduce scope in `next_steps`.
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
