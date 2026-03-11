---
type: reference
title: GitHub Expert Knowledge Base
description: Focused knowledge for GitHub and git operations — common patterns, guardrails, and decisions
agent: github-expert
knowledge_count: 3
last_updated: "2026-02-24"
categories:
  - operations
  - guardrails
  - decisions
---

# GitHub Expert Knowledge Base

Focused knowledge covering the 80% of GitHub and git operations needed for daily work. For the 20%
long tail (obscure flags, advanced API schemas, edge cases), the agent fetches official documentation
from the external references listed below.

## Knowledge Files

### Operations (1 file)

The top 30-40 commands and patterns an expert knows by heart:

- **`operations.md`** — Common git and gh CLI operations organized by task. Correct flags, `--json`
  field names, config-aware defaults. Covers: PR lifecycle, issue management, branching, worktrees,
  project boards, releases, labels, milestones, Actions, common git operations.

### Guardrails (1 file)

The highest-value knowledge — what goes wrong and how to avoid it:

- **`guardrails.md`** — Anti-patterns, gotchas, deprecated commands, "never do this" rules.
  Covers: PR merge metadata, worktree cleanup, force push safety, stale refs, interactive rebase
  limitations, Projects v2 CLI availability, branch deletion after squash.

### Decisions (1 file)

Frameworks for when the right action isn't obvious:

- **`decisions.md`** — Decision matrices and frameworks. Covers: merge strategy selection
  (squash vs merge vs rebase), branching model selection (trunk-based vs GitHub flow vs gitflow),
  CLI vs API decision tree, rebase vs merge context analysis, worktree vs standard checkout.

## External References

When you need details beyond what's in the local knowledge files, fetch these URLs:

### gh CLI Manual (complete flag reference and examples)

| Domain | URL |
| ------ | --- |
| PR | [gh_pr](https://cli.github.com/manual/gh_pr) |
| Issue | [gh_issue](https://cli.github.com/manual/gh_issue) |
| Repo | [gh_repo](https://cli.github.com/manual/gh_repo) |
| Project | [gh_project](https://cli.github.com/manual/gh_project) |
| Release | [gh_release](https://cli.github.com/manual/gh_release) |
| Run | [gh_run](https://cli.github.com/manual/gh_run) |
| Workflow | [gh_workflow](https://cli.github.com/manual/gh_workflow) |
| Search | [gh_search](https://cli.github.com/manual/gh_search) |
| Label | [gh_label](https://cli.github.com/manual/gh_label) |
| API | [gh_api](https://cli.github.com/manual/gh_api) |
| Secret | [gh_secret](https://cli.github.com/manual/gh_secret) |
| Variable | [gh_variable](https://cli.github.com/manual/gh_variable) |
| Ruleset | [gh_ruleset](https://cli.github.com/manual/gh_ruleset) |
| Auth | [gh_auth](https://cli.github.com/manual/gh_auth) |
| Full manual | [gh manual](https://cli.github.com/manual/) |

### GitHub Platform Documentation

| Topic | URL |
| ----- | --- |
| Actions workflow syntax | [Workflow syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions) |
| Branch protection rules | [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches) |
| Repository rulesets | [Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets) |
| Projects v2 | [Planning and tracking](https://docs.github.com/en/issues/planning-and-tracking-with-projects) |
| GraphQL API | [GraphQL API](https://docs.github.com/en/graphql) |
| REST API | [REST API](https://docs.github.com/en/rest) |
| Webhooks | [Webhooks](https://docs.github.com/en/webhooks) |
| GitHub Apps | [GitHub Apps](https://docs.github.com/en/apps) |

### Git Documentation

| Topic | URL |
| ----- | --- |
| Git reference (all commands) | [Git docs](https://git-scm.com/docs) |
| Pro Git book | [Pro Git](https://git-scm.com/book/en/v2) |
| Git worktree | [git-worktree](https://git-scm.com/docs/git-worktree) |
| Git rebase | [git-rebase](https://git-scm.com/docs/git-rebase) |
| Git reflog | [git-reflog](https://git-scm.com/docs/git-reflog) |
| Git bisect | [git-bisect](https://git-scm.com/docs/git-bisect) |

## How to Use This Knowledge Base

### For Common Operations

1. Check `operations.md` first — it covers 80% of daily tasks
2. If the specific command/flag isn't there, fetch the relevant gh CLI manual page

### For "Is This Safe?" Questions

1. Check `guardrails.md` — it lists known dangerous patterns
2. When in doubt, prefer the defensive option (e.g., `--force-with-lease` over `--force`)

### For "Which Approach?" Questions

1. Check `decisions.md` — it has decision matrices for common choices
2. Gather context (branch state, team setup, project config) before deciding

### For Edge Cases and Advanced Operations

1. Check the external reference URLs above
2. Use `WebFetch` to retrieve the specific documentation page
3. Parse for the relevant flags, examples, or API schema

## Contributing to This Knowledge Base

When adding knowledge:

1. **80% rule:** Only add to local files if it's a pattern you'd use frequently
2. **No doc duplication:** Don't reproduce official docs — link to them
3. **Guardrails are gold:** If you discover a new gotcha, add it to `guardrails.md` immediately
4. **Keep it current:** If a `gh` command changes, update `operations.md` and `guardrails.md`
5. **Update this index:** Keep file descriptions and external URLs current
