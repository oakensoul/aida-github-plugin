---
type: reference
title: "Branch and Worktree Recipes"
description: "Operational recipes for branch creation, naming, cleanup, and worktree management"
skill: github
category: branching
version: 1.0.0
---

# Branch and Worktree Recipes

Lean recipe reference for branch lifecycle and worktree operations. Organized by task.

## Branch Recipes

### 1. Create and Switch

```bash
git switch -c feature/123-add-auth
```

Prefer `git switch -c` over `git checkout -b`. Both work, but `switch` is purpose-built for branching.

### 2. Create Branch from Issue

```bash
gh issue develop 42 --checkout
```

Auto-generates a branch name from the issue title, links it in the GitHub UI sidebar, and checks it out.
To override the name with project conventions:

```bash
gh issue develop 42 --name "fix/42-auth-refresh" --checkout
```

**Config-aware:** Check `github.branch_prefix.*` and pass `--name` with the configured prefix when the
default slug does not match project conventions.

### 3. Push and Set Upstream

```bash
git push -u origin feature/123-add-auth
```

The `-u` flag sets upstream tracking so subsequent `git push` and `git pull` work without arguments.

### 4. Show Current Branch

```bash
git branch --show-current
```

### 5. List with Tracking Info

```bash
git branch -vv
```

Shows each local branch, its tracking remote, and ahead/behind counts.

### 6. Check Ahead/Behind

```bash
git fetch origin && git rev-list --left-right --count origin/main...HEAD
```

Returns two numbers: commits on `origin/main` not in `HEAD` (behind), and commits on `HEAD` not in
`origin/main` (ahead).

### 7. Delete Local Branch After Squash Merge

```bash
git branch -D feature/123-add-auth
```

**Must use `-D` (force), not `-d`.** After a squash merge, git cannot detect that the branch was merged
because the squashed commit has a different SHA than the branch commits. `-d` will refuse with
"not fully merged."

### 8. Delete Remote Branch

```bash
git push origin --delete feature/123-add-auth
```

Prefer `gh pr merge --delete-branch` during PR merge to handle this automatically.

### 9. Clean Stale Remote Refs

```bash
git fetch origin --prune
```

Removes local remote-tracking references for branches that no longer exist on the remote. Run after
merges to keep `git branch -vv` output clean.

## Naming Conventions

**Pattern:** `<prefix>/<issue-number>-<short-description>`

| Prefix | Usage | Example |
| ------ | ----- | ------- |
| `feature/` | New features | `feature/123-add-auth` |
| `fix/` | Bug fixes | `fix/456-null-pointer-crash` |
| `chore/` | Maintenance, config, CI | `chore/789-update-deps` |
| `hotfix/` | Urgent production fixes | `hotfix/fix-payment-timeout` |
| `release/` | Release preparation | `release/1.2.0` |

**Config-aware:** Check AIDA config `github.branch_prefix.feature`, `github.branch_prefix.fix`, and
`github.branch_prefix.chore` for project-specific overrides. `hotfix/` and `release/` are conventional
defaults (not configurable). Some projects use `feat/` instead of `feature/`, or omit issue numbers.
Check `github.branching_model` to determine which branch types are relevant for the project.

## Worktree Recipes

### 1. Create Worktree for New Branch

```bash
git worktree add ../feature-123 -b feature/123-add-auth
```

Creates a new branch and checks it out in a sibling directory.

### 2. Create Worktree for Existing Branch

```bash
git worktree add ../hotfix-path hotfix/fix-payment-timeout
```

### 3. List Worktrees

```bash
git worktree list
```

Shows all worktrees with their paths, HEAD commits, and branch names.

### 4. Remove Worktree

```bash
git worktree remove ../feature-123
```

**Never** `rm -rf` a worktree directory. That leaves orphaned registrations in `.git/worktrees/`.

### 5. Force Remove Dirty Worktree

```bash
git worktree remove --force ../feature-123
```

Use when the worktree has uncommitted changes you want to discard.

### 6. Prune Orphaned Worktrees

```bash
git worktree prune
```

Cleans up registrations for worktrees whose directories were already removed (e.g., by accidental
`rm -rf` or filesystem cleanup).

## Worktree Modes

Check `github.worktree.enabled` in AIDA config before defaulting to worktree operations.

### Bare Mode (`github.worktree.mode: bare`)

Repository cloned with `git clone --bare`. No default checkout exists. All work happens in worktrees
created as sibling directories:

```text
project.git/           # bare repo (no working tree)
  main/                # worktree for main
  feature-123/         # worktree for feature branch
  hotfix-payment/      # worktree for hotfix
```

```bash
git clone --bare git@github.com:org/repo.git repo.git
cd repo.git
git worktree add ../main main
git worktree add ../feature-123 -b feature/123-add-auth
```

### Traditional Mode (`github.worktree.mode: traditional`)

Normal clone with worktrees created alongside the main checkout:

```text
project/               # normal clone (main checked out)
  .worktrees/          # or sibling directories
    feature-123/
    hotfix-payment/
```

```bash
git worktree add .worktrees/feature-123 -b feature/123-add-auth
```

## Gotchas

- **Never `rm -rf` a worktree.** Use `git worktree remove`. Manual deletion leaves orphaned entries in
  `.git/worktrees/` that cause "already checked out" errors on future operations.
- **After squash merge, use `-D` not `-d`.** Git cannot detect the branch was merged because squashing
  rewrites history into a single new commit.
- **Remove worktree BEFORE deleting its branch.** If the branch is deleted first, the worktree still
  references it and `git worktree remove` may require `--force`.
- **Always prune after accidents.** If a worktree directory was removed outside of git, run
  `git worktree prune` to clean up the stale registration.
- **`git fetch origin --prune` after merges.** Without this, `git branch -vv` shows stale
  `[origin/feature-123: gone]` references indefinitely.

## Go Deeper

- [git worktree](https://git-scm.com/docs/git-worktree)
- [git switch](https://git-scm.com/docs/git-switch)
- [git branch](https://git-scm.com/docs/git-branch)
- [gh issue develop](https://cli.github.com/manual/gh_issue_develop)
