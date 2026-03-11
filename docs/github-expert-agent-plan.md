---
type: plan
title: github-expert Agent Implementation Plan
version: 0.1.0
status: draft
---

# github-expert Agent Implementation Plan

## Summary

Build the `github-expert` agent as the conversational core of the aida-github-plugin. This agent is the
first deliverable — it provides GitHub/git expertise and will later assist in building and refining all skills.

---

## Key Discovery: `gh project` EXISTS Now

The existing `github-workflow` skill states: "`gh project` command doesn't exist." **This is outdated.**
The current gh CLI manual shows a full `gh project` command surface:

```text
gh project close, copy, create, delete, edit, field-create, field-delete, field-list,
  item-add, item-archive, item-create, item-delete, item-edit, item-list,
  link, list, mark-template, unlink, view
```

This means the `project-*` skills can use `gh project` directly rather than raw GraphQL for most operations.
The agent's knowledge base must reflect this current reality, and the plugin spec's technical notes about
"always use `gh api graphql`" need revision. GraphQL via `gh api` is still needed for some advanced
operations (complex field queries, bulk operations), but the CLI covers the common cases now.

---

## Agent Architecture

### Naming

- **Agent name:** `github-expert` (replaces the scaffolded `aida-github-plugin` placeholder)
- **Plugin name:** `aida-github-plugin` (unchanged)
- **Subagent type registration:** `aida-github-plugin:github-expert:github-expert`

### Frontmatter

```yaml
---
name: github-expert
version: 1.0.0
description: GitHub and git expert for repository management, workflows, automation, and troubleshooting
short_description: GitHub and git expertise
category: github
model: claude-sonnet-4.5
color: gray
temperature: 0.7
---
```

### Agent File Structure

```text
agents/
└── github-expert/
    ├── github-expert.md           # Agent definition (rich — covers 80% of use cases)
    └── knowledge/
        ├── index.md               # Knowledge catalog + external reference URLs
        ├── operations.md          # Common commands with correct patterns and flags
        ├── guardrails.md          # Anti-patterns, gotchas, deprecated commands, "never do this"
        └── decisions.md           # Decision frameworks (merge strategy, branching, CLI vs API)
```

**Total: 3 knowledge files + index. Lean by design.**

---

## Agent Definition (github-expert.md)

### Core Expertise Areas

1. **Git operations** — rebase, merge, cherry-pick, bisect, stash, worktree, reflog, conflict resolution
2. **gh CLI mastery** — complete command surface, JSON output parsing, `gh api` for REST/GraphQL
3. **GitHub platform** — Actions, branch protection, rulesets, environments, deploy keys, webhooks, Apps
4. **Projects v2** — `gh project` commands + GraphQL API for advanced operations
5. **Repository management** — setup, configuration, branching models, label taxonomies
6. **Release engineering** — tagging, releases, semantic versioning, changelog generation
7. **Troubleshooting** — stale refs, detached HEAD, merge conflicts, failed Actions, auth issues

### Behavioral Rules

1. **Skill awareness** — knows the `github` skill and its reference domains, recommends activation for well-defined tasks
2. **No deprecated commands** — always uses current gh CLI syntax, never legacy flags
3. **Worktree-aware** — detects worktree vs standard setup, adapts commands accordingly
4. **Clean output** — parses JSON from `gh --json`, returns structured readable results
5. **Defensive execution** — validates state before destructive operations, confirms before force actions
6. **Config-aware** — reads AIDA config for branching model, naming conventions, worktree preferences

### Two-Tier Knowledge Architecture

Following the established AIDA pattern:

- **Tier 1 (User-level):** `~/.claude/agents/github-expert/knowledge/` — generic git/GitHub expertise
- **Tier 2 (Project-level):** `{project}/.claude/project/context/github-expert/` — project-specific
  branching model, repo conventions, team workflow preferences

### Coordination with Other Agents

| Agent | Relationship |
| ------- | ------------- |
| `devops-engineer` | CI/CD pipeline design, deployment automation |
| `security-engineer` | Branch protection, secret scanning, deploy keys |
| `tech-lead` | Branching strategy decisions, code review standards |
| `code-reviewer` | PR review workflows, merge readiness checks |

