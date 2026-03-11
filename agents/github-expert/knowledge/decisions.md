---
type: reference
title: GitHub and Git Decision Frameworks
description: Decision matrices for merge strategy, branching model, CLI vs API, and other common choices
agent: github-expert
category: decisions
last_updated: "2026-02-24"
---

# GitHub and Git Decision Frameworks

Five decision frameworks for situations where the right git or GitHub action is not obvious. Each framework
is self-contained: gather context, evaluate factors, choose an approach.

## 1. Merge Strategy Selection

Choose squash, merge commit, or rebase when merging a pull request via `gh pr merge`.

### Context Signals to Check

```bash
# How many commits on this branch?
git log --oneline main..HEAD | wc -l

# How many distinct authors?
git log --format='%ae' main..HEAD | sort -u | wc -l

# Are commit messages clean?
git log --oneline main..HEAD

# Is this branch shared (pushed by others)?
git log --format='%ae' main..HEAD | sort -u
```

### Decision Matrix

| Factor                   | Squash                    | Merge Commit                | Rebase                     |
| ------------------------ | ------------------------- | --------------------------- | -------------------------- |
| History cleanliness      | Clean, linear             | Preserves full branch shape | Clean, linear              |
| Bisectability            | One commit per PR         | Full granularity            | Full granularity           |
| Author attribution       | Single author on result   | All authors preserved       | All authors preserved      |
| CI on intermediate       | N/A (one commit)          | Intermediate may fail       | Each commit must pass      |
| Commit discipline needed | Low (messages rewritten)  | Medium                      | High (each commit atomic)  |
| Revert granularity       | Revert entire PR at once  | Revert individual commits   | Revert individual commits  |
| Team size fit            | Any                       | Larger teams                | Solo or disciplined teams  |
| Default recommendation   | **Most repositories**     | Multi-author features       | Solo work, clean history   |

### When to Override the Project Default

Even when a project has a configured default merge strategy, override it in these cases:

**Project defaults to squash, but use merge commit when:**

- PR has commits from 3+ authors (preserves attribution)
- PR represents a large feature where individual commits tell a meaningful story
- Downstream consumers need to cherry-pick individual changes

**Project defaults to merge commit, but use squash when:**

- PR has a messy commit history (fixup commits, "WIP", "oops" messages)
- PR is a single logical change spread across many incremental commits
- Branch has merge commits from repeated `git merge main` updates

**Project defaults to squash, but use rebase when:**

- Each commit is atomic, tested, and has a clear message
- The team practices trunk-based development with small, frequent PRs
- You need each commit individually bisectable in the target branch

### Decision Steps

1. Check project config for default merge strategy
2. Count commits: 1 commit = squash is natural; 2-5 = evaluate quality; 6+ = likely squash
3. Count authors: multiple authors = prefer merge commit for attribution
4. Read commit messages: clean and atomic = rebase or merge; messy = squash
5. Check for override conditions above
6. Execute: `gh pr merge --squash`, `gh pr merge --merge`, or `gh pr merge --rebase`

## 2. Branching Model Selection

Choose the branching model for a repository or team.

### Context Signals to Check

```bash
# What branches exist?
git branch -r | grep -v HEAD

# How often do releases happen? (check tags)
git tag --sort=-creatordate | head -20

# Are there release branches?
git branch -r | grep -E 'release|hotfix'

# Is there a develop branch?
git branch -r | grep develop
```

### Decision Matrix

| Factor                 | Trunk-Based          | GitHub Flow          | Gitflow               | Custom / Hybrid       |
| ---------------------- | -------------------- | -------------------- | --------------------- | --------------------- |
| Team size              | Any                  | Small to medium      | Medium to large       | Any                   |
| Release cadence        | Continuous           | Frequent (days)      | Scheduled (weeks)     | Varies                |
| Deployment automation  | Required             | Recommended          | Optional              | Varies                |
| Feature flags          | Required for WIP     | Optional             | Not needed            | Depends on cadence    |
| Testing infrastructure | Strong CI required   | Good CI recommended  | CI per branch         | Varies                |
| Compliance / audit     | Tag-based tracking   | PR-based tracking    | Release branch audit  | Custom gates          |
| Monorepo suitability   | Excellent            | Good                 | Poor (branch sprawl)  | Depends               |
| Polyrepo suitability   | Good                 | Excellent            | Good                  | Depends               |
| Cognitive overhead     | Low                  | Low                  | High                  | Medium to high        |
| Recommendation         | **Default choice**   | Good for most teams  | Only if required      | When others don't fit |

### Migration Paths

**Gitflow to GitHub Flow:**

1. Stop creating new `release/*` branches
2. Merge `develop` into `main` and delete `develop`
3. Set `main` as the default branch with required PR reviews
4. Ship from `main` using tags for release tracking
5. Use hotfix branches off `main` instead of off `release/*`

**GitHub Flow to Trunk-Based:**

