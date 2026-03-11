# Issue #3: Python helper scripts for gh/git operations

**Milestone**: v0.2.0
**Labels**: scripts
**Branch**: v0.2.0/issue-3/python-scripts

## Summary

Create Python CLI scripts that wrap complex or error-prone gh/git operations. These save context
window tokens and eliminate common mistakes (wrong flags, jq syntax, multi-step lookups).

All scripts use AIDA's virtual environment (`~/.aida/venv/`). Target Python 3.11+.

## Scripts

### High Impact

- **`gh_project.py`** — Project field lookup/edit by human-readable names (eliminates 4-step ID dance)
- **`gh_query.py`** — Structured queries with clean output for PRs, issues, runs (replaces jq fumbling)
- **`gh_label_sync.py`** — Label sync + batch label operations with error handling (renamed from gh_bulk.py)

### Medium Impact

- **`gh_api.py`** — REST API wrapper for milestones, rulesets, etc. (correct method + endpoint)
- **`gh_pr_body.py`** — Template-based PR/issue body generation via Jinja2

### Lower Priority

- **`gh_release.py`** — Release creation workflow (detect-bump dropped as too opinionated)

## Conventions

- All scripts callable as `python scripts/gh_project.py <action> [--flags]`
- Use `subprocess.run` with 30s default timeout to call `gh`/`git` under the hood
- Return clean JSON or formatted output
- Handle errors with actionable messages
- Exit codes: 0=success, 1=error, 2=usage
- Follow aida-core script patterns (`scripts/` dir, `scripts/utils/` for shared code)
- `__init__.py` files in `scripts/` and `scripts/utils/` for proper imports

## Dependencies

- #1 (foundation — merged via PR #80)
- #2 (dispatcher — merged via PR #81, scripts are called by handlers)

## Acceptance Criteria

- [ ] Scripts directory with shared utils (`__init__.py`, cli.py, output.py, errors.py)
- [ ] gh_project.py with status and edit-field actions (pagination-aware)
- [ ] gh_query.py for structured PR/issue/run queries
- [ ] gh_label_sync.py for label sync and batch label operations
- [ ] gh_api.py for REST API operations (milestones, etc.)
- [ ] gh_pr_body.py for template-based body generation
- [ ] gh_release.py for release creation
- [ ] Handler files updated to reference scripts where marked with <!-- SCRIPT: -->
- [ ] Tests for script structure and basic invocation
- [ ] Linting passes
