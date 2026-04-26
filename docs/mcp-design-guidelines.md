<!-- AGENTS SUMMARY
Principles for designing MCP tools that are token-efficient, safe, and tailored for AI consumption.
Sessions:
- TOKEN-ECONOMY: Strategies for reducing context waste (summaries, excerpts, dynamic toolsets).
- SAFE-AUTOMATION: Guardrails for write operations and protected filesystem areas.
- HIGH-LEVEL-COMMANDS: Designing tools based on intent rather than raw primitives.
- TOOL-DESIGN-STANDARDS: Schema requirements, input validation, error reporting, BAD vs GOOD examples.
- RESPONSE-STANDARDS: Standardized JSON fields (summary, matches, warnings, meta).
- SEMANTIC-SEARCH: Embedding model requirements, similarity thresholds, fallback strategy.
- TOKEN-BUDGET: Concrete soft/hard caps per content type with overflow strategies.
- CACHING-STRATEGY: What to cache, TTLs, invalidation rules.
-->

# MCP Tool Design Guidelines for AI Agents

This document defines the principles for designing MCP tools that are token-efficient, safe, and easy for AI agents to
use correctly.

## Table of Contents

* [Core Philosophy](#core-philosophy)
* [Token Economy First](#token-economy-first)
* [Safe Filesystem Automation](#safe-filesystem-automation)
* [High-Level Commands Over Low-Level Access](#high-level-commands-over-low-level-access)
* [Tool Design Standards](#tool-design-standards)
* [Tool Response Standards](#tool-response-standards)
* [Semantic Search Guidelines](#semantic-search-guidelines)
* [Token Budget Thresholds](#token-budget-thresholds)
* [Caching for Token Efficiency](#caching-for-token-efficiency)
* [Token Economy Examples](#token-economy-examples)
---

<!-- START CORE-PHILOSOPHY -->
## Core Philosophy

The differentiator of mcp-experto-filesystem is intent-based filesystem intelligence. Instead of giving an agent a
dumb filesystem, we provide a project-aware layer that helps the agent decide **what matters**.

Each tool must earn its place by reducing the total tokens an agent needs to reason about the filesystem - not by
exposing more raw primitives.
<!-- END CORE-PHILOSOPHY -->

---

<!-- START TOKEN-ECONOMY -->
## Token Economy First

Every feature must reduce unnecessary context usage.

**Prefer:**

* Summaries over full file content.
* Excerpts/snippets over complete files.
* Structured metadata over raw logs.
* File maps over recursive dumps.
* Cached analysis over repeated scanning.
* Semantic retrieval over brute-force reading.
* Dynamic toolsets when the runtime supports them cleanly. In the current implementation, prefer compact
  runtime help over a custom discovery layer.

**Avoid:**

* Returning entire repositories.
* Returning full logs by default.
* Reading dependency folders (`.venv`, `node_modules`).
* Loading large generated or binary files.
* Sending all tool descriptions to the LLM at once (can cost 5,000-10,000 tokens for 20+ tools).
<!-- END TOKEN-ECONOMY -->

---

<!-- START SAFE-AUTOMATION -->
## Safe Filesystem Automation

The project treats the user's repository as valuable data. Default behavior must be read-only.

**Write operations must be:**

* **Narrow:** Change only what is necessary.
* **Reversible:** Use backups or git-friendly patterns.
* **Explainable:** Provide a dry-run or a summary of changes before applying.
* **Validated:** Check paths and safety rules before writing.

**Dangerous operations requiring explicit intent:**

* Recursive deletes or bulk renames.
* Editing secrets or `.env` files.
* Changing dependency versions.
* Deleting tests or validation logic.
<!-- END SAFE-AUTOMATION -->

---

<!-- START HIGH-LEVEL-COMMANDS -->
## High-Level Commands Over Low-Level Access

Avoid forcing agents to combine dozens of low-level `read_file` and `list_dir` calls.

**Preferred Tooling Pattern:**

* `project_overview` instead of listing every directory.
* `find_relevant_files` instead of manual searching.
* `read_file_excerpt` instead of reading 2000 lines.
* `apply_patch` instead of overwriting the whole file.

These examples describe the intended tooling direction. Some capabilities may still be exposed as POC placeholders
until their underlying implementation is delivered.
<!-- END HIGH-LEVEL-COMMANDS -->

---

<!-- START TOOL-DESIGN-STANDARDS -->
## Tool Design Standards

References: [MCP Tools Spec](https://modelcontextprotocol.io/specification/2025-06-18/server/tools),
[MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/),
[15 Production Best Practices](https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/)

### Single Responsibility

Each tool must do exactly one thing. Tools that combine read + search + summarize in a single call
are forbidden. One tool, one action, one output schema.

### Schema Requirements

* Every parameter must have a `type`, `description`, and explicit `required` declaration.
* Use `enum` whenever the set of valid values is finite.
* Annotate with `format` when applicable (e.g., `"format": "path"`, `"format": "regex"`).
* Output must conform to a declared JSON schema; the server validates before returning.
* Tool descriptions must be under 200 tokens. In the current architecture, rely on `FastMCP` tool metadata and
  project-authored help payloads rather than a custom registry.

### Input Validation Rules

* Validate all inputs at the tool boundary before any I/O.
* Sanitize file paths: reject `..`, symlinks pointing outside the project root, and absolute paths
  from untrusted callers.
* Reject oversized inputs early: define a `max_bytes` or `max_chars` limit per tool.
* For shell-adjacent operations: use an allowlist of permitted operations, never a blocklist.
* Agents and tool callers must never infer undocumented parameters or capabilities by pattern matching.
* If a tool is documented as a POC placeholder, that placeholder status is the source of truth until the
  implementation changes.

### Error Reporting

* Tool errors MUST be reported inside the result object (not as MCP protocol-level errors).
  This allows the LLM to see and react to the error rather than receiving an opaque failure.
* Every error must include: `error_code` (machine-readable), `message` (human-readable),
  `category` (CLIENT_ERROR / SERVER_ERROR / EXTERNAL_ERROR), and `retryable` (bool).
* Never leak stack traces, internal paths, or environment variable names in error messages.
* If a tool exceeds its hard performance limit, it should return a structured server-side error with
  `retryable: true` and guidance in `next_steps` to reduce scope.

### BAD vs GOOD Tool Design

**BAD** - Low-level, raw, forces the LLM to reason about bytes:

```text
read_file(path: str) -> str   # returns the entire file as a raw string
```

**GOOD** - High-level, intent-aware, token-efficient:

```text
read_file_excerpt(path, query, max_tokens=800) -> {summary, excerpt, line_range, warnings}
```

If the implementation is not ready yet, the tool must explicitly report that limitation. It must never return
fabricated file content.

**BAD** - Overly broad, no schema, no safety:

```text
run_command(cmd: str) -> str   # returns raw stdout
```

**GOOD** - Scoped, validated, returns structured data:

```text
search_in_file(path, pattern, context_lines=3) -> {matches: [{line, content, context}]}
```
<!-- END TOOL-DESIGN-STANDARDS -->

---

<!-- START RESPONSE-STANDARDS -->
## Tool Response Standards

All MCP tool outputs must be designed for language models. Use predictable, structured JSON.

### Required Fields

* **summary:** A concise description of the result (max 200 tokens).
* **items / files / matches:** The primary data requested.
* **warnings:** Information about skipped files or risks.
* **next_steps:** Suggested follow-up actions for the agent.
* **metadata:** Technical context (e.g., token-saving strategies applied).

The current runtime also wraps every tool response in the project-wide MCP envelope:
`status`, `message`, `data`, `error`, `meta`, and `metrics`.

### Example Response Shape

```json
{
  "summary": "Found 3 files related to authentication.",
  "files": [
    {
      "path": "src/auth.py",
      "reason": "Contains the main login function.",
      "line_range": { "start": 10, "end": 50 }
    }
  ],
  "warnings": [
    { "type": "large_file_skipped", "message": "auth.log was skipped (> 1 MB)." }
  ],
  "next_steps": ["Read src/auth.py excerpts to understand the flow."]
}
```
<!-- END RESPONSE-STANDARDS -->

---

<!-- START SEMANTIC-SEARCH -->
## Semantic Search Guidelines

Semantic search helps agents find concepts instead of just keywords.

### Embedding Model Requirements

* Minimum: a model that produces 384-dimensional vectors (e.g., `all-MiniLM-L6-v2`).
* Preferred: 768-d+ model trained on code (e.g., `code-search-net` family).
* Embeddings must be stored locally; no external API calls for indexing private code.
* Re-embed a file when its `mtime` changes; use a content hash to detect no-op saves.

### Similarity Score Thresholds

| Score Range | Action |
| :--- | :--- |
| >= 0.75 | Return as high-confidence match |
| 0.50 - 0.74 | Return as candidate with a warning in the response |
| < 0.50 | Do not return; trigger fallback strategy |

### Fallback Strategy

When no result exceeds the minimum threshold:

1. Fall back to keyword (BM25) search on the same corpus.
2. If keyword also yields nothing, return an empty `matches` list with `next_steps` suggesting the
   caller broaden the query or verify index freshness.
3. Never fabricate results or return low-confidence matches without flagging them in `warnings`.

### Result Ranking

* Return a maximum of 5 results per semantic query by default (configurable, hard max: 20).
* Each result must include: file path, matched snippet (max 3 lines), similarity score, line range.
* Full file content is never returned from a search tool; use `read_file_excerpt` for that.
* Do not index: `.git/`, `.venv/`, binary files, files matching the ignore list.
<!-- END SEMANTIC-SEARCH -->

---

<!-- START TOKEN-BUDGET -->
## Token Budget Thresholds

| Content Type | Soft Cap | Hard Cap | Overflow Strategy |
| :--- | :--- | :--- | :--- |
| Tool description (for LLM discovery) | 100 tokens | 200 tokens | Truncate with `...` |
| Tool summary field | 200 tokens | 400 tokens | Truncate with `...` |
| File excerpt | 800 tokens | 2000 tokens | Paginate via `offset` param |
| Full file read | 2000 tokens | 8000 tokens | Require explicit `full=true` flag |
| Search results list | 1500 tokens | 4000 tokens | Reduce `max_results` |
| Complete tool response | 2000 tokens | 8000 tokens | Split into pages |

All responses include `approx_output_tokens` in the `metrics` block so the caller can adjust
the scope of the next request.
<!-- END TOKEN-BUDGET -->

---

<!-- START CACHING-STRATEGY -->
## Caching for Token Efficiency

The table below separates implemented caching from planned caching. Only `get_help()` payload
caching (server lifetime TTL) is active in the current runtime. All other entries describe the
target architecture and are not yet implemented.

### What to Cache

| Resource | TTL | Invalidation Trigger |
| :--- | :--- | :--- |
| Directory listings | 30 s | Any write in that directory |
| File content hash | filesystem `mtime` | File `mtime` changed |
| File summary | file content hash | Hash changed |
| Semantic embeddings | file content hash | Hash changed |
| `get_help()` runtime help payload | server lifetime | Server restart |

### What NOT to Cache

* Security-sensitive operations (path validation, permission checks).
* Results of write operations.
* Any result where the tool specifies `"cache": false`.

### Stale Cache Behavior

* Never return stale content silently when correctness is critical.
* If the cache is stale and re-computation would exceed a time budget, return the stale result
  with a `warning` field noting the staleness and the age of the cache entry.
* Future metadata layers should complement the `FastMCP` composition model instead of replacing it with a
  parallel runtime registry.
<!-- END CACHING-STRATEGY -->

---

<!-- START TOKEN-ECONOMY-EXAMPLES -->
## Token Economy Examples

### Context Loading

* **Bad:** Read the entire repository and return all files.
* **Good:** Return a compact project map and read only the necessary excerpts on demand.

### File Reading

* **Bad:** Return a 2,000-line file because one function may be relevant.
* **Good:** Return the target function, its direct imports, and a 3-line context window.

### Command Output

* **Bad:** Run tests and paste the full 500-line raw output into the context.
* **Good:** Summarize results, include failing test names and error excerpts only.

### Tool Discovery

* **Bad:** Load all 20+ tool descriptions into every LLM request (5,000-10,000 tokens overhead).
* **Good:** Use semantic tool discovery when the capability exists, or otherwise use compact runtime help and
  load only the tool details needed for the current request.
<!-- END TOKEN-ECONOMY-EXAMPLES -->

