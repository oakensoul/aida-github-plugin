---
type: reference
title: "Project Board Operations"
description: "Recipes for GitHub Projects v2 — list, add, edit fields, archive, and GraphQL fallback"
skill: github
category: projects
version: 1.0.0
---

# Project Board Operations

Recipes for GitHub Projects (v2). All project commands use `--format json` for structured output,
**not** `--json field1,field2`. Requires `project` OAuth scope — if you get permission errors:

```bash
gh auth refresh -s project
```

## Recipes

### 1. List Projects

```bash
gh project list --owner @me --format json
```

For an org: `--owner org-name`. Output includes project number, title, URL, and state.

### 2. List Project Items

```bash
gh project item-list 5 --owner @me --format json --limit 100
```

Returns all items (issues, PRs, draft items) with their item IDs, titles, and field values.
Increase `--limit` for large boards (default is 30).

### 3. Add Item by URL

```bash
gh project item-add 5 --owner @me --url https://github.com/owner/repo/issues/42
```

Works with both issue and PR URLs. Returns the new item ID.

### 4. Create Draft Item

```bash
gh project item-create 5 --owner @me --title "Spike: evaluate auth library" --body "Compare options"
```

Draft items are not linked to an issue or PR. Useful for notes, spikes, and ad-hoc tasks.

### 5. List Fields (Required Before Editing)

```bash
gh project field-list 5 --owner @me --format json
```

Returns field IDs, field names, field types, and option IDs for single-select fields.
**Always run this first** before editing item fields — IDs are project-specific.

Extract a specific field's option IDs:

```bash
gh project field-list 5 --owner @me --format json | jq '.fields[] | select(.name == "Status") | .options'
```

### 6. Edit Item Field (Single-Select)

```bash
gh project item-edit --id ITEM_ID --project-id PROJECT_ID \
  --field-id FIELD_ID --single-select-option-id OPTION_ID
```

Common use: moving an item between status columns (e.g., "Todo" to "In Progress").

Typical workflow:

```bash
# Step 1: Get project ID
gh project list --owner @me --format json | jq '.projects[] | select(.number == 5) | .id'

# Step 2: Get field ID and option IDs
gh project field-list 5 --owner @me --format json | jq '.fields[] | select(.name == "Status")'

# Step 3: Get item ID
gh project item-list 5 --owner @me --format json | jq '.items[] | select(.content.number == 42) | .id'

# Step 4: Edit
gh project item-edit --id ITEM_ID --project-id PROJECT_ID \
  --field-id FIELD_ID --single-select-option-id OPTION_ID
```

### 7. Edit Item Field (Text, Number, Date)

```bash
# Text field
gh project item-edit --id ITEM_ID --project-id PROJECT_ID \
  --field-id FIELD_ID --text "value"

# Number field
gh project item-edit --id ITEM_ID --project-id PROJECT_ID \
  --field-id FIELD_ID --number 5

# Date field
gh project item-edit --id ITEM_ID --project-id PROJECT_ID \
  --field-id FIELD_ID --date "2026-03-15"

# Iteration field
gh project item-edit --id ITEM_ID --project-id PROJECT_ID \
  --field-id FIELD_ID --iteration-id ITERATION_ID
```

### 8. Create Project

```bash
gh project create --owner @me --title "Q1 Sprint Board" --format json
```

Returns the new project number and URL.

### 9. Archive Item

```bash
gh project item-archive 5 --owner @me --id ITEM_ID
```

Archived items are hidden from default views but not deleted. Undo with `gh project item-archive --undo`.

### 10. Link Project to Repository

```bash
gh project link 5 --owner @me --repo owner/repo
```

Links the project to a repository so it appears in the repo's "Projects" tab. Unlink with
`gh project unlink`.

## GraphQL Fallback

The `gh project` CLI covers most operations. Fall back to `gh api graphql` when you need:

- Bulk field updates across many items
- Operations not yet exposed by the CLI
- Complex filtering or aggregation

### Get Project Node ID

```bash
gh project list --owner @me --format json | jq '.projects[] | select(.title == "Q1 Sprint Board") | .id'
```

### Example: Bulk Update via GraphQL

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) {
      projectV2Item { id }
    }
  }' \
  -f projectId="PVT_..." \
  -f itemId="PVTI_..." \
  -f fieldId="PVTSSF_..." \
  -f optionId="..."
```

Wrap in a loop for bulk operations. Each mutation is one API call.

### Example: Query All Items with Field Values

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            id
            fieldValues(first: 20) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2SingleSelectField { name } }
                }
                ... on ProjectV2ItemFieldTextValue {
                  text
                  field { ... on ProjectV2Field { name } }
                }
              }
            }
            content {
              ... on Issue { number title }
              ... on PullRequest { number title }
            }
          }
        }
      }
    }
  }' \
  -f projectId="PVT_..."
```

## Gotchas

- **OAuth scope required.** All `gh project` commands need the `project` scope. Run
  `gh auth refresh -s project` if you get 403 or "insufficient scopes" errors.
- **`--format json`, not `--json`.** Project commands use `--format json`. Using `--json field1,field2`
  produces an error. This is the opposite of `gh pr`/`gh issue`/`gh run` commands.
- **Field and option IDs are project-specific.** Never hardcode them. Always look up with
  `gh project field-list` first. IDs look like `PVTSSF_...` (fields) and UUIDs (options).
- **Item IDs differ from issue/PR numbers.** An item ID (`PVTI_...`) is the project-board-specific
  identifier, not the issue number. Pipe `item-list --format json` to system `jq` to map between them.
- **`gh project` CLI exists now.** Do not default to raw GraphQL for standard CRUD operations.
  Use the CLI first, GraphQL only for bulk or unsupported operations.
- **Draft items have no linked content.** They lack `.content.number` — filter accordingly when
  scripting with `jq`.

## Go Deeper

- [gh project](https://cli.github.com/manual/gh_project)
- [Planning and tracking with projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Projects GraphQL API](https://docs.github.com/en/graphql/reference/objects#projectv2)
