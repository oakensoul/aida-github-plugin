---
type: reference
title: Common GitHub and Git Operations
description: Top 30-40 commands and patterns for daily git and GitHub CLI work
agent: github-expert
category: operations
last_updated: "2026-02-24"
---

# Common GitHub and Git Operations

The commands and patterns an expert uses daily, organized by task. Exact flags, correct syntax, brief notes
only where non-obvious. For guardrails on what NOT to do, see `guardrails.md`. For choosing between
approaches, see `decisions.md`.

## Cross-Cutting Notes

Before diving into commands, know these patterns that apply everywhere:

- **`--json` vs `--format json`:** PR, issue, run, and label commands use `--json field1,field2`. Project
  commands use `--format json`. Mixing them up produces errors.
- **`@me` convention:** Works in `--assignee`, `--owner`, `--author` across `gh` commands.
- **`--repo` / `-R`:** Available on virtually every `gh` command to target a different repository without
  changing directories. Example: `gh pr list -R owner/repo`.
- **Project OAuth scope:** All `gh project` commands require the `project` scope. If you get permission
  errors: `gh auth refresh -s project`.
- **Common aliases:** `gh pr new` = `gh pr create`, `gh issue new` = `gh issue create`,
  `gh issue ls` = `gh issue list`, `gh run ls` = `gh run list`, `gh project ls` = `gh project list`.

## 1. Pull Requests

### Create

```bash
gh pr create --title "Add auth module" --body "Closes #123" \
  --label feature --reviewer team-lead --assignee @me \
  --milestone v2.0 --draft
```

- Mention `Closes #123` (or `Fixes #123`) in the body to auto-link and auto-close the issue on merge.
- `--fill` populates title/body from commits. `--fill-first` uses only the first commit.
- `--template TEMPLATE` uses a PR template file. `--dry-run` previews without creating.
- Adding to projects requires the `project` OAuth scope.

### List

```bash
gh pr list --state open --author @me --label bug --base main --limit 30

# Structured output with filtering
gh pr list --json number,title,state,reviewDecision,url \
  --jq '.[] | select(.reviewDecision == "APPROVED")'

# Draft PRs only
gh pr list --draft
```

Key `--json` fields: `number`, `title`, `state`, `author`, `baseRefName`, `headRefName`, `labels`,
`reviewDecision`, `mergeable`, `isDraft`, `url`, `createdAt`, `updatedAt`, `reviews`,
`statusCheckRollup`.

### Merge

```bash
# Squash merge (most common) with branch cleanup
gh pr merge 42 --squash --delete-branch

# Merge commit (multi-author features)
gh pr merge 42 --merge --delete-branch

# Rebase (clean linear history)
gh pr merge 42 --rebase --delete-branch

# Auto-merge when checks pass
gh pr merge 42 --squash --delete-branch --auto

# Custom commit message
gh pr merge 42 --squash --subject "feat: add auth" --body "Closes #123"
```

- Always specify merge method explicitly. Omitting it may prompt interactively (fails in automation).
- For repos with merge queues, no strategy flag is needed.

### View and Check

```bash
# Summary
gh pr view 42

# Structured data
gh pr view 42 --json title,state,reviews,mergeable,statusCheckRollup

# CI status
gh pr checks 42
```

### Review

```bash
gh pr review 42 --approve
gh pr review 42 --request-changes --body "Needs error handling in auth.py"
gh pr review 42 --comment --body "Looks good overall, minor suggestions inline"
```

### Edit

```bash
gh pr edit 42 --add-label "needs-review" --add-reviewer "alice" --milestone "v1.0"
```

### Diff and Revert

```bash
# View PR diff locally
gh pr diff 42

# Revert a merged PR (creates a new revert PR)
gh pr create --title "Revert: Add auth module" --body "Reverts #42"
```

For the revert body, `git revert` the merge commit first, push the branch, then create the PR.

## 2. Issues

### Create

```bash
gh issue create --title "Login fails on Safari" --body "Steps to reproduce..." \
  --label bug --assignee @me --milestone v1.0

# With template
gh issue create --template "bug_report.md"
```

- Adding to projects requires `project` scope.

### List

```bash
gh issue list --state open --label bug --assignee @me --milestone "v1.0" --limit 50

# Structured output
gh issue list --json number,title,state,labels,milestone,url \
  --jq '.[] | select(.milestone.title == "v1.0")'
```

Key `--json` fields: `number`, `title`, `state`, `author`, `labels`, `milestone`, `assignees`, `url`,
`createdAt`, `closedAt`, `body`, `comments`, `projectItems`.

### Edit and Close

```bash
gh issue edit 15 --add-label "priority-high" --remove-label "triage" --add-assignee "bob"

# Close with comment
gh issue close 15 --comment "Fixed in #42"

# Link issue to PR (create a branch from issue)
gh issue develop 15 --checkout
```

## 3. Branches and Worktrees

