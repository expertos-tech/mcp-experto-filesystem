<!-- AGENTS SUMMARY
Runtime help document for the read_document_excerpt MCP tool.
Sessions:
- TLDR: Fast summary of document excerpt reading.
- OVERVIEW: Supported document formats and behavior.
- PARAMETERS: Input contract for document reads.
- RETURNS: Success payload shape.
- ERRORS: Tool-specific error cases.
-->

# read_document_excerpt

## Table of Contents

* [Overview](#overview)
* [Parameters](#parameters)
* [Returns](#returns)
* [Errors](#errors)

---

<!-- START TLDR -->
## TL;DR

* `read_document_excerpt` reads bounded content from `pdf`, `docx`, and `pptx`.
* It returns logical pages or slides when the format preserves them.
* Legacy `doc` and `ppt` files require an external conversion runtime and may appear in `index_errors`.
<!-- END TLDR -->

---

<!-- START OVERVIEW -->
## Overview

Reads a bounded excerpt from a supported document format. Use it instead of `read_file_excerpt` when
the file is a rich document rather than a plain text file.
<!-- END OVERVIEW -->

---

<!-- START PARAMETERS -->
## Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `str` | Yes | - | Project-relative path to `pdf`, `docx`, or `pptx` |
| `page` | `int` | No | `1` | First logical page or slide to return |
| `max_pages` | `int` | No | `3` | Number of logical items to include |
| `max_chars` | `int` | No | `8000` | Maximum characters per returned item |
<!-- END PARAMETERS -->

---

<!-- START RETURNS -->
## Returns

On success, `data` contains:

```json
{
  "summary": "str - High-level read summary",
  "path": "str - Project-relative path",
  "file_kind": "str - pdf, docx, or pptx",
  "extractor": "str - Active extractor implementation",
  "requested_page": "int - Requested starting page or slide",
  "returned_items": [
    {
      "kind": "str - page, slide, or section",
      "index": "int - Logical item number",
      "content": "str - Bounded extracted text"
    }
  ],
  "warnings": ["str - Extraction caveats"]
}
```
<!-- END RETURNS -->

---

<!-- START ERRORS -->
## Errors

| Error Code | Status | When it occurs |
| :--- | :--- | :--- |
| `VALIDATION_ERROR` | 400 | Unsupported page parameters or unsupported document family |
| `PATH_SECURITY_ERROR` | 403 | The path escapes the workspace root |
| `TOOL_EXECUTION_ERROR` | 500 | A parser dependency is missing or extraction fails |
<!-- END ERRORS -->
