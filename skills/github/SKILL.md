---
type: skill
name: github
version: 1.0.0
description: Git and GitHub CLI operations — PRs, issues, branches, projects, releases, Actions, and recovery
short_description: Git and GitHub operations
category: devops
tags: [github, git, cli, devops, automation]
activation: Use when performing git or GitHub CLI operations
---

# GitHub Skill

Operational skill for git and GitHub CLI (`gh`) commands. Covers the full lifecycle of PRs, issues,
branches, project boards, releases, CI/CD, and git recovery operations. Organized by **what you are
trying to do**, not which binary runs it.

## How This Skill Works

- **Quick reference tables below** cover high-frequency commands inline
- **Reference files** (`references/`) contain deeper recipes for complex domains
- **Agent knowledge** (`agents/github-expert/knowledge/`) handles "why" and "when" decisions
- **External docs** are linked for the 20% long tail (obscure flags, advanced API)

## Cross-Cutting Patterns

Before using any commands, know these patterns that apply everywhere:

- **`--jq`:** Filter JSON output inline. Available on `--json`-capable commands and `gh api`.
  Project commands (`--format json`) do **not** support `--jq` — pipe to system `jq` instead.
- **`@me` convention:** Works in `--assignee`, `--owner`, `--author` across `gh` commands.
- **`--repo` / `-R`:** Target a different repository without changing directories.
- **Project OAuth scope:** All `gh project` commands require the `project` scope.
  If you get permission errors: `gh auth refresh -s project`.
- **Config-aware:** Check AIDA config for branching model, merge strategy, branch prefixes,
  and worktree preferences before assuming defaults.

## Quick Reference

### Pull Requests

| Action | Command | More |
| ------ | ------- | ---- |
| Create PR | `gh pr create --title "..." --body "Closes #123"` | [references/pr.md](references/pr.md) |
| Create draft PR | `gh pr create --title "..." --draft` | [references/pr.md](references/pr.md) |
| Merge (squash) | `gh pr merge <#> --squash --delete-branch` | [references/pr.md](references/pr.md) |
| Merge (merge commit) | `gh pr merge <#> --merge --delete-branch` | [references/pr.md](references/pr.md) |
| Merge (rebase) | `gh pr merge <#> --rebase --delete-branch` | [references/pr.md](references/pr.md) |
| Auto-merge on green | `gh pr merge <#> --squash --delete-branch --auto` | [references/pr.md](references/pr.md) |
| Review (approve) | `gh pr review <#> --approve` | |
| Review (request changes) | `gh pr review <#> --request-changes --body "..."` | |
| List open PRs | `gh pr list --json number,title,state,reviewDecision` | |
| View PR details | `gh pr view <#> --json title,state,reviews,mergeable` | |
| Check CI status | `gh pr checks <#>` | |
| View PR diff | `gh pr diff <#>` | |
| Edit PR metadata | `gh pr edit <#> --add-label "..." --add-reviewer "..."` | |
| PR status dashboard | `gh pr status` | |
| Update PR branch | `gh pr update-branch <#>` | |

**Always** use `gh pr merge`, never `git merge --squash` for PRs. Check AIDA config
`github.merge_strategy` for the project's preferred strategy. See [references/pr.md](references/pr.md)
for full recipes including linked issues, templates, and JSON field names.

### Issues

| Action | Command | More |
| ------ | ------- | ---- |
| Create issue | `gh issue create --title "..." --label bug --assignee @me` | [references/issue.md](references/issue.md) |
| Create from template | `gh issue create --template "bug_report.md"` | [references/issue.md](references/issue.md) |
| List open issues | `gh issue list --state open --label bug --limit 50` | |
| List with JSON | `gh issue list --json number,title,state,labels,milestone` | |
| Edit issue | `gh issue edit <#> --add-label "..." --remove-label "..."` | |
| Close with comment | `gh issue close <#> --comment "Fixed in #42"` | |
| Create branch from issue | `gh issue develop <#> --checkout` | |
| Comment on issue | `gh issue comment <#> --body "..."` | |
| Lock conversation | `gh issue lock <#> --reason "resolved"` | |

See [references/issue.md](references/issue.md) for transfer, pinning, and linking patterns.

### Branches and Worktrees

| Action | Command | More |
| ------ | ------- | ---- |
| Create branch | `git switch -c feature/123-description` | [references/branching.md](references/branching.md) |
| Create from issue | `gh issue develop <#> --checkout` | |
| List with tracking | `git branch -vv` | |
| Push and set upstream | `git push -u origin <branch>` | |
| Delete local (after squash) | `git branch -D <branch>` | |
| Delete remote | `git push origin --delete <branch>` | |
| Clean stale refs | `git fetch origin --prune` | |
| Create worktree | `git worktree add <path> -b <branch>` | [references/branching.md](references/branching.md) |
| Remove worktree | `git worktree remove <path>` | [references/branching.md](references/branching.md) |
| List worktrees | `git worktree list` | |

