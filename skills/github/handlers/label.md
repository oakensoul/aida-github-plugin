---
type: handler
name: label
title: Label Operations
description: Handler for /github label commands
skill: github
domain: label
version: 1.0.0
---

# /github label

## sync

Synchronize labels to match the project's label taxonomy.

<!-- SCRIPT: scripts/gh_label_sync.py sync — diff current vs taxonomy, create/update/report -->

### Recommended

```bash
python scripts/gh_label_sync.py sync --dry-run    # preview changes
python scripts/gh_label_sync.py sync              # apply changes
```

Use `--file path/to/labels.json` for a custom taxonomy. Use `--json` for machine-readable output.

### From a Source Repo

Clone all labels from a source repository (creates or updates with `--force`):

```bash
gh label clone source-org/source-repo --force
```

### Manual Sync

Check AIDA config `github.label_taxonomy` for the project's label set. If "standard", apply the
standard AIDA label taxonomy.

1. List current labels:

```bash
gh label list --json name,color,description --limit 200
```

1. Create or update each label:

```bash
gh label create "<name>" --color <HEX> --description "<desc>" --force
```

The `--force` flag updates the label if it already exists.

### Config Dependencies

- `github.label_taxonomy` — which label set to sync (`standard` or custom path)

## create

Create a single label.

```bash
gh label create "<name>" --color <HEX> --description "<description>"
```

### Common Label Colors

| Category | Color | Example Labels |
| -------- | ----- | -------------- |
| Bug/Error | `d73a4a` | `bug`, `error`, `crash` |
| Feature | `0075ca` | `feature`, `enhancement` |
| Priority | `e4e669` | `priority:high`, `priority:low` |
| Status | `0e8a16` | `ready`, `in-progress`, `blocked` |
| Type | `5319e7` | `documentation`, `test`, `chore` |
| Size | `c5def5` | `size:xs`, `size:s`, `size:m`, `size:l` |

### Guardrails

- Color is a 6-character hex **without** the `#` prefix.

## list

List all labels in the repository.

```bash
# Human-readable
gh label list

# JSON for processing
gh label list --json name,color,description --limit 200

# Filter by search term
gh label list --json name,color,description --jq '.[] | select(.name | startswith("priority"))'
```

## edit

Rename or update a label.

```bash
# Rename
gh label edit "old-name" --name "new-name"

# Change color
gh label edit "bug" --color FF0000

# Update description
gh label edit "bug" --description "Something is broken"
```

## delete

Delete a label.

```bash
gh label delete "label-name" --yes
```

### Guardrails

- Deleting a label removes it from all issues and PRs — this is not reversible.
- Confirm with the user before deleting labels that are in active use.