### Branch Operations

```bash
# Create and switch
git switch -c feature/123-add-auth

# Create from issue (sets up tracking automatically)
gh issue develop 15 --checkout

# List with remote tracking info
git branch -vv

# List remote branches
git branch -r

# Push new branch and set upstream
git push -u origin feature/123-add-auth

# Delete local branch (after squash merge, use -D)
git branch -D feature/123-add-auth

# Delete remote branch
git push origin --delete feature/123-add-auth

# Clean stale remote tracking refs
git fetch origin --prune

# Show current branch name
git branch --show-current

# Check ahead/behind (fetch first!)
git fetch origin && git rev-list --left-right --count origin/main...HEAD
```

### Worktree Operations

```bash
# List active worktrees
git worktree list

# Create worktree for a new branch
git worktree add ../hotfix-branch -b hotfix/fix-login

# Create worktree for an existing branch
git worktree add ../review-branch feature/review-target

# Remove worktree (always use this, never rm -rf)
git worktree remove ../hotfix-branch

# Clean orphaned registrations
git worktree prune
```

Check AIDA config for worktree mode (bare vs traditional) before creating. See `guardrails.md` for
worktree safety rules.

## 4. Project Boards

All project commands require `project` OAuth scope: `gh auth refresh -s project`.

Project commands use `--format json`, NOT `--json <fields>`.

### List and View

```bash
# List your projects
gh project list --owner @me --format json

# List items in a project
gh project item-list 5 --owner @me --format json --limit 100
```

### Add Items

```bash
# Add issue or PR to project by URL
gh project item-add 5 --owner @me --url https://github.com/owner/repo/issues/42
```

### Update Fields

```bash
# List available fields (to get field IDs and option IDs)
gh project field-list 5 --owner @me --format json

# Set a single-select field
gh project item-edit --id ITEM_ID --project-id PROJECT_ID \
  --field-id FIELD_ID --single-select-option-id OPTION_ID
```

For bulk operations or complex field queries, fall back to `gh api graphql`. See `decisions.md` for the
CLI vs API decision tree.

## 5. Releases and Tags

### Create a Release

```bash
# Auto-generate release notes from merged PRs
gh release create v1.2.0 --generate-notes --title "v1.2.0"

# Pre-release / draft
gh release create v2.0.0-rc.1 --prerelease --draft --generate-notes

# With specific range for release notes
gh release create v1.2.0 --generate-notes --notes-start-tag v1.1.0

# Upload assets (positional args after tag)
gh release create v1.2.0 --generate-notes dist/*.tar.gz "docs/guide.pdf#User Guide"

# Target a specific branch
gh release create v1.2.0 --target release/1.2 --generate-notes
```

- `--verify-tag` aborts if the tag does not already exist.
- `--fail-on-no-commits` prevents empty releases when no changes have landed.
- Append `#label` to asset filenames for display names.

### List and View

```bash
gh release list --limit 10
gh release view v1.2.0
```

### Tag Operations

```bash
# Annotated tag (preferred for releases)
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# List tags sorted by date
git tag --sort=-creatordate | head -20

# Delete a tag (local and remote)
git tag -d v1.2.0-bad
git push origin --delete v1.2.0-bad
```

### Version Bump Pattern

```bash
# Check latest release tag
gh release list --limit 1

# View commits since last tag to decide bump level
git log --oneline v1.1.0..HEAD
```

## 6. Labels and Milestones

### Labels

```bash
# Create (--force updates if exists)
gh label create "priority/high" --color FF0000 --description "High priority" --force

# List all
gh label list --json name,color,description --limit 100

# Edit
gh label edit "old-name" --name "new-name" --color 00FF00

# Delete
gh label delete "stale-label" --yes

# Clone labels from another repo
gh label clone source-org/source-repo --force
```

### Milestones (REST API -- no gh CLI command)

```bash
# Create
gh api repos/{owner}/{repo}/milestones --method POST \
  -f title="v2.0" -f due_on="2026-06-01T00:00:00Z" -f description="Q2 release"

# List
gh api repos/{owner}/{repo}/milestones --jq '.[] | {number, title, state, open_issues}'

# Close
gh api repos/{owner}/{repo}/milestones/3 --method PATCH -f state="closed"
```

## 7. CI/CD (Actions)

### List Runs

```bash
# Recent runs for a workflow
gh run list --workflow ci.yml --branch main --limit 10

# Failed runs only
gh run list --status failure --limit 10

# Structured output
gh run list --json databaseId,displayTitle,conclusion,headBranch,url --limit 20
```

### View and Debug

```bash
# View failed logs (the key debugging flag)
gh run view 12345 --log-failed

# Full output with all job logs
gh run view 12345 --log

# Structured with job details
gh run view 12345 --json jobs
```

### Trigger and Manage

