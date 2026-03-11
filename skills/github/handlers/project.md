---
type: handler
name: project
title: Project Board Operations
description: Handler for /github project commands
skill: github
domain: project
version: 1.0.0
---

# /github project

**Prerequisites**: All `gh project` commands require the `project` OAuth scope.
If you get permission errors: `gh auth refresh -s project`.

**Important**: Project commands use `--format json` (not `--json`). They do **not** support
`--jq` — pipe to system `jq` instead.

## status

View project board status with item counts by field value (e.g., status column).

<!-- SCRIPT: scripts/gh_project.py status — multi-step: get project number, list items, aggregate by status -->

### Manual Steps

1. Find the project number:

```bash
gh project list --owner @me --format json | jq '.projects[] | {number, title}'
```

1. List items with their fields:

```bash
gh project item-list <#> --owner @me --format json | jq '.items[] | {title, status: .status}'
```

1. Summarize by status:

```bash
gh project item-list <#> --owner @me --format json | jq '[.items[] | .status] | group_by(.) | map({status: .[0], count: length})'
```

### Options

| Flag | Purpose |
| ---- | ------- |
| `--owner @me` | Your projects (or org name) |
| `--format json` | Machine-readable output |

## add

Add an issue or PR to a project board.

```bash
gh project item-add <project-number> --owner @me --url <issue-or-pr-url>
```

The URL must be a full GitHub URL like `https://github.com/owner/repo/issues/42`.

## edit

Edit a project item's field value (e.g., move between status columns).

<!-- SCRIPT: scripts/gh_project.py edit-field — 4-step process, prime Python script candidate -->

### Manual Steps

This is a multi-step process — each step requires output from the previous:

1. Get the project ID:

```bash
gh project list --owner @me --format json | jq '.projects[] | select(.number == <#>) | .id'
```

1. Get the field ID:

```bash
gh project field-list <#> --owner @me --format json | jq '.fields[] | select(.name == "<field>") | .id'
```

1. Get the item ID:

```bash
gh project item-list <#> --owner @me --format json | jq '.items[] | select(.title == "<title>") | .id'
```

1. Edit the field:

```bash
# For single-select fields (like Status)
gh project item-edit --id <item-id> --project-id <project-id> --field-id <field-id> --single-select-option-id <option-id>

# For text fields
gh project item-edit --id <item-id> --project-id <project-id> --field-id <field-id> --text "<value>"

# For date fields
gh project item-edit --id <item-id> --project-id <project-id> --field-id <field-id> --date "2026-04-01"
```

### Guardrails

- Each step depends on the previous step's output — do not guess IDs.
- Single-select fields require the **option ID**, not the option name.
  Get options: `gh project field-list <#> --owner @me --format json | jq '.fields[] | select(.name == "Status") | .options'`

## create

Create a new project.

```bash
gh project create --owner @me --title "Project Name"
```

## view

View project details.

```bash
# Summary view
gh project view <#> --owner @me

# With items
gh project item-list <#> --owner @me --format json | jq '.items[] | {title, status: .status, type: .type}'
```

## Reference

See [../references/project.md](../references/project.md) for field types, GraphQL fallback patterns,
and project template workflows.
