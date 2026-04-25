<!-- AGENTS SUMMARY
Mandatory structure and formatting rules for all Markdown files in the project.
Sessions:
- RATIONALE: Why these standards exist and what they protect.
- CORE-STANDARDS: Basic rules for AGENTS SUMMARY and Table of Contents.
- TAGGING: Instructions for session tagging using HTML comments.
- TYPOGRAPHY: Rules for line length, line breaks, and characters.
- CODE-BLOCKS: Language selection and sizing rules for code blocks.
- CROSS-FILE-LINKING: Conventions for linking between documentation files.
- TOC-GENERATION: Guidelines for maintaining the Table of Contents.
- APPENDIX: Markdown syntax cheat sheet for quick reference.
-->

# Markdown Standards

## Table of Contents

* [Rationale](#rationale)
* [Mandatory AGENTS SUMMARY](#mandatory-agents-summary)
* [Table of Contents Requirement](#table-of-contents-requirement)
* [Session Tagging Standards](#session-tagging-standards)
* [Typographic and Style Rules](#typographic-and-style-rules)
* [Code Block Standards](#code-block-standards)
* [Cross-File Linking Conventions](#cross-file-linking-conventions)
* [TOC Generation](#toc-generation)
* [Compliant Template](#compliant-template)
* [Appendix: Markdown Syntax Cheat Sheet](#appendix-markdown-syntax-cheat-sheet)

---

<!-- START RATIONALE -->
## Rationale

These standards exist for three reasons:

1. **AI agent chunking:** The `AGENTS SUMMARY` block and session tags give LLMs a predictable
   entry point, so they can skip to relevant sections without reading the full file.
2. **Token economy:** Structured, predictable formatting lets agents extract targeted excerpts
   rather than loading entire documents. Consistent line length also reduces token waste.
3. **Human maintainability:** A shared template removes ambiguity about where content belongs,
   making reviews faster and diffs easier to read.
<!-- END RATIONALE -->

---

<!-- START CORE-STANDARDS -->
## Mandatory AGENTS SUMMARY

Every Markdown file must begin with an `<!-- AGENTS SUMMARY -->` block. This block is an HTML comment
that provides a high-level overview of the document's purpose and its main sections.

**Format:**

```markdown
<!-- AGENTS SUMMARY
Brief description of the document.
Sessions:
- Session Name: Brief description of what this session covers.
- ...
-->
```

## Table of Contents Requirement

Every Markdown file must include a "Table of Contents" section immediately after the main title.
This facilitates quick navigation for both humans and AI agents.
<!-- END CORE-STANDARDS -->

---

<!-- START TAGGING -->
## Session Tagging Standards

To improve chunking and targeted reading, all major sections of a document must be wrapped in session tags.

**Syntax:**

* **Start Tag:** `<!-- START SESSION-NAME -->`
* **End Tag:** `<!-- END SESSION-NAME -->`

The `SESSION-NAME` should be uppercase and use hyphens for spaces (e.g., `CORE-PRINCIPLES`).
Session names must match the names listed in the `AGENTS SUMMARY` block at the top of the file.
<!-- END TAGGING -->

---

<!-- START TYPOGRAPHY -->
## Typographic and Style Rules

* **Max Line Length:** Do not exceed 120 columns. Break lines manually to maintain readability.
* **No Em Dashes:** Never use the "-" character. Use commas (",") or hyphens ("-").
* **No Emojis:** Emojis are strictly prohibited in documentation files.
* **Headers:** Use hierarchical ATX headers (`#`, `##`, `###`). Do not skip levels.
* **List Markers:** Use `*` for unordered lists at all nesting levels.
* **Blank Lines:** Separate every section with a `---` horizontal rule and a blank line above and below.

**Why no hard line breaks (trailing two spaces)?**
Trailing spaces are invisible, cause noisy diffs, and are stripped by most editors silently.
Rely on prose paragraphs with intentional blank lines instead.
<!-- END TYPOGRAPHY -->

---

<!-- START CODE-BLOCKS -->
## Code Block Standards

### Language Selection

Always specify the language identifier after the opening fence:

| Content | Identifier |
| :--- | :--- |
| Python source | `python` |
| Shell commands | `bash` |
| JSON payloads | `json` |
| YAML config | `yaml` |
| Plain text / diagrams | `text` |
| Markdown examples | `markdown` |
| TOML config | `toml` |

Never use an unlabeled code fence (` ``` ` with no language) except for inline snippets
where the language is obvious from context.

### Code Block Sizing

* Keep code blocks short enough to illustrate a point, not to substitute for a full implementation.
* For long examples (> 30 lines), link to the source file instead: `See [src/auth.py](../src/auth.py)`.
* Shell command blocks should show only the commands, not the full terminal output,
  unless the output itself is what is being documented.
<!-- END CODE-BLOCKS -->

---

<!-- START CROSS-FILE-LINKING -->
## Cross-File Linking Conventions

* Use relative paths for all internal links: `[text](../other-file.md)`.
* Link to a specific section with an anchor: `[text](../other-file.md#section-name)`.
* Anchor slugs are lowercase with hyphens replacing spaces; parentheses and special characters are dropped.
  Example: "Standard Response Payload (The Universal Contract)" -> `#standard-response-payload-the-universal-contract`.
* Never use absolute filesystem paths or hardcoded repository URLs for internal links.
* Always verify that the target section exists before committing a link.
<!-- END CROSS-FILE-LINKING -->

---

<!-- START TOC-GENERATION -->
## TOC Generation

The Table of Contents must be kept in sync with the actual headings in the file.

* Generate or update the TOC using [`doctoc`](https://github.com/thlorenz/doctoc):

```bash
npx doctoc docs/my-file.md --github --title "## Table of Contents" --maxlevel 2
```

* Run `doctoc` on any file after adding or renaming a heading before committing.
* Limit TOC depth to level 2 (`##`) for long documents; use level 3 (`###`) only for short files
  where sub-sections are critical for navigation.
<!-- END TOC-GENERATION -->

---

## Compliant Template

```markdown
<!-- AGENTS SUMMARY
This is a template for project documentation.
Sessions:
- INTRODUCTION: Purpose of the document.
- DETAILS: Deep dive into the topic.
-->

# Document Title

## Table of Contents

* [Introduction](#introduction)
* [Details](#details)

---

<!-- START INTRODUCTION -->
## Introduction

Content here.
<!-- END INTRODUCTION -->

---

<!-- START DETAILS -->
## Details

Content here.
<!-- END DETAILS -->
```

---

<!-- START APPENDIX -->
## Appendix: Markdown Syntax Cheat Sheet

### Headers

```markdown
# Level 1
## Level 2
### Level 3
```

### Emphasis

* **Bold:** `**text**`
* *Italic:* `*text*`
* ~~Strikethrough:~~ `~~text~~`

### Lists

**Unordered:**

```markdown
* Item 1
* Item 2
  * Sub-item
```

**Ordered:**

```markdown
1. First item
2. Second item
```

**Task List:**

```markdown
- [x] Completed task
- [ ] Pending task
```

### Links and Images

* **Link:** `[Title](https://url.com)`
* **Relative link:** `[Title](../docs/file.md#anchor)`
* **Image:** `![Alt text](path/to/img.png)`

### Code

**Inline:** `` `code` ``

**Block:**

```python
def hello():
    print("world")
```

### Blockquotes

```markdown
> This is a blockquote.
> It can span multiple lines.
```

### Tables

```markdown
| Header 1 | Header 2 |
| :--- | :--- |
| Cell 1 | Cell 2 |
```

### Horizontal Rules

```markdown
---
```
<!-- END APPENDIX -->
