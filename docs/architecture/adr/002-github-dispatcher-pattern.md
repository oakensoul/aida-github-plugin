---
type: adr
title: "ADR-002: /github Dispatcher Pattern"
status: accepted
date: "2026-03-10"
deciders:
  - "oakensoul"
context: Software
tags: [architecture, skill-design, token-efficiency, ux]
---

# ADR-002: /github Dispatcher Pattern

**Status**: Accepted
**Date**: 2026-03-10
**Context**: Software

## Context and Problem Statement

The original plugin spec proposed ~50 individual skills — one per `gh <noun> <verb>` combination
(e.g., `pr-create`, `pr-merge`, `branch-cleanup`, `project-item-update`). This creates a fundamental
token efficiency problem: AIDA loads skill metadata into context, and 50 skills at ~100 words each
means ~5,000 words of metadata always in context, whether or not the user needs any of them.

Additionally, 50 separate skills create discoverability and consistency challenges. Users must know
which skill exists for their task, and each skill may have slightly different conventions.

## Decision Drivers

- Token efficiency — metadata tax should be minimal (tens of words, not thousands)
- Discoverability — users should find commands easily without memorizing skill names
- Consistency — all GitHub operations should feel like one cohesive tool
- Extensibility — adding new commands shouldn't require new skill registration
- Follows established patterns — AIDA core uses `/aida (subcommand)` dispatcher

## Considered Options

### Option A: 50 Individual Skills

One skill per operation: `/pr-create`, `/branch-cleanup`, `/project-item-update`, etc.

**Pros**: Each skill is self-contained, simple to implement individually
**Cons**: ~5,000 words always in context, poor discoverability, inconsistent UX across skills,
adding a new command requires registering a new skill

### Option B: Domain-Grouped Skills (5-8 skills)

Group by domain: `/github-pr`, `/github-branch`, `/github-project`, etc.

**Pros**: Reduces metadata tax to ~500-800 words, logical grouping
**Cons**: Still multiple entry points, user must know which domain their task falls under,
`git` vs `gh` boundary becomes visible (is rebase a branch or git operation?)

### Option C: Single Dispatcher Skill (Chosen)

One skill with `(domain) (action)` routing: `/github branch create`, `/github pr merge`, etc.

**Pros**: ~100 words metadata tax (1 skill), one entry point, `/github` with no args shows help,
adding commands only requires a new handler file, follows `/aida` pattern
**Cons**: Dispatcher adds a routing layer, help menu must be well-organized to avoid overwhelming users

## Decision Outcome

**Chosen option**: Option C - Single Dispatcher Skill

**Rationale**:

- Token cost: ~100 words always-on (1 skill) vs ~5,000 words (50 skills) — 98% reduction
- One entry point: `/github` is the only thing users need to remember
- `/github` with no arguments shows a categorized help menu — full discoverability
- `/github help <topic>` provides deep guidance on any domain
- New commands are just new handler files — no skill registration, no metadata bloat
- Consistent with AIDA's own `/aida (subcommand)` pattern

### Consequences

**Positive**:

- Minimal context tax — one skill registration regardless of how many commands exist
- Users learn one pattern: `/github <domain> <action>`
- Help menu provides natural navigation
- Adding commands is purely additive (new handler file, update routing table)
- git and gh operations unified under one interface — users don't think about which binary runs

**Negative**:

- Dispatcher routing logic must be maintained
- **Mitigation**: Simple pattern match, routing table in SKILL.md
- Help menu could become overwhelming as command count grows
- **Mitigation**: Categorized help, `/github help <domain>` for focused views

## Implementation Notes

- Dispatcher lives in `skills/github/SKILL.md`
- Handlers live in `skills/github/handlers/<domain>.md`
- Reference docs remain in `skills/github/references/` (deep knowledge, not routing)
- Routing table maps `(domain, action)` pairs to handler files
- Unknown commands show helpful "did you mean?" suggestions

## References

- AIDA `/aida` dispatcher pattern in aida-core-plugin
- Issue #2: /github dispatcher skill with (domain) (action) routing
- Issue #45: /github help system
