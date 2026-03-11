---
type: adr
title: "ADR-007: Three-Tier Progressive Loading"
status: accepted
date: "2026-03-10"
deciders:
  - "oakensoul"
context: Software
tags: [architecture, token-efficiency, progressive-loading]
---

# ADR-007: Three-Tier Progressive Loading

**Status**: Accepted
**Date**: 2026-03-10
**Context**: Software

## Context and Problem Statement

ADR-002 established the `/github` dispatcher pattern with a single SKILL.md entry point. ADR-005
established the 80/20 knowledge model with lean local files. During implementation, the original
two-tier design (SKILL.md hub with inline quick-reference tables, plus reference files for deep
recipes) proved suboptimal: the hub grew to 308 lines containing tables for every domain, all of
which loaded into context on every `/github` invocation regardless of which domain the user needed.

## Decision Drivers

- Token efficiency — only load what is needed for the current operation
- Progressive disclosure — users discover capabilities incrementally
- Maintainability — each file has a clear, single responsibility
- Scalability — adding a new domain should not bloat the dispatcher

## Considered Options

### Option A: Two-Tier (Original Plan)

`SKILL.md` (hub with quick-reference tables) routes to `references/` (deep recipes).

**Pros**: Simple, fewer files
**Cons**: Hub grows linearly with domains (~308 lines for 10 domains), all tables load even when
the user only needs one domain, mixing routing logic with command details

### Option B: Three-Tier (Chosen)

`SKILL.md` (pure dispatcher) routes to `handlers/` (action-oriented execution), which link to
`references/` (deep recipes) on demand.

**Pros**: Dispatcher stays slim regardless of domain count, each handler loads independently,
clean separation between routing/execution/reference
**Cons**: One more level of indirection, more files to maintain

## Decision Outcome

**Chosen option**: Option B - Three-Tier Progressive Loading

**Rationale**:

The three tiers map to three distinct responsibilities:

| Tier | Directory | Responsibility | When Loaded | Size |
| ---- | --------- | -------------- | ----------- | ---- |
| 1 | `SKILL.md` | Routing + help menu | Always (on `/github`) | ~150 lines |
| 2 | `handlers/` | Execution instructions per domain | On domain match | ~100-180 lines each |
| 3 | `references/` | Deep recipes and edge cases | On demand for complex scenarios | ~200-300 lines each |

For a typical operation like `/github pr create`:

- **Tier 1**: SKILL.md loads (~150 lines) — dispatcher identifies `pr` domain
- **Tier 2**: `handlers/pr.md` loads (~180 lines) — execution steps for `create` action
- **Tier 3**: `references/pr.md` loads only if needed (~215 lines) — for edge cases

Total: ~330 lines for the common case, ~545 lines worst case. Compare to the two-tier approach
where the hub alone was 308 lines before even reaching reference files.

### Consequences

**Positive**:

- Dispatcher stays under 200 lines regardless of how many domains are added
- Adding a new domain means adding one handler file and one routing table row — no hub bloat
- Each handler is self-contained and can be reviewed independently
- Token cost is proportional to what is actually needed per invocation

**Negative**:

- More files to maintain (9 handlers + 9 references vs 1 hub + 9 references)
- **Mitigation**: Handler files are lean and follow a strict template — maintenance cost is low
- One more file read per invocation (dispatcher + handler vs hub alone)
- **Mitigation**: File reads are cheap; the token savings from not loading irrelevant domains
  far outweigh the cost of one additional read

## File Responsibilities

| File Type | Contains | Does NOT Contain |
| --------- | -------- | ---------------- |
| `SKILL.md` | Routing table, help menu, cross-cutting patterns | Command details, recipes |
| `handlers/*.md` | Step-by-step execution, config dependencies, guardrails | Deep recipes, edge cases |
| `references/*.md` | Comprehensive recipes, gotchas, external links | Routing, execution steps |

## References

- ADR-002: /github Dispatcher Pattern (establishes the dispatcher concept)
- ADR-004: Agent Teaches, Skill Does (separation of execution vs explanation)
- ADR-005: 80/20 Knowledge Model (lean local files philosophy)
