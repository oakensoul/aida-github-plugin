---
type: handler
name: branch
title: Branch Operations
description: Handler for /github branch commands
skill: github
domain: branch
version: 1.0.0
---

# /github branch

## create

Create a new branch following the project's naming conventions.

### Steps

1. Check AIDA config for `github.branch_prefix.*` to determine the correct prefix
   (`feature/`, `fix/`, `chore/`).
1. Check AIDA config `github.worktree.enabled` — if true, create a worktree instead
   of a standard checkout.
1. If an issue number is provided, prefer `gh issue develop`:

```bash
# From an issue (creates branch and checks it out)
gh issue develop <#> --checkout
```

1. Otherwise, create manually with the correct prefix:

```bash
# Standard branch
git switch -c <prefix>/<description>

# With worktree (bare mode)
git worktree add ../<branch-name> -b <prefix>/<description>

# With worktree (traditional mode)
git worktree add .worktrees/<branch-name> -b <prefix>/<description>
```

1. Push and set upstream:

```bash
git push -u origin <branch>
```

### Naming Conventions

| Type | Prefix | Example |
| ---- | ------ | ------- |
| Feature | `feature/` | `feature/123-add-auth` |
| Bug fix | `fix/` | `fix/456-null-check` |
| Chore | `chore/` | `chore/update-deps` |

These are defaults — check AIDA config `github.branch_prefix.*` for project overrides.

### Config Dependencies

- `github.branch_prefix.feature` — prefix for feature branches
- `github.branch_prefix.fix` — prefix for fix branches
- `github.branch_prefix.chore` — prefix for chore branches
- `github.worktree.enabled` — use worktrees instead of checkout
- `github.worktree.mode` — `bare` (sibling dirs) or `traditional` (`.worktrees/` subdir)
- `github.branching_model` — overall branching strategy

## list

List branches with tracking info.

```bash
# Local branches with upstream tracking
git branch -vv

# Remote branches
git branch -r

# All branches (local + remote)
git branch -a
```

### Useful Filters

```bash
# Branches merged into main
git branch --merged main

# Branches NOT merged into main
git branch --no-merged main

# Recent branches by commit date
git branch --sort=-committerdate --format='%(refname:short) %(committerdate:relative)' | head -20
```

## cleanup

Remove stale and merged branches.

### Steps

1. Fetch and prune stale remote references:

```bash
git fetch origin --prune
```

1. Identify merged branches (safe to delete):

```bash
git branch --merged main | grep -v '^\*\|main'
```

1. Delete merged local branches:

```bash
git branch -d <branch>
```

1. If using worktrees, prune stale worktrees:

```bash
git worktree prune
git worktree list
```

### Guardrails

- Use `git branch -d` (lowercase) for merged branches — it refuses if unmerged.
- Use `git branch -D` (uppercase) only with explicit user approval for unmerged branches.
- **Never** `rm -rf` a worktree directory — always use `git worktree remove`.
- **Never** delete `main` or the default branch.
- **Never** `git push --force` — always use `git push --force-with-lease`.
- **Never** force-push to `main` or the default branch.

## Reference

See [../references/branching.md](../references/branching.md) for worktree workflows, branching model
comparisons, and naming conventions.