### Relationship to Existing `github-workflow` Skill

The existing `github-workflow` skill in `~/.claude/skills/` covers workflow best practices (merge via gh,
worktree management, project boards via GraphQL). The `github-expert` agent **subsumes and extends** this:

- The agent's knowledge base incorporates all of `github-workflow`'s guidance
- The agent can handle the nuanced cases the skill can't (e.g., "should I rebase or merge here?")
- The skill remains useful as a quick-reference activation for other agents/skills that do git operations
- Over time, the `github-workflow` skill should reference the plugin's knowledge as the source of truth

---

## Knowledge Base Design: The 80/20 Model

### Philosophy

An expert doesn't memorize every flag — they know the common stuff cold, know the gotchas by heart,
and know **exactly where to look** for the rest. Our knowledge base follows this principle:

- **80% coverage** from local knowledge: common operations, guardrails, decision frameworks
- **20% long tail** via external docs: obscure flags, advanced API patterns, edge cases

This means we write 3 focused knowledge files instead of 18, avoid duplicating well-maintained
official docs, and the agent stays current by fetching docs rather than relying on stale local copies.

### Knowledge Files

#### `operations.md` (~2-3k words) — "What an expert knows by heart"

The top 30-40 commands and patterns that cover daily work, with the **correct** flags and usage:

- **PR lifecycle:** create, list, merge (with strategy), edit, review, checks, close
- **Issue management:** create, list, edit, close, comment, link to PR
- **Branching:** create (with naming conventions), list (with tracking), cleanup, worktree operations
- **Project boards:** `gh project` commands for common operations (add item, set field, list)
- **Releases:** tag, create release, list, version bump pattern
- **Labels & milestones:** CRUD operations, sync pattern
- **Common git:** rebase onto, stash/pop, cherry-pick, log, diff, reflog
- **Actions:** list runs, view logs, rerun failed, trigger workflow

Organized by **task** (not by binary), with the exact command + most important flags. Not exhaustive —
just what you need 80% of the time.

#### `guardrails.md` (~1-2k words) — "What goes wrong and how to avoid it"

This is the highest-value knowledge — the stuff you can't learn from reading official docs:

- **PR merging:** Always `gh pr merge`, never `git merge --squash` (breaks GitHub metadata)
- **Worktree cleanup:** Always `git worktree remove`, never `rm -rf` (orphans git registration)
- **Projects v2:** `gh project` CLI exists now — don't use raw GraphQL for standard operations
- **Remote refs:** Always `git fetch origin` after push/merge (prevents stale tracking display)
- **Branch deletion after squash:** Use `git branch -D` (force), not `-d` (will say "not merged")
- **Interactive rebase:** Claude can't do interactive — advise the user, provide the plan
- **Deprecated patterns:** List of `gh` flags/commands that changed, with current replacements
- **Force push safety:** Never to main/master, always `--force-with-lease` over `--force`
- **Config-aware operations:** Check AIDA config before assuming branching model, merge strategy, etc.

#### `decisions.md` (~1-2k words) — "When and why, not just how"

Decision frameworks the agent uses when the right action isn't obvious:

- **Merge strategy selection:** Squash vs merge commit vs rebase — factors: history cleanliness,
  bisectability, attribution, CI requirements. Decision matrix.
- **Branching model selection:** Trunk-based vs GitHub flow vs gitflow — factors: team size, release
  cadence, deployment model. When to recommend which.
- **CLI vs API:** When to use `gh <command>` vs `gh api` (REST) vs `gh api graphql`. Decision tree:
  does a CLI command exist? Do you need fields the CLI doesn't expose? Is it a bulk operation?
- **Rebase vs merge:** Context-dependent — linear history vs merge commits, force push implications,
  shared branch considerations.
- **Worktree vs standard checkout:** When worktrees add value vs unnecessary complexity.

### `index.md` — Knowledge Catalog + External Reference URLs

