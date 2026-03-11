---
type: handler
name: actions
title: CI/CD and Actions Operations
description: Handler for /github actions commands
skill: github
domain: actions
version: 1.0.0
---

# /github actions

## list

List recent workflow runs.

```bash
# All recent runs
gh run list --limit 10

# Failed runs only
gh run list --status failure --limit 10

# Filter by workflow and branch
gh run list --workflow ci.yml --branch main --limit 10

# JSON output for processing
gh run list --json databaseId,displayTitle,conclusion,headBranch,url --limit 20
```

## view

View a specific run's details and logs.

```bash
# Summary
gh run view <id>

# Failed job logs only (the key debugging command)
gh run view <id> --log-failed

# Full logs
gh run view <id> --log

# Job details as JSON
gh run view <id> --json jobs --jq '.jobs[] | {name, conclusion, status}'
```

## debug

Standard triage flow for CI failures.

### Steps

1. Find the failed run:

```bash
gh run list --status failure --limit 5 --json databaseId,displayTitle,headBranch
```

1. View failed logs:

```bash
gh run view <id> --log-failed
```

1. Identify which jobs and steps failed:

```bash
gh run view <id> --json jobs \
  --jq '.jobs[] | select(.conclusion == "failure") |
    {job: .name, steps: [.steps[] | select(.conclusion == "failure") | .name]}'
```

1. After fixing locally, rerun only the failed jobs:

```bash
gh run rerun <id> --failed
```

## rerun

Rerun a workflow run.

```bash
# Rerun only failed jobs (faster, cheaper)
gh run rerun <id> --failed

# Rerun all jobs from scratch
gh run rerun <id>

# Rerun with debug logging
gh run rerun <id> --debug
```

## cancel

Cancel an in-progress run.

```bash
gh run cancel <id>
```

## trigger

Manually trigger a workflow.

```bash
# Basic dispatch
gh workflow run ci.yml --ref main

# With input parameters
gh workflow run ci.yml --ref main -f environment=staging -f debug=true
```

Requires `workflow_dispatch` trigger defined in the workflow YAML.

## workflows

List and manage workflows.

```bash
# List all workflows
gh workflow list

# Enable a disabled workflow
gh workflow enable ci.yml

# Disable a workflow
gh workflow disable ci.yml
```

### Guardrails

- **`--log-failed` requires a completed run** — it errors on in-progress runs. Use
  `gh run watch <id>` first if the run is still going.
- **Run IDs are `databaseId`**, not the display number. Confirm with `--json databaseId`.
- **Cancelled runs cannot be rerun** — trigger a fresh run instead.
- **`gh workflow run` requires `workflow_dispatch`** in the workflow YAML.

## Reference

See [../references/actions.md](../references/actions.md) for debugging patterns, common failure
signatures, and workflow dispatch details.
