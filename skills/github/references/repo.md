---
type: reference
title: "Repository Setup and Configuration"
description: "Recipes for cloning, creating, forking, configuring, and managing GitHub repositories"
skill: github
category: repository
version: 1.0.0
---

# Repository Setup and Configuration

Recipes for repo lifecycle operations: clone, fork, create, configure, archive, and advanced settings
that require the REST API. For branching and worktree setup after cloning, see [branching.md](branching.md).

## Clone

```bash
# Preferred — uses existing gh auth, respects SSH/HTTPS preference, sets upstream for forks
gh repo clone owner/repo

# Clone into a specific directory
gh repo clone owner/repo ./my-directory

# Clone with git (only when gh CLI is unavailable)
git clone https://github.com/owner/repo.git
```

Prefer `gh repo clone` over `git clone` — it automatically configures the `upstream` remote when
cloning a fork and uses the protocol configured in `gh config get git_protocol`.

## Fork and Clone

```bash
# Fork to your account and clone locally in one step
gh repo fork owner/repo --clone

# Fork without cloning (remote only)
gh repo fork owner/repo

# Fork to an organization
gh repo fork owner/repo --clone --org my-org

# Fork with a custom name
gh repo fork owner/repo --fork-name my-custom-name
```

After forking, the clone has `origin` pointing to your fork and `upstream` pointing to the source repo.

## Create

```bash
# Public repo, cloned locally
gh repo create my-project --public --clone

# Private repo, cloned locally
gh repo create my-project --private --clone

# Create under an organization
gh repo create my-org/my-project --private --clone

# Create from a template repo
gh repo create my-project --template owner/template-repo --clone --private

# Create remote only (no local clone)
gh repo create my-project --public --description "Project description"

# Create with specific settings
gh repo create my-project --public --clone \
  --license MIT --gitignore Python --description "My new project"
```

## View Repo Info

```bash
# Human-readable summary
gh repo view

# Structured output — key fields
gh repo view --json name,defaultBranchRef,description,url,isPrivate

# Useful fields for scripting
gh repo view --json name,owner,defaultBranchRef,homepageUrl,isArchived,isFork,isPrivate,pushedAt \
  --jq '{name: .name, owner: .owner.login, default_branch: .defaultBranchRef.name, private: .isPrivate}'

# View a specific remote repo without cloning
gh repo view owner/repo --json name,description,url
```

Key `--json` fields: `name`, `owner`, `defaultBranchRef`, `description`, `url`, `homepageUrl`,
`isArchived`, `isFork`, `isPrivate`, `pushedAt`, `stargazerCount`, `forkCount`,
`repositoryTopics`, `licenseInfo`.

## Edit Repo Settings

```bash
# Update description
gh repo edit --description "New project description"

# Change default branch
gh repo edit --default-branch main

# Toggle features
gh repo edit --enable-issues --enable-wiki=false --enable-projects

# Set visibility
gh repo edit --visibility public

# Set homepage
gh repo edit --homepage "https://docs.example.com"

# Set multiple options at once
gh repo edit --description "Updated" --default-branch main --enable-issues --enable-wiki=false

# Edit a remote repo
gh repo edit owner/repo --description "Updated remotely"
```

## Archive

```bash
# Archive (irreversible via CLI — unarchive requires the web UI or API)
gh repo archive owner/repo --yes

# Archive current repo
gh repo archive --yes
```

## Sync Fork

```bash
# Sync current fork's default branch with upstream
gh repo sync

# Sync a specific fork from a specific upstream
gh repo sync owner/fork --source upstream/repo

# Sync a specific branch
gh repo sync --branch develop
```

## Rulesets

Rulesets are the newer, more flexible replacement for branch protection rules.

```bash
# List rulesets for current repo
gh ruleset list

# List rulesets for a specific repo
gh ruleset list --repo owner/repo

# View ruleset details
gh ruleset view <id>

# Check which rulesets apply to a branch (branch name is a positional argument)
gh ruleset check main

# Check a specific ref (use the ref name as positional argument)
gh ruleset check refs/heads/release/1.0
```

Creating and editing rulesets requires the REST API:

```bash
# List rulesets via API (includes full configuration)
gh api repos/{owner}/{repo}/rulesets

# View a specific ruleset
gh api repos/{owner}/{repo}/rulesets/<id>
```

## API-Only Operations

These repo settings have no dedicated `gh` CLI command. Use `gh api` with the REST endpoints.

### Deploy Keys

```bash
# List deploy keys
gh api repos/{owner}/{repo}/keys --jq '.[] | {id, title, read_only}'

# Add a deploy key (read-only)
gh api repos/{owner}/{repo}/keys --method POST \
  -f title="CI deploy key" -f key="ssh-ed25519 AAAA..." -F read_only=true

# Remove a deploy key
gh api repos/{owner}/{repo}/keys/<id> --method DELETE
```

### Environments

```bash
# List environments
gh api repos/{owner}/{repo}/environments --jq '.environments[] | {name, id}'

# Get environment details (includes protection rules)
gh api repos/{owner}/{repo}/environments/<name>

# Create or update an environment
gh api repos/{owner}/{repo}/environments/<name> --method PUT
```

### Webhooks

```bash
# List webhooks
gh api repos/{owner}/{repo}/hooks --jq '.[] | {id, name, active, events}'

# Create a webhook
gh api repos/{owner}/{repo}/hooks --method POST \
  -f name="web" -f 'config[url]=https://example.com/webhook' \
  -f 'config[content_type]=json' -f 'events[]=push' -f 'events[]=pull_request'

# Delete a webhook
gh api repos/{owner}/{repo}/hooks/<id> --method DELETE
```

### Autolinks

```bash
# List autolink references
gh api repos/{owner}/{repo}/autolinks

# Create an autolink (e.g., JIRA-<num> links to Jira)
gh api repos/{owner}/{repo}/autolinks --method POST \
  -f key_prefix="JIRA-" -f url_template="https://jira.example.com/browse/JIRA-<num>" \
  -F is_alphanumeric=true
```

## Gotchas

- **`gh repo clone` over `git clone`** — Automatically sets `upstream` remote for forks and respects
  your configured SSH/HTTPS preference. Only fall back to `git clone` when `gh` is unavailable.
- **Rulesets vs branch protection** — Rulesets are the newer, more flexible replacement. They support
  tag rules, org-level inheritance, and bypass lists. Prefer rulesets for new repos.
- **Admin permissions required** — Rulesets, deploy keys, webhooks, environments, and visibility changes
  all require admin (or org owner) permissions.
- **`gh api` for the gaps** — Deploy keys, webhooks, environments, and autolinks have no dedicated CLI
  command. Always use `gh api repos/{owner}/{repo}/...` for these.
- **Archive is one-way via CLI** — `gh repo archive` has no `unarchive` counterpart. Use the web UI or
  `gh api repos/{owner}/{repo} --method PATCH -F archived=false` to unarchive.
- **Fork sync direction** — `gh repo sync` syncs your fork FROM upstream. It does not push your local
  changes to the fork.

## Go Deeper

- [gh repo](https://cli.github.com/manual/gh_repo)
- [gh ruleset](https://cli.github.com/manual/gh_ruleset)
- [Managing rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)
- [Deploy keys API](https://docs.github.com/en/rest/deploy-keys)
- [Environments API](https://docs.github.com/en/rest/deployments/environments)
- [Webhooks API](https://docs.github.com/en/rest/webhooks/repos)
- [Autolinks API](https://docs.github.com/en/rest/repos/autolinks)
