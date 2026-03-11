---
issue: 26
title: "Rich terminal output formatting and color coding"
status: "Completed"
created: "2026-03-11 00:03:43"
completed: "2026-03-10"
pr: 83
branch: "milestone-v0.2/feature/26-rich-terminal-output-formatting"
---

# Issue #26: Rich terminal output formatting and color coding

**Status**: Completed
**Labels**: enhancement, scripts
**Milestone**: v0.2.0
**Assignees**: oakensoul
**PR**: [#83](https://github.com/oakensoul/aida-github-plugin/pull/83)

## Description

All plugin output displayed in Claude Code should be well-formatted,
scannable, and use color/styling to aid readability. This is a
cross-cutting concern that affects every handler.

## Implementation Summary

Added shared formatting utilities using the `rich` library with a
two-stream architecture: stdout stays plain (machine-consumable),
stderr gets rich formatting with icons and color.

### Files Created

- `scripts/utils/style.py` — 28 GitHub API state mappings, icons,
  case-insensitive lookup
- `docs/architecture/adr/008-rich-terminal-formatting.md` — design
  decisions and stdout-plain invariant

### Files Modified

- `pyproject.toml` — added `rich>=13.0,<14.0`
- `scripts/utils/output.py` — Rich Console for stderr, 8 new
  functions (`print_warning`, `print_info`, `print_status`,
  `print_diff_stat`, `print_section`, `print_items`, `_print_styled`,
  `status_console`)
- `scripts/utils/errors.py` — `die()` delegates to `print_error()`
- `tests/test_scripts/test_utils.py` — 40 new tests (119 total)
- `Makefile` — use `.venv/bin` for Python tools

### Key Decisions

- stdout stays plain (design invariant per ADR-008)
- `rich` library for TTY detection, `NO_COLOR`, ANSI handling
- Single `_STATUS_MAP` with NamedTuple (no duplicate dicts)
- Case-insensitive `.lower()` lookup for GitHub API mixed casing
- Per-call Console creation for pytest `capsys` compatibility
- Icons always paired with text (accessibility)

### Deferred

- `print_progress` spinner (zero callers, deferred to follow-up)
- Agent knowledge file updates for formatting utilities

## Expert Reviews

Two rounds by 4 agents (system-architect, tech-lead,
claude-code-expert, github-expert). Round 2: all APPROVE,
0 ERRORs, 0 WARNINGs.

## Work Tracking

- Branch: `milestone-v0.2/feature/26-rich-terminal-output-formatting`
- Started: 2026-03-10
- Completed: 2026-03-10
- PR: #83

## Related Links

- [GitHub Issue](https://github.com/oakensoul/aida-github-plugin/issues/26)
- [Pull Request](https://github.com/oakensoul/aida-github-plugin/pull/83)