1. Adopt feature flags for work-in-progress features
2. Reduce PR size (target < 200 lines changed)
3. Increase CI speed (target < 10 minutes)
4. Enable auto-merge on green CI
5. Move toward merging multiple times per day

**Gitflow to Trunk-Based (gradual):**

1. First migrate to GitHub Flow (steps above)
2. Stabilize on GitHub Flow for 1-2 months
3. Then migrate to trunk-based (steps above)
4. Do not attempt direct gitflow-to-trunk — the cultural shift is too large

### Decision Steps

1. Check for existing branching model in project config
2. Identify release cadence: continuous = trunk-based, scheduled = evaluate gitflow need
3. Check for feature flag infrastructure: present = trunk-based viable
4. Check for compliance requirements: strict audit = gitflow may be needed
5. Assess CI maturity: fast CI enables trunk-based, slow CI favors longer-lived branches
6. Default to trunk-based unless specific factors push toward alternatives

## 3. CLI vs API Decision Tree

Choose between `gh <command>`, `gh <command> --json`, `gh api` (REST), or `gh api graphql` (GraphQL).

### Context Signals to Check

```bash
# Does a gh subcommand exist for this resource?
gh help <resource>   # e.g., gh help pr, gh help issue, gh help project

# What JSON fields does the CLI expose?
gh pr list --json   # (no value) prints available field names

# Does the REST endpoint exist?
gh api repos/{owner}/{repo}/<resource> --method GET 2>&1 | head -5
```

### Decision Tree

```text
1. Is there a gh <command> for this operation?
   |
   +-- YES: Does it support all the fields/options you need?
   |   |
   |   +-- YES --> Use gh <command>
   |   |            Example: gh pr create --title "..." --body "..."
   |   |
   |   +-- NO: Does --json + --jq cover the missing fields?
   |       |
   |       +-- YES --> Use gh <command> --json field1,field2 --jq '.[]'
   |       |            Example: gh pr list --json number,title,labels --jq '.[] | select(.labels[].name == "bug")'
   |       |
   |       +-- NO --> Fall through to step 2
   |
   +-- NO: Fall through to step 2
   |
2. Is this a simple CRUD operation on a single resource?
   |
   +-- YES --> Use gh api (REST)
   |            Example: gh api repos/{owner}/{repo}/milestones --method POST -f title="v2.0"
   |
   +-- NO: Fall through to step 3
   |
3. Do you need nested data, bulk queries, or mutations on Projects v2?
   |
   +-- YES --> Use gh api graphql
   |            Example: gh api graphql -f query='{ repository(owner:"o", name:"r") { ... } }'
   |
   +-- NO --> Re-evaluate. You likely missed a CLI command in step 1.
```

### Specific Resource Guidance

| Resource          | CLI Available?      | Notes                                                            |
| ----------------- | ------------------- | ---------------------------------------------------------------- |
| Pull requests     | Yes: `gh pr`        | Full lifecycle support                                           |
| Issues            | Yes: `gh issue`     | Full lifecycle support                                           |
| Projects v2       | Yes: `gh project`   | CLI for standard ops; GraphQL for bulk/advanced field queries    |
| Releases          | Yes: `gh release`   | Includes asset upload                                            |
| Labels            | Yes: `gh label`     | Full CRUD                                                        |
| Milestones        | **No CLI command**  | Use `gh api repos/{owner}/{repo}/milestones`                     |
| Branch rulesets   | Yes: `gh ruleset`   | View and list; creation may need API                             |
| Deploy keys       | **No CLI command**  | Use `gh api repos/{owner}/{repo}/keys`                           |
| Webhooks          | **No CLI command**  | Use `gh api repos/{owner}/{repo}/hooks`                          |
| Environments      | **No CLI command**  | Use `gh api repos/{owner}/{repo}/environments`                   |
| Actions secrets   | Yes: `gh secret`    | Full CRUD                                                        |
| Actions vars      | Yes: `gh variable`  | Full CRUD                                                        |
| Actions runs      | Yes: `gh run`       | List, view, rerun, watch                                         |
| Actions workflows | Yes: `gh workflow`  | List, view, run, enable/disable                                  |
| Code search       | Yes: `gh search`    | Code, commits, issues, repos                                     |
| Repository        | Yes: `gh repo`      | Create, clone, fork, edit, archive                               |

### GraphQL Fallback Pattern (Projects v2)

Use GraphQL when `gh project` does not expose the operation:

```bash
# Get project node ID (needed for mutations)
gh project list --owner {owner} --format json | jq '.projects[] | select(.title == "Board Name") | .id'

# Then use the node ID in a GraphQL mutation
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!) {
    deleteProjectV2Item(input: {projectId: $projectId, itemId: $itemId}) {
      deletedItemId
    }
  }' -f projectId="..." -f itemId="..."
```

## 4. Rebase vs Merge (Updating a Feature Branch)

This is about keeping a feature branch current with `main` — not about how to merge the PR.

### Context Signals to Check

