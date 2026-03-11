---
type: adr
title: "ADR-003: Config-Driven Workflows"
status: accepted
date: "2026-03-10"
deciders:
  - "oakensoul"
context: Software
tags: [architecture, configuration, workflows, conventions]
---

# ADR-003: Config-Driven Workflows

**Status**: Accepted
**Date**: 2026-03-10
**Context**: Software

## Context and Problem Statement

Every team has conventions: branching model, merge strategy, branch naming, worktree usage, commit
format, default reviewers. When Claude performs git/GitHub operations, it either guesses these
conventions (often wrong) or asks the user every time (friction). Neither outcome is acceptable.

The existing `github-workflow` skill attempted to encode some of these (e.g., worktree mode in
`.claude/.github.yml`), but it was ad-hoc, not integrated with AIDA's config system, and couldn't
scale to cover the full range of project conventions.

## Decision Drivers

- Operations should respect project conventions without asking every time
- Configuration should be declarative, not scattered across skill files
- Sensible defaults that work out of the box (zero-config start)
- Override at project level for team-specific conventions
- Integrate with AIDA's existing configuration infrastructure

## Considered Options

### Option A: Hardcoded Defaults

Pick reasonable defaults (GitHub Flow, squash merge, `feature/` prefix) and hardcode them. Users
who want different behavior edit the skill files.

**Pros**: Zero setup, simple implementation
**Cons**: Doesn't respect team conventions, editing skill files is fragile, no per-project
customization

### Option B: Ask Every Time

When conventions matter (merge strategy, branch prefix), always ask the user.

**Pros**: Always correct, no configuration needed
**Cons**: Repetitive friction, breaks automation, Claude asks "squash or merge?" on every PR

### Option C: AIDA Config Integration (Chosen)

Define preferences in `aida-config.json` with sensible defaults, overridable at project level.
Every command reads config before acting.

**Pros**: Set once, respected everywhere. Sensible defaults for zero-config. AIDA infrastructure
handles config loading, merging, and validation.
**Cons**: Config schema must be maintained, users need to know config exists

## Decision Outcome

**Chosen option**: Option C - AIDA Config Integration

**Rationale**:

- AIDA already has a config system with preference definitions, type validation, and defaults
- `aida-config.json` already defines 11 preferences (branching model, merge strategy, worktree mode,
  branch prefixes, label taxonomy, PR defaults)
- Commands read config and act accordingly — no guessing, no asking
- `/github config show|set` provides user-friendly config management
- New users get sensible defaults; teams customize once and it sticks

### Consequences

**Positive**:

- "Set it and forget it" — conventions are encoded, not improvised
- Consistent behavior across conversations and team members
- `/github branch create` always uses the right prefix, creates worktree if configured
- `/github pr merge` always uses the team's merge strategy
- `/github config init` provides guided first-time setup

**Negative**:

- Config schema must evolve as new commands are added
- **Mitigation**: Schema is additive — new preferences always have defaults
- Users who don't configure get GitHub Flow defaults, which may not match their team
- **Mitigation**: `/github config init` wizard guides through key decisions

## Configuration Domains

| Domain | Key Preferences |
| ------ | --------------- |
| Branching | Model (trunk/github-flow/gitflow), branch prefixes, naming templates |
| Worktree | Enabled, mode (bare/traditional), symlinks, auto-setup |
| Merge | Default strategy (squash/merge/rebase), auto-delete branch |
| PR | Default reviewers, auto-link issues, template |
| Commit | Convention (conventional/none), allowed types, auto-link issue |
| Labels | Taxonomy (standard or custom definition) |
| Sync | Update strategy (rebase/merge) |
| Preflight | Lint command, test command, enabled checks |

## Implementation Notes

- Preferences defined in `.claude-plugin/aida-config.json`
- Config loaded by Python scripts and skill handlers before executing
- `/github config show|set|reset` commands for management (Issue #43)
- `/github config init` wizard for first-time setup
- Project-level overrides in `.aida/github.json` or project `aida-config.json`

## References

- `.claude-plugin/aida-config.json` — current preference definitions
- Issue #43: /github config show|set|reset
- Issue #4: Branching config and templates
