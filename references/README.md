<!-- AGENTS SUMMARY
Index of all technical documentation and standards for the project.
Sessions:
- TLDR: Fast map of the project documentation.
- DOCUMENTATION-MAP: Table with all documentation files, their purposes, and when to use each.
- AGENT-RULES: Links to agent rule files that AI agents must read before acting.
- USAGE-GUIDE: Instructions on how to navigate and use the documentation.
-->

# Project Documentation Index

## Table of Contents

* [Documentation Map](#documentation-map)
* [Agent Rule Files](#agent-rule-files)
* [How to use this documentation](#how-to-use-this-documentation)

---

<!-- START TLDR -->
## TL;DR

* This file is the central index for repository documentation.
* Start here to choose the right architecture, standards, or operational guide before editing the project.
* AI agents must still read `AGENTS.md` first, then use this index for deeper references.
<!-- END TLDR -->

---

<!-- START DOCUMENTATION-MAP -->
## Documentation Map

| File | Summary | When to Use |
| :--- | :--- | :--- |
| **[architecture.md](./architecture.md)** | stdio protocol, FastMCP composition flow, Universal Response Payload, error schema, and performance SLAs. | Designing new tools or modifying the server's response contract. |
| **[local-telemetry-operations.md](./local-telemetry-operations.md)** | Operational guide for the local telemetry stack that observes the MCP, the host CLI, and model usage signals when emitted. | Running, troubleshooting, or extending the local observability stack under `local-telemetry/`. |
| **[development-standards.md](./development-standards.md)** | Python engineering standards: code style, error taxonomy, testing, dependency management, and CI/CD. | Writing or reviewing any Python code in this repository. |
| **[markdown-standards.md](./markdown-standards.md)** | Mandatory formatting and structure rules for all Markdown files. | Creating or editing any `.md` file. |
| **[docsify-standards.md](./docsify-standards.md)** | Repository-specific Docsify instructions for site structure, navigation, plugins, and validation. | Editing the `docs/` site shell, navigation, or published Markdown pages. |
| **[mcp-design-guidelines.md](./mcp-design-guidelines.md)** | Principles for MCP tool design: token economy, safety, semantic search, and caching strategy. | Designing the behavior or UX of any MCP tool exposed to agents. |
| **[code-review.md](./code-review.md)** | Deep technical review of the FastMCP migration and POC tool implementation. | Evaluating the quality and architecture of recent server changes. |
<!-- END DOCUMENTATION-MAP -->

---

<!-- START AGENT-RULES -->
## Agent Rule Files

These files define mandatory behavior for AI agents working in this repository.
They are distinct from the technical docs above and must be read before any other file.

| File | Purpose |
| :--- | :--- |
| **[AGENTS.md](https://github.com/expertos-tech/mcp-experto-filesystem/blob/main/AGENTS.md)** | Canonical agent persona, safety rules, git conventions, and command shortcuts. |
| **[CLAUDE.md](https://github.com/expertos-tech/mcp-experto-filesystem/blob/main/CLAUDE.md)** | Claude Code-specific overrides and persona settings (mirrors AGENTS.md with adjustments). |
<!-- END AGENT-RULES -->

---

<!-- START USAGE-GUIDE -->
## How to use this documentation

* **Implementing new features:** Start with [Development Standards](./development-standards.md),
  then consult [Architecture](./architecture.md) for the response contract.
* **Designing new MCP tools:** Read [MCP Design Guidelines](./mcp-design-guidelines.md) first,
  then [Architecture](./architecture.md) for the current FastMCP composition flow.
* **Running the telemetry stack:** Use [Local Telemetry Operations](./local-telemetry-operations.md)
  for startup, persistence, OTLP wiring, and troubleshooting.
* **Writing documentation:** Follow [Markdown Standards](./markdown-standards.md) before
  creating or editing any `.md` file.
* **Maintaining the Docsify site:** Read [Docsify Standards](./docsify-standards.md) before
  changing `docs/index.html`, `docs/_sidebar.md`, or published docs pages.
* **AI agents:** Read [AGENTS.md](https://github.com/expertos-tech/mcp-experto-filesystem/blob/main/AGENTS.md)
  or [CLAUDE.md](https://github.com/expertos-tech/mcp-experto-filesystem/blob/main/CLAUDE.md) first,
  then use this index to navigate to the relevant technical reference.
<!-- END USAGE-GUIDE -->