In addition to cataloging the 3 knowledge files, `index.md` serves as the **"where to look" index**
for the 20% long tail. Organized by domain:

```markdown
## External References

When you need details beyond what's in the local knowledge files, fetch these:

### gh CLI Manual (complete flag reference and examples)
- PR: https://cli.github.com/manual/gh_pr
- Issue: https://cli.github.com/manual/gh_issue
- Repo: https://cli.github.com/manual/gh_repo
- Project: https://cli.github.com/manual/gh_project
- Release: https://cli.github.com/manual/gh_release
- Run: https://cli.github.com/manual/gh_run
- Workflow: https://cli.github.com/manual/gh_workflow
- Search: https://cli.github.com/manual/gh_search
- Label: https://cli.github.com/manual/gh_label
- API: https://cli.github.com/manual/gh_api
- Secret: https://cli.github.com/manual/gh_secret
- Variable: https://cli.github.com/manual/gh_variable
- Ruleset: https://cli.github.com/manual/gh_ruleset

### GitHub Platform Docs
- Actions workflow syntax: https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
- Branch protection rules: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository
- Rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets
- Projects v2: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- GraphQL API: https://docs.github.com/en/graphql

### Git Documentation
- Git reference: https://git-scm.com/docs
- Pro Git book: https://git-scm.com/book/en/v2
```

The agent can `WebFetch` any of these when it needs specific flag details, advanced examples, or
API schema information for the long tail of use cases.

---

## Skill Architecture: 1 Skill with Progressive Loading

### Why Not 50 Skills?

The original spec proposed ~50 individual skills (one per `gh <noun> <verb>`). This has a critical
token efficiency problem:

- **50 skills x ~100 words metadata each = ~5,000 words always in context**
- Every conversation pays this tax whether or not the user needs any of those skills
- AIDA's three-level progressive disclosure is designed to avoid exactly this

### Why Not 2 Skills?

The `gh` vs `git` boundary is an implementation detail, not a user-facing concern. Users say "rebase my
branch" or "create a PR" — they don't think about which binary handles it. And Claude doesn't need them
separated to choose the right tool. One skill, one activation, zero artificial boundaries.

### The Single-Skill Design: `github`

One hub skill covers **all** git and GitHub operations. Internally, reference files use whichever CLI
is correct (`git` or `gh`). The user and the agent never need to think about the boundary.

### How Progressive Loading Works

AIDA's three-level disclosure:

1. **Level 1 — Metadata** (~100 words, always in context): Name, description, activation hint
2. **Level 2 — SKILL.md body** (<5k words, loaded when skill activates): Routing logic, essential
   quick reference, "See:" links to domain-specific references
3. **Level 3 — References** (loaded on demand): Deep domain knowledge files, only pulled when Claude
   needs them for the specific task at hand

**Token cost: ~100 words always-on** (1 skill) vs ~5,000 words (50 skills). The deep knowledge loads
only when needed.

### Skill Structure

```text
skills/
└── github/
    ├── SKILL.md                        # Hub: routing + quick reference (~4-5k words)
    └── references/
        ├── pr.md                       # PR lifecycle recipes + links to gh_pr manual
        ├── issue.md                    # Issue management recipes + links
        ├── project.md                  # gh project recipes + GraphQL fallback patterns
        ├── repo.md                     # Repo setup, config, rulesets recipes
        ├── actions.md                  # Workflow runs, debugging, triggering recipes
        ├── release.md                  # Release + tagging + version bump recipes
        ├── branching.md               # Branch + worktree operations, naming conventions
        ├── rebase-and-merge.md        # Rebase strategies, merge strategies, conflict handling
        └── recovery.md                # Reflog, reset, revert, stash, cherry-pick, bisect
```

**9 reference files, 1 skill.** Lean by design.

Compared to the earlier 18-file plan, we consolidated:

- `label.md`, `milestone.md`, `search.md`, `admin.md` → absorbed into SKILL.md quick reference
  (these are simple enough that a one-liner in the hub is sufficient; link to official docs for flags)
