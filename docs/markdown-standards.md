<!-- AGENTS SUMMARY
Mandatory structure and formatting rules for all Markdown files in the project.  
Sessions:
- CORE-STANDARDS: Basic rules for AGENTS SUMMARY and Table of Contents.
- TAGGING: Instructions for session tagging using HTML comments.
- TYPOGRAPHY: Rules for line length, line breaks, and characters.
- APPENDIX: Markdown syntax cheat sheet for quick reference.
-->

# Markdown Standards

## Table of Contents

* [Mandatory AGENTS SUMMARY](#mandatory-agents-summary)
* [Table of Contents Requirement](#table-of-contents-requirement)
* [Session Tagging Standards](#session-tagging-standards)
* [Typographic and Style Rules](#typographic-and-style-rules)
* [Compliant Template](#compliant-template)
* [Appendix: Markdown Syntax Cheat Sheet](#appendix-markdown-syntax-cheat-sheet)

---

<!-- START CORE-STANDARDS -->
## Mandatory AGENTS SUMMARY

Every Markdown file must begin with an `<!-- AGENTS SUMMARY -->` block. This block is an HTML comment that provides a  
high-level overview of the document's purpose and its main sections.  

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

Every Markdown file must include a "Table of Contents" section immediately after the summary and the main title. This  
facilitates quick navigation for both humans and AI.  
<!-- END CORE-STANDARDS -->

---

<!-- START TAGGING -->
## Session Tagging Standards

To improve chunking and targeted reading, all major sections of a document must be wrapped in session tags.  

**Syntax:**
* **Start Tag:** `<!-- START SESSION-NAME -->`  
* **End Tag:** `<!-- END SESSION-NAME -->`  

The `SESSION-NAME` should be uppercase and use hyphens for spaces (e.g., `CORE-PRINCIPLES`).  
<!-- END TAGGING -->

---

<!-- START TYPOGRAPHY -->
## Typographic and Style Rules

* **Max Line Length:** Do not exceed 120 columns. Break lines manually to maintain readability.  
* **Hard Line Breaks:** Every line must end with two spaces (`  `) before the newline character.  
* **No Em Dashes:** Never use the "—" character. Use commas (",") or hyphens ("-").  
* **No Emojis:** Emojis are strictly prohibited in documentation files.  
* **Headers:** Use hierarchical ATX headers (`#`, `##`, `###`).  
<!-- END TYPOGRAPHY -->

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
Content here...  
<!-- END INTRODUCTION -->

---

<!-- START DETAILS -->
## Details
Content here...  
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
* **Image:** `![Alt text](path/to/img.png)`  

### Code
**Inline:** `` `code` ``  

**Block:**
```python
def hello():
    print("world")
```

### Blockquotes
> This is a blockquote.  
> It can span multiple lines.  

### Tables
| Header 1 | Header 2 |
| :--- | :--- |
| Cell 1 | Cell 2 |
| Left aligned | Right aligned |

### Horizontal Rules
`---`
<!-- END APPENDIX -->