```bash
# Is the branch pushed to a remote that others use?
git branch -r | grep "$(git branch --show-current)"

# Have others pushed commits to this branch?
git log --format='%ae' origin/$(git branch --show-current)..HEAD 2>/dev/null | sort -u

# How many commits on the branch?
git log --oneline main..HEAD | wc -l

# Are there conflicts with main?
git merge-tree $(git merge-base HEAD main) main HEAD | grep -c 'CONFLICT' 2>/dev/null || echo "check manually"
```

### Decision Matrix

| Factor                          | Rebase onto main             | Merge main into branch         |
| ------------------------------- | ---------------------------- | ------------------------------ |
| Branch is solo (only you)       | Preferred                    | Works, but adds merge commits  |
| Branch is shared (others push)  | **Dangerous — avoid**        | Preferred                      |
| Few commits (1-5)               | Easy, low risk               | Works fine                     |
| Many commits (10+)              | Tedious, conflict per commit | One conflict resolution        |
| Clean history matters           | Yes, rewrites cleanly        | Adds merge commit noise        |
| Preserving exact commit SHAs    | No (SHAs change)             | Yes (original SHAs preserved)  |
| CI must pass each commit        | Validates per-commit         | Only validates merge result    |

### Decision Steps

1. **Check if branch is shared:**
   `git branch -r | grep "$(git branch --show-current)"`
   - If others have pushed to it: **merge, do not rebase**
   - Rebasing a shared branch rewrites history that others depend on
2. **Check commit count:**
   - 1-5 commits on a solo branch: rebase is straightforward
   - 10+ commits: merge is safer (one conflict resolution instead of many)
3. **Check for conflicts:**
   - No conflicts: rebase is clean and preferred for solo branches
   - Conflicts exist: merge if there are many commits; rebase if few
4. **Execute:**
   - Rebase: `git fetch origin && git rebase origin/main`
   - Merge: `git fetch origin && git merge origin/main`
5. **After rebase (solo branch):** `git push --force-with-lease` (never `--force`)
6. **After merge:** `git push` (no force needed)

### Safety Rule

When in doubt, merge. Merging is always safe. Rebasing requires confidence that the branch is not shared
and that you are comfortable with conflict resolution across multiple commits.

## 5. Worktree vs Standard Checkout

Choose between `git worktree` and standard `git checkout` / `git switch` for working on multiple branches.

### Context Signals to Check

```bash
# Are worktrees already in use?
git worktree list

# Is this a bare clone (common with worktree-heavy setups)?
git rev-parse --is-bare-repository

# Is there an AIDA worktree preference?
# Check: github.worktree.enabled in project AIDA config

# How many branches need simultaneous work?
# (No command — this is a judgment call based on the task)
```

### Decision Matrix

| Factor                           | Worktree                          | Standard Checkout                |
| -------------------------------- | --------------------------------- | -------------------------------- |
| Parallel work on 2+ branches     | **Ideal** — no stashing needed    | Requires stash/commit/switch     |
| Single branch at a time          | Unnecessary overhead              | **Simpler**                      |
| Long-running feature + hotfix    | **Ideal** — keep both open        | Disruptive context switching     |
| Comparing output across branches | **Ideal** — both built at once    | Must switch back and forth       |
| CI bisect while working          | **Ideal** — bisect in worktree    | Blocks your working tree         |
| Quick hotfix (< 30 min)          | Overhead not worth it             | **Faster to start**              |
| User familiarity with worktrees  | Required                          | N/A (everyone knows checkout)    |
| IDE support                      | Varies (some IDEs struggle)       | Universal                        |
| Disk space                       | Uses more (separate working tree) | Minimal                          |

### Bare vs Traditional Mode

| Mode                     | When to Use                                   | Setup                                   |
| ------------------------ | --------------------------------------------- | --------------------------------------- |
| Bare clone + worktrees   | Dedicated worktree workflow, no "main" copy   | `git clone --bare repo.git .bare`       |
| Traditional + worktrees  | Occasional parallel work alongside normal use | `git worktree add ../feature-branch`    |

**Bare mode advantages:** No ambiguity about which directory is the "real" checkout. Every branch lives in its
own worktree directory. Works well when the team has fully adopted worktrees.

**Traditional mode advantages:** Simpler mental model. Main branch lives in the original clone. Add worktrees
only when needed for parallel work. Lower adoption barrier.

### Decision Steps

1. **Check AIDA config** for `github.worktree.enabled` preference
2. **Ask: do I need two branches simultaneously?**
   - No: use standard checkout
   - Yes: proceed to step 3
3. **Ask: is this a quick task (< 30 min)?**
   - Yes and current work can be stashed cleanly: standard checkout is faster
   - No: worktree avoids repeated context switching
4. **Check existing worktree mode:**
   - Bare repository: create worktree in the standard location
   - Traditional: `git worktree add <path> <branch>`
5. **Clean up after:** always `git worktree remove <path>`, never `rm -rf`