- `stash.md`, `cherry-pick.md`, `bisect.md` → merged into `recovery.md` (all "rescue and repair" ops)
- `merge.md` + `rebase.md` → combined as `rebase-and-merge.md` (users think of these together)
- `log-and-diff.md` → absorbed into SKILL.md quick reference (common formats are short)

### SKILL.md Content Pattern

The hub provides a quick reference organized by **what you're trying to do**, not which binary runs it.
For high-frequency operations, the command is right in the table. For domains with more depth, it
links to a reference file. For simple/infrequent domains, it gives the command + a link to the
official docs.

```markdown
## Quick Reference

### Branches & Worktrees
| Action | Command | More |
|--------|---------|------|
| Create branch | `git checkout -b <name>` | [references/branching.md] |
| Create worktree | `git worktree add -b <branch> <path>` | [references/branching.md] |
| List branches | `git branch -vv` | |
| Delete branch | `git branch -D <name>` | |
| Cleanup stale | `git fetch origin --prune` | [references/branching.md] |

### Pull Requests
| Action | Command | More |
|--------|---------|------|
| Create PR | `gh pr create --title "..." --body "..."` | [references/pr.md] |
| Merge PR (squash) | `gh pr merge <#> --squash --delete-branch` | [references/pr.md] |
| Review PR | `gh pr review <#> --approve` | [references/pr.md] |
| List PRs | `gh pr list --json number,title,state` | |
| Check status | `gh pr checks <#>` | |

### Issues
| Action | Command | More |
|--------|---------|------|
| Create issue | `gh issue create --title "..." --label bug` | [references/issue.md] |
| List issues | `gh issue list --state open --label bug` | |
| Link branch | `gh issue develop <#>` | |

### Labels, Milestones, Search (simple — full docs linked)
| Action | Command | Docs |
|--------|---------|------|
| Create label | `gh label create <name> --color <hex>` | [gh_label manual] |
| List labels | `gh label list` | |
| Create milestone | `gh api repos/{owner}/{repo}/milestones -f title="..."` | [REST API docs] |
| Search code | `gh search code "query" --repo owner/repo` | [gh_search manual] |
| Search issues | `gh search issues "query" --repo owner/repo` | |

### Project Boards
| Action | Command | More |
|--------|---------|------|
| Add item | `gh project item-add <#> --owner <org> --url <url>` | [references/project.md] |
| Edit item field | `gh project item-edit ...` | [references/project.md] |
| List items | `gh project item-list <#> --owner <org>` | |

### CI/CD & Releases
| Action | Command | More |
|--------|---------|------|
| List workflow runs | `gh run list` | [references/actions.md] |
| View failed logs | `gh run view <id> --log-failed` | [references/actions.md] |
| Create release | `gh release create v1.0.0 --generate-notes` | [references/release.md] |
| Create tag | `git tag -a v1.0.0 -m "..."` | |

### Rebase, Merge & History
| Action | Command | More |
|--------|---------|------|
| Rebase onto main | `git rebase main` | [references/rebase-and-merge.md] |
| Abort rebase | `git rebase --abort` | |
| View log (pretty) | `git log --oneline --graph -20` | |
| Diff (staged) | `git diff --staged` | |

### Recovery & Rescue
| Action | Command | More |
|--------|---------|------|
| Stash changes | `git stash push -m "..."` | [references/recovery.md] |
| Pop stash | `git stash pop` | |
| Find lost commit | `git reflog` | [references/recovery.md] |
| Cherry-pick | `git cherry-pick <sha>` | [references/recovery.md] |
| Bisect | `git bisect start` | [references/recovery.md] |

### Admin (infrequent — full docs linked)
| Action | Command | Docs |
|--------|---------|------|
| Set secret | `gh secret set <name>` | [gh_secret manual] |
| Set variable | `gh variable set <name>` | [gh_variable manual] |
| View rulesets | `gh ruleset list` | [gh_ruleset manual] |
| Auth status | `gh auth status` | |
```

### Reference File Content Pattern

Each reference file is a **lean recipe book** (~500-1000 words), not a doc reproduction:

1. **Top 5-8 recipes** for that domain — the exact command patterns with correct flags
2. **Gotchas** specific to that domain (if not already in agent's `guardrails.md`)
3. **Config-aware notes** — where AIDA config affects behavior
4. **"Go deeper" links** — official doc URLs for the full flag reference

Example structure for `references/pr.md`:

```markdown
## PR Recipes

