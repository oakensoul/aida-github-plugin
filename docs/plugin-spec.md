---
type: specification
title: GitHub Plugin Specification
version: 0.1.0
status: draft
---

# GitHub Plugin Spec

## Overview

A Claude Code plugin that wraps git and gh CLI commands into well-defined skills, paired with a
`github-expert` agent for complex or ambiguous tasks. This plugin covers **actions, not processes**
— it provides the capabilities that workflow/persona plugins can build on top of.

**No custom MCP required.** All skills invoke `git` and `gh` CLI directly.

---

## Design Principles

- **Actions, not processes.** Every skill answers "what command(s) does this execute?" If the answer
  is "it depends on your workflow," it belongs in a different plugin.
- **Naming convention:** `<domain>-<action>` (e.g., `pr-create`, `branch-cleanup`)
- **Defensive coding over warning suppression.** Skills use the correct APIs (e.g., Projects v2 via
  `gh api` / GraphQL) rather than deprecated paths. Never trigger deprecation warnings in the first
  place.
- **Worktree-aware by default.** Skills that deal with branches/repos detect whether the repo uses
  worktrees and behave accordingly.
- **Clean output.** Skills handle JSON parsing from `gh` so the agent (or user) gets structured,
  readable results — not raw API output.
- **Skills as guardrails.** The more a skill encodes the right way to do something, the less room
  for the agent to improvise badly.
- **Agent and skills are peers.** The agent doesn't formally invoke skills, but its system prompt is
  aware of them and can recommend their use.

---

## Agent: `github-expert`

**Purpose:** The conversational entry point for anything complex, ambiguous, or multi-step.
"I don't know exactly what I need — help me figure it out."

**Build this first.** It can then assist with building and refining all the skills.

### Knowledge Base

The agent needs deep knowledge across:

- **Git internals:** reflog, rebase strategies (interactive and non-interactive), merge vs rebase,
  worktree mechanics, stash internals, cherry-pick conflict resolution, bisect workflows
- **gh CLI:** complete command surface, flags, JSON output formatting, `gh api` for direct
  API/GraphQL calls
- **GitHub platform:** Actions (workflow syntax, debugging), branch protection rules, rulesets,
  environments, deploy keys, webhooks, GitHub Apps
- **Projects v2:** GraphQL API, custom fields, views, iterations, automations
- **Best practices:** conventional commits, semantic versioning, branching strategies (trunk-based,
  gitflow, GitHub flow), PR etiquette, issue templates

### Behavioral Notes

- When a task is well-defined and a matching skill exists, the agent should suggest or defer to
  the skill
- When a task requires interactive decision-making (e.g., "should I rebase or merge here?"), the
  agent gathers context through conversation, then either executes directly or hands off to the
  appropriate skill
- The agent should never use deprecated gh flags or subcommands — it knows the current correct way
  to do things

---

## Skills

### `branch-*`

| Skill | Description |
| ----- | ----------- |
| `branch-create` | Create a new branch with naming conventions, correct base branch selection. Detects worktree setup and creates worktree if appropriate. |
| `branch-list` | List branches with ahead/behind tracking, stale detection, worktree status. |
| `branch-cleanup` | Prune stale local and remote branches. Worktree-aware — handles worktree removal when needed. |

### `pr-*`

| Skill | Description |
| ----- | ----------- |
| `pr-create` | Create a PR with template populated, linked issues, reviewers, labels, project assignment. |
| `pr-list` | List PRs filtered by state, author, reviewer, label, milestone. |
| `pr-search` | Full-text and multi-field PR search with complex filter support. |
| `pr-merge` | Merge a PR with strategy selection (merge, squash, rebase), check verification, post-merge branch cleanup. |
| `pr-update` | Update PR metadata: reviewers, labels, assignees, milestone, draft status. |

### `issue-*`

| Skill | Description |
| ----- | ----------- |
| `issue-create` | Create an issue from template, with labels, project/milestone assignment. |
| `issue-list` | List issues filtered by state, label, assignee, milestone. |
| `issue-search` | Full-text issue search with complex filters. |
| `issue-update` | Update issue state, labels, assignees, milestone, project. |

### `label-*`

