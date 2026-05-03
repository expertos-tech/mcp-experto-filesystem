<!-- AGENTS SUMMARY
Canonical authoring template for runtime tool help markdown files.
Sessions:
- TLDR: Fast summary of how to use the template.
- TEMPLATE-OVERVIEW: Purpose and usage rules for this template.
- TEMPLATE-BODY: Required markdown structure for each tool help document.
-->

# Tool Help Template

## Table of Contents

* [Template Overview](#template-overview)
* [Template Body](#template-body)

---

<!-- START TLDR -->
## TL;DR

* This file is the canonical template for runtime tool help documents under `src/server/docs/`.
* Use it to keep tool docs structurally consistent with the repository markdown standard.
* The embedded template below must also include a TL;DR section in generated tool docs.
<!-- END TLDR -->

---

<!-- START TEMPLATE-OVERVIEW -->
## Template Overview

Copy the template body below into `src/server/docs/<tool_name>.md` and replace placeholders.

Rules:

* Keep the section headings unchanged.
* Remove instructional HTML comments before saving the final doc.
* Use concise English focused on tool behavior.
* Keep the footer line with the matching tool name.
<!-- END TEMPLATE-OVERVIEW -->

---

<!-- START TEMPLATE-BODY -->
## Template Body

```markdown
<!-- AGENTS SUMMARY
Runtime help document for <tool_name>.
Sessions:
- TLDR: Short summary of the tool for quick scanning.
- OVERVIEW: What the tool does and its current implementation status.
- PARAMETERS: Input contract and parameter details.
- RETURNS: Success payload details.
- ERRORS: Tool-specific error conditions.
- EXAMPLES: Example calls for common usage.
- NOTES: Optional implementation notes or limits.
-->

# <tool_name>

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

* One short summary of what the tool does.
* One short summary of the current implementation status or main constraint.
* One short summary of when callers should use this tool.
<!-- END TLDR -->

---

<!-- START OVERVIEW -->
## Overview

One or two sentences describing what the tool does and why it exists.

**Status:** `implemented`
<!-- END OVERVIEW -->

---

<!-- START PARAMETERS -->
## Parameters

### Quick Reference

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `param_name` | `str` | Yes | - | One-line description |

### Detailed Description

#### `param_name`

**Type:** `str`  
**Required:** Yes  
**Default:** -

Detailed explanation of valid values, limits, and interactions.
<!-- END PARAMETERS -->

---

<!-- START RETURNS -->
## Returns

On success (`status 200`), `data` contains:

```json
{
  "field_name": "str - description"
}
```
<!-- END RETURNS -->

---

<!-- START ERRORS -->
## Errors

| Error Code | Status | When it occurs |
| :--- | :--- | :--- |
| `VALIDATION_ERROR` | 400 | Invalid caller input |
<!-- END ERRORS -->

---

<!-- START EXAMPLES -->
## Examples

```python
<tool_name>()
```
<!-- END EXAMPLES -->

---

<!-- START NOTES -->
## Notes

Remove this section entirely if there are no noteworthy limits or behaviors.
<!-- END NOTES -->

---

*To get more information call `get_help(topic="<tool_name>")`*
```
<!-- END TEMPLATE-BODY -->
