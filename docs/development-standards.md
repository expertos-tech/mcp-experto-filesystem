<!-- AGENTS SUMMARY
Technical development standards for Python engineering and internal software architecture.
Sessions:
- RUNTIME-STANDARDS: Python version, package management (uv), and configuration.
- DEPENDENCY-MANAGEMENT: uv lock file rules, dependency separation, upgrade workflow.
- CODE-STYLE: Formatting rules, naming conventions, and inline comment prohibitions.
- BOILERPLATE-REDUCTION: Usage of dataclasses and Pydantic, with a decision table.
- DESIGN-PATTERNS: Implementation of OOP principles and specific design patterns.
- INTERNAL-ARCHITECTURE: Layered boundaries (Tool, Service, Domain, Infrastructure).
- ERROR-HANDLING: Exception taxonomy, hierarchy, and structured error rules.
- DOCSTRING-STANDARDS: Mandatory documentation for public APIs using Google/NumPy style.
- TESTING-STANDARDS: pytest layout, coverage thresholds, fixture rules, mocking rules.
- PERFORMANCE-STANDARDS: Latency targets, token budget caps, benchmarking requirements.
- CI-CD: Local pre-commit commands and CI gate requirements.
- INSPECTOR-WORKFLOW: How to start the FastMCP Inspector and inspect the server tools.
-->

# Development Standards (Python & Engineering)

This document defines the technical development standards for mcp-experto-filesystem. For AI-specific tool design and
token economy guidelines, see [MCP Design Guidelines](./mcp-design-guidelines.md).

## Table of Contents

