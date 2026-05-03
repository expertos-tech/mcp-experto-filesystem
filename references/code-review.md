<!-- AGENTS SUMMARY
Code review standard for Python and FastMCP projects.
Sessions:
- TLDR: Fast summary of the required review approach.
- REVIEW-PURPOSE: Purpose, scope, and required output location.
- REVIEW-SOURCES: Local and external references that must guide every review.
- REVIEW-WORKFLOW: Step-by-step review execution workflow.
- PYTHON-GATES: Python style, typing, error handling, logging, and maintainability checks.
- FASTMCP-GATES: FastMCP and MCP-specific review checks for tools, resources, prompts, and transports.
- TESTING-GATES: Required pytest, coverage, fixture, mocking, and edge-case checks.
- OOP-DESIGN-GATES: Object-oriented design and design pattern validation.
- DRY-CONSTANTS-GATES: Boilerplate reduction, duplication, constants, and configuration checks.
- SECURITY-PERFORMANCE-GATES: Safety, token economy, filesystem, observability, and performance checks.
- OUTPUT-CONTRACT: Required format for ./docs/last-code-revew.md.
- REVIEW-PROMPT: Copy-ready prompt for AI-assisted code review.
-->

# Code Review Standard

This document defines how code reviews must be performed for this project. It is intentionally strict.
The goal is to keep the codebase boring, safe, testable, object-oriented where useful, and optimized for
FastMCP-based agent workflows.

Every review result must be saved to:

```text
./docs/last-code-revew.md
```

The filename above intentionally follows the project-requested path. Do not silently rename it during review.

## Table of Contents

