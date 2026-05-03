<!-- AGENTS SUMMARY
Runtime help document for the read_file_excerpt MCP tool.
Sessions:
- TLDR: Fast summary of the tool and its current status.
- OVERVIEW: What the tool does and its current implementation status.
- PARAMETERS: Input contract and parameter details.
- RETURNS: Current placeholder success payload.
- ERRORS: Tool-specific error conditions.
- EXAMPLES: Example calls for common usage.
- NOTES: Limits of the current placeholder implementation.
-->

# read_file_excerpt

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

* `read_file_excerpt` reads a bounded line range from a text-like file in the workspace.
* It validates the relative path, blocks traversal, and truncates oversized excerpts.
* Use it for code, markdown, config, and other known text formats.
<!-- END TLDR -->

---

<!-- START OVERVIEW -->
## Overview

Reads a bounded excerpt from a text-like file inside the configured project root. The tool supports
markdown, source code, configs, and other known text formats, while rejecting binary and document
formats that require `read_document_excerpt`.

**Status:** `implemented`
<!-- END OVERVIEW -->

---

<!-- START PARAMETERS -->
## Parameters

### Quick Reference

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `str` | Yes | - | Project-relative file path |
| `start_line` | `int` | No | `1` | First line to include |
| `end_line` | `int` | No | `50` | Last line to include |
| `max_chars` | `int` | No | `8000` | Maximum characters returned in the excerpt |

### Detailed Description

#### `path`

**Type:** `str`  
**Required:** Yes  
**Default:** -

Must be a project-relative path inside the configured workspace root. Absolute paths and traversal
attempts are rejected.

#### `start_line`

**Type:** `int`  
**Required:** No  
**Default:** `1`

The first one-based line to return.

#### `end_line`

**Type:** `int`  
**Required:** No  
**Default:** `50`

The last one-based line to return.

#### `max_chars`

**Type:** `int`
**Required:** No
**Default:** `8000`

Upper bound for the returned content payload. The tool truncates the excerpt and reports a warning
when needed.
<!-- END PARAMETERS -->

---

<!-- START RETURNS -->
## Returns

On success (`status 200`), `data` contains:

```json
{
  "summary": "str - High-level read summary",
  "path": "str - Project-relative file path",
  "file_kind": "str - text, markdown, code, or config",
  "encoding": "str - Decoding used for the file",
  "requested_range": {
    "start_line": "int - Requested first line",
    "end_line": "int - Requested last line"
  },
  "returned_range": {
    "start_line": "int - Actual first line returned",
    "end_line": "int - Actual last line returned"
  },
  "content": "str - Bounded excerpt content",
  "warnings": [
    "str - Truncation or format warnings"
  ]
}
```
<!-- END RETURNS -->

---

<!-- START ERRORS -->
## Errors

| Error Code | Status | When it occurs |
| :--- | :--- | :--- |
| `VALIDATION_ERROR` | 400 | Invalid line range or unsupported text request |
| `PATH_SECURITY_ERROR` | 403 | The path is absolute or escapes the workspace root |
| `TOOL_EXECUTION_ERROR` | 500 | The file cannot be decoded or exceeds configured size limits |
<!-- END ERRORS -->

---

<!-- START EXAMPLES -->
## Examples

```python
read_file_excerpt(path="README.md")
read_file_excerpt(path="src/server/tools/help.py", start_line=10, end_line=40)
```
<!-- END EXAMPLES -->

---

<!-- START NOTES -->
## Notes

For `pdf`, `docx`, and `pptx`, use `read_document_excerpt` instead.
<!-- END NOTES -->


---

*To get more information call `get_help(topic="read_file_excerpt")`*
