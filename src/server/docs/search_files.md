<!-- AGENTS SUMMARY
Runtime help document for the search_files MCP tool.
Sessions:
- TLDR: Fast summary of hybrid search.
- OVERVIEW: Query modes and ranking behavior.
- PARAMETERS: Input contract for search queries.
- RETURNS: Success payload shape.
-->

# search_files

## Table of Contents

* [Overview](#overview)
* [Parameters](#parameters)
* [Returns](#returns)

---

<!-- START TLDR -->
## TL;DR

* `search_files` queries the local index by keyword, semantic intent, or both.
* It returns ranked snippets, not full files.
* Use it for exact code fragments, natural-language intent, or mixed multilingual lookup.
<!-- END TLDR -->

---

<!-- START OVERVIEW -->
## Overview

Searches indexed workspace content and returns ranked snippets with metadata. Hybrid mode merges
lexical and semantic signals and is the default retrieval strategy.
<!-- END OVERVIEW -->

---

<!-- START PARAMETERS -->
## Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `query` | `str` | Yes | - | Search string or natural-language query |
| `mode` | `str` | No | `hybrid` | `keyword`, `semantic`, or `hybrid` |
| `top_k` | `int` | No | `10` | Number of matches to return |
| `file_types` | `list[str] \| None` | No | `None` | Restrict search to selected file kinds |
| `path_prefix` | `str \| None` | No | `None` | Restrict search to a relative subtree |
<!-- END PARAMETERS -->

---

<!-- START RETURNS -->
## Returns

On success, `data` contains:

```json
{
  "summary": "str - High-level search summary",
  "query": "str - Original query",
  "mode": "str - Effective ranking mode",
  "matches": [
    {
      "path": "str - Project-relative file path",
      "file_kind": "str - Retrieved file family",
      "excerpt": "str - Bounded matching snippet",
      "line_range": "dict | null - Returned line range when available",
      "page": "int | null - Returned page number for documents",
      "slide": "int | null - Returned slide number for presentations",
      "score": "float - Final merged rank score",
      "match_type": "str - keyword, semantic, or hybrid",
      "reason": "str - Ranking rationale"
    }
  ],
  "warnings": ["str - Fallback or no-result notices"],
  "embedding_provider": "str - Active provider id"
}
```
<!-- END RETURNS -->
