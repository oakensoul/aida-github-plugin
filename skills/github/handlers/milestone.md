---
type: handler
name: milestone
title: Milestone Operations
description: Handler for /github milestone commands
skill: github
domain: milestone
version: 1.0.0
---

# /github milestone

There is no `gh milestone` CLI command — all milestone operations use `gh api` with the REST
endpoint.

## create

Create a milestone.

```bash
gh api repos/{owner}/{repo}/milestones --method POST \
  -f title="v2.0" \
  -f description="Version 2.0 release" \
  -f due_on="2026-06-01T00:00:00Z" \
  -f state="open"
```

### Fields

| Field | Required | Format |
| ----- | -------- | ------ |
| `title` | Yes | String |
| `description` | No | String (markdown) |
| `due_on` | No | ISO 8601 datetime (`YYYY-MM-DDT00:00:00Z`) |
| `state` | No | `open` (default) or `closed` |

### Guardrails

- `gh api` defaults to GET — always specify `--method POST` for creates.
- `due_on` must be ISO 8601 with time component — `2026-06-01` alone is not valid.

## list

List milestones.

```bash
# Open milestones
gh api repos/{owner}/{repo}/milestones --jq '.[] | {number, title, state, due_on, open_issues, closed_issues}'

# Include closed
gh api repos/{owner}/{repo}/milestones?state=all --jq '.[] | {number, title, state, due_on}'

# Just titles and progress
gh api repos/{owner}/{repo}/milestones --jq '.[] | "\(.title): \(.closed_issues)/\(.open_issues + .closed_issues) done"'
```

## close

Close a milestone.

```bash
gh api repos/{owner}/{repo}/milestones/<number> --method PATCH -f state="closed"
```

### Steps

1. Find the milestone number:

```bash
gh api repos/{owner}/{repo}/milestones --jq '.[] | {number, title}'
```

1. Close it:

```bash
gh api repos/{owner}/{repo}/milestones/<number> --method PATCH -f state="closed"
```

## edit

Edit a milestone's title, description, or due date.

```bash
# Update due date
gh api repos/{owner}/{repo}/milestones/<number> --method PATCH \
  -f due_on="2026-07-01T00:00:00Z"

# Update description
gh api repos/{owner}/{repo}/milestones/<number> --method PATCH \
  -f description="Updated scope for v2.0"
```

## delete

Delete a milestone.

```bash
gh api repos/{owner}/{repo}/milestones/<number> --method DELETE
```

### Guardrails

- Deleting a milestone **does not** delete associated issues — they become unassigned from the
  milestone.
- Confirm with the user before deleting, as this is not reversible.
