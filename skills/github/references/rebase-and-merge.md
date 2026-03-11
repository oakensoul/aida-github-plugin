---
type: reference
title: "Rebase and Merge Recipes"
description: "Operational recipes for rebasing, merging, conflict resolution, and safe force-push workflows"
skill: github
category: rebase-and-merge
version: 1.0.0
---

# Rebase and Merge Recipes

Recipes for rebase and merge operations, conflict resolution, and the decision of when to use each.
For PR-level merge strategies (`--squash`, `--rebase`, `--merge`), see [pr.md](pr.md).

## Rebase Recipes

### Rebase onto Main

```bash
git fetch origin
git rebase origin/main
```

Always fetch first to rebase onto the current remote state, not a stale local copy.

### Rebase onto a Specific Branch

```bash
# Replay commits from feature-base..feature-branch onto main
git rebase --onto main feature-base feature-branch
```

Useful when a feature branch was started from another feature branch and needs to move to main.

### Abort a Conflicted Rebase

```bash
git rebase --abort
```

Returns the branch to its exact state before the rebase started. Safe to run at any point during
conflict resolution.

### Continue After Resolving Conflicts

```bash
# 1. Resolve conflicts in each file (remove markers)
# 2. Stage resolved files
git add <file>
# 3. Continue the rebase
git rebase --continue
```

Repeat for each commit that conflicts. The rebase replays commits one at a time.

### Skip a Commit During Rebase

```bash
git rebase --skip
```

Use when a commit is no longer relevant after rebasing (e.g., it duplicates a change already on the
target branch). The skipped commit is dropped from the branch.

### Push After Rebase

```bash
git push --force-with-lease
```

**NEVER use `--force`.** `--force-with-lease` fails if someone else pushed to the remote branch since
your last fetch, preventing you from overwriting their work.

## Merge Recipes

### Merge Main into Feature Branch

```bash
git fetch origin
git merge origin/main
```

Creates a merge commit on your feature branch. Safe for shared branches.

### Fast-Forward Only

```bash
git merge --ff-only origin/main
```

Fails if a fast-forward is not possible (i.e., your branch has diverged). Useful to confirm your branch
is a direct descendant of the target.

### No-Fast-Forward (Force Merge Commit)

```bash
git merge --no-ff <branch>
```

Forces a merge commit even when a fast-forward is possible. Creates an explicit record of the merge in
history.

### Abort a Conflicted Merge

```bash
git merge --abort
```

Returns the working tree to its pre-merge state. Safe to run at any point during conflict resolution.

### Continue After Resolving Merge Conflicts

```bash
# 1. Resolve conflicts in each file (remove markers)
# 2. Stage resolved files
git add <file>
# 3. Complete the merge
git commit
```

Unlike rebase, merge resolves all conflicts at once in a single commit.

## Conflict Resolution

Step-by-step procedure that applies to both rebase and merge conflicts.

```bash
# 1. Identify conflicting files
git status
# Look for "both modified" entries

# 2. Open conflicting files — look for markers:
#    <<<<<<< HEAD
#    (your changes)
#    =======
#    (incoming changes)
#    >>>>>>> branch-name

# 3. Edit to resolve: keep the correct code, remove all markers

# 4. Stage resolved files
git add <file>

# 5. Continue
git rebase --continue   # if rebasing
git commit              # if merging

# 6. If too complex — bail out and start over
git rebase --abort      # if rebasing
git merge --abort       # if merging
```

## When to Rebase vs Merge

Quick decision guide:

| Situation | Use | Why |
| --------- | --- | --- |
| Solo branch, few commits | Rebase | Clean linear history |
| Shared branch (others pushed to it) | Merge | **NEVER rebase shared branches** |
| Many commits (10+) | Merge | One conflict resolution vs potentially many |
| Want explicit merge record | Merge | `--no-ff` creates a merge commit |
| Updating feature branch from main | Either | Rebase if solo, merge if shared |
| When in doubt | Merge | Always safe, never rewrites history |

## Interactive Rebase Limitation

Claude **cannot** run `git rebase -i` with a manual editor — it requires interactive input.
Scripted non-interactive use via `GIT_SEQUENCE_EDITOR` is possible for simple cases.

**Alternatives:**

```bash
# Scripted squash (non-interactive) — squash last 3 commits
GIT_SEQUENCE_EDITOR="sed -i '' '2,\$s/pick/squash/'" git rebase -i HEAD~3

# Cherry-pick specific commits onto a new base (manual reorder)
git switch main
git switch -c feature-clean
git cherry-pick <sha1> <sha2> <sha3>

# For complex interactive rebase needs, advise the user:
# "Run `git rebase -i HEAD~N` in your terminal and [exact steps]"
```

Note: On macOS, `sed -i ''` requires the empty string argument. On Linux, use `sed -i`.

## Config-Aware Notes

- Check AIDA config `github.merge_strategy` for the project's preferred merge strategy before
  defaulting to rebase or merge. Some projects enforce squash-only or merge-commit-only workflows.
- When a project uses trunk-based development (`github.branching_model: trunk-based`), prefer
  rebase to keep history linear.

## Gotchas

- **NEVER `--force`, always `--force-with-lease`.** `--force` overwrites the remote unconditionally.
  `--force-with-lease` fails if someone else pushed since your last fetch, preventing data loss.
- **NEVER rebase a shared branch.** Rebase rewrites commit SHAs. Anyone else working on the branch will
  have divergent history and face painful reconciliation.
- **NEVER force push to main/master/production.** Not even with `--force-with-lease`.
- **After rebase:** `git push --force-with-lease` is required because SHAs changed. Normal push will be
  rejected.
- **After merge:** Normal `git push` works. No force needed because no history was rewritten.
- **Always `git fetch origin` before rebase or merge.** Without it, you rebase/merge against stale local
  refs, not the current remote state.
- **Rebase replays commits one at a time.** You may need to resolve the same conflict multiple times
  across commits. Merge resolves everything in one pass.

## Go Deeper

- [git rebase](https://git-scm.com/docs/git-rebase)
- [git merge](https://git-scm.com/docs/git-merge)
- [Git Branching - Rebasing](https://git-scm.com/book/en/v2/Git-Branching-Rebasing)
