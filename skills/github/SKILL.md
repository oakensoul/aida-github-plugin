---
type: skill
name: github
version: 2.0.0
description: "Dispatcher for /github (domain) (action) commands — PRs, issues, branches, projects, releases, and more"
short_description: "/github command dispatcher"
category: devops
tags: [github, git, cli, devops, automation, dispatcher]
activation: "Use when the user invokes /github or needs to perform git/GitHub CLI operations"
---

# /github Dispatcher

Single entry point for all git and GitHub CLI operations. Parses `/github (domain) (action)` and
routes to the appropriate handler.

## Routing

When the user invokes `/github`:

1. Parse the **first word** after `/github` as the **domain**.
2. Parse the **second word** (if any) as the **action**.
3. Look up the domain in the routing table below.
4. Read the matching handler file from `handlers/<domain>.md`.
5. Execute the action described in the handler.

If **no arguments** are provided, show the help menu below.
If the **domain is unrecognized**, show the help menu and suggest the closest match.
If the **action is missing**, show available actions for that domain from the handler.

### Routing Table

| Domain | Handler | Actions |
| ------ | ------- | ------- |
| `pr` | [handlers/pr.md](handlers/pr.md) | `create`, `list`, `merge`, `review`, `edit`, `view`, `ready` |
| `branch` | [handlers/branch.md](handlers/branch.md) | `create`, `list`, `cleanup` |
| `issue` | [handlers/issue.md](handlers/issue.md) | `create`, `list`, `edit`, `close`, `comment`, `develop` |
| `project` | [handlers/project.md](handlers/project.md) | `status`, `add`, `edit`, `create`, `view` |
| `release` | [handlers/release.md](handlers/release.md) | `create`, `list`, `tag`, `view` |
| `label` | [handlers/label.md](handlers/label.md) | `sync`, `create`, `list`, `edit`, `delete` |
| `milestone` | [handlers/milestone.md](handlers/milestone.md) | `create`, `list`, `close`, `edit`, `delete` |
| `actions` | [handlers/actions.md](handlers/actions.md) | `list`, `view`, `debug`, `rerun`, `cancel`, `trigger`, `workflows` |
| `repo` | [handlers/repo.md](handlers/repo.md) | `clone`, `fork`, `create`, `view`, `edit`, `sync`, `archive`, `rulesets` |
| `search` | [handlers/search.md](handlers/search.md) | `issues`, `prs`, `code`, `commits`, `repos` |

## Help Menu

Shown when `/github` is invoked with no arguments:

```text
/github — Git & GitHub Operations

  Pull Requests
    /github pr create        Create a pull request (config-aware)
    /github pr list          List open PRs with status
    /github pr merge         Merge a PR (config-aware strategy)
    /github pr review        Approve or request changes
    /github pr edit          Edit PR labels, reviewers, title
    /github pr view          View PR details and CI status
    /github pr ready         Mark draft PR as ready for review

  Branches
    /github branch create    Create a branch (config-aware naming)
    /github branch list      List branches with tracking info
    /github branch cleanup   Remove merged/stale branches

  Issues
    /github issue create     Create an issue with labels
    /github issue list       List issues with filters
    /github issue edit       Edit issue labels, assignees, milestone
    /github issue close      Close with comment and reason
    /github issue comment    Add a comment to an issue
    /github issue develop    Create branch linked to issue

  Projects
    /github project status   View board status and item counts
    /github project add      Add issue/PR to project
    /github project edit     Edit item field (move between columns)
    /github project create   Create a new project
    /github project view     View project details and items

  Releases
    /github release create   Create release with auto-generated notes
    /github release list     List recent releases
    /github release tag      Create and push a git tag
    /github release view     View release details

  Labels
    /github label sync       Sync label taxonomy to repo
    /github label create     Create a label with color
    /github label list       List all repo labels
    /github label edit       Rename or update a label
    /github label delete     Delete a label

  Milestones
    /github milestone create   Create a milestone with due date
    /github milestone list     List milestones with progress
    /github milestone close    Close a milestone
    /github milestone edit     Update milestone details
    /github milestone delete   Delete a milestone

  CI/CD & Actions
    /github actions list     List recent workflow runs
    /github actions view     View run details and logs
    /github actions debug    Triage CI failures step by step
    /github actions rerun    Rerun failed jobs
    /github actions trigger  Manually trigger a workflow

  Repository
    /github repo clone       Clone a repository
    /github repo fork        Fork and clone a repository
    /github repo create      Create a new repository
    /github repo view        View repository info
    /github repo edit        Edit repository settings
    /github repo sync        Sync fork with upstream

  Search
    /github search issues    Search issues across repos
    /github search prs       Search PRs across repos
    /github search code      Search code across repos

Run /github <domain> without an action to see all available actions.
For conceptual questions, ask the github-expert agent
("explain rebasing", "what branching model should I use?").
```

## Cross-Cutting Patterns

These apply to all handlers — read once, use everywhere:

- **`--jq`**: Filter JSON inline on `--json`-capable commands (`gh pr`, `gh issue`, `gh run`,
  `gh label`). Project commands use `--format json` and do **not** support `--jq` — pipe to
  system `jq` instead.
- **`@me`**: Works in `--assignee`, `--owner`, `--author` across `gh` commands.
- **`--repo` / `-R`**: Target a different repository without changing directories.
- **Project OAuth**: `gh project` commands require the `project` scope. If permission errors:
  `gh auth refresh -s project`.
- **Config-aware**: Check AIDA config for `github.merge_strategy`, `github.branch_prefix.*`,
  `github.worktree.*`, `github.label_taxonomy`, and `github.pr.*` before assuming defaults.

## Output Formats

| Command Family | Structured Output | Filter |
| -------------- | ----------------- | ------ |
| `gh pr`, `gh pr checks`, `gh issue`, `gh run`, `gh label`, `gh release` | `--json field1,field2` | `--jq '...'` |
| `gh project` | `--format json` | pipe to `jq` |
| `gh api` | Returns JSON natively | `--jq '...'` |

## Architecture

- **Handlers** (`handlers/`) — action-oriented execution docs, loaded per-domain
- **References** (`references/`) — deep recipes and edge cases, loaded on demand
- **Agent knowledge** (`agents/github-expert/knowledge/`) — "why" and "when" decisions
- **Python scripts** (`scripts/`) — deterministic multi-step operations (see `<!-- SCRIPT: -->` markers in handlers)
