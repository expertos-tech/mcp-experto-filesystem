<!-- AGENTS SUMMARY
Runtime help document for the project_overview MCP tool.
Sessions:
- TLDR: Fast summary of the tool and its current status.
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

<!-- START TLDR -->
## TL;DR

* `project_overview` returns a bounded map of the current workspace.
* It summarizes the root, visible tree, candidate file counts, and local index location.
* Use it before deeper reads or indexing when you need orientation without dumping the repo.
<!-- END TLDR -->

---

<!-- START OVERVIEW -->
## Overview

Returns a token-efficient project map rooted at the configured workspace. The tool traverses the
workspace up to the requested depth, skips ignored areas such as `.git/` and `node_modules/`, and
reports index-related metadata that helps downstream retrieval tools.

**Status:** `implemented`
<!-- END OVERVIEW -->

---

<!-- START PARAMETERS -->
## Parameters

### Quick Reference

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `max_depth` | `int` | No | `3` | Maximum traversal depth for the returned tree |

### Detailed Description

#### `max_depth`

**Type:** `int`  
**Required:** No  
**Default:** `3`

Controls how deep the returned tree should go. The tool validates the value and only returns a
bounded structure, not a recursive full dump.
<!-- END PARAMETERS -->

---

<!-- START RETURNS -->
## Returns

On success (`status 200`), `data` contains:

```json
{
  "summary": "str - High-level summary of the workspace map",
  "root": "str - Absolute configured workspace root",
  "max_depth": "int - Effective traversal depth",
  "tree": [
    {
      "name": "str - File or directory name",
      "path": "str - Project-relative path",
      "kind": "str - directory or file",
      "file_kind": "str | null - Retrieval-oriented file family for files",
      "children": "list | null - Nested nodes when inside depth budget"
    }
  ],
  "counts": {
    "indexed_candidate_files": "int - Files that can be indexed",
    "ignored_entries": "int - Files or directories skipped by default"
  },
  "index_location": "str - Local SQLite index path",
  "watcher_status": "str - running, unavailable, or disabled"
}
```
<!-- END RETURNS -->

---

<!-- START ERRORS -->
## Errors

| Error Code | Status | When it occurs |
| :--- | :--- | :--- |
| `VALIDATION_ERROR` | 400 | `max_depth < 1` |
| `PATH_SECURITY_ERROR` | 403 | An internal traversal path escapes the workspace root |
| `TOOL_EXECUTION_ERROR` | 500 | The workspace cannot be traversed safely |
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

This tool is read-only and skips ignored or noisy areas by default.
<!-- END NOTES -->

---

*To get more information call `get_help(topic="project_overview")`*
