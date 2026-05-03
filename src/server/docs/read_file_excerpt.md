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

* `read_file_excerpt` is currently a placeholder runtime help document, not a real file reader.
* It echoes the requested path and line range instead of reading repository content.
* Use this doc to understand the current input contract and placeholder response shape.
<!-- END TLDR -->

---

<!-- START OVERVIEW -->
## Overview

Reports the current placeholder state for a future line-range file reader. It does not read files
yet and instead echoes the requested path and line range.

**Status:** `poc_placeholder`
<!-- END OVERVIEW -->

---

<!-- START PARAMETERS -->
## Parameters

### Quick Reference

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `str` | Yes | - | Echoed back in the placeholder response |
| `start_line` | `int` | No | `1` | First requested line in the placeholder response |
| `end_line` | `int` | No | `50` | Last requested line in the placeholder response |

### Detailed Description

#### `path`

**Type:** `str`  
**Required:** Yes  
**Default:** -

The current placeholder stores the raw value in `data["path"]`. No file access or path validation
is implemented yet.

#### `start_line`

**Type:** `int`  
**Required:** No  
**Default:** `1`

The current placeholder stores the value in `data["requested_range"]["start_line"]`.

#### `end_line`

**Type:** `int`  
**Required:** No  
**Default:** `50`

The current placeholder stores the value in `data["requested_range"]["end_line"]`.
<!-- END PARAMETERS -->

---

<!-- START RETURNS -->
## Returns

On success (`status 200`), `data` contains:

```json
{
  "summary": "str - Placeholder status summary",
  "implementation_status": "str - Always poc_placeholder",
  "path": "str - The value passed by the caller",
  "requested_range": {
    "start_line": "int - Requested first line",
    "end_line": "int - Requested last line"
  },
  "notes": [
    "str - Explains that file reading is not implemented"
  ]
}
```
<!-- END RETURNS -->

---

<!-- START ERRORS -->
## Errors

This placeholder currently defines no tool-specific application errors. Any `status 500` response
would indicate an internal fault rather than a documented usage error.
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

This tool intentionally avoids fabricated file content until real file-reading logic exists.
<!-- END NOTES -->

---

*To get more information call `get_help(topic="read_file_excerpt")`*
