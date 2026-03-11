---
type: adr
title: "ADR-008: Rich Terminal Output Formatting"
status: accepted
date: "2026-03-10"
deciders:
  - "oakensoul"
context: Software
tags: [architecture, output, formatting, accessibility]
---

# ADR-008: Rich Terminal Output Formatting

**Status**: Accepted
**Date**: 2026-03-10
**Context**: Software

## Context and Problem Statement

The plugin's Python scripts produce plain-text output with no color, icons, or styling. Status messages
like `ok: Created release v1.0.0` and `error: HTTP 404` are functional but hard to scan in a terminal
full of other output. As the plugin grows to cover more GitHub operations, output readability becomes a
cross-cutting concern that affects every script and handler.

Key requirements:

- Color coding for status categories (success/failure/warning/info)
- Icons paired with text for accessibility (never color-only)
- Graceful degradation when color is unavailable (`NO_COLOR`, non-TTY, `TERM=dumb`)
- Shared library in `scripts/utils/` — not reimplemented per command

## Decision Drivers

- Accessibility: must work without color (icons + text always present)
- Machine-readability: stdout is consumed by `--json` callers and piped to other tools
- Backwards compatibility: existing callers of `print_table`, `print_success`, `print_error` must not break
- Maintainability: avoid reimplementing ANSI handling, TTY detection, `NO_COLOR` support

## Considered Options

### Option A: Custom ANSI Escape Codes

Write a small utility that wraps strings in ANSI escape sequences, with manual TTY detection.

**Pros**: Zero dependencies, minimal code
**Cons**: Must reimplement `NO_COLOR` support, `TERM=dumb` detection, Windows compatibility,
Unicode width calculation. Ongoing maintenance burden for solved problems.

### Option B: `colorama` + Custom Formatting

Use `colorama` for cross-platform ANSI support, build tables and formatting on top.

**Pros**: Lightweight dependency, good Windows support
**Cons**: `colorama` only provides ANSI escape wrapping. Tables, status badges, and semantic
styling must still be built from scratch.

### Option C: `rich` Library (Chosen)

Use the `rich` library for Console-based output with automatic TTY detection, `NO_COLOR` support,
and semantic text styling.

**Pros**: Handles TTY detection, `NO_COLOR`, `TERM=dumb`, Unicode width — all out of the box.
Provides `Console`, `Text`, `Table`, and status spinners. De facto standard for Python CLI formatting.
**Cons**: Medium-sized dependency (~50ms import time). Acceptable for CLI scripts that run once.

## Decision Outcome

**Chosen option**: Option C - `rich` library (`rich>=13.0,<14.0`)

### Design Invariant: stdout Stays Plain

This is the most important architectural decision. The plugin's output contract is:

- **stdout** = machine-consumable data (`print_json`, `print_table`)
- **stderr** = human-readable status messages (`print_success`, `print_error`, `die()`)

**Rich formatting applies only to stderr.** The `print_table` and `print_json` functions remain
unchanged — no Rich Console, no ANSI escapes, no color. This preserves the machine-readability
contract established in ADR-001 and ensures scripts can be piped to `jq`, `grep`, or other tools.

### Two-Stream Architecture

A single `rich.console.Console(file=sys.stderr)` instance handles all stderr output. A fresh
Console is created per call to ensure compatibility with pytest's `capsys` fixture (which swaps
`sys.stderr`).

### Icon + Text Accessibility

Every colored message includes a Unicode icon so meaning is conveyed without relying on color:

- `✔ ok: message` (green) — success
- `✘ error: message` (red) — failure
- `⚠ warning: message` (yellow) — warning
- `ℹ message` (blue) — informational

### Consequences

**Positive**:

- Status messages are immediately scannable in dense terminal output
- `NO_COLOR` and non-TTY environments degrade gracefully (icons remain, color stripped)
- Shared `style.py` constants ensure consistent color mapping across all scripts
- New functions (`print_warning`, `print_info`, `print_status`, `print_diff_stat`,
  `print_section`, `print_items`) provide a complete formatting vocabulary

**Negative**:

- Adds `rich` as a runtime dependency (alongside `jinja2`)
- **Mitigation**: AIDA venv handles installation transparently
- Console creation per call has minor overhead vs caching
- **Mitigation**: Negligible for CLI scripts; required for test compatibility

## Implementation Notes

- `scripts/utils/style.py` — pure constants module (icons, status-color mappings)
- `scripts/utils/output.py` — enhanced with Rich Console for stderr functions
- `scripts/utils/errors.py` — `die()` uses Rich for colored error/hint output
- Existing function signatures preserved — zero changes to calling scripts
- `print_progress` (spinner) deferred to follow-up (no callers at launch)

## References

- [Rich documentation](https://rich.readthedocs.io/)
- [NO_COLOR standard](https://no-color.org/)
- ADR-001: Python Scripts for Deterministic Execution
- Issue #26: Rich terminal output formatting and color coding
