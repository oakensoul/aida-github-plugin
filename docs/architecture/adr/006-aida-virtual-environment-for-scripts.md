---
type: adr
title: "ADR-006: AIDA Virtual Environment for Scripts"
status: accepted
date: "2026-03-10"
deciders:
  - "oakensoul"
context: Software
tags: [architecture, python, infrastructure, aida-integration]
---

# ADR-006: AIDA Virtual Environment for Scripts

**Status**: Accepted
**Date**: 2026-03-10
**Context**: Software

## Context and Problem Statement

ADR-001 established that Python scripts will handle complex gh/git operations. These scripts need
a Python runtime with dependencies (argparse is stdlib, but Jinja2 for templates and potentially
other libraries are not). The question is: how do we manage the Python environment?

## Decision Drivers

- Zero manual setup for users — scripts should "just work"
- No conflict with system Python or other projects' virtual environments
- Consistent across all AIDA plugins that use Python
- Dependencies must be declared and isolated

## Considered Options

### Option A: System Python

Use whatever Python is installed on the system. No virtual environment.

**Pros**: No setup, no venv management
**Cons**: Version conflicts with other tools, dependency pollution, different behavior across
machines, no isolation

### Option B: Project-Local Virtual Environment

Create a venv in the plugin directory (e.g., `.venv/`).

**Pros**: Isolated per project, standard Python practice
**Cons**: Every plugin needs its own venv, disk space multiplication, users must activate manually
or scripts must manage activation, not integrated with AIDA ecosystem

### Option C: AIDA Shared Virtual Environment (Chosen)

Use AIDA's existing shared venv at `~/.aida/venv/`, which auto-bootstraps on first use.

**Pros**: Already exists, auto-bootstrap (zero manual setup), shared across all AIDA plugins,
managed by AIDA infrastructure, stamp file prevents redundant installs
**Cons**: All AIDA plugins share one venv (potential dependency conflicts), tied to AIDA framework

## Decision Outcome

**Chosen option**: Option C - AIDA Shared Virtual Environment

**Rationale**:

- AIDA already maintains a venv at `~/.aida/venv/` with auto-bootstrap
- First run creates venv, installs dependencies, stamps — subsequent runs skip installation
- Users never interact with the venv directly — it's transparent
- Dependencies declared in `requirements.txt` are installed automatically
- Consistent with how aida-core-plugin handles its Python scripts
- Shared venv means common utilities (Jinja2, PyYAML, jsonschema) are installed once

### Consequences

**Positive**:

- Zero setup for users — scripts work immediately after plugin installation
- Dependencies are isolated from system Python
- Consistent Python version and packages across all AIDA plugins
- Auto-bootstrap pattern is proven in aida-core-plugin

**Negative**:

- Dependency conflicts possible if two plugins need incompatible versions
- **Mitigation**: AIDA plugins should use compatible version ranges; stamp file
  can be invalidated to force reinstall
- Plugin is coupled to AIDA framework
- **Mitigation**: This is an AIDA plugin by definition — coupling is expected

## Technical Details

| Component | Path |
| --------- | ---- |
| Virtual environment | `~/.aida/venv/` |
| Python executable | `~/.aida/venv/bin/python3` |
| Activation script | `~/.aida/venv/bin/activate` |
| Stamp file | `~/.aida/.venv-stamp` |
| Plugin dependencies | `requirements.txt` in plugin root |

### Script Invocation

```bash
# From skill handlers or Claude Code
~/.aida/venv/bin/python3 scripts/gh_project.py move-item --project "Sprint" --issue 42

# During development
source ~/.aida/venv/bin/activate
python scripts/gh_project.py --help
```

### Dependencies

Current plugin dependencies (beyond stdlib):

- `jinja2>=3.1` — template rendering for PR/issue bodies, workflow scaffolding
- Additional dependencies as scripts are developed

## References

- AIDA venv documentation in aida-core-plugin DEVELOPMENT.md
- `~/.aida/venv/pyvenv.cfg` — venv configuration
- Issue #3: Python helper scripts for gh/git operations
