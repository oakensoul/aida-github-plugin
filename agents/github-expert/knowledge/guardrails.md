---
type: reference
title: GitHub and Git Guardrails
description: Anti-patterns, gotchas, and deprecated commands to avoid
agent: github-expert
category: guardrails
last_updated: "2026-02-24"
---

# GitHub and Git Guardrails

Everything that goes wrong with git and GitHub CLI operations and how to avoid it. Organized by
severity — data loss first, annoyances last. For each rule: what not to do, what to do instead,
and why in one sentence.

## 1. Data Loss and Irreversible Operations

These mistakes destroy work. There is no undo.

### Force Push to Protected Branches

- **Never:** `git push --force origin main` (or master, release, production)
- **Instead:** Only force push feature branches, always with `git push --force-with-lease origin <branch>`
- **Why:** `--force` overwrites remote history unconditionally; `--force-with-lease` fails if someone
  else pushed since your last fetch, preventing silent data loss.

### Force Push to Shared Branches

- **Never:** Force push any branch that other people have checked out or are working on.
- **Instead:** Check if the branch is shared first: `git branch -r | grep <branch>` and coordinate
  with collaborators before rewriting history.
- **Why:** Force pushing a shared branch forces everyone else to manually recover their local state,
  often losing uncommitted work in the process.

### Hard Reset Without Verification

- **Never:** `git reset --hard` without first verifying what you are about to discard.
- **Instead:** Run `git status` and `git stash` (or `git stash --include-untracked`) before resetting.
  If you need to undo a reset, use `git reflog` within 30 days.
- **Why:** Hard reset permanently discards all uncommitted changes in the working tree and index —
  there is no way to recover unstaged work after the fact.

### Worktree Directory Deletion

- **Never:** `rm -rf <worktree-path>` to remove a worktree directory.
- **Instead:** `git worktree remove <path>` (or `git worktree remove --force <path>` if dirty).
- **Why:** `rm -rf` leaves orphaned registrations in `.git/worktrees/`, causing errors on subsequent
  worktree operations and potentially locking branches as "already checked out."

### Deleting Unmerged Branches Without Backup

- **Never:** `git branch -D <branch>` without confirming the commits exist elsewhere (remote, PR, tag).
- **Instead:** Verify the branch is pushed (`git log origin/<branch>...<branch>`) or that the PR is
  merged before force-deleting.
- **Why:** `-D` bypasses the "not fully merged" safety check — if those commits only exist locally,
  they are gone (recoverable via reflog only within the retention window).

## 2. Metadata Corruption

These mistakes break GitHub state — PRs show wrong status, automation doesn't trigger, tracking
data is lost. The repository still works, but the GitHub layer is damaged.

### PR Merging via Local Git

- **Never:** `git merge --squash <branch> && git push` to merge a pull request.
- **Instead:** `gh pr merge <number> --squash --delete-branch` (or `--merge` / `--rebase`).
- **Why:** Local merge bypasses GitHub's PR API — the PR shows gray "Closed" instead of purple
  "Merged," linked issues don't auto-close, status checks and branch protection events don't fire,
  and automation (Actions on `pull_request.closed` with `merged == true`) never triggers. This
  cannot be fixed after the fact.

### Branch Deletion After Squash Merge

- **Never:** `git branch -d <branch>` after a squash merge (it will fail with "not fully merged").
- **Instead:** `git branch -D <branch>` (force delete).
- **Why:** Squash merge creates a new commit on the target branch — git cannot see that the feature
  branch's commits are "contained" in the target, so `-d` (safe delete) refuses. The `-D` flag is
  safe here because the squashed content already exists on the target branch.

### Stale Remote Refs After Push or Merge

- **Never:** Assume local tracking refs are current after push, merge, or PR operations.
- **Instead:** Run `git fetch origin` (or `git fetch origin --prune` to also clean deleted remote
  branches) after any operation that changes the remote.
- **Why:** Stale refs cause incorrect ahead/behind counts, shell prompts showing phantom unpushed
  commits, and `git log origin/main..HEAD` returning misleading results.

### Deleting Worktree Branch Before Removing Worktree

- **Never:** Delete a branch while a worktree still has it checked out.
- **Instead:** Remove the worktree first (`git worktree remove <path>`), then delete the branch.
- **Why:** Git refuses to delete a branch checked out in any worktree. If you force it, the worktree
  enters a detached HEAD state and the registration becomes inconsistent.

## 3. Deprecated and Changed Commands

Commands that used to work differently, no longer exist, or have been replaced. Using the old form
produces errors, deprecation warnings, or silently wrong behavior.

### Projects v2 CLI

- **Never:** Assume `gh project` doesn't exist and default to raw GraphQL for all project operations.
- **Instead:** Use `gh project list`, `gh project view`, `gh project item-list`, and other
  `gh project` subcommands for standard operations. Fall back to `gh api graphql` only for bulk
  mutations, complex field queries, or operations the CLI doesn't cover.
- **Why:** The `gh project` command set was added to the GitHub CLI and covers most common project
  board operations. The earlier guidance (including in the github-workflow skill) that says
  "gh project command doesn't exist" is outdated. Using raw GraphQL for simple operations is
  unnecessary complexity.

### gh pr merge Flags

- **Never:** Use `gh pr merge --delete-branch` alone without specifying a merge method.
- **Instead:** Always specify the merge method explicitly: `gh pr merge --squash --delete-branch`,
  `gh pr merge --merge --delete-branch`, or `gh pr merge --rebase --delete-branch`.
- **Why:** Without an explicit method, `gh` may prompt interactively (which fails in automation) or
  use the repository's default, which may not match your intent.