Check AIDA config for `github.worktree.enabled`, `github.worktree.mode`, and branch prefixes.
**Never** `rm -rf` a worktree directory. See [references/branching.md](references/branching.md) for naming conventions
and worktree mode details.

### Rebase, Merge, and History

| Action | Command | More |
| ------ | ------- | ---- |
| Rebase onto main | `git fetch origin && git rebase origin/main` | [references/rebase-and-merge.md](references/rebase-and-merge.md) |
| Rebase onto specific | `git rebase --onto <newbase> <upstream> <branch>` | [references/rebase-and-merge.md](references/rebase-and-merge.md) |
| Abort rebase | `git rebase --abort` | |
| Continue after conflict | `git rebase --continue` | |
| Merge main into branch | `git fetch origin && git merge origin/main` | [references/rebase-and-merge.md](references/rebase-and-merge.md) |
| Push after rebase | `git push --force-with-lease` | |
| View log (compact) | `git log --oneline -20` | |
| View log (graph) | `git log --oneline --graph --all -30` | |
| View branch commits | `git log --oneline main..HEAD` | |
| Diff staged | `git diff --cached` | |
| Diff vs main | `git diff main..HEAD --stat` | |

**Never** `--force`, always `--force-with-lease`. Claude cannot run interactive rebase (`-i`).
See [references/rebase-and-merge.md](references/rebase-and-merge.md) for conflict resolution and strategy selection.

### Recovery and Rescue

| Action | Command | More |
| ------ | ------- | ---- |
| Stash changes | `git stash push -m "description"` | [references/recovery.md](references/recovery.md) |
| Stash with untracked | `git stash --include-untracked` | |
| Pop stash | `git stash pop` | |
| List stashes | `git stash list` | |
| Find lost commit | `git reflog -20` | [references/recovery.md](references/recovery.md) |
| Cherry-pick commit | `git cherry-pick <sha>` | [references/recovery.md](references/recovery.md) |
| Cherry-pick range | `git cherry-pick <start>..<end>` | [references/recovery.md](references/recovery.md) |
| Start bisect | `git bisect start` | [references/recovery.md](references/recovery.md) |
| Revert a commit | `git revert <sha>` | |
| Undo soft reset | `git reflog`, then `git reset --soft <sha>` | [references/recovery.md](references/recovery.md) |

See [references/recovery.md](references/recovery.md) for guided bisect workflow, reflog recovery, and stash management.

### Project Boards

| Action | Command | More |
| ------ | ------- | ---- |
| List projects | `gh project list --owner @me --format json` | [references/project.md](references/project.md) |
| List items | `gh project item-list <#> --owner @me --format json` | [references/project.md](references/project.md) |
| Add item by URL | `gh project item-add <#> --owner @me --url <url>` | [references/project.md](references/project.md) |
| List fields | `gh project field-list <#> --owner @me --format json` | [references/project.md](references/project.md) |
| Edit item field | `gh project item-edit --id <item> --project-id <proj> ...` | [references/project.md](references/project.md) |
| Create project | `gh project create --owner @me --title "..."` | |
| View project | `gh project view <#> --owner @me` | |
| Mark as template | `gh project mark-template <#> --owner @me` | |

Project commands use `--format json` (not `--json`). Requires `project` OAuth scope.
See [references/project.md](references/project.md) for field editing and GraphQL fallback patterns.

### CI/CD and Actions

| Action | Command | More |
| ------ | ------- | ---- |
| List recent runs | `gh run list --limit 10` | [references/actions.md](references/actions.md) |
| List failed runs | `gh run list --status failure --limit 10` | [references/actions.md](references/actions.md) |
| View failed logs | `gh run view <id> --log-failed` | [references/actions.md](references/actions.md) |
| View with job details | `gh run view <id> --json jobs` | |
| Rerun failed jobs | `gh run rerun <id> --failed` | [references/actions.md](references/actions.md) |
| Trigger workflow | `gh workflow run ci.yml --ref main -f key=value` | [references/actions.md](references/actions.md) |
| Enable/disable workflow | `gh workflow enable ci.yml` / `gh workflow disable ci.yml` | |
| List workflows | `gh workflow list` | |

See [references/actions.md](references/actions.md) for debugging patterns, workflow dispatch, and common
failure signatures.

### Releases and Tags

| Action | Command | More |
| ------ | ------- | ---- |
| Create release | `gh release create v1.0.0 --generate-notes` | [references/release.md](references/release.md) |
| Create pre-release | `gh release create v2.0.0-rc.1 --prerelease --draft` | [references/release.md](references/release.md) |
| Create with assets | `gh release create v1.0.0 dist/*.tar.gz --generate-notes` | [references/release.md](references/release.md) |
| List releases | `gh release list --limit 10` | |
| View release | `gh release view v1.0.0` | |
| Create annotated tag | `git tag -a v1.0.0 -m "Release v1.0.0"` | |
| Push tag | `git push origin v1.0.0` | |
| List tags | `git tag --sort=-creatordate \| head -20` | |

