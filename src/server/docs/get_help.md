<!-- AGENTS SUMMARY
Runtime help document for the get_help MCP tool.
Sessions:
- TLDR: Fast summary of the help tool behavior.
- OVERVIEW: What the tool does and its current implementation status.
- PARAMETERS: Input contract and supported topic values.
- RETURNS: Success payload details for each mode.
- ERRORS: Tool-specific error conditions.
- EXAMPLES: Example calls for common usage.
- NOTES: Current fallback behavior when a dedicated doc file is missing.
-->

# get_help

## Table of Contents

* [Overview](#overview)
* [Parameters](#parameters)
* [Returns](#returns)
* [Errors](#errors)
* [Examples](#examples)
* [Notes](#notes)

---

<!-- START TLDR -->
## TL;DR

* `get_help` is the main runtime documentation entrypoint for this MCP server.
* It returns server help, tool-specific docs, or the shared response standard depending on `topic`.
* Use it after initialization to inspect live capabilities without relying on guesswork.
<!-- END TLDR -->

---

<!-- START OVERVIEW -->
## Overview

Returns documentation for this MCP server and its registered tools. Use it to discover the
response contract, inspect the live tool list, and fetch full markdown docs for a specific tool
after the MCP lifecycle `initialize` step has completed.

**Status:** `implemented`
<!-- END OVERVIEW -->

---

<!-- START PARAMETERS -->
## Parameters

### Quick Reference

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `topic` | `str \| None` | No | `None` | Controls which documentation view is returned |

### Detailed Description

#### `topic`

**Type:** `str | None`  
**Required:** No  
**Default:** `None`

Supported values:

* `None` returns the `get_help` document plus the live tool list.
* `"standards"` returns the shared response-envelope schema and a Python parsing snippet.
* `"<tool_name>"` returns the dedicated markdown doc for that tool when available.

If a registered tool has no dedicated markdown file, `get_help` falls back to runtime metadata
for that tool. Any unknown value raises `VALIDATION_ERROR`.
<!-- END PARAMETERS -->

---

<!-- START RETURNS -->
## Returns

When `topic is None`, `data` contains:

```json
{
  "documentation": "str - Full markdown content of get_help.md",
  "available_tools": [
    {
      "name": "str - Tool name",
      "description": "str - One-line summary",
      "implementation_status": "str - implemented or poc_placeholder",
      "more_info": "str - Follow-up get_help call"
    }
  ]
}
```

When `topic == "standards"`, `data` contains:

```json
{
  "title": "str - Name of the shared response contract",
  "schema": {
    "status": "str - HTTP-style status code meaning",
    "message": "str - Human-readable summary",
    "data": "str - Tool payload contract",
    "error": "dict - Structured error payload contract",
    "meta": "dict - Warnings and next steps contract",
    "metrics": "dict - Token and latency metrics contract"
  },
  "python_parse_snippet": "str - Example code for parsing the envelope"
}
```

When `topic == "<tool_name>"`, `data` contains one of these shapes:

```json
{
  "tool": "str - Tool name",
  "documentation": "str - Full markdown content of the tool doc",
  "implementation_status": "str - implemented or poc_placeholder"
}
```

```json
{
  "tool": "str - Tool name",
  "description": "str - Runtime tool description",
  "implementation_status": "str - implemented or poc_placeholder",
  "input_schema": "dict | null - FastMCP input schema when exposed",
  "note": "str - Explains that no dedicated markdown doc exists"
}
```
<!-- END RETURNS -->

---

<!-- START ERRORS -->
## Errors

| Error Code | Status | When it occurs |
| :--- | :--- | :--- |
| `VALIDATION_ERROR` | 400 | `topic` does not match a supported keyword or a known tool |
| `TOOL_EXECUTION_ERROR` | 500 | The FastMCP instance is missing or a required doc file cannot be loaded |
<!-- END ERRORS -->

---

<!-- START EXAMPLES -->
## Examples

```python
get_help()
get_help(topic="standards")
get_help(topic="project_overview")
```
<!-- END EXAMPLES -->

---

<!-- START NOTES -->
## Notes

Runtime markdown files are loaded from `src/server/docs/`. Files under
`src/server/templates/` are authoring assets only and are never returned to callers. Server-level
onboarding is provided through the FastMCP `instructions` field, sourced from
`src/server/docs/server_instructions.md`.
<!-- END NOTES -->

---

*To get more information call `get_help(topic="get_help")`*
