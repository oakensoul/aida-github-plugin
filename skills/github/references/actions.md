---
type: reference
title: "Actions and CI/CD Recipes"
description: "Operational recipes for GitHub Actions runs, workflow management, and CI/CD debugging via gh CLI"
skill: github
category: actions
version: 1.0.0
---

# Actions and CI/CD Recipes

Lean recipe reference for `gh run` and `gh workflow` operations. Organized by task.

## List Recent Runs

```bash
# All recent runs
gh run list --limit 10

# Filter by workflow and branch
gh run list --workflow ci.yml --branch main --limit 10

# Failed runs only
gh run list --status failure --limit 10

# In-progress runs
gh run list --status in_progress
```

## List with JSON

```bash
# Key fields for triage
gh run list --json databaseId,displayTitle,conclusion,headBranch,url --limit 20

# Filter to failures with jq
gh run list --json databaseId,displayTitle,conclusion,headBranch \
  --jq '.[] | select(.conclusion == "failure") | "\(.databaseId) \(.displayTitle) (\(.headBranch))"'

# Runs for a specific event type
gh run list --json databaseId,displayTitle,event --jq '.[] | select(.event == "pull_request")'
```

### Key JSON Fields for Runs

| Field | Description |
| ----- | ----------- |
| `databaseId` | Numeric run ID (use this for `gh run view`, `gh run rerun`) |
| `displayTitle` | Run title (usually commit message or PR title) |
| `status` | queued, in_progress, completed |
| `conclusion` | success, failure, cancelled, skipped, timed_out, or null if in-progress |
| `headBranch` | Branch that triggered the run |
| `headSha` | Commit SHA |
| `url` | Web URL to the run |
| `event` | Trigger event: push, pull_request, workflow_dispatch, schedule |
| `workflowName` | Name of the workflow |
| `jobs` | Array of job objects (only via `gh run view --json jobs`) |

## View Failed Logs

```bash
# THE key debugging command — shows only failed job output
gh run view <id> --log-failed

# Full output with all job logs
gh run view <id> --log

# Job details as JSON
gh run view <id> --json jobs

# Identify which jobs failed
gh run view <id> --json jobs --jq '.jobs[] | select(.conclusion == "failure") | .name'

# Get failed step names within failed jobs
gh run view <id> --json jobs \
  --jq '.jobs[] | select(.conclusion == "failure") |
    {job: .name, steps: [.steps[] | select(.conclusion == "failure") | .name]}'
```

## Rerun Runs

```bash
# Rerun only the failed jobs (faster, cheaper)
gh run rerun <id> --failed

# Rerun all jobs from scratch
gh run rerun <id>

# Rerun with debug logging enabled
gh run rerun <id> --debug
```

## Watch a Run

```bash
# Poll until complete, then show result
gh run watch <id>

# Exit with non-zero if run fails (useful in scripts)
gh run watch <id> --exit-status
```

## Cancel a Run

```bash
gh run cancel <id>
```

## Trigger Workflow Manually

```bash
# Basic dispatch
gh workflow run ci.yml --ref main

# With input parameters
gh workflow run ci.yml --ref main -f environment=staging -f debug=true

# From a specific branch
gh workflow run deploy.yml --ref release/v2.0
```

Requires `workflow_dispatch` trigger defined in the workflow YAML.

## Manage Workflows

```bash
# List all workflows
gh workflow list

# Enable a disabled workflow
gh workflow enable ci.yml

# Disable a workflow
gh workflow disable ci.yml

# View workflow details
gh workflow view ci.yml
```

## Debugging Pattern

Standard triage flow for CI failures:

```bash
# 1. Find the failed run
gh run list --status failure --limit 5 --json databaseId,displayTitle,headBranch

# 2. View failed logs (this is the money command)
gh run view <id> --log-failed

# 3. Identify which jobs failed
gh run view <id> --json jobs --jq '.jobs[] | select(.conclusion == "failure") | .name'

# 4. Fix the issue locally, push the fix

# 5. Rerun only failed jobs (or let the new push trigger a fresh run)
gh run rerun <id> --failed
```

### Common Failure Signatures

| Signature | Likely Cause |
| --------- | ------------ |
| `npm ERR! network timeout` / `pip install` hangs | Dependency install timeout; retry usually fixes |
| Test passes locally, fails in CI | Test flake, timing sensitivity, or missing env var |
| Lint errors only in CI | Different tool version or config; check CI tool pinning |
| `Error: Input required and not supplied` | Missing secrets or variables in fork PR |
| `Resource not accessible by integration` | Insufficient `GITHUB_TOKEN` permissions |
| `This request was denied` on `gh api` calls | Token scope missing; `gh auth refresh -s <scope>` |

## Gotchas

- **`--log-failed` requires completed run.** It errors on in-progress runs. Use `gh run watch <id>` first
  if the run is still going.
- **Run IDs are `databaseId`, not the display number.** The number shown in the GitHub UI URL path is the
  `databaseId`. Confirm with `--json databaseId` when scripting.
- **Secrets not available in fork PRs.** This is by design for security. Workflows triggered by
  `pull_request` from forks cannot access repository secrets. Use `pull_request_target` carefully if needed.
- **`gh workflow run` requires `workflow_dispatch` trigger.** Without it in the workflow YAML, the command
  fails with "could not create workflow dispatch event."
- **`gh run rerun --debug` enables step debug logging.** Equivalent to setting the `ACTIONS_STEP_DEBUG`
  secret. Useful for opaque failures but produces verbose output.
- **Cancelled runs cannot be rerun.** You must trigger a fresh run instead.

## Go Deeper

- [gh run](https://cli.github.com/manual/gh_run)
- [gh workflow](https://cli.github.com/manual/gh_workflow)
- [Workflow syntax reference](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions)
