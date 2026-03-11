# Issue #2: /github dispatcher skill with (domain) (action) routing

**Milestone**: v0.2.0
**Labels**: skill
**Branch**: v0.2.0/issue-2/github-dispatcher

## Summary

Rewrite the `github` skill as a dispatcher following the same pattern as `/aida`.
The skill becomes the single entry point: `/github (domain) (action)`.

## Design

```text
/github branch create
/github issue create
/github pr create
/github pr merge
/github project status
/github release create
/github label sync
/github milestone create
```

- `/github` with no args shows help menu with all available domains and actions
- Dispatcher parses domain + action and routes to the appropriate handler
- Handlers live in `skills/github/handlers/` (separate from reference docs)
- Each handler calls Python scripts for reliable execution

## Structure

```text
skills/github/
├── SKILL.md              # Dispatcher + help menu + routing
├── handlers/             # Per-domain action handlers
│   ├── branch.md
│   ├── issue.md
│   ├── pr.md
│   ├── project.md
│   ├── release.md
│   ├── label.md
│   └── milestone.md
├── references/           # Deep reference docs (existing, keep as-is)
└── templates/            # Jinja2 templates for PR/issue bodies
```

## Dependencies

- #1 (foundation — merged via PR #80)

## Acceptance Criteria

- [ ] SKILL.md rewritten as dispatcher with routing logic
- [ ] `/github` with no args shows help menu
- [ ] Handler files created for each domain
- [ ] Handlers route to Python scripts where available
- [ ] Existing reference files preserved and linked
- [ ] Tests updated to validate new structure
- [ ] Linting passes