### Create with linked issue
gh pr create --title "Fix: description" --body "Closes #123" \
  --reviewer user1,user2 --label bug --milestone v1.0

### Merge (respects configured strategy)
# Check AIDA config for github.merge_strategy
gh pr merge <#> --squash --delete-branch

### View with JSON fields
gh pr view <#> --json title,state,reviews,checks,mergeable

### List with filters
gh pr list --json number,title,author,createdAt --jq '.[] | ...'

## Gotchas
- Always `gh pr merge`, never `git merge --squash` (breaks GitHub metadata)
- After merge: `git fetch origin` to update tracking refs

## Go Deeper
- Full flag reference: https://cli.github.com/manual/gh_pr_create
- JSON field names: https://cli.github.com/manual/gh_pr_view
```

### What the Agent Knows vs What the Skill Encodes

| Concern | Agent handles | Skill encodes |
| --------- | -------------- | --------------- |
| "Should I rebase or merge?" | Gathers context, makes recommendation | N/A (decision, not action) |
| "Rebase my branch onto main" | Delegates to skill (or just runs it) | Correct flags, conflict handling, abort guidance |
| "Create a PR for this" | Delegates to skill (or just runs it) | Template, reviewers, labels from config, linked issues |
| "Why is my Actions workflow failing?" | Reads logs, reasons about the error | `gh run view --log-failed` pattern, common failure signatures |
| "Set up this repo for our team" | Multi-step orchestration, asks questions | Individual commands for each step |

### Relationship Between Agent Knowledge and Skill References

There is intentional overlap — and that's fine:

- **Agent knowledge** (`agents/github-expert/knowledge/`) = deep understanding, decision frameworks,
  cross-domain patterns, "why" and "when"
- **Skill references** (`skills/github/references/`) = operational procedures, correct commands, flags,
  error handling, "how"

The agent loads knowledge when reasoning about what to do. The skill loads references when executing.
A user invoking the skill directly (without the agent) still gets the right commands. An agent working
without explicitly activating the skill still has the knowledge to do the right thing.

### Full Domain Coverage

#### GitHub platform operations (via `gh` CLI)

| Domain | Key operations | Notes |
| -------- | --------------- | ------- |
| **pr** | create, list, merge, edit, review, checks, close, reopen, diff, status, update-branch, revert | High frequency, most value-add |
| **issue** | create, list, edit, close, reopen, comment, pin, transfer, develop, lock | High frequency |
| **label** | create, list, edit, delete, clone + sync pattern | Sync is custom logic over CRUD |
| **milestone** | create, list, update (via `gh api`, no direct CLI) | REST API wrappers |
| **project** | create, edit, field-create/list/delete, item-add/edit/list/archive/delete, view, link | `gh project` now exists! |
| **release** | create, list, edit, delete, download + version bump pattern | Version bump is custom logic |
| **repo** | create, clone, fork, edit, archive, sync, deploy-key, autolink, ruleset | Config/rulesets via `gh api` |
| **actions** | run list/view/rerun/cancel/watch + workflow enable/disable/run/list | `gh run` + `gh workflow` |
| **search** | code, commits, issues, prs, repos | `gh search` |
| **admin** | secret set/list/delete, variable set/list/delete, ruleset check/list/view, auth status | Lower frequency operations |

#### Local git operations (via `git` CLI)

| Domain | Key operations | Notes |
| -------- | --------------- | ------- |
| **branching** | create, list, cleanup, naming conventions, worktree add/list/remove/prune | Config-aware, worktree-aware |
| **rebase** | onto, interactive planning, conflict handling, abort/continue | Agent advises for interactive |
| **merge** | fast-forward, no-ff, strategy selection, conflict resolution | |
| **stash** | push, pop, list, apply, drop | |
| **cherry-pick** | single, range, conflict resolution | |
| **bisect** | start, good, bad, reset — guided workflow | |
| **log-and-diff** | pretty formats, date/author/path filters, stat vs patch | |
| **recovery** | reflog, reset (soft/mixed/hard), revert, rescue commits | Safety-critical operations |

---

## Implementation Sequence

### Phase 1: Agent Foundation

1. **Rename agent directory** — `agents/aida-github-plugin/` to `agents/github-expert/`
2. **Write `github-expert.md`** — Rich agent definition following security-engineer pattern
3. **Write `knowledge/index.md`** — Knowledge catalog + external reference URL index
4. **Update `.claude-plugin/aida-config.json`** — Register `github-expert` agent name

### Phase 2: Agent Knowledge (3 files)

1. **`knowledge/operations.md`** — Common commands with correct patterns
2. **`knowledge/guardrails.md`** — Anti-patterns, gotchas, deprecated commands
3. **`knowledge/decisions.md`** — Decision frameworks

### Phase 3: Skill

1. **`skills/github/SKILL.md`** — Hub with quick reference tables
2. **`skills/github/references/`** — 9 lean recipe files (~500-1000 words each)

### Phase 4: Config Schema

Define the AIDA config preferences in `aida-config.json`:

```json
{
  "preferences": [
    { "key": "github.branching_model", "type": "select",
      "options": ["trunk-based", "github-flow", "gitflow", "custom"],
      "default": "github-flow" },
    { "key": "github.branch_prefix.feature", "type": "string", "default": "feature/" },
    { "key": "github.branch_prefix.fix", "type": "string", "default": "fix/" },
    { "key": "github.branch_prefix.chore", "type": "string", "default": "chore/" },
    { "key": "github.worktree.enabled", "type": "boolean", "default": false },
    { "key": "github.worktree.mode", "type": "select",
      "options": ["bare", "traditional"], "default": "bare" },
    { "key": "github.merge_strategy", "type": "select",
      "options": ["squash", "merge", "rebase"], "default": "squash" },
    { "key": "github.label_taxonomy", "type": "string",
      "default": "standard",
      "description": "Label set to sync: 'standard' or path to custom label definition" },
    { "key": "github.pr.default_reviewers", "type": "string", "default": "" },
    { "key": "github.pr.auto_link_issues", "type": "boolean", "default": true }
  ]
}
```

### Total Deliverables

| Component | Files | Words (est.) |
| ----------- | ------- | ------------- |
| Agent definition | 1 (`github-expert.md`) | ~3-4k |
| Agent knowledge | 3 + index | ~5-7k |
| Skill hub | 1 (`SKILL.md`) | ~4-5k |
| Skill references | 9 | ~5-8k |
| Config | 1 (`aida-config.json` update) | — |
| **Total** | **15 files** | **~17-24k words** |

Compare to the original plan: 36+ files at ~50k+ words. Same coverage, 60% fewer files, 60% less
content to write and maintain. The official docs handle the long tail.

---

## Open Questions for Review

1. **Agent model:** Spec uses `claude-sonnet-4.5`. For a knowledge-heavy expert agent, should this be
   opus instead? Sonnet is faster/cheaper but opus reasons better for ambiguous multi-step tasks.

2. **Existing `github-workflow` skill:** Should this eventually be deprecated in favor of the plugin's
   `github` skill, or maintained as a lightweight activator that defers to it?

3. **`gh project` vs GraphQL:** Now that `gh project` exists with a rich command surface, the spec's
   "always use GraphQL" stance needs updating. Proposal: use `gh project` for standard operations,
   fall back to `gh api graphql` only when the CLI can't do it.

---

## Immediate Next Steps

After plan approval:

1. Rename `agents/aida-github-plugin/` to `agents/github-expert/`
2. Write `github-expert.md` (rich agent definition)
3. Write `knowledge/index.md` + 3 knowledge files
4. Update `aida-config.json`
5. Write `skills/github/SKILL.md` + 9 reference files
6. Update `docs/plugin-spec.md` with discoveries
