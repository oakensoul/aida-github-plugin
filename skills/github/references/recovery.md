---
type: reference
title: "Recovery and Rescue Recipes"
description: "Operational recipes for stash, reflog recovery, cherry-pick, bisect, reset, and revert via git CLI"
skill: github
category: recovery
version: 1.0.0
---

# Recovery and Rescue Recipes

Lean recipe reference for git recovery operations: stash, reflog, cherry-pick, bisect, reset, and revert.
Organized by task.

## Stash

### Stash with Message

```bash
git stash push -m "WIP: description of in-progress work"
```

### Stash Including Untracked Files

```bash
git stash --include-untracked
```

Without `--include-untracked`, new files not yet `git add`-ed are left behind.

### List Stashes

```bash
git stash list
```

### Pop Most Recent

```bash
git stash pop
```

Applies and removes the top stash. Fails if applying causes conflicts — use `git stash apply` instead
to keep the stash safe while resolving.

### Apply Specific Stash

```bash
git stash apply stash@{1}
```

Applies without removing from the stash list. Use when you want to apply the same stash to multiple branches.

### View Stash Contents

```bash
git stash show -p stash@{0}
```

### Drop Specific Stash

```bash
git stash drop stash@{0}
```

## Reflog Recovery

The reflog records every HEAD movement locally. It is the primary tool for recovering from mistakes.

### View Recent HEAD Movements

```bash
git reflog -20
```

### Find a Lost Commit

```bash
git reflog | grep "commit message fragment"
```

### Recover After Bad Reset

```bash
# 1. Find the SHA before the reset
git reflog

# 2. Look for the entry just before the reset operation
# 3. Soft reset to restore (keeps changes staged)
git reset --soft <sha>
```

### Recover Deleted Branch

```bash
# 1. Find the last checkout of the deleted branch
git reflog | grep "checkout: moving from <branch-name>"

# 2. Recreate from the SHA shown in that reflog entry
git switch -c <branch-name> <sha>
```

## Cherry-Pick

### Pick Single Commit

```bash
git cherry-pick <sha>
```

### Pick a Range

```bash
git cherry-pick <start>..<end>
```

Range is **exclusive** of `<start>`, **inclusive** of `<end>`. To include `<start>`, use `<start>^..<end>`.

### Pick Without Committing

```bash
git cherry-pick <sha> --no-commit
```

Stages the changes without creating a commit. Useful when combining multiple picks into one commit.

### Abort Conflicted Pick

```bash
git cherry-pick --abort
```

### Continue After Resolving Conflicts

```bash
# 1. Resolve conflicts in the affected files
# 2. Stage resolved files
git add <file>

# 3. Continue
git cherry-pick --continue
```

## Bisect (Find the Commit That Broke It)

### Guided Workflow

```bash
# Start bisect
git bisect start

# Mark current as bad
git bisect bad HEAD

# Mark known good point (tag, commit, etc.)
git bisect good v1.0.0

# Git checks out a midpoint — test your reproduction case, then:
git bisect good   # if this commit is fine
git bisect bad    # if this commit has the bug

# Repeat until git identifies the first bad commit
# When done:
git bisect reset  # returns to original branch
```

### Automated Bisect

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
git bisect run <test-script>
```

The script must exit `0` for good, non-zero for bad. Example: `git bisect run pytest tests/auth_test.py`.

## Reset (Rewrite History)

### Soft Reset

```bash
git reset --soft HEAD~1
```

Undoes the commit, keeps all changes **staged**. Use when you want to amend or restructure a commit.

### Mixed Reset (Default)

```bash
git reset HEAD~1
```

Undoes the commit, keeps changes **unstaged**. Use when you want to selectively re-stage files.

### Hard Reset

```bash
git reset --hard HEAD~1
```

**DANGEROUS** — discards the commit and all changes permanently. Always verify with `git status` and
`git stash` before running.

## Revert (Safe Undo)

### Revert a Commit

```bash
git revert <sha>
```

Creates a new commit that undoes the specified change. Safe for shared branches — does not rewrite history.

### Revert Without Committing

```bash
git revert <sha> --no-commit
```

Stages the inverse changes without creating a commit. Useful when combining multiple reverts.

### Revert a Merge Commit

```bash
git revert -m 1 <merge-sha>
```

The `-m 1` flag specifies the parent to keep (usually the branch you merged **into**).

## Gotchas

- **`git reset --hard` permanently discards uncommitted work.** Always `git stash` first. After a hard
  reset, the only recovery path is `git reflog` (and only if the commits existed).
- **Reflog entries expire.** Default: 90 days for reachable commits, 30 days for unreachable. Recover
  sooner rather than later.
- **Cherry-pick range `A..B` excludes A.** Use `A^..B` to include commit A in the range.
- **`git revert` is safe, `git reset` rewrites history.** Revert creates a new commit (safe for shared
  branches). Reset moves HEAD backward (may require force push on shared branches).
- **After `git reset --hard`, reflog is the only recovery.** The reflog entry exists only if the commits
  were previously recorded locally.

## Go Deeper

- [git reflog](https://git-scm.com/docs/git-reflog)
- [git stash](https://git-scm.com/docs/git-stash)
- [git cherry-pick](https://git-scm.com/docs/git-cherry-pick)
- [git bisect](https://git-scm.com/docs/git-bisect)
- [git reset](https://git-scm.com/docs/git-reset)
- [git revert](https://git-scm.com/docs/git-revert)
