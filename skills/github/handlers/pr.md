---
type: handler
name: pr
title: Pull Request Operations
description: Handler for /github pr commands
skill: github
domain: pr
version: 1.0.0
---

# /github pr

## create

Create a pull request from the current branch.

### Steps

1. Verify the current branch is not `main` (or the default branch).
1. Check for unpushed commits: `git log origin/<branch>..HEAD --oneline`. If any, push first:
   `git push -u origin <branch>`.
1. Check AIDA config `github.pr.auto_link_issues` — if enabled, scan branch name and recent commits
   for issue references (e.g., `#42`, `issue-42`) and include `Closes #42` in the body.
1. Check AIDA config `github.pr.default_reviewers` — if set, add `--reviewer` flags.
1. Check AIDA config `github.merge_strategy` — if `squash`, consider `--squash` label conventions.

```bash
gh pr create --title "<title>" --body "<body>" [--label <label>] [--reviewer <reviewer>] [--draft]
```

### Options

| Flag | Purpose |
| ---- | ------- |
| `--title "..."` | PR title (required) |
| `--body "..."` | PR body with issue links |
| `--draft` | Create as draft PR |
| `--label <name>` | Add label (repeat for multiple) |
| `--reviewer <user>` | Request reviewer (repeat for multiple) |
| `--assignee @me` | Self-assign |
| `--milestone <name>` | Associate with milestone |
| `--base <branch>` | Target branch (default: repo default) |

### Config Dependencies

- `github.pr.default_reviewers` — auto-added as `--reviewer`
- `github.pr.auto_link_issues` — scan for issue refs in branch/commits
- `github.merge_strategy` — informs squash vs merge conventions

## list

List open pull requests.

```bash
gh pr list --json number,title,state,reviewDecision,headRefName --jq '.[] | "\(.number) [\(.reviewDecision // "PENDING")] \(.title)"'
```

### Common Filters

```bash
# By author
gh pr list --author @me

# By label
gh pr list --label bug

# By state
gh pr list --state merged --limit 10

# Full status dashboard
gh pr status
```

## merge

Merge a pull request.

### Steps

1. Check AIDA config `github.merge_strategy` for the project's preferred strategy.
1. Verify CI is green: `gh pr checks <#>`.
1. Merge with the configured strategy:

```bash
# Squash (default for most projects)
gh pr merge <#> --squash --delete-branch

# Merge commit
gh pr merge <#> --merge --delete-branch

# Rebase
gh pr merge <#> --rebase --delete-branch

# Auto-merge when CI passes
gh pr merge <#> --squash --delete-branch --auto
```

1. Post-merge cleanup:

```bash
git switch main && git pull origin main
git fetch origin --prune
```

### Config Dependencies

- `github.merge_strategy` — determines `--squash`, `--merge`, or `--rebase`

### Guardrails

- **Always** use `gh pr merge`, never `git merge --squash` for PRs.
- **Always** use `--delete-branch` to clean up.
- Never force-merge over failed CI without explicit user approval.

## review

Review a pull request.

```bash
# Approve
gh pr review <#> --approve

# Request changes
gh pr review <#> --request-changes --body "Please fix..."

# Comment only
gh pr review <#> --comment --body "Looks good, minor suggestion..."
```

## edit

Edit PR metadata (labels, reviewers, title, milestone).

```bash
# Add label (one per flag, no commas)
gh pr edit <#> --add-label "bug" --add-label "priority:high"

# Add reviewer
gh pr edit <#> --add-reviewer "username"

# Change title
gh pr edit <#> --title "New title"

# Set milestone
gh pr edit <#> --milestone "v1.0"

# Update PR branch to latest base
gh pr update-branch <#>
```

### Guardrails

- `--add-label` takes **one label per flag** — do not comma-separate.

## view

View PR details and status.

```bash
# Summary
gh pr view <#>

# JSON fields
gh pr view <#> --json title,state,reviews,mergeable,statusCheckRollup

# Check CI status
gh pr checks <#>

# View diff
gh pr diff <#>
```

## ready

Mark a draft PR as ready for review.

```bash
gh pr ready <#>
```

## Reference

See [../references/pr.md](../references/pr.md) for advanced recipes, full JSON field list, and
linked issue patterns.

### Guardrails

- **Never** `git push --force` — always use `git push --force-with-lease`.
- **Never** force-push to `main` or the default branch.
