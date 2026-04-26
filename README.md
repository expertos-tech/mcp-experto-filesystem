<!-- AGENTS SUMMARY
High-level overview of the Expertos Tech Filesystem MCP project for human users and AI agents.  
Sessions:
- PROBLEM-DEFINITION: Why this project exists and the problems it solves.
- ARCHITECTURAL-GOALS: Key objectives (token economy, safety, intelligence).
- DOCUMENTATION: Links to documentation and mandatory rules.
- ROADMAP: Planned features and core capabilities.
-->

# Expertos Tech Filesystem MCP

An opinionated, intelligence-first MCP (Model Context Protocol) server designed to give AI agents safe, token-efficient,
and semantically guided access to local codebases.

This project is an open-source initiative from the Expertos Tech community: [https://expertostech.dev](https://expertostech.dev)  

## Table of Contents

* [The Problem: Why This Project Exists](#the-problem-why-this-project-exists)
* [Key Architectural Goals](#key-architectural-goals)
* [Documentation](#documentation)
* [Core Capabilities (Roadmap)](#core-capabilities-roadmap)
* [Contributing](#contributing)
* [About Expertos Tech](#about-expertos-tech)

---

<!-- START PROBLEM-DEFINITION -->
## The Problem: Why This Project Exists

Current AI agents interact with filesystems inefficiently. When asked to fix a bug or add a feature, they often:
* Blindly read entire repositories or massive files.
* Pollute their context window, wasting tokens and degrading reasoning.
* Perform risky write operations without understanding the project architecture.
* Fail to find relevant code because they rely on exact keyword matches.

mcp-experto-filesystem solves this by acting as a Project-Aware Context Layer. Instead of giving the LLM a dumb
terminal to run commands, we provide high-level, strategic tools designed for Generative AI workflows.
<!-- END PROBLEM-DEFINITION -->

---

<!-- START ARCHITECTURAL-GOALS -->
## Key Architectural Goals

* **Extreme Token Economy:** We prioritize summaries, targeted line-range excerpts, and semantic retrieval over
  raw file dumps.
* **Safe and Guardrailed Automation:** Read-only by default. Write operations require explicit intent, diff-based
  previews, and respect project-specific protected areas.
* **High-Level Intelligence:** Tools that automatically understand project structure, separating source code
  from tests, configuration, and dependencies.
* **Local-First and Private:** Embeddings, caches, and indexes remain entirely on the developer's machine.
<!-- END ARCHITECTURAL-GOALS -->

---

<!-- START DOCUMENTATION -->
## Documentation

Whether you are a human contributor or an AI agent, our documentation is your source of truth:

* **[Technical Documentation Index](./docs/README.md):** The central hub for Python architecture, design
  guidelines, and engineering standards.
* **[AGENTS.md](./AGENTS.md):** Mandatory rules, persona, and command shortcuts for AI agents working in this
  repository. AI agents must read this first.
<!-- END DOCUMENTATION -->

---

<!-- START ROADMAP -->
## Core Capabilities (Roadmap)

### 1. Smart Project Discovery
* Automatic stack and framework detection.  
* Entry point and configuration file mapping.  
* Strict adherence to .gitignore and environment file protection.  

### 2. Token-Optimized Reading
* File summarization to understand intent before reading code.  
* Symbol extraction for classes, functions, and interfaces.  
* Targeted line-range excerpts to minimize context noise.  

### 3. Semantic and Intent-Based Search
* Local vector-based retrieval to find concepts (e.g., "Where is the auth middleware?") instead of just  
  regex matching.  

### 4. Safe Modification
* Dry-run file edits and surgical patch applications.  
* Reversible changes with clear functional summaries.  
<!-- END ROADMAP -->

---

## Current Implementation Status

The current runtime is based on `FastMCP` and exposes three public tools:

* `get_help`, implemented and backed by runtime tool introspection.
* `project_overview`, currently exposed as a POC placeholder.
* `read_file_excerpt`, currently exposed as a POC placeholder.

Every public tool is wrapped by the project's universal response contract, which standardizes
`status`, `message`, `data`, `error`, `meta`, and `metrics`.

Semantic search, filesystem traversal, intelligent excerpts, local caching, and safe write
operations remain roadmap capabilities and are not implemented yet.

---

## Getting Started

> The server is under active development. The steps below reflect the current local development workflow.

```bash
# 1. Clone the repository
git clone https://github.com/expertostech/mcp-experto-filesystem.git
cd mcp-experto-filesystem

# 2. Install dependencies (requires Python 3.11+)
uv sync --all-extras

# 3. Run the validation suite
uv run ruff check src tests
uv run mypy src
uv run pytest --cov=src --cov-branch

# 4. Register with your MCP client (e.g., Claude Desktop)
# Add the server entry to your client's mcp_servers config pointing to the stdio entrypoint.
```

For configuration options and detailed integration instructions, see [docs/architecture.md](./docs/architecture.md).

---

## Contributing

We are in the early stages of architecting this solution and welcome all contributions.

1. Check the [Development Standards](./docs/development-standards.md).
2. Understand our AI philosophy in the [MCP Design Guidelines](./docs/mcp-design-guidelines.md).
3. Open an issue to discuss your ideas or submit a PR.

---

## About Expertos Tech

We are a community focused on software engineering, cloud architecture, and AI education. We believe in building
tools that help developers work smarter, not harder.

* **Website:** [expertostech.dev](https://expertostech.dev)
* **License:** MIT. See [LICENSE](./LICENSE) for details.
