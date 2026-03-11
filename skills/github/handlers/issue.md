---
type: handler
name: issue
title: Issue Operations
description: Handler for /github issue commands
skill: github
domain: issue
version: 1.0.0
---

# /github issue

## create

Create a GitHub issue.

```bash
gh issue create --title "<title>" --body "<description>" --label <label> --assignee @me [--milestone <name>] [--project <name>]
```

**Important**: Always provide `--body` — without it, `gh issue create` opens an interactive editor
that Claude cannot use.

### Options

| Flag | Purpose |
| ---- | ------- |
| `--title "..."` | Issue title (required) |
| `--body "..."` | Issue body (markdown) |
| `--label <name>` | Add label (repeat for multiple) |
| `--assignee <user>` | Assign (use `@me` for self) |
| `--milestone <name>` | Associate with milestone |
| `--project <name>` | Add to project board |
| `--template <name>` | Use issue template (e.g., `bug_report.md`) |

### With Template

```bash
gh issue create --template "bug_report.md" --title "<title>" --body "<body>"
```

Templates live in `.github/ISSUE_TEMPLATE/`. Always provide `--title` and `--body` alongside
`--template` to avoid interactive mode. Without them, `gh issue create` opens an editor that
Claude cannot use.

### Guardrails

- `--label` takes **one label per flag** — repeat the flag for multiple labels.
- `gh api` defaults to GET — use `--method POST` when creating via REST.

## list

List issues with optional filters.

```bash
# Open issues (default)
gh issue list

# With filters
gh issue list --state open --label bug --assignee @me --limit 50

# JSON output for processing
gh issue list --json number,title,state,labels,milestone,assignees
```

### Common Filters

| Filter | Flag |
| ------ | ---- |
| State | `--state open\|closed\|all` |
| Label | `--label <name>` (repeat for AND) |
| Assignee | `--assignee <user>` |
| Milestone | `--milestone <name>` |
| Author | `--author <user>` |
| Limit | `--limit <n>` (default 30) |

### Search (Cross-Repo)

```bash
gh search issues "query" --repo owner/repo --state open --label bug
```

## edit

Edit issue metadata.

```bash
# Add labels
gh issue edit <#> --add-label "priority:high" --add-label "bug"

# Remove label
gh issue edit <#> --remove-label "triage"

# Change assignee
gh issue edit <#> --add-assignee "username"

# Set milestone
gh issue edit <#> --milestone "v1.0"

# Add to project (requires project OAuth scope)
gh issue edit <#> --add-project "Sprint Board"
```

### Guardrails

- `--add-label` takes **one label per flag** — do not comma-separate.
- `--add-project` requires the `project` OAuth scope — run `gh auth refresh -s project` if needed.

## close

Close an issue.

```bash
# Close with comment
gh issue close <#> --comment "Fixed in PR #42"

# Close as not planned
gh issue close <#> --reason "not planned" --comment "Duplicate of #10"
```

### Valid Close Reasons

- `completed` (default)
- `not planned`
- `duplicate` — not a valid API reason; use `not planned` with a comment noting the duplicate

## comment

Add a comment to an issue.

```bash
gh issue comment <#> --body "Status update: working on this now"
```

## develop

Create a branch linked to an issue.

```bash
gh issue develop <#> --checkout
```

This creates a branch named after the issue and checks it out. Prefer this over manual
`git switch -c` when working from an issue, as it creates the GitHub branch-to-issue link
automatically.

## Reference

See [../references/issue.md](../references/issue.md) for transfer, pinning, linking, and advanced
issue patterns.
