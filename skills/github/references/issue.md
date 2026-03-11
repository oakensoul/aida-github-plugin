---
type: reference
title: "Issue Operations"
description: "Recipes for creating, managing, filtering, and closing GitHub issues via the gh CLI"
skill: github
category: issues
version: 1.0.0
---

# Issue Operations

Recipes for the full issue lifecycle: create, filter, edit, close, branch, and transfer.

## Recipes

### 1. Create Issue

```bash
gh issue create --title "Auth fails on token refresh" --body "Steps to reproduce..." \
  --label bug --assignee @me --milestone "v1.0"
```

Multiple labels: `--label bug --label "high priority"` (repeat the flag, no comma-separated list).

Add to a project at creation time:

```bash
gh issue create --title "..." --body "..." --project "Sprint Board"
```

### 2. Create from Template

```bash
gh issue create --template "bug_report.md"
```

Opens the template with pre-filled sections. Combine with `--title` and `--label` to skip prompts:

```bash
gh issue create --template "feature_request.md" --title "Add dark mode" --label enhancement
```

List available templates: check `.github/ISSUE_TEMPLATE/` in the repo.

### 3. List with Filters

```bash
# Open bugs assigned to me in a milestone
gh issue list --state open --label bug --assignee @me --milestone "v1.0" --limit 50

# All closed issues by a specific author
gh issue list --state closed --author octocat --limit 30

# Issues mentioning a search term
gh issue list --search "auth token expired" --state open
```

### 4. List with JSON and jq

```bash
# Full structured output
gh issue list --json number,title,state,labels,milestone,assignees,url --limit 50

# Extract bug issue numbers
gh issue list --json number,labels \
  --jq '.[] | select(.labels[].name == "bug") | .number'

# Tabular output: number, title, milestone
gh issue list --json number,title,milestone \
  --jq '.[] | [.number, .title, (.milestone.title // "none")] | @tsv'

# Count issues by label
gh issue list --json labels --limit 200 \
  --jq '[.[].labels[].name] | group_by(.) | map({label: .[0], count: length}) | sort_by(-.count)'
```

**Key JSON fields:** `number`, `title`, `state`, `author`, `labels`, `milestone`, `assignees`, `url`,
`createdAt`, `closedAt`, `body`, `comments`, `projectItems`.

### 5. Edit Issue

```bash
# Add and remove labels
gh issue edit 42 --add-label "in-progress" --remove-label "triage"

# Reassign
gh issue edit 42 --add-assignee "teammate" --remove-assignee @me

# Change milestone and title
gh issue edit 42 --milestone "v2.0" --title "Updated title"

# Add to project
gh issue edit 42 --add-project "Sprint Board"
```

### 6. Close with Comment

```bash
gh issue close 42 --comment "Fixed in #55"

# Close as not-planned
gh issue close 42 --reason "not planned" --comment "Duplicate of #10"
```

Valid `--reason` values: `completed` (default), `not planned`.

### 7. Create Branch from Issue

```bash
# Create and checkout a branch linked to issue 42
gh issue develop 42 --checkout

# Specify a custom branch name
gh issue develop 42 --name "fix/42-auth-refresh" --checkout

# Create in a specific base branch
gh issue develop 42 --base develop --checkout
```

Default branch name follows the pattern `<number>-<slugified-title>`. The branch is linked to the issue
automatically in the GitHub UI sidebar.

### 8. Comment on Issue

```bash
gh issue comment 42 --body "Reproduced on macOS 15. Stack trace attached."
```

**Note**: `gh issue comment --editor` opens an interactive editor — Claude cannot use this.
Always use `--body` for non-interactive execution.

### 9. Transfer Issue

```bash
gh issue transfer 42 destination-org/destination-repo
```

Transfers the issue to another repository in the same owner or organization. Labels, milestones, and
project assignments do not carry over.

### 10. Pin and Unpin

```bash
gh issue pin 42
gh issue unpin 42
```

Repos support up to 3 pinned issues. Pinning requires write access.

## Gotchas

- **Auto-close from PRs:** Use `Closes #123`, `Fixes #123`, or `Resolves #123` in the PR body. GitHub
  closes the linked issue when the PR merges into the default branch. Only works for the default branch
  unless configured otherwise.
- **`gh issue develop` branch naming:** Creates a linked branch. If the repo has branch naming rules, pass
  `--name` explicitly to conform. Check AIDA config `github.branch_prefix.*` for prefix conventions.
- **Cross-repo search:** `gh issue list` only searches the current repo. To search across repos, use
  `gh search issues "query" --owner <org>` instead.
- **Labels must exist:** `--label "new-label"` fails if the label does not exist in the repo. Create it
  first with `gh label create`.
- **Milestone by title:** `--milestone` takes the milestone title string, not a number.

## Config-Aware Notes

- **`github.pr.auto_link_issues`:** When `true`, the agent should scan commit messages and branch names for
  issue references and include `Closes #N` in PR bodies automatically.
- **`github.branch_prefix.*`:** When using `gh issue develop`, consider passing `--name` with the configured
  prefix (e.g., `fix/42-description` instead of the default `42-description`).

## Go Deeper

- [gh issue create](https://cli.github.com/manual/gh_issue_create)
- [gh issue list](https://cli.github.com/manual/gh_issue_list)
- [gh issue edit](https://cli.github.com/manual/gh_issue_edit)
- [gh issue develop](https://cli.github.com/manual/gh_issue_develop)
- [gh search issues](https://cli.github.com/manual/gh_search_issues)
