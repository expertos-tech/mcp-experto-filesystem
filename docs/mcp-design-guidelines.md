# MCP Tool Design Guidelines for AI Agents

This document defines the principles for designing MCP tools that are token-efficient, safe, and easy for AI agents to use correctly.

## Table of Contents

* [Core Philosophy](#core-philosophy)
* [Token Economy First](#token-economy-first)
* [Safe Filesystem Automation](#safe-filesystem-automation)
* [High-Level Commands Over Low-Level Access](#high-level-commands-over-low-level-access)
* [Tool Response Standards](#tool-response-standards)
* [Semantic Search Guidelines](#semantic-search-guidelines)
* [Caching for Token Efficiency](#caching-for-token-efficiency)
* [Token Economy Examples](#token-economy-examples)

---

## Core Philosophy

The differentiator of `mcp-experto-filesystem` is intent-based filesystem intelligence. Instead of giving an agent a "dumb" filesystem, we provide a project-aware layer that helps the agent decide **what matters**.

---

## Token Economy First

Every feature must reduce unnecessary context usage.

**Prefer:**
* Summaries over full file content.
* Excerpts/snippets over complete files.
* Structured metadata over raw logs.
* File maps over recursive dumps.
* Cached analysis over repeated scanning.
* Semantic retrieval over brute-force reading.

**Avoid:**
* Returning entire repositories.
* Returning full logs by default.
* Reading dependency folders (`node_modules`, `.venv`).
* Loading large generated or binary files.

---

## Safe Filesystem Automation

The project treats the user’s repository as valuable data. Default behavior must be read-only.

**Write operations must be:**
* **Narrow:** Change only what is necessary.
* **Reversible:** Use backups or git-friendly patterns.
* **Explainable:** Provide a dry-run or a summary of changes.
* **Validated:** Check paths and safety rules before writing.

**Dangerous operations requiring explicit intent:**
* Recursive deletes or bulk renames.
* Editing secrets or `.env` files.
* Changing dependency versions.
* Deleting tests or validation logic.

---

## High-Level Commands Over Low-Level Access

Avoid forcing agents to combine dozens of low-level `read_file` and `list_dir` calls.

**Preferred Tooling Pattern:**
* `project_overview` instead of listing every directory.
* `find_relevant_files` instead of manual searching.
* `read_file_excerpt` instead of reading 2000 lines.
* `apply_patch` instead of overwriting the whole file.

---

## Tool Response Standards

All MCP tool outputs must be designed for language models. Use predictable, structured JSON-like fields.

### Required Fields
* `summary`: A concise description of the result.
* `items` / `files` / `matches`: The primary data requested.
* `warnings`: Information about skipped files, size limits, or risks.
* `next_steps`: Suggested follow-up actions for the agent.
* `metadata`: Technical context (e.g., "returned excerpts instead of full files").

### Example Response Shape
```json
{
  "summary": "Found 3 files related to authentication.",
  "files": [
    {
      "path": "src/auth.py",
      "reason": "Contains the main login logic.",
      "line_range": { "start": 10, "end": 50 }
    }
  ],
  "warnings": [
    { "type": "large_file_skipped", "message": "auth.log was skipped due to size." }
  ],
  "next_steps": ["Read the excerpts from src/auth.py to understand the flow."]
}
```

---

## Semantic Search Guidelines

Semantic search helps agents find concepts instead of just keywords.

**Design Rules:**
* Return matching file paths and relevant excerpts.
* Include similarity scores and a reason for the match.
* Do not embed or index secrets, binary files, or ignored paths.

---

## Caching for Token Efficiency

Caching is a first-class feature. We cache project tree snapshots, file summaries, and symbol indexes to avoid paying the same token cost twice.

**Invalidation Rules:**
* Cache must be invalidated when file content or relevant config changes.
* Do not return stale content silently when correctness is critical.

---

## Token Economy Examples

### Context Loading
* **Bad:** Read the entire repository and return all files.
* **Good:** Return a compact project map, identify relevant files, and read only necessary excerpts.

### File Reading
* **Bad:** Return a 2,000-line file because one function may be relevant.
* **Good:** Return the target function, its imports, and nearby related definitions.

### Command Output
* **Bad:** Run tests and paste the full 500-line raw output.
* **Good:** Summarize the test result, include failing test names, error excerpts, and suggested next steps.
