<!-- AGENTS SUMMARY
Repository-specific instructions and standards for maintaining the Docsify documentation site.
Sessions:
- TLDR: Fast summary of the Docsify operating rules in this repository.
- SITE-CONTRACT: Canonical Docsify shell and routing contract used by the project.
- FILE-CONVENTIONS: Expected file layout and ownership for Docsify content.
- AUTHORING-STANDARDS: Markdown and navigation patterns for Docsify pages.
- ENHANCEMENT-PATTERNS: Rules for enabling or changing Docsify plugins and UI behavior.
- VALIDATION-CHECKLIST: Minimum checks before merging Docsify-related changes.
-->

# Docsify Standards

## Table of Contents

* [TL;DR](#tldr)
* [Site Contract](#site-contract)
* [File Conventions](#file-conventions)
* [Authoring Standards](#authoring-standards)
* [Enhancement Patterns](#enhancement-patterns)
* [Validation Checklist](#validation-checklist)

---

<!-- START TLDR -->
## TL;DR

* The Docsify site is served from `docs/` and configured centrally in `docs/index.html`.
* New human-facing docs pages must use repository Markdown standards and be linked from
  `docs/_sidebar.md`.
* Keep routing relative, keep navigation simple, and add UI plugins only when they solve a real
  documentation problem.
* Tabs and Mermaid are already enabled, use them only when they make the page easier to scan.
<!-- END TLDR -->

---

<!-- START SITE-CONTRACT -->
## Site Contract

The current Docsify shell is the source of truth for how documentation is rendered in this
repository. At the time of writing, `docs/index.html` establishes these baseline rules:

* `homepage: "README.md"` defines `docs/README.md` as the landing page.
* `loadSidebar: true` makes `docs/_sidebar.md` the primary navigation source.
* `loadNavbar: false` means `docs/_navbar.md` is currently present but not active at runtime.
* `relativePath: true` keeps page-to-page navigation portable within the `docs/` tree.
* `maxLevel: 3` and `subMaxLevel: 3` allow heading extraction without overloading the sidebar.
* `alias` remaps nested routes back to the root `_sidebar.md` and `_navbar.md`.

Current plugins and UI behaviors include:

* `docsify-themeable` for the visual base and CSS variable control
* `search` for full-text search
* `zoom-image` for image inspection
* `docsify-copy-code` for code snippet copy actions
* `docsify-tabs` for tabbed content
* `docsify-pagination` for previous and next navigation
* `docsify-sidebar-collapse` for denser navigation trees
* `docsify-mermaid` with Mermaid loaded as an ES module
* custom theme toggle behavior from `docs/_media/theme-toggle.js`
<!-- END SITE-CONTRACT -->

---

<!-- START FILE-CONVENTIONS -->
## File Conventions

Use the following ownership model inside `docs/`:

| Path | Purpose | Rule |
| :--- | :--- | :--- |
| `docs/index.html` | Docsify app shell and global config | Centralize all runtime config here. Do not duplicate config in page files. |
| `docs/README.md` | Homepage content | Keep it concise and reader-oriented. Treat it as the default entry point. |
| `docs/_sidebar.md` | Primary navigation map | Every new human-facing page must be discoverable here. |
| `docs/_navbar.md` | Optional top navigation | Keep only if there is a concrete plan to enable `loadNavbar`. |
| `docs/_media/` | Shared assets and custom client code | Store images, CSS, and small scripts here. |
| `docs/*.md` | Human-facing documentation pages | Use lowercase kebab-case filenames except for `README.md`. |

Recommended file naming rules:

* Use lowercase kebab-case for page files, for example `agent-telemetry.md`.
* Keep asset names stable and descriptive, for example `logo-480.png` or `theme-toggle.js`.
* Avoid spaces, uppercase names, and deeply nested folders unless the docs tree becomes large enough
  to justify domain grouping.
<!-- END FILE-CONVENTIONS -->

---

<!-- START AUTHORING-STANDARDS -->
## Authoring Standards

All Docsify pages must also comply with [Markdown Standards](./markdown-standards.md). In addition,
use these Docsify-specific rules:

* Add every new reader-facing page to `docs/_sidebar.md`.
* Use relative links that stay inside `docs/` whenever the target is part of the published site.
* Link to GitHub URLs when the target lives at the repository root and would escape `docs/`.
* Keep headings meaningful because Docsify uses them for the page outline and search results.
* Prefer short sections and shallow nesting so sidebar extraction remains readable.
* Use labeled code fences for all examples.
* Use HTML only when Markdown or an enabled plugin cannot express the layout cleanly.

Use Docsify features with restraint:

* Use tabs only for true alternatives, such as local versus CI or Python versus shell workflows.
* Do not nest tab groups.
* In tab labels and tab content, prefer plain descriptive wording aimed at readers, for example
  `Reader View`, `Contributor View`, `Local`, or `CI`.
* Use Mermaid for architecture, sequence, or flow diagrams that would otherwise become noisy prose.
* Keep Mermaid diagrams compact and left-to-right by default unless the content clearly reads better
  top-to-bottom.
* Keep tables compact because wide tables degrade mobile reading even with responsive styling.

Navigation expectations:

* The sidebar is the canonical navigation surface in the current setup.
* The navbar should not be treated as active until `loadNavbar` is enabled in `docs/index.html`.
* If a new page is intentionally hidden from the sidebar, document the reason in the related change.
<!-- END AUTHORING-STANDARDS -->

---

<!-- START ENHANCEMENT-PATTERNS -->
## Enhancement Patterns

When changing the Docsify shell or adding plugins, follow these patterns:

1. Add new CSS and JavaScript assets in `docs/index.html`, keeping load order explicit.
2. Prefer CDN URLs with an intentional major or exact version, matching the current repository style.
3. Keep custom behavior in small files under `docs/_media/` when inline scripts become noisy.
4. Do not add plugins that duplicate an existing capability or introduce heavy runtime cost for minor
   cosmetic gain.
5. If a plugin changes authoring syntax, add a short example to the relevant docs page or to this
   file when the guidance is cross-cutting.

Recommended change heuristic:

* Shell concern, update `docs/index.html`
* Shared asset or custom behavior, update `docs/_media/`
* Navigation change, update `docs/_sidebar.md`
* Reader-facing explanation, update a Markdown page in `docs/`
* Operational rule or contributor guidance, update this file in `references/`
<!-- END ENHANCEMENT-PATTERNS -->

---

<!-- START VALIDATION-CHECKLIST -->
## Validation Checklist

Before merging Docsify-related changes, verify at least the following:

* The target page is reachable from `docs/_sidebar.md`, unless intentionally private.
* Internal links resolve correctly with `relativePath: true`.
* New headings render correctly and do not create noisy or duplicated sidebar items.
* Tabs, Mermaid diagrams, images, and code blocks render correctly on desktop and mobile widths.
* The shell still loads with the current plugin stack and without console errors.

Useful local commands:

```bash
npx docsify-cli serve docs
npx docsify-cli generate docs --sidebar _sidebar.md
```

Use `generate` carefully. Review the diff before keeping any generated sidebar changes because this
repository treats navigation as curated, not purely automatic.
<!-- END VALIDATION-CHECKLIST -->