See [references/release.md](references/release.md) for version bump patterns, release notes customization,
and tag management.

### Repository Setup

| Action | Command | More |
| ------ | ------- | ---- |
| Clone repo | `gh repo clone owner/repo` | [references/repo.md](references/repo.md) |
| Fork and clone | `gh repo fork owner/repo --clone` | [references/repo.md](references/repo.md) |
| Create repo | `gh repo create name --public --clone` | [references/repo.md](references/repo.md) |
| View repo info | `gh repo view --json name,defaultBranchRef,description` | |
| Archive repo | `gh repo archive owner/repo --yes` | |
| List rulesets | `gh ruleset list` | [references/repo.md](references/repo.md) |
| View ruleset | `gh ruleset view <id>` | |

See [references/repo.md](references/repo.md) for rulesets, branch protection, deploy keys, and repo configuration.

### Labels

| Action | Command |
| ------ | ------- |
| Create label | `gh label create "name" --color FF0000 --description "..."` |
| Create or update | `gh label create "name" --color FF0000 --force` |
| List all | `gh label list --json name,color,description --limit 100` |
| Edit label | `gh label edit "old-name" --name "new-name" --color 00FF00` |
| Delete label | `gh label delete "name" --yes` |
| Clone from repo | `gh label clone source-org/source-repo --force` |

Check AIDA config `github.label_taxonomy` for the project's label set. Use `gh label clone` to
sync a standard taxonomy across repositories.

Full reference: [gh_label manual](https://cli.github.com/manual/gh_label)

### Milestones (REST API)

| Action | Command |
| ------ | ------- |
| Create | `gh api repos/{owner}/{repo}/milestones --method POST -f title="v2.0" -f due_on="2026-06-01T00:00:00Z"` |
| List | `gh api repos/{owner}/{repo}/milestones --jq '.[] \| {number, title, state}'` |
| Close | `gh api repos/{owner}/{repo}/milestones/<#> --method PATCH -f state="closed"` |

No `gh milestone` CLI command exists — use `gh api` with the REST endpoint.

### Search

| Action | Command |
| ------ | ------- |
| Search issues | `gh search issues "query" --repo owner/repo --state open` |
| Search code | `gh search code "query" --repo owner/repo --language python` |
| Search PRs | `gh search prs "query" --repo owner/repo --state merged` |
| Search repos | `gh search repos "query" --language go --stars ">100"` |
| Search commits | `gh search commits "query" --repo owner/repo` |

Full reference: [gh_search manual](https://cli.github.com/manual/gh_search)

### Admin and Auth

| Action | Command |
| ------ | ------- |
| Check auth status | `gh auth status` |
| Refresh with scope | `gh auth refresh -s project` |
| Switch accounts | `gh auth switch` |
| Set secret | `gh secret set API_KEY` |
| List secrets | `gh secret list` |
| Set variable | `gh variable set ENV --body "production"` |
| List variables | `gh variable list` |

Full references: [gh_secret](https://cli.github.com/manual/gh_secret),
[gh_variable](https://cli.github.com/manual/gh_variable),
[gh_auth](https://cli.github.com/manual/gh_auth)

## Output Format Cheat Sheet

| Command Family | Structured Output | Example |
| -------------- | ----------------- | ------- |
| `gh pr` | `--json field1,field2` | `gh pr list --json number,title` |
| `gh issue` | `--json field1,field2` | `gh issue list --json number,state` |
| `gh run` | `--json field1,field2` | `gh run list --json databaseId,conclusion` |
| `gh label` | `--json field1,field2` | `gh label list --json name,color` |
| `gh release` | `--json field1,field2` | `gh release list --json tagName,isPrerelease` |
| `gh project` | `--format json` | `gh project list --format json` |
| `gh api` | Returns JSON natively | `gh api repos/{owner}/{repo}/milestones` |

Filter with `--jq` on any `--json`-capable command:

```bash
gh pr list --json number,title,labels --jq '.[] | select(.labels[].name == "bug") | .number'
```

## Common Multi-Step Patterns

### Full PR Workflow

```bash
git switch -c feature/123-add-auth
# ... make changes ...
git add <files> && git commit -m "feat: add auth module"
git push -u origin feature/123-add-auth
gh pr create --title "Add auth module" --body "Closes #123" --label feature
# After approval:
gh pr merge <#> --squash --delete-branch
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
git branch -D <merged-branch>
git fetch origin --prune
git worktree prune   # if using worktrees
```
