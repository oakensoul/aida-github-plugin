---
type: reference
title: "Pull Request Recipes"
description: "Operational recipes for PR creation, merging, reviewing, and management via gh CLI"
skill: github
category: pr
version: 1.0.0
---

# Pull Request Recipes

Lean recipe reference for `gh pr` operations. Organized by task.

## Create PR with Linked Issue

```bash
gh pr create \
  --title "feat: add authentication module" \
  --body "Closes #123" \
  --reviewer alice,bob \
  --label feature --label auth \
  --milestone v2.0 \
  --assignee @me \
  --draft
```

Omit `--draft` when the PR is ready for review immediately.

**Config-aware:** Check `github.pr.default_reviewers` for configured reviewers. When
`github.pr.auto_link_issues` is enabled, the agent should detect issue numbers from the branch name
and include `Closes #N` in the body automatically.

## Create from Template

```bash
# Use a specific PR template
gh pr create --template TEMPLATE_NAME

# Auto-fill title and body from commit messages
gh pr create --fill

# Auto-fill title from first commit, open editor for body
gh pr create --fill-first
```

Templates live in `.github/PULL_REQUEST_TEMPLATE/` or `.github/pull_request_template.md`.

## Merge with Strategy

```bash
# Squash merge (most common — clean linear history)
gh pr merge 42 --squash --delete-branch

# Merge commit (preserves full history)
gh pr merge 42 --merge --delete-branch

# Rebase (linear history, preserves individual commits)
gh pr merge 42 --rebase --delete-branch

# Auto-merge when checks pass
gh pr merge 42 --squash --delete-branch --auto
```

**Always specify strategy explicitly.** Omitting the flag triggers an interactive prompt that fails in
automation. For repos with merge queues enabled, omit the strategy flag — the queue handles it.

**Config-aware:** Check `github.merge_strategy` for the project default (squash, merge, or rebase).

## Custom Merge Commit Message

```bash
gh pr merge 42 --squash \
  --subject "feat: add authentication module" \
  --body "Closes #123. Adds OAuth2 flow with PKCE support." \
  --delete-branch
```

Use `--subject` and `--body` to override the default squash commit message.

## View PR with JSON Fields

```bash
# Key fields for decision-making
gh pr view 42 --json title,state,reviews,mergeable,statusCheckRollup

# Full detail set
gh pr view 42 --json number,title,state,author,baseRefName,headRefName,labels,reviewDecision,\
mergeable,isDraft,url,createdAt,updatedAt,reviews,statusCheckRollup
```

### Key JSON Fields

| Field | Description |
| ----- | ----------- |
| `number` | PR number |
| `title` | PR title |
| `state` | OPEN, CLOSED, MERGED |
| `author` | Author login and ID |
| `baseRefName` | Target branch (e.g., main) |
| `headRefName` | Source branch |
| `labels` | Array of label objects |
| `reviewDecision` | APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED, or empty |
| `mergeable` | MERGEABLE, CONFLICTING, UNKNOWN |
| `isDraft` | Boolean |
| `url` | Web URL |
| `createdAt` | ISO timestamp |
| `updatedAt` | ISO timestamp |
| `reviews` | Array of review objects with state and author |
| `statusCheckRollup` | Array of CI check results |

## List with Filters and jq

```bash
# List open PRs with key fields
gh pr list --json number,title,author,createdAt --jq '.[] | "\(.number) \(.title) (\(.author.login))"'

# Filter by label
gh pr list --json number,title,labels \
  --jq '.[] | select(.labels[].name == "bug") | "\(.number) \(.title)"'

# Filter by review status
gh pr list --json number,title,reviewDecision \
  --jq '.[] | select(.reviewDecision == "APPROVED") | .number'

# List draft PRs
gh pr list --json number,title,isDraft --jq '.[] | select(.isDraft) | "\(.number) \(.title)"'
```

## Review

```bash
# Approve
gh pr review 42 --approve

# Approve with comment
gh pr review 42 --approve --body "LGTM, nice refactor"

# Request changes
gh pr review 42 --request-changes --body "Need error handling in auth flow"

# Comment without approving or blocking
gh pr review 42 --comment --body "Consider extracting this into a helper"
```

## Edit Metadata

```bash
# Add labels and reviewers
gh pr edit 42 --add-label "needs-review" --add-label "security" --add-reviewer charlie

# Set milestone
gh pr edit 42 --milestone "v2.0"

# Remove label
gh pr edit 42 --remove-label "wip"

# Change title
gh pr edit 42 --title "feat: add OAuth2 authentication"

# Change base branch
gh pr edit 42 --base develop
```

## Check CI Status

```bash
# Summary view
gh pr checks 42

# Watch until complete (blocks)
gh pr checks 42 --watch

# Fail if any check fails (useful in scripts)
gh pr checks 42 --fail-fast
```

## Revert a Merged PR

```bash
# Find the merge commit on main
git log --oneline main -10

# Revert the merge commit (for squash merges, it's a regular commit)
git revert <sha>

# For actual merge commits (non-squash), specify parent
git revert -m 1 <sha>

# Push and create a revert PR
git push -u origin revert/42-auth-module
gh pr create --title "revert: remove auth module (reverts #42)" --body "Reverts #42. Reason: ..."
```

## Gotchas

- **Always `gh pr merge`, never `git merge --squash`.** The git approach breaks GitHub metadata: the PR
  shows gray "Closed" instead of purple "Merged", linked issues don't auto-close, and automation
  workflows keyed on `pull_request.merged` don't trigger.
- **After merge:** Run `git fetch origin` to update local tracking refs. Without this, `git branch -vv`
  shows stale remote references.
- **Always specify merge method explicitly.** Omitting `--squash`/`--merge`/`--rebase` triggers an
  interactive prompt that fails in automation and scripts.
- **Merge queues:** When a repo uses merge queues, omit the strategy flag — the queue configuration
  determines the merge method.

## Go Deeper

- [gh pr create](https://cli.github.com/manual/gh_pr_create)
- [gh pr merge](https://cli.github.com/manual/gh_pr_merge)
- [gh pr view](https://cli.github.com/manual/gh_pr_view)
- [gh pr list](https://cli.github.com/manual/gh_pr_list)
- [gh pr review](https://cli.github.com/manual/gh_pr_review)
- [gh pr edit](https://cli.github.com/manual/gh_pr_edit)
- [gh pr checks](https://cli.github.com/manual/gh_pr_checks)
