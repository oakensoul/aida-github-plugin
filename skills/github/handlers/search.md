---
type: handler
name: search
title: Search Operations
description: Handler for /github search commands
skill: github
domain: search
version: 1.0.0
---

# /github search

Cross-repository search via the GitHub search API. For searching within the current repo,
use `/github issue list` or `/github pr list` with filters instead.

## issues

Search issues across repositories.

```bash
# Search by query
gh search issues "auth token expired" --repo owner/repo --state open

# With label filter
gh search issues "bug" --repo owner/repo --label "priority:high" --state open

# Across an organization
gh search issues "memory leak" --owner my-org --state open --limit 20

# JSON output
gh search issues "query" --repo owner/repo --json number,title,repository,state,url
```

## prs

Search pull requests across repositories.

```bash
# Open PRs
gh search prs "feature" --repo owner/repo --state open

# Merged PRs by author
gh search prs "auth is:merged" --repo owner/repo --author @me

# JSON output
gh search prs "query" --repo owner/repo --json number,title,state,url
```

## code

Search code across repositories.

```bash
# Search by content
gh search code "className" --repo owner/repo

# Filter by language
gh search code "def authenticate" --repo owner/repo --language python

# Filter by file path
gh search code "API_KEY" --repo owner/repo --filename "*.env*"
```

### Guardrails

- Code search results show file matches, not full file contents. Use `gh api` or read the file
  directly for full content.
- Code search indexes the default branch only — recently pushed branches may not appear.

## commits

Search commits across repositories.

```bash
gh search commits "fix auth" --repo owner/repo
gh search commits "query" --repo owner/repo --author @me
```

## repos

Search for repositories.

```bash
# By topic and language
gh search repos "cli tool" --language go --stars ">100"

# By owner
gh search repos "plugin" --owner my-org

# JSON output
gh search repos "query" --json fullName,description,stargazerCount,url
```