### gh repo clone vs git clone

- **Never:** Use `git clone` with full GitHub URLs when `gh` is available and authenticated.
- **Instead:** `gh repo clone owner/repo` — shorter, uses existing auth, sets up remote correctly.
- **Why:** `gh repo clone` configures the upstream remote automatically for forks and respects your
  SSH/HTTPS preference from `gh auth`.

## 4. Claude-Specific Limitations

Operations that require interactive terminal input. Claude cannot type keystrokes mid-stream,
select lines in an editor, or respond to prompts during execution.

### Interactive Rebase

- **Never:** Run `git rebase -i` or `git rebase --interactive` directly.
- **Instead:** Plan the rebase steps, then either: (a) use non-interactive equivalents like
  `git rebase --onto`, individual `git cherry-pick` commands, or `GIT_SEQUENCE_EDITOR` scripting;
  or (b) advise the user on the exact interactive rebase commands to run manually.
- **Why:** Interactive rebase opens an editor for commit selection — Claude cannot interact with it.

### Interactive Staging

- **Never:** Run `git add -i` or `git add -p` (interactive or patch mode).
- **Instead:** Stage specific files by name (`git add <file>`), or advise the user to run patch
  mode manually if partial staging is needed.
- **Why:** Patch mode requires per-hunk y/n input that Claude cannot provide.

### Prompts Requiring User Input

- **Never:** Run commands that may prompt for confirmation without suppressing the prompt
  (e.g., `gh pr merge` without `--yes` in contexts where it would prompt).
- **Instead:** Use flags that bypass prompts: `--yes`, `--confirm`, `--force`, or pipe `yes |`
  where safe and appropriate.
- **Why:** Any mid-execution prompt causes the command to hang until timeout.

## 5. Configuration Awareness

Assumptions that break when project configuration doesn't match defaults.

### Branching Model Assumptions

- **Never:** Hardcode branch naming conventions (e.g., always using `feature/`, `bugfix/`).
- **Instead:** Read AIDA config for configured branch prefixes and naming patterns. Fall back to
  sensible defaults only when no config exists.
- **Why:** Different projects use different conventions — trunk-based development may not use prefixes
  at all, while gitflow uses a strict prefix taxonomy.

### Worktree Path Assumptions

- **Never:** Assume worktrees live in `.worktrees/` or assume they are sibling directories.
- **Instead:** Check AIDA config for worktree mode:
  - **Bare mode** (`use_bare_repo: true`): worktrees are siblings (e.g., `../<branch-dir>/`)
  - **Traditional mode** (`use_bare_repo: false`): worktrees are in `.worktrees/` subdirectory
- **Why:** Using the wrong path creates worktrees in unexpected locations, confuses cleanup scripts,
  and breaks relative path references in build tooling.

### Merge Strategy Assumptions

- **Never:** Default to squash merge without checking project preferences.
- **Instead:** Read AIDA config for the project's preferred merge strategy. Different repos may
  prefer merge commits (for full history) or rebase (for linear history).
- **Why:** Using the wrong merge strategy creates inconsistent history and may violate team
  conventions or break CI pipelines that expect a specific commit structure.

## 6. Common Mistakes

Patterns that aren't catastrophic but waste time, create confusion, or require cleanup.

### Forgetting to Fetch Before Comparing

- **Never:** Run `git log origin/main..HEAD` or check ahead/behind counts without fetching first.
- **Instead:** `git fetch origin && git log origin/main..HEAD`
- **Why:** Without a fresh fetch, you are comparing against a stale snapshot of the remote — your
  counts and diffs will be wrong, leading to incorrect decisions about rebasing or merging.

### Creating PRs Without Pushing

- **Never:** Run `gh pr create` before pushing the branch to the remote.
- **Instead:** `git push -u origin <branch> && gh pr create`
- **Why:** `gh pr create` will push for you in some cases, but it is better to be explicit — you
  control the remote branch name and can verify the push succeeded before creating the PR.

### Using git log Without Limiting Output

- **Never:** Run `git log` without `--oneline`, `-n`, or other limiters when you only need a summary.
- **Instead:** `git log --oneline -20` or `git log --oneline main..HEAD` for bounded output.
- **Why:** Unlimited log output on a large repository can produce thousands of lines, causing
  truncation, slow rendering, and wasted context window in AI-assisted workflows.

### Ignoring Exit Codes

- **Never:** Chain git commands with `;` when the second depends on the first succeeding.
- **Instead:** Use `&&` to short-circuit on failure: `git fetch origin && git rebase origin/main`
- **Why:** A failed fetch followed by a rebase against stale refs silently produces wrong results.

### Orphaned Worktrees After Branch Deletion

- **Never:** Delete a remote branch (via PR merge or manual delete) and forget about local worktrees
  pointing to that branch.
- **Instead:** After merging, always run `git worktree list` to identify and remove stale worktrees,
  then `git worktree prune` to clean up any orphaned registrations.
- **Why:** Orphaned worktrees accumulate over time, consume disk space, and cause confusing errors
  when trying to create new worktrees or branches with the same name.

## Quick Reference: The Five Rules

When in doubt, remember these five rules that prevent the most damage:

1. **PRs merge through GitHub, not git.** Always `gh pr merge`, never local merge for PRs.
2. **Worktrees remove through git, not rm.** Always `git worktree remove`, never `rm -rf`.
3. **Force push uses lease, not force.** Always `--force-with-lease`, never `--force`.
4. **Fetch before you compare.** Always `git fetch origin` before ahead/behind checks.
5. **Read config before you assume.** Check AIDA config for branching, merge, and worktree settings.