| Skill | Description |
| ----- | ----------- |
| `label-create` | Create a label with name, color, description. |
| `label-list` | List all labels for a repo. |
| `label-sync` | Apply a standard label taxonomy to a repo, reconcile differences (add missing, optionally remove extras). |
| `label-delete` | Remove a label from a repo. |

### `milestone-*`

| Skill | Description |
| ----- | ----------- |
| `milestone-create` | Create a milestone with title, description, due date. |
| `milestone-list` | List milestones with open/closed state and progress stats. |
| `milestone-update` | Update milestone title, description, due date, state. |

### `project-*` (v2, full depth)

| Skill | Description |
| ----- | ----------- |
| `project-create` | Create a project with title, description, visibility. |
| `project-list` | List org and user projects. |
| `project-view-create` | Create a view with layout (table/board/roadmap), filters, grouping, sort. |
| `project-view-list` | List views on a project. |
| `project-field-create` | Create custom fields: text, number, date, single select, iteration. |
| `project-field-list` | List fields and their options. |
| `project-field-update` | Modify options on single select fields, rename fields, etc. |
| `project-item-add` | Add an issue or PR to a project. |
| `project-item-update` | Set field values on a project item (status, priority, sprint, custom fields). Moving between statuses is a field update. |
| `project-item-list` | List project items with field-value filters. |
| `project-item-remove` | Remove an item from a project. |
| `project-item-archive` | Archive project items. |

### `repo-*`

| Skill | Description |
| ----- | ----------- |
| `repo-init` | Initialize a new repo — standard or worktree setup, branching model, initial config. |
| `repo-clone` | Clone an existing repo — standard or worktree setup. |
| `repo-config` | Configure branch protection rules, rulesets, repo settings. |

> **Note:** `repo-init` and `repo-clone` will hook into the AIDA config system for branching model,
> naming conventions, and worktree preferences. To be wired up when this moves to an AIDA-aware
> thread.

### `actions-*`

| Skill | Description |
| ----- | ----------- |
| `actions-create` | Scaffold a GitHub Actions workflow file. |
| `actions-list` | List workflow runs with status. |
| `actions-debug` | Parse workflow run logs, identify failure point, suggest fix. |
| `actions-enable` | Enable a workflow. |
| `actions-disable` | Disable a workflow. |

### `git-*`

| Skill | Description |
| ----- | ----------- |
| `git-rebase` | Rebase with conflict handling. Agent gathers context first for interactive rebase scenarios; skill handles execution when the plan is clear. If truly interactive, agent advises the user on what to run manually. |
| `git-stash` | Stash, pop, list, apply, drop. |
| `git-cherry-pick` | Single commit and range, with conflict handling. |
| `git-bisect` | Guided binary search to identify a bug-introducing commit. |
| `git-log` | Pretty formatted, filtered by date/author/path. |
| `git-diff` | Diff with useful defaults and file filtering. |

### `release-*`

| Skill | Description |
| ----- | ----------- |
| `release-tag` | Create an annotated tag. |
| `release-create` | Create a GitHub release via `gh release create` with notes and assets. |
| `release-list` | List releases with download/view stats. |

> **Open question:** Is "determine version bump from conventional commits" an action or a process?
> Leaning toward action if it's purely mechanical (parse commits, apply semver rules, output a
> version string). To revisit.

---

## Configuration (AIDA Integration)

The following settings will be managed through AIDA's config system. Placeholder for now.

- **Branching model:** trunk-based, gitflow, GitHub flow, custom
- **Branch naming conventions:** prefix patterns per branch type (feature/, fix/, etc.)
- **Worktree preferences:** default to worktree setup or standard
- **Label taxonomy:** standard set of labels to sync across repos
- **PR template defaults:** default reviewers, labels, project
- **Default project fields:** standard custom fields for new projects

---

## Technical Notes

- All `gh`-wrapping skills use Projects v2 GraphQL API via `gh api graphql` — never the deprecated
  Projects Classic flags
- Skills parse `gh` JSON output into clean structured data before returning results
- Error handling should provide actionable messages, not raw API errors
- Skills that modify state (create, update, delete, merge) should confirm the action in their output
- Worktree detection: check for `.git` file (not directory) or `git worktree list` output
