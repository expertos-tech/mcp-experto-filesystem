<!-- AGENTS SUMMARY
Runtime help document for the project_overview MCP tool.
Sessions:
- OVERVIEW: What the tool does and its current implementation status.
- PARAMETERS: Input contract and parameter details.
- RETURNS: Current placeholder success payload.
- ERRORS: Tool-specific error conditions.
- EXAMPLES: Example calls for common usage.
- NOTES: Limits of the current placeholder implementation.
-->

# project_overview

## Table of Contents

* [Overview](#overview)
* [Parameters](#parameters)
* [Returns](#returns)
* [Errors](#errors)
* [Examples](#examples)
* [Notes](#notes)

---

<!-- START OVERVIEW -->
## Overview

Reports the current placeholder state for a future project tree summary tool. It does not inspect
the repository yet and instead confirms the requested depth and implementation status.

**Status:** `poc_placeholder`
<!-- END OVERVIEW -->

---

<!-- START PARAMETERS -->
## Parameters

### Quick Reference

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `max_depth` | `int` | No | `3` | Echoed back in the placeholder response |

### Detailed Description

#### `max_depth`

**Type:** `int`  
**Required:** No  
**Default:** `3`

The current placeholder stores the requested value in `data["requested_max_depth"]`. No directory
traversal or depth validation is implemented yet.
<!-- END PARAMETERS -->

---

<!-- START RETURNS -->
## Returns

On success (`status 200`), `data` contains:

```json
{
  "summary": "str - Placeholder status summary",
  "implementation_status": "str - Always poc_placeholder",
  "requested_max_depth": "int - The value passed by the caller",
  "notes": [
    "str - Explains that traversal is not implemented"
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
project_overview()
project_overview(max_depth=5)
```
<!-- END EXAMPLES -->

---

<!-- START NOTES -->
## Notes

This tool intentionally avoids fabricated filesystem output until real traversal logic exists.
<!-- END NOTES -->

---

*To get more information call `get_help(topic="project_overview")`*
