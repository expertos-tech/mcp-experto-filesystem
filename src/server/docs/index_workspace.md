<!-- AGENTS SUMMARY
Runtime help document for the index_workspace MCP tool.
Sessions:
- TLDR: Fast summary of local indexing.
- OVERVIEW: What gets indexed and how updates work.
- PARAMETERS: Input contract for index runs.
- RETURNS: Success payload shape.
-->

# index_workspace

## Table of Contents

* [Overview](#overview)
* [Parameters](#parameters)
* [Returns](#returns)

---

<!-- START TLDR -->
## TL;DR

* `index_workspace` builds or refreshes the local SQLite retrieval index.
* It indexes text-like files directly and uses document extractors for rich formats.
* Semantic vectors are computed locally and may fall back to hashing if the preferred model runtime is unavailable.
<!-- END TLDR -->

---

<!-- START OVERVIEW -->
## Overview

Creates or updates the local workspace index used by `search_files` and `find_similar_content`. The
tool skips ignored areas, records extraction failures, and supports full or incremental refreshes.
<!-- END OVERVIEW -->

---

<!-- START PARAMETERS -->
## Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `force_full` | `bool` | No | `false` | Rebuild the whole index from scratch |
| `paths` | `list[str] \| None` | No | `None` | Restrict the refresh to specific relative paths |
| `file_types` | `list[str] \| None` | No | `None` | Restrict indexing to selected file kinds |
<!-- END PARAMETERS -->

---

<!-- START RETURNS -->
## Returns

On success, `data` contains:

```json
{
  "summary": "str - High-level indexing summary",
  "indexed_count": "int - Files updated in the index",
  "skipped_count": "int - Files skipped because they were unchanged or unsupported",
  "error_count": "int - Files that failed extraction",
  "paths_scanned": "int - Candidate paths traversed",
  "embedding_provider": "str - Active embedding provider id",
  "embedding_warnings": ["str - Provider fallback notices"],
  "watcher_status": "str - running, unavailable, or disabled"
}
```
<!-- END RETURNS -->
