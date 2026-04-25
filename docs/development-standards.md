# Development Standards (Python & Engineering)

This document defines the technical development standards for `mcp-experto-filesystem`. For AI-specific tool design and token economy guidelines, see [MCP Design Guidelines](./mcp-design-guidelines.md).

## Table of Contents

* [Purpose](#purpose)
* [Reference Basis](#reference-basis)
* [Python Version and Runtime Standards](#python-version-and-runtime-standards)
* [Code Style](#code-style)
* [Boilerplate Reduction Standards](#boilerplate-reduction-standards)
* [Object-Oriented Design Standards](#object-oriented-design-standards)
* [Design Patterns by Objective](#design-patterns-by-objective)
* [Recommended Internal Architecture](#recommended-internal-architecture)
* [Filesystem Standards](#filesystem-standards)
* [Ignore Rules](#ignore-rules)
* [Type Hinting Standards](#type-hinting-standards)
* [Docstring Standards](#docstring-standards)
* [Error Handling Standards](#error-handling-standards)
* [Logging Standards](#logging-standards)
* [Boilerplate-Minimized Tool Registration](#boilerplate-minimized-tool-registration)
* [Testing Standards](#testing-standards)
* [Validation Commands](#validation-commands)
* [Documentation Standards](#documentation-standards)
* [Pull Request Standards](#pull-request-standards)
* [Definition of Done](#definition-of-done)
* [Strong Opinions](#strong-opinions)

---

## Purpose

This document defines how to write and organize the Python code for `mcp-experto-filesystem`. The goal is to maintain a boring, stable, and highly maintainable codebase that powers a powerful external MCP interface.

---

## Reference Basis

Aligned with official Python guidance (PEPs), docstring conventions, and modern packaging via `pyproject.toml`.

---

## Python Version and Runtime Standards

* **Target:** Python `3.11+` (Prefer `3.12+`).
* **Package Management:** `uv` is recommended for local development.
* **Configuration:** Centralize everything in `pyproject.toml`.

---

## Code Style

Follow PEP 8.
* 4 spaces for indentation.
* `snake_case` for functions/variables.
* `PascalCase` for classes.
* Functions must be small and focused.
* No inline comments. Code should be self-explanatory through descriptive naming.
* Avoid hidden magic and global mutable state.

---

## Boilerplate Reduction Standards

* **Dataclasses:** Use for simple internal data containers (prefer `frozen=True`).
* **Pydantic:** Use for external contracts (MCP tools, config validation).
* **Composition:** Inject collaborators instead of repeating plumbing.
* **Factories:** Use for complex object setup.

---

## Object-Oriented Design Standards

Use OOP to model clear boundaries, not for ceremony.

* **Single Responsibility:** Each class has one clear reason to change.
* **Dependency Inversion:** Depend on protocols (`typing.Protocol`) where useful.
* **Composition Over Inheritance:** Avoid deep inheritance trees.
* **Private by Default:** Internal methods start with `_`.

---

## Design Patterns by Objective

| Objective | Recommended Pattern |
| --- | --- |
| Choose behavior at runtime | Strategy |
| Create tool instances | Factory Method |
| Coordinate complex workflows | Facade |
| Decouple contracts from implementations | Adapter |
| Cache expensive operations | Repository |
| Represent validated data | DTO (Pydantic) |
| Manage write transactions | Unit of Work |
| Encapsulate commands | Command |
| Build complex responses | Builder |

---

## Recommended Internal Architecture

```text
MCP Tool Layer
    ↓
Application Services (Orchestration)
    ↓
Domain Services (Core Logic)
    ↓
Infrastructure Adapters (Filesystem, SQLite, etc.)
```

---

## Filesystem Standards

* Always use `pathlib.Path`.
* **Path Safety:** Resolve paths, ensure they stay inside project root, and reject traversal attacks.

---

## Ignore Rules

The server must default to ignoring noisy paths:
* `.git/`, `.venv/`, `node_modules/`, `__pycache__/`, etc.
* Binary files, logs, and sensitive files (`.env`).

---

## Type Hinting Standards

All public functions must have type hints.
* Use modern union syntax: `str | None`.
* Use built-in generics: `list[str]`.
* Avoid `Any` where possible.

---

## Docstring Standards

All public modules, classes, and functions must have Docstrings.
* Use triple double-quotes (`\"\"\"`).
* Follow Google Style or NumPy Style docstrings for consistency.
* Documentation should focus on the contract, parameters, return types, and exceptions raised.
* Private methods (starting with `_`) should also be documented if their logic is complex, though docstrings are mandatory only for the public API.

---

## Error Handling Standards

Errors must be explicit and domain-specific.
* Use custom exception classes.
* Avoid broad `try/except Exception`.
* Include "why it failed" and "what to do next" in error messages.

---

## Logging Standards

Use Python’s `logging` module.
* Never use `print()` for application logs.
* Do not log secrets or full file contents.

---

## Boilerplate-Minimized Tool Registration

Registration should be declarative, handling validation and error mapping automatically:

```python
tool_registry.register(
    name="project_overview",
    input_model=ProjectOverviewRequest,
    output_model=ProjectOverviewResponse,
    handler=project_overview_tool.handle,
)
```

---

## Testing Standards

* **Pytest:** Use as the test runner.
* **Isolation:** Use temporary directories for filesystem tests.
* **Categories:** Unit tests (domain logic), Integration tests (filesystem), Contract tests (MCP schema).

---

## Validation Commands

```bash
ruff check .
ruff format --check .
pytest
mypy src
```

---

## Documentation Standards

Documentation must stay close to behavior. Update READMEs, AGENTS.md, or /docs whenever contracts or safety rules change.

---

## Pull Request Standards

PRs should be small, focused, and include a description of the "why" and how it was tested.

---

## Definition of Done

* Behavior is implemented and verified.
* Tests (unit/integration) pass.
* Code is linted and formatted.
* Documentation is updated.
* Safety rules remain intact.

---

## Strong Opinions

* **Boring Interior:** Use established Python patterns.
* **Explicit Over Implicit:** No magic behavior.
* **Composition Over Everything:** High-level services coordinate small, focused components.
* **Safety First:** Guardrails are non-negotiable features.
drails are non-negotiable features.
