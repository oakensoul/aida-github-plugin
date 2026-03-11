---
type: adr
title: "ADR-001: Python Scripts for Deterministic Execution"
status: accepted
date: "2026-03-10"
deciders:
  - "oakensoul"
context: Software
tags: [architecture, token-efficiency, reliability, python]
---

# ADR-001: Python Scripts for Deterministic Execution

**Status**: Accepted
**Date**: 2026-03-10
**Context**: Software

## Context and Problem Statement

Claude Code interacts with `git` and `gh` CLI tools by constructing shell commands inline. In practice,
this leads to two costly problems:

1. **Wasted context tokens.** Complex operations (e.g., editing a project board field) require 3-4
   sequential commands where each depends on the previous result. Claude often gets flags wrong on the
   first attempt (`--json` vs `--format json`, incorrect `--jq` syntax, wrong `--method` on `gh api`),
   leading to 2-3 retries per operation. Each retry consumes context window tokens.

2. **Non-deterministic behavior.** The same request may produce different command sequences across
   conversations. Sometimes Claude remembers that `gh project` uses `--format json`; sometimes it
   uses `--json` and fails. The user experience is inconsistent.

These problems compound: a 4-step operation with a 30% error rate per step means the happy path is
hit only ~24% of the time. The other 76% involves at least one retry cycle burning tokens and time.

## Decision Drivers

- Token efficiency is critical for Claude Code users (context windows are finite)
- Operations should succeed on the first attempt, every time
- Complex multi-step workflows (project field editing, bulk operations) are the highest-value targets
- Scripts must integrate with AIDA's existing virtual environment infrastructure
- The solution must be testable and maintainable

## Considered Options

### Option A: Better Skill Documentation

Improve the reference files with more examples, gotchas, and correct flag usage so Claude gets it
right more often.

**Pros**: No new code, low maintenance, works with existing architecture
**Cons**: Still non-deterministic (Claude may not follow docs perfectly), doesn't solve multi-step
operations, doesn't save tokens on complex workflows

### Option B: Bash Wrapper Scripts

Create bash scripts that wrap common multi-step `gh`/`git` operations.

**Pros**: Simple, no Python dependency, fast execution
**Cons**: Bash error handling is fragile, complex JSON parsing is painful, not easily testable,
cross-platform differences between macOS and Linux shells

### Option C: Python Helper Scripts (Chosen)

Create Python CLI scripts that wrap complex `gh`/`git` operations, callable as single commands
with human-readable arguments.

**Pros**: Robust error handling, `subprocess.run` for reliable CLI invocation, `json` module for
parsing, testable with pytest, AIDA venv already exists, Jinja2 available for templates
**Cons**: Python dependency (mitigated by AIDA venv), slightly slower than raw bash

## Decision Outcome

**Chosen option**: Option C - Python Helper Scripts

**Rationale**:

- A single `python scripts/gh_project.py move-item --project "Sprint" --issue 42 --status "In Progress"`
  replaces 4 sequential `gh` commands and their `jq` pipes
- Claude calls one command instead of constructing a multi-step pipeline — deterministic, first-attempt success
- AIDA's virtual environment (`~/.aida/venv/`) already exists with auto-bootstrap — no new infrastructure
- Python's `subprocess`, `json`, and `argparse` are purpose-built for this exact use case
- Scripts are testable with pytest using mocked subprocess calls

### Consequences

**Positive**:

- Operations that previously took 3-4 commands (and 2-3 retries) now take 1 command
- Consistent behavior across conversations — same input always produces same output
- Context window savings of 60-80% per complex operation
- Scripts serve as executable documentation of the correct way to do things
- Test coverage provides confidence in command correctness

**Negative**:

- Python scripts need maintenance when `gh` CLI changes flags or output format
- **Mitigation**: Scripts are thin wrappers — changes are localized to one file per domain
- Adds a Python dependency to what could be a pure-markdown plugin
- **Mitigation**: AIDA venv handles this transparently; users never install manually

## Implementation Notes

- All scripts live in `scripts/` directory
- Shared utilities in `scripts/utils/` (output formatting, subprocess helpers, error handling)
- Scripts use AIDA venv: `~/.aida/venv/bin/python3 scripts/gh_project.py`
- Each script is a standalone CLI tool with `argparse` for argument parsing
- Return clean JSON or formatted text, never raw `gh` output
- Handle errors with actionable messages, not stack traces

## References

- [AIDA Virtual Environment](~/.aida/venv/) — auto-bootstrap, `include-system-site-packages = false`
- Issue #3: Python helper scripts for gh/git operations