* [Purpose](#purpose)
* [Review Scope](#review-scope)
* [Reference Basis](#reference-basis)
* [Review Workflow](#review-workflow)
* [Python Review Gates](#python-review-gates)
* [FastMCP and MCP Review Gates](#fastmcp-and-mcp-review-gates)
* [Testing Review Gates](#testing-review-gates)
* [Object-Oriented Design Review Gates](#object-oriented-design-review-gates)
* [Design Patterns Review Gates](#design-patterns-review-gates)
* [Boilerplate and Duplication Review Gates](#boilerplate-and-duplication-review-gates)
* [Constants and Configuration Review Gates](#constants-and-configuration-review-gates)
* [Security and Filesystem Safety Gates](#security-and-filesystem-safety-gates)
* [Performance and Token Economy Gates](#performance-and-token-economy-gates)
* [Review Severity Model](#review-severity-model)
* [Required Local Commands](#required-local-commands)
* [Review Output Contract](#review-output-contract)
* [Copy-Ready AI Review Prompt](#copy-ready-ai-review-prompt)
* [Definition of Review Done](#definition-of-review-done)

---

<!-- START TLDR -->
## TL;DR

* Reviews in this project must focus on correctness, safety, maintainability, tests, and MCP-specific architecture quality.
* Every review must use the project standards as the source of truth and save its result to `./docs/last-code-revew.md`.
* A good review explains long-term risk, not just whether the current code appears to work.
<!-- END TLDR -->

---

## Purpose

The review must validate whether the code follows the project engineering standard, especially:

* Python 3.11+ standards, preferably Python 3.12+.
* `uv` as the only package manager.
* `ruff`, `mypy`, and `pytest` as mandatory quality gates.
* FastMCP-first implementation when building MCP capabilities.
* Unit tests for all new or changed behavior.
* Strong object-oriented boundaries without unnecessary ceremony.
* Clear design patterns where they reduce complexity.
* No duplicated business logic.
* No magic numbers.
* No hardcoded user-facing text, paths, limits, tool names, or protocol values.
* No unsafe filesystem operations.
* No hidden global mutable state.

A good review does not only say whether the code works. It explains whether the code will remain safe,
extensible, and easy for an AI agent or human maintainer to use correctly.

---

## Review Scope

Review all changed files that can affect behavior, safety, tests, or documentation.

Include at minimum:

* `src/**/*.py`
* `tests/**/*.py`
* `pyproject.toml`
* `uv.lock`
* `README.md`
* `AGENTS.md`
* `docs/**/*.md`
* FastMCP server entrypoints
* MCP tool, resource, prompt, and transport definitions
* Configuration, constants, schemas, and exception classes

Do not limit the review to the exact diff if the changed code depends on existing architecture. Follow the
call path far enough to validate the real behavior.

---

## Reference Basis

### Local project standards

Read these files before producing a final review:

1. `AGENTS.md`
2. `README.md`
3. `docs/development-standards.md`
4. `docs/mcp-design-guidelines.md`
5. `docs/architecture.md`
6. `docs/markdown-standards.md`
7. `docs/code-review.md`

### External engineering references

Use these references to resolve ambiguity:

* [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
* [Python typing documentation](https://docs.python.org/3/library/typing.html)
* [Python Protocols and structural subtyping](https://typing.python.org/en/latest/reference/protocols.html)
* [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
* [pytest documentation](https://docs.pytest.org/)
* [pytest parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html)
* [ruff documentation](https://docs.astral.sh/ruff/)
* [FastMCP tools documentation](https://gofastmcp.com/servers/tools)
* [FastMCP resources documentation](https://gofastmcp.com/servers/resources)
* [FastMCP server runtime and transports](https://gofastmcp.com/deployment/running-server)
* [MCP transports specification](https://modelcontextprotocol.io/specification/draft/basic/transports)
* [MCP schema reference](https://modelcontextprotocol.io/specification/draft/schema)

---

## Review Workflow

Follow this order. Do not jump directly into style issues before validating architecture and tests.

### 1. Identify changed files

Use git to identify the real review scope:

```bash
git status --short
git diff --name-only
git diff --stat
```

When reviewing a branch against a base branch:

```bash
git diff --name-only origin/main...HEAD
git diff --stat origin/main...HEAD
```

### 2. Read the local standards

Read the local project standards listed in [Reference Basis](#reference-basis). The local rules win over
general Python preference.

### 3. Map the architecture impact

Classify each changed file by layer:

```text
MCP Tool Layer
Application Services
Domain Services
Infrastructure Adapters
Configuration
Tests
Documentation
```

Reject code that violates dependency direction. Domain services must not import tool handlers or
infrastructure adapters. Tool handlers must call application services, not implement core business logic.

### 4. Run automated checks

Run the commands in [Required Local Commands](#required-local-commands). If a command cannot be run,
record the reason and mark the review as incomplete.

### 5. Review behavior manually

For every changed function, class, tool, or schema, verify:

* What changed.
* Why it changed.
* Which inputs are valid.
* Which inputs are rejected.
* Which exceptions are raised.
* Which logs are produced.
* Which tests prove the behavior.
* Which documentation changed with the contract.

### 6. Produce the final review file

Save the final review using exactly the format in [Review Output Contract](#review-output-contract).

---

## Python Review Gates

### Style and formatting

The code must satisfy all project formatting rules:

* Follow PEP 8.
* Use 4 spaces for indentation.
* Keep max line length at 100 characters.
* Use `snake_case` for functions and variables.
* Use `PascalCase` for classes.
* Use `UPPER_SNAKE_CASE` for module-level constants.
* Prefer small functions, ideally under 30 lines.
* Do not add inline comments for obvious logic.
* Do not use `print()` for application logs.
* Do not introduce global mutable state.

### Typing

All public functions and classes must be typed.

Required checks:

* Public functions have complete parameter and return type hints.
* Modern syntax is used: `str | None`, `list[str]`, `dict[str, int]`.
* `typing.Protocol` is used at architectural boundaries when it improves decoupling.
* `Any` is avoided unless there is a justified boundary case.
* `object` is preferred over `Any` for truly unknown values.
* `mypy src` passes with strict configuration.

### Data models

Use the right model at the right boundary:

| Use case | Required approach |
| :--- | :--- |
| Tool input/output validation | `pydantic.BaseModel` |
| Internal immutable value object | `@dataclass(frozen=True)` |
| Internal DTO without validation needs | `@dataclass` |
| Environment/configuration model | Pydantic settings model or centralized config object |
| Finite set of choices | `Enum` or `Literal` |

Reject code that uses raw dictionaries for stable contracts when a typed model would reduce ambiguity.

### Error handling

Validate the exception strategy:

* Raise the most specific project exception available.
* Preserve cause chains with `raise X from Y`.
* Do not catch broad exceptions unless converting them to a safe project error.
* Do not use `except Exception: pass`.
* Attach useful context without leaking secrets or internal file contents.
* Convert tool-level failures into structured response payloads where required by the MCP design.
* Log unexpected failures with stack trace before converting them into safe responses.

### Logging

Logging must be useful and safe:

* Use the standard `logging` module.
* Never log secrets, tokens, credentials, `.env` values, or full private file contents.
* Prefer structured key-value context in log messages.
* Use `DEBUG` for internal details, `INFO` for successful tool invocation, `WARNING` for
  recoverable issues, and `ERROR` for unexpected failures.

---

## FastMCP and MCP Review Gates

FastMCP is a good fit for this project when it reduces protocol boilerplate while preserving the project
architecture. It must not become an excuse to put business logic directly inside decorated functions.

### Tool design

Each MCP tool must pass these checks:

* One tool performs one clear action.
* Tool name is stable, descriptive, and not hardcoded in multiple files.
* Tool description is concise and agent-oriented.
* Tool input schema is explicit and validated.
* Tool output schema is predictable and typed.
* Tool handler delegates to an application service.
* Tool handler does not perform deep domain logic.
* Tool handler does not perform raw filesystem access directly unless it is the infrastructure boundary.
* Tool response includes useful metadata where required, such as `execution_time_ms`.
* Tool response does not return excessive content by default.

### Resources

Use FastMCP resources only for read-only contextual data.

Review checks:

* Resource URI is stable and clearly scoped.
* Resource function is side-effect free.
* Resource does not expose secrets, `.env` files, private keys, or raw large files.
* Resource output has a clear MIME type when relevant.
* Dynamic resources enforce input limits.

### Prompts

Use MCP prompts for reusable interaction templates, not business logic.

Review checks:

* Prompt names are stable and descriptive.
* Prompt arguments are explicit and validated.
* Prompt content is concise and easy for the client to render.
* Prompt does not include hidden policy, secrets, or private internal implementation details.
* Prompt does not duplicate large instructions already stored in documentation.

### Transports

Transport choice must match deployment intent:

| Scenario | Preferred transport |
| :--- | :--- |
| Local CLI, Claude Desktop, single-user local automation | `stdio` |
| Remote server, shared access, network deployment | Streamable HTTP |
| Legacy compatibility only | SSE, only if explicitly required |

Review checks:

* `mcp.run()` is guarded by `if __name__ == "__main__":`.
* Transport configuration is centralized.
* Network transports have authentication and authorization strategy documented.
* Logs go to `stderr` when using `stdio`, never to `stdout`.
* No JSON-RPC payload is polluted with debug text.

### FastMCP architecture rule

This pattern is acceptable:

```python
@mcp.tool
async def analyze_project(request: AnalyzeProjectRequest) -> AnalyzeProjectResponse:
    """Analyze the project and return a structured summary."""
    return await service.analyze_project(request)
```

This pattern is not acceptable:

```python
@mcp.tool
async def analyze_project(path: str) -> dict[str, object]:
    # Opens files, traverses directories, parses data, handles errors, and builds responses here.
    ...
```

Tool functions are adapters. They are not the application.

---

## Testing Review Gates

Testing is non-negotiable. Any changed behavior must be covered.

### Required test categories

| Changed area | Required tests |
| :--- | :--- |
| Domain service | Unit tests for normal, edge, and failure cases |
| Application service | Unit tests with mocked I/O boundaries |
| Infrastructure adapter | Integration-style tests using `tmp_path` or local fakes |
| FastMCP tool handler | Tool-level tests validating input, output, and error mapping |
| Config loader | Tests for defaults, missing values, invalid values, and overrides |
| Path safety | Tests for traversal, symlink escape, absolute paths, and allowed paths |
| Error handling | Tests for exception type, cause chain, and safe response payload |

### Coverage expectations

Follow the local coverage table from `development-standards.md`:

| Layer | Minimum line coverage | Minimum branch coverage |
| :--- | ---: | ---: |
| Domain / Services | 90% | 80% |
| Infrastructure adapters | 75% | 60% |
| Tool handlers | 85% | 70% |

The project goal is 100% unit coverage where technically feasible. New code without tests is a major
review failure unless the reviewer documents a precise reason.

### pytest standards

Required checks:

* Use `pytest` only.
* Mirror source layout with `tests/unit`, `tests/integration`, and `tests/e2e` where applicable.
* Test files use `test_<module>.py`.
* Test functions use `test_<behaviour>_when_<condition>`.
* Use `tmp_path` for filesystem tests.
* Use `pytest.mark.parametrize` for input matrix cases.
* Use `pytest-mock` for mocks.
* Mock only I/O boundaries, not domain logic.
* Assert mock call arguments explicitly.
* Avoid shared mutable fixtures.
* Use `yield` fixtures when cleanup is required.

### Required edge cases

Every relevant review must look for missing tests around:

* Empty input.
* Null or omitted optional values.
* Invalid enum values.
* Long input.
* Large files.
* Missing files.
* Permission failures.
* Path traversal attempts.
* Symlink escape attempts.
* Timeout or cancellation.
* External dependency failure.
* Duplicate records.
* Non-UTF-8 or binary content where relevant.

---

## Object-Oriented Design Review Gates

Use object orientation to create boundaries, not ceremony.

Required checks:

* Each class has one clear responsibility.
* Class names describe the domain role, not the implementation detail only.
* Collaborators are injected through constructors or factories.
* Services depend on protocols when a concrete dependency would couple layers.
* Composition is preferred over inheritance.
* Inheritance is used only when the base abstraction is stable and meaningful.
* Private helper methods start with `_`.
* Public methods expose a small, intentional API.
* Classes do not become bags of unrelated static methods.
* Functions are acceptable for pure utilities, but core workflows should be modeled explicitly.

Reject over-engineering. A class that does nothing except wrap one function without adding a useful boundary is
not good OOP. A protocol that has only one implementation and no testing or replacement value is probably noise.

---

## Design Patterns Review Gates

Use patterns to remove ambiguity, not to impress reviewers.

| Objective | Preferred pattern | Review expectation |
| :--- | :--- | :--- |
| Choose behavior at runtime | Strategy | Behavior is replaceable without condition sprawl |
| Create configured objects | Factory Method | Construction logic is centralized and tested |
| Coordinate a workflow | Facade | High-level use case hides lower-level orchestration |
| Decouple external contracts | Adapter | External APIs or filesystem calls do not leak into domain |
| Cache or retrieve data | Repository | Storage concerns stay outside domain logic |
| Represent validated contracts | DTO | Pydantic models protect boundaries |
| Manage write operations | Unit of Work | Commit/rollback behavior is explicit |
| Encapsulate executable actions | Command | Actions are named, testable, and composable |
| Build complex responses | Builder | Response assembly is readable and testable |

Reject pattern misuse:

* No factory for trivial constructors.
* No repository for a single in-memory list unless it represents a future storage boundary.
* No builder for a simple dictionary.
* No command pattern for a one-line call unless it participates in a workflow.
* No inheritance hierarchy where composition would be clearer.

---

## Boilerplate and Duplication Review Gates

The project values low boilerplate, but not at the cost of hidden behavior.

Required checks:

* Repeated validation rules are centralized.
* Repeated response-shaping logic is centralized.
* Repeated path-safety logic is centralized.
* Repeated error mapping is centralized.
* Repeated tool registration is declarative.
* Repeated test setup is moved into fixtures.
* Repeated constants are moved into constants, config, or enums.
* Repeated business rules are not copied into multiple tools or services.

Preferred boilerplate reducers:

* `@dataclass` for internal DTOs.
* `@dataclass(frozen=True)` for value objects.
* Pydantic models for validated boundaries.
* Protocols for dependency inversion.
* Factories for complex setup.
* Shared fixtures for test setup.
* Centralized exception mapping for tool responses.

Do not hide simple code behind clever metaprogramming. The project prefers explicit, boring Python over dynamic
magic.

---

## Constants and Configuration Review Gates

No magic numbers. No hardcoded text. No scattered protocol strings.

### Reject these patterns

```python
if file_size > 1048576:
    ...

return {"error": "Invalid path"}

mcp.run(transport="stdio")
```

### Prefer these patterns

```python
MAX_FILE_SIZE_BYTES = 1_048_576
DEFAULT_MCP_TRANSPORT = "stdio"
ERROR_INVALID_PATH = "invalid_path"
```

Or, when values are environment-specific:

```python
@dataclass(frozen=True)
class FileScanSettings:
    max_file_size_bytes: int
    max_results: int
    ignored_directories: frozenset[str]
```

Review checks:

* Numeric limits are named constants or config fields.
* User-facing messages are centralized.
* Error codes are centralized.
* Tool names are centralized.
* Resource URI prefixes are centralized.
* Transport names are centralized.
* Default ignored directories are centralized.
* Timeouts and token budgets are centralized.
* Tests assert behavior through named values, not repeated literals.

Allowed literals:

* `0`, `1`, and `-1` when they are conventional and obvious.
* Short local test values that do not encode business rules.
* Enum member values defined once.

---

## Security and Filesystem Safety Gates

Filesystem safety is a core requirement.

Required checks:

* Use `pathlib.Path` for paths.
* Resolve paths with `.resolve()` before access.
* Confirm resolved paths are inside the allowed project root.
* Reject traversal attempts.
* Reject unsafe symlink escapes.
* Ignore noisy and sensitive directories by default.
* Never shell out using untrusted input.
* Never expose `.env`, private keys, tokens, secrets, or full private logs.
* Default write operations to safe, narrow, reversible behavior.
* Provide dry-run behavior for destructive or broad operations.

For MCP tools, prefer high-level, intent-aware operations instead of raw filesystem primitives.

---

## Performance and Token Economy Gates

The MCP server exists to reduce agent context waste. Reviewers must reject tools that flood the client with raw data.

Required checks:

* Tool responses are summarized by default.
* Full file content is not returned unless explicitly requested and size-limited.
* Large generated files and binary files are skipped.
* Directory traversal has an upper bound.
* Search results have a default limit and hard maximum.
* Response payloads include warnings when content is skipped or truncated.
* Tool metadata explains token-saving strategies when relevant.
* Expensive operations are cached only when invalidation is clear.
* `execution_time_ms` is included in response metadata where required.

Performance targets from project standards:

| Operation | Target | Hard limit |
| :--- | :--- | :--- |
| File read up to 1 MB | < 200 ms | 500 ms |
| Directory traversal up to 1000 files | < 500 ms | 2 s |
| Semantic search query | < 1 s | 3 s |
| Token budget per tool response | < 2000 tokens | 8000 tokens |

---

## Review Severity Model

Use this severity scale consistently.

| Severity | Meaning | Required action |
| :--- | :--- | :--- |
| Blocker | Unsafe, broken, untested critical path, or merge-blocking architecture violation | Must fix before merge |
| Major | Important maintainability, testing, type, or behavior issue | Should fix before merge |
| Minor | Local improvement that does not block correctness | Can fix in current or next PR |
| Nit | Style or naming polish | Optional |

Examples of blockers:

* Path traversal vulnerability.
* Secret leakage.
* Tool writes files without explicit intent.
* New behavior without tests.
* Domain layer importing infrastructure.
* `mypy`, `ruff`, or required tests failing.
* FastMCP tool returning unbounded raw repository content.

---

## Required Local Commands

Run these before finalizing the review:

```bash
uv sync --all-extras
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
uv run pytest --cov=src --cov-branch
```

When FastMCP integration tests exist, also run:

```bash
uv run pytest tests/integration
uv run pytest tests/e2e
```

When only a subset is possible, document exactly what was not run and why.

---

## Review Output Contract

The final review result must be written to:

```text
./docs/last-code-revew.md
```

Use the exact structure below.

```markdown
<!-- AGENTS SUMMARY
Last code review result for the current project state.
Sessions:
- REVIEW-METADATA: Branch, commit, reviewer, and command execution metadata.
- EXECUTIVE-SUMMARY: Approval status and high-level result.
- FINDINGS: Blockers, major issues, minor issues, and nits.
- TEST-EVIDENCE: Commands executed and results.
- ARCHITECTURE-ASSESSMENT: Layering, OOP, FastMCP, and MCP design assessment.
- ACTION-PLAN: Required fixes and recommended follow-ups.
-->

# Last Code Review

## Table of Contents

* [Review Metadata](#review-metadata)
* [Executive Summary](#executive-summary)
* [Decision](#decision)
* [Findings](#findings)
* [Test Evidence](#test-evidence)
* [Architecture Assessment](#architecture-assessment)
* [FastMCP and MCP Assessment](#fastmcp-and-mcp-assessment)
* [Security and Safety Assessment](#security-and-safety-assessment)
* [Performance and Token Economy Assessment](#performance-and-token-economy-assessment)
* [Action Plan](#action-plan)
* [Reviewed Files](#reviewed-files)
* [Notes and Limitations](#notes-and-limitations)

## Review Metadata

| Field | Value |
| :--- | :--- |
| Date | YYYY-MM-DD |
| Reviewer | AI / Human name |
| Branch | branch-name |
| Commit | commit-sha |
| Base branch | main |
| Review scope | Changed files / full review |

## Executive Summary

Short summary of the review result in 3 to 6 bullets.

## Decision

Status: `APPROVED` / `APPROVED_WITH_CHANGES` / `REJECTED`

Rationale:

* Explain the decision objectively.

## Findings

| Severity | Area | File | Issue | Impact | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Blocker/Major/Minor/Nit | Python/FastMCP/Test/Security/etc. | path/to/file.py | What is wrong | Why it matters | How to fix |

## Test Evidence

| Command | Result | Notes |
| :--- | :--- | :--- |
| `uv run ruff check src tests` | Passed/Failed/Not run | Summary |
| `uv run ruff format --check src tests` | Passed/Failed/Not run | Summary |
| `uv run mypy src` | Passed/Failed/Not run | Summary |
| `uv run pytest --cov=src --cov-branch` | Passed/Failed/Not run | Summary |

## Architecture Assessment

Assess layering, dependency direction, OOP boundaries, design patterns, duplication, and config usage.

## FastMCP and MCP Assessment

Assess tool design, resource usage, prompt usage, transport configuration, schemas, and response shape.

## Security and Safety Assessment

Assess path safety, secret handling, write operations, logging, and input validation.

## Performance and Token Economy Assessment

Assess payload size, traversal limits, caching, execution time metadata, and token budget.

## Action Plan

| Priority | Action | Owner | Status |
| :--- | :--- | :--- | :--- |
| P0/P1/P2 | Concrete action | Owner | Pending/In progress/Done |

## Reviewed Files

* `path/to/file.py`

## Notes and Limitations

Document anything that could not be validated.
```

---

## Copy-Ready AI Review Prompt

Use this prompt when asking an AI agent to perform the review.

```text
Review the current project code using ./docs/code-review.md as the mandatory review standard.

You must:
1. Read AGENTS.md, README.md, ./docs/development-standards.md,
   ./docs/mcp-design-guidelines.md, ./docs/architecture.md, and ./docs/markdown-standards.md.
2. Identify changed files with git.
3. Validate Python standards, FastMCP/MCP design, tests, OOP boundaries, design patterns,
   duplicated code, constants, configuration, security, and token economy.
4. Run or request execution of the required local commands:
   - uv sync --all-extras
   - uv run ruff check src tests
   - uv run ruff format --check src tests
   - uv run mypy src
   - uv run pytest --cov=src --cov-branch
5. Produce the final result only in ./docs/last-code-revew.md using the output contract from
   ./docs/code-review.md.

Do not approve the review if new behavior has no unit tests, if FastMCP tools bypass the service/domain
architecture, if path safety is weak, if constants are hardcoded repeatedly, or if required quality gates fail.
```

---

## Definition of Review Done

A review is complete only when:

* All relevant local standards were read.
* All changed files were classified by layer.
* Automated commands were executed or explicitly marked as not run with a reason.
* All new behavior has unit tests.
* FastMCP tools are validated as thin adapters.
* Domain logic is separated from infrastructure.
* OOP boundaries are justified and not ceremonial.
* Duplicated logic is flagged.
* Magic numbers and hardcoded strings are flagged.
* Security and filesystem safety are checked.
* Token economy and response size are checked.
* The final result is saved to `./docs/last-code-revew.md`.
