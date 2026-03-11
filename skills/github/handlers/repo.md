---
type: handler
name: repo
title: Repository Operations
description: Handler for /github repo commands
skill: github
domain: repo
version: 1.0.0
---

# /github repo

## clone

Clone a repository.

```bash
# Preferred — uses gh auth, sets upstream for forks automatically
gh repo clone owner/repo

# Clone into a specific directory
gh repo clone owner/repo ./my-directory
```

Prefer `gh repo clone` over `git clone` — it configures the `upstream` remote for forks and
uses the protocol configured in `gh config get git_protocol`.

## fork

Fork and clone a repository.

```bash
# Fork and clone in one step
gh repo fork owner/repo --clone

# Fork to an organization
gh repo fork owner/repo --clone --org my-org

# Fork without cloning (remote only)
gh repo fork owner/repo
```

## create

Create a new repository.

```bash
# Public repo, cloned locally
gh repo create my-project --public --clone

# Private repo under an org
gh repo create my-org/my-project --private --clone

# From a template
gh repo create my-project --template owner/template-repo --clone --private

# With settings
gh repo create my-project --public --clone \
  --license MIT --gitignore Python --description "Project description"
```

## view

View repository information.

```bash
# Human-readable summary
gh repo view

# JSON output
gh repo view --json name,defaultBranchRef,description,url,isPrivate

# View a remote repo
gh repo view owner/repo --json name,description,url
```

## edit

Edit repository settings.

```bash
# Update description
gh repo edit --description "New project description"

# Change default branch
gh repo edit --default-branch main

# Toggle features
gh repo edit --enable-issues --enable-wiki=false --enable-projects

# Change visibility
gh repo edit --visibility public
```

## sync

Sync a fork with its upstream.

```bash
# Sync current fork's default branch
gh repo sync

# Sync a specific branch
gh repo sync --branch develop
```

## archive

Archive a repository.

```bash
gh repo archive owner/repo --yes
```

### Guardrails

- Archive is **one-way via CLI** — unarchive requires the web UI or REST API.
- Confirm with the user before archiving.

## rulesets

View repository rulesets.

```bash
# List rulesets
gh ruleset list

# View ruleset details
gh ruleset view <id>

# Check which rulesets apply to a branch
gh ruleset check main
```

### Guardrails

- Creating/editing rulesets requires the REST API (`gh api repos/{owner}/{repo}/rulesets`).
- Rulesets, deploy keys, and webhooks require **admin permissions**.

## Reference

See [../references/repo.md](../references/repo.md) for deploy keys, environments, webhooks,
autolinks, and advanced API-only operations.