```bash
# Manually trigger a workflow
gh workflow run ci.yml --ref main -f param=value

# Enable / disable
gh workflow enable ci.yml
gh workflow disable ci.yml

# Re-run failed jobs
gh run rerun 12345 --failed
```

## 8. History and Recovery

### Log and Diff

```bash
# Bounded commit history
git log --oneline -20
git log --oneline main..HEAD

# With graph
git log --oneline --graph --all -30

# Diff staged changes
git diff --cached

# Diff between branches
git diff main..HEAD

# Diff with stat summary
git diff main..HEAD --stat
```

### Stash

```bash
git stash
git stash --include-untracked
git stash list
git stash pop
git stash apply stash@{1}
git stash drop stash@{0}
git stash show -p stash@{0}
```

### Cherry-Pick

```bash
# Single commit
git cherry-pick abc1234

# Range (exclusive start, inclusive end)
git cherry-pick abc1234..def5678

# Without committing (stage only)
git cherry-pick abc1234 --no-commit
```

### Bisect

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# Git checks out a midpoint — test, then:
git bisect good   # or: git bisect bad
# Repeat until found, then:
git bisect reset
```

### Reflog (Recovery)

```bash
# Show recent HEAD movements
git reflog -20

# Recover a lost commit
git reflog | grep "commit message fragment"
git cherry-pick <sha>

# Undo a reset
git reflog
git reset --soft <sha-before-reset>
```

### Rebase (Non-Interactive)

```bash
# Rebase onto main
git fetch origin && git rebase origin/main

# Rebase onto specific branch
git rebase --onto main feature-base feature-branch

# Abort a conflicted rebase
git rebase --abort

# Continue after resolving conflicts
git rebase --continue
```

Claude cannot run interactive rebase (`-i`). See `guardrails.md` for alternatives.

## 9. Search

```bash
# Search issues across a repo
gh search issues "auth bug" --repo owner/repo --state open --label bug

# Search code
gh search code "handleAuth" --repo owner/repo --language python

# Search merged PRs
gh search prs "refactor" --repo owner/repo --state merged

# Search repos
gh search repos "cli tool" --language go --stars ">100"
```

## 10. Admin

### Secrets and Variables

```bash
# Set a secret (reads from stdin or prompt)
gh secret set API_KEY
gh secret set API_KEY --body "value"
gh secret set API_KEY < secret.txt

# List secrets
gh secret list

# Set a variable
gh variable set ENVIRONMENT --body "production"

# List variables
gh variable list
```

### Authentication

```bash
# Check current auth status
gh auth status

# Refresh with additional scopes
gh auth refresh -s project

# Switch between accounts
gh auth switch
```

### Repository Configuration

```bash
# Clone (uses existing auth, sets up remotes correctly)
gh repo clone owner/repo

# Fork and clone
gh repo fork owner/repo --clone

# View repo info
gh repo view --json name,defaultBranchRef,description

# List rulesets
gh ruleset list
gh ruleset view 1
```

## Common Multi-Step Patterns

### Full PR Workflow (Branch to Merge)

```bash
git switch -c feature/123-add-auth
# ... make changes ...
git add <files> && git commit -m "feat: add auth module"
git push -u origin feature/123-add-auth
gh pr create --title "Add auth module" --body "Closes #123" --label feature --assignee @me
# After approval:
gh pr merge 123 --squash --delete-branch
git switch main && git pull origin main
```

### Sync Feature Branch with Main

```bash
git fetch origin && git rebase origin/main
# If conflicts: resolve, then git rebase --continue
git push --force-with-lease
```

### Investigate and Rerun Failed CI

```bash
gh run list --status failure --limit 5 --json databaseId,displayTitle,headBranch
gh run view <id> --log-failed
gh run rerun <id> --failed
```

### Clean Up After Merge

```bash
git switch main && git pull origin main
git branch -D feature/123-add-auth
git fetch origin --prune
git worktree list    # check for orphaned worktrees
git worktree prune   # clean up any found
```

## Quick Reference: Output Format Cheat Sheet

| Command Family | Structured Output Flag | Example                                          |
| -------------- | ---------------------- | ------------------------------------------------ |
| `gh pr`        | `--json field1,field2` | `gh pr list --json number,title`                 |
| `gh issue`     | `--json field1,field2` | `gh issue list --json number,state`              |
| `gh run`       | `--json field1,field2` | `gh run list --json databaseId,conclusion`       |
| `gh label`     | `--json field1,field2` | `gh label list --json name,color`                |
| `gh release`   | `--json field1,field2` | `gh release list --json tagName,isPrerelease`    |
| `gh project`   | `--format json`        | `gh project list --format json`                  |
| `gh api`       | Returns JSON natively  | `gh api repos/{owner}/{repo}/milestones`         |

Filter JSON output with `--jq` on any command that supports `--json`:

```bash
gh pr list --json number,title,labels --jq '.[] | select(.labels[].name == "bug") | .number'
```