* [Purpose](#purpose)
* [Reference Basis](#reference-basis)
* [Python Version and Runtime Standards](#python-version-and-runtime-standards)
* [Dependency Management](#dependency-management)
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
* [Tool Registration](#tool-registration)
* [Testing Standards](#testing-standards)
* [Performance Standards](#performance-standards)
* [CI/CD Validation Pipeline](#cicd-validation-pipeline)
* [Documentation Standards](#documentation-standards)
* [Pull Request Standards](#pull-request-standards)
* [Definition of Done](#definition-of-done)
* [Strong Opinions](#strong-opinions)
* [Inspector Workflow](#inspector-workflow)

---

## Purpose

This document defines how to write and organize the Python code for mcp-experto-filesystem. The goal is to maintain a
boring, stable, and maintainable codebase that powers a powerful external MCP interface.

---

## Reference Basis

Aligned with [PEP 8](https://peps.python.org/pep-0008/), [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html),
[Python exception docs](https://docs.python.org/3/library/exceptions.html), and modern packaging via pyproject.toml.

---

<!-- START RUNTIME-STANDARDS -->
## Python Version and Runtime Standards

* **Target:** Python 3.11+ (prefer 3.12+).
* **Package Management:** `uv` is the sole package manager; never use `pip` directly.
* **Configuration:** Centralize everything in `pyproject.toml`.
<!-- END RUNTIME-STANDARDS -->

---

<!-- START DEPENDENCY-MANAGEMENT -->
## Dependency Management

* Use `uv` exclusively; never invoke `pip` directly, even in CI scripts.
* Commit `uv.lock`; it is the authoritative pin for all direct and transitive dependencies.
* Separate runtime from dev/test:
  * `[project.dependencies]` - runtime only.
  * `[project.optional-dependencies] dev` - linters, formatters, type checkers.
  * `[project.optional-dependencies] test` - pytest, pytest-mock, hypothesis.
* Never pin transitive dependencies in `pyproject.toml`; let the lock file own them.
* To upgrade a single package: `uv lock --upgrade-package <name>`.
* To upgrade all: `uv lock --upgrade` (review diff before committing).
<!-- END DEPENDENCY-MANAGEMENT -->

---

<!-- START CODE-STYLE -->
## Code Style

Follow PEP 8.

* 4 spaces for indentation.
* `snake_case` for functions and variables.
* `PascalCase` for classes.
* `UPPER_SNAKE_CASE` for module-level constants.
* Functions must be small and focused; prefer < 30 lines per function.
* No inline comments. Code must be self-explanatory through descriptive naming.
* Avoid hidden magic and global mutable state.
* Max line length: 100 characters (configured in `pyproject.toml` via ruff).
<!-- END CODE-STYLE -->

---

<!-- START BOILERPLATE-REDUCTION -->
## Boilerplate Reduction Standards

* **Composition:** Inject collaborators instead of repeating plumbing.
* **Factories:** Use for complex object setup.

### When to Use Dataclass vs Pydantic

| Use Case | Use |
| :--- | :--- |
| Internal data transfer objects (no validation needed) | `@dataclass` |
| Tool input/output models (validated at the boundary) | `pydantic.BaseModel` |
| Config loaded from env or files | `pydantic.BaseSettings` |
| Simple value objects with no serialization | `@dataclass(frozen=True)` |

Rule of thumb: Pydantic at the boundary, dataclasses inside.
<!-- END BOILERPLATE-REDUCTION -->

---

## Object-Oriented Design Standards

Use OOP to model clear boundaries, not for ceremony.

* **Single Responsibility:** Each class has one clear reason to change.
* **Dependency Inversion:** Depend on protocols (`typing.Protocol`) where useful.
* **Composition Over Inheritance:** Avoid deep inheritance trees.
* **Private by Default:** Internal methods start with `_`.

---

<!-- START DESIGN-PATTERNS -->
## Design Patterns by Objective

| Objective | Recommended Pattern |
| :--- | :--- |
| Choose behavior at runtime | Strategy |
| Create tool instances | Factory Method |
| Coordinate complex workflows | Facade |
| Decouple contracts from implementations | Adapter |
| Cache expensive operations | Repository |
| Represent validated data | DTO (Pydantic) |
| Manage write transactions | Unit of Work |
| Encapsulate commands | Command |
| Build complex responses | Builder |
<!-- END DESIGN-PATTERNS -->

---

<!-- START INTERNAL-ARCHITECTURE -->
## Recommended Internal Architecture

```text
MCP Tool Layer          (tool handlers - input validation, response shaping)
    |
Application Services    (orchestration - coordinates domain services)
    |
Domain Services         (core logic - pure, no I/O)
    |
Infrastructure Adapters (filesystem, SQLite, embeddings - all I/O lives here)
```

* Dependencies only flow downward; domain services must never import from infrastructure.
* Tool handlers depend on application services via `typing.Protocol`, not concrete classes.
<!-- END INTERNAL-ARCHITECTURE -->

---

## Filesystem Standards

* Always use `pathlib.Path`; never use raw string concatenation for paths.
* **Path Safety:** Resolve all paths with `.resolve()`, confirm they are inside the project
  root, and raise `PathSecurityError` on traversal attempts.
* Reject symlinks that point outside the allowed root.
* Never pass user-supplied paths to shell commands without allowlisting.
* Use `tmp_path` (pytest built-in) for test fixtures; never hardcode absolute paths in tests.

---

## Ignore Rules

The server must default to ignoring noisy paths:

* `.git/`, `.venv/`, `node_modules/`, `__pycache__/`, `.mypy_cache/`, `.ruff_cache/`.
* Binary files, logs, build artifacts, and sensitive files (`.env`, `*.key`, `*.pem`).
* Provide a configurable allowlist override for advanced users.

---

## Type Hinting Standards

All public functions must have type hints.

* Use modern union syntax: `str | None`.
* Use built-in generics: `list[str]`, `dict[str, int]`.
* Use `typing.Protocol` for structural subtyping at layer boundaries.
* Avoid `Any` where possible; use `object` for truly unknown types.
* Run `mypy src` with `strict = true` in `pyproject.toml`.

---

<!-- START DOCSTRING-STANDARDS -->
## Docstring Standards

All public modules, classes, and functions must have docstrings.

* Use triple double-quotes (`"""`).
* Follow Google Style or NumPy Style consistently within the project.
* Document the contract: parameters, return types, exceptions raised.
* Private methods require a docstring only when their logic is non-obvious.
* One-line docstrings keep the closing `"""` on the same line.
<!-- END DOCSTRING-STANDARDS -->

---

<!-- START ERROR-HANDLING -->
## Error Handling Standards

### Exception Taxonomy

Define a domain-specific hierarchy rooted at a single base exception:

```text
MCPError (base)
    ValidationError      - bad input from the caller
    PathSecurityError    - traversal or permission violation
    ToolExecutionError   - runtime failure inside a tool
        IOError          - filesystem read/write failure
        TimeoutError     - operation exceeded its time budget
    ConfigurationError   - bad server or environment configuration
```

All exception classes live in `src/mcp_experto/exceptions.py`.

### Rules

* Always raise the most specific subclass available.
* Enrich exceptions with context fields: `raise ToolExecutionError("...", path=p, operation="read")`.
* Use `raise X from Y` to preserve exception cause chains.
* Never silence exceptions with bare `except:` or `except Exception: pass`.
* Use `add_note()` (Python 3.11+) to attach breadcrumbs as exceptions bubble up.
* Reserve `finally` blocks for resource cleanup only (file handles, locks).
* Validate all external inputs at the system boundary; never re-validate internal calls.
* Log the full stack trace at `ERROR` level before converting exceptions into response payloads.
<!-- END ERROR-HANDLING -->

---

## Logging Standards

Use Python's `logging` module exclusively.

* Never use `print()` for application logs.
* Do not log secrets, tokens, full file contents, or PII.
* Use structured log records where possible (key=value pairs in the message).
* Log at `DEBUG` inside domain/infrastructure layers; `INFO` for tool invocations;
  `WARNING` for recoverable issues; `ERROR` for unexpected failures.

---

## Tool Registration

Tool registration follows the FastMCP composition model specified in
[Architecture - Tool Registration Flow](./architecture.md#3-tool-registration-flow).

---

<!-- START TESTING-STANDARDS -->
## Testing Standards

### Framework and Layout

* Use `pytest` as the sole test runner.
* Mirror the source layout: `tests/unit/`, `tests/integration/`, `tests/e2e/`.
* Name test files `test_<module>.py`; name test functions `test_<behaviour>_when_<condition>`.

### Coverage Thresholds

| Layer | Minimum Line Coverage | Branch Coverage |
| :--- | :--- | :--- |
| Domain / Services | 90% | 80% |
| Infrastructure adapters | 75% | 60% |
| Tool handlers | 85% | 70% |

Run with:

```bash
uv run pytest --cov=src --cov-branch
```

> **Unit tests evaluation:** The project maintains an ambitious goal of **100% unit test coverage** (or the nearest 
> technically feasible percentage). High coverage is a core signal of reliability for our AI-agent users.

### Fixture Standards

* Use `yield` fixtures for setup/teardown; always clean up resources.
* Scope fixtures deliberately: `function` (default), `module`, `session` (shared, read-only only).
* Never share mutable state between tests via session-scoped fixtures.
* Use `tmp_path` (built-in pytest fixture) for all filesystem tests.

### Mocking Rules

* Mock at the I/O boundary only - never mock domain logic.
* Prefer `pytest-mock` (`mocker` fixture) over `unittest.mock` directly.
* Assert mock call arguments explicitly; avoid `assert mock.called` without checking args.

### Parametrize and Property Tests

* Use `@pytest.mark.parametrize` for data-driven cases.
* Use `hypothesis` for property-based testing of parsers, validators, and path sanitizers.
<!-- END TESTING-STANDARDS -->

---

<!-- START PERFORMANCE-STANDARDS -->
## Performance Standards

| Operation | Target | Hard Limit |
| :--- | :--- | :--- |
| File read (up to 1 MB) | < 200 ms | 500 ms |
| Directory traversal (up to 1000 files) | < 500 ms | 2 s |
| Semantic search query | < 1 s | 3 s |
| Token budget per tool response | < 2000 tokens | 8000 tokens |

* Measure elapsed time with `time.perf_counter()`.
* Include `execution_time_ms` in every response payload `meta` block.
* Add a `@pytest.mark.benchmark` test for any tool that performs I/O.
<!-- END PERFORMANCE-STANDARDS -->

---

<!-- START CI-CD -->
## CI/CD Validation Pipeline

### Local (run before every commit)

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
uv run pytest --cov=src --cov-branch
```

### CI Gate (blocks merge)

All four commands above must pass. No exceptions, no overrides.

### Recommended pre-commit configuration

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
      - id: ruff-format
```
<!-- END CI-CD -->

---

## Documentation Standards

Documentation must stay close to behavior. Update READMEs, AGENTS.md, or `/docs` whenever
contracts or safety rules change.

---

## Pull Request Standards

PRs must be small and focused. Include:

* A description of the "why" (not just the "what").
* Evidence of how it was tested (command output or test names).
* A docs update if any public contract, tool schema, or safety rule changed.

---

## Definition of Done

* Behavior is implemented and verified against acceptance criteria.
* Unit and integration tests pass; coverage thresholds are met.
* `ruff check`, `ruff format --check`, and `mypy` all pass with zero warnings.
* All public APIs have docstrings and type hints.
* Documentation is updated (if contracts or safety rules changed).
* No new exceptions are caught without logging or re-raising.
* No secrets, tokens, or file contents are logged.

---

## Strong Opinions

* **Boring Interior:** Use established Python patterns; avoid framework magic.
* **Explicit Over Implicit:** No dynamic attribute injection, no `__getattr__` tricks.
* **Composition Over Everything:** High-level services coordinate small, focused components.
* **Safety First:** Guardrails are non-negotiable features, not optional add-ons.
* **Fail Loud, Fail Early:** Raise at the boundary; never silently return partial results.

---

<!-- START INSPECTOR-WORKFLOW -->
## Inspector Workflow

Use the FastMCP Inspector to validate the current server runtime and inspect the tools exposed by
`src/server/main.py`.

### Start the Inspector

Run the following command from the repository root:

```bash
uv run fastmcp dev inspector src/server/main.py
```

This starts the local Inspector flow for the FastMCP application defined in `src/server/main.py`.

### Connect to the Server

After the Inspector UI opens:

* Use the left-side menu and open **Connect**.
* Confirm that the target points to the server loaded from `src/server/main.py`.
* Start the connection so the Inspector can attach to the local FastMCP server runtime.

### Initialize the Session

Once connected:

* Trigger **Initialize** from the Inspector flow.
* Wait for the MCP session to complete initialization successfully.
* Confirm that the server metadata is returned without protocol errors before testing tools.

### Inspect the Tools

After initialization:

* Open the tools list in the Inspector.
* Review the registered tools exposed by the current runtime.
* Verify the tool names, descriptions, and input schemas before sending any test calls.

For this project, the expected flow is:

1. Connect from the left-side menu.
2. Initialize the MCP session.
3. Open the tool list and inspect the available tools.

This sequence should be used before validating behavior in `get_help`, `project_overview`, or
`read_file_excerpt`.
<!-- END INSPECTOR-WORKFLOW -->
