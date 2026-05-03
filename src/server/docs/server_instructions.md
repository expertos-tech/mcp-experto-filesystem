Note: for this file and all markdown content served by this MCP server, use the `AGENTS SUMMARY`
block as the high-level index and use the `START ...` / `END ...` session tags to jump directly to
the section you need without reading the whole document.

Example:

```markdown
<!-- AGENTS SUMMARY
Lorem ipsum overview for a markdown document.
Sessions:
- LOREM-OVERVIEW: Lorem ipsum dolor sit amet.
- LOREM-DETAILS: Consectetur adipiscing elit.
-->

# Lorem Ipsum

## Table of Contents

* [Lorem Overview](#lorem-overview)
* [Lorem Details](#lorem-details)

---

<!-- START LOREM-OVERVIEW -->
## Lorem Overview

Lorem ipsum dolor sit amet.
<!-- END LOREM-OVERVIEW -->

---

<!-- START LOREM-DETAILS -->
## Lorem Details

Consectetur adipiscing elit.
<!-- END LOREM-DETAILS -->
```

<!-- AGENTS SUMMARY
Server onboarding guidance returned through the MCP lifecycle initialize response.
Sessions:
- TLDR: Fast onboarding summary for MCP clients.
- OVERVIEW: Purpose of this server and the intended first-use flow.
- DISCOVERY: How clients and LLMs should discover and inspect tools.
- RESPONSE-CONTRACT: How to understand the shared response envelope.
- TOOL-STATUS: Current implementation status of the exposed tools.
-->

# Server Instructions

## Table of Contents

* [Overview](#overview)
* [Discovery](#discovery)
* [Response Contract](#response-contract)
* [Tool Status](#tool-status)

---

<!-- START TLDR -->
## TL;DR

* This document is the short onboarding guide returned through the MCP initialize flow.
* Clients should list tools, then use `get_help()` for deeper runtime guidance instead of guessing capabilities.
* The server expects compact discovery and structured payload handling through the shared response contract.
<!-- END TLDR -->

---

<!-- START OVERVIEW -->
## Overview

`mcp-experto-filesystem` is an MCP server for safe, token-efficient filesystem workflows.
Prefer compact discovery and targeted reads over broad repository dumps.
<!-- END OVERVIEW -->

---

<!-- START DISCOVERY -->
## Discovery

Use the standard MCP tool listing to discover the currently registered tools.

After listing tools:

* Call `get_help()` to get the runtime help overview and current tool list.
* Call `get_help(topic="<tool_name>")` to get the dedicated markdown help for a tool.
* Call `get_help(topic="standards")` to inspect the shared response contract.
<!-- END DISCOVERY -->

---

<!-- START RESPONSE-CONTRACT -->
## Response Contract

All tools return the same outer envelope:

* `status` for the HTTP-style result code
* `message` for the human-readable summary
* `data` for successful payloads
* `error` for structured failures
* `meta` for warnings and next steps
* `metrics` for execution and token estimates

Treat `status >= 400` as an application-level failure and inspect `error` for details.
<!-- END RESPONSE-CONTRACT -->

---

<!-- START TOOL-STATUS -->
## Tool Status

Current tool guidance:

* `get_help` is implemented.
* `project_overview` is currently a `poc_placeholder`.
* `read_file_excerpt` is currently a `poc_placeholder`.

POC placeholders intentionally avoid fabricated filesystem content. They report current status
until the underlying implementation is delivered.
<!-- END TOOL-STATUS -->
