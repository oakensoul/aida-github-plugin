---
type: adr
title: "ADR-005: 80/20 Knowledge Model"
status: accepted
date: "2026-03-10"
deciders:
  - "oakensoul"
context: Software
tags: [architecture, knowledge-management, token-efficiency]
---

# ADR-005: 80/20 Knowledge Model

**Status**: Accepted
**Date**: 2026-03-10
**Context**: Software

## Context and Problem Statement

The `github-expert` agent needs deep knowledge across git, `gh` CLI, GitHub platform features,
and best practices. The naive approach is to write exhaustive documentation covering every flag,
option, and edge case — but this produces massive files that are expensive to load into context
and painful to maintain.

Meanwhile, official documentation for `gh` CLI, GitHub APIs, and git already exists and is
well-maintained. Duplicating it locally creates a maintenance burden and risks going stale.

## Decision Drivers

- Token efficiency — knowledge files should be lean, not encyclopedic
- Maintainability — avoid duplicating content that's maintained elsewhere
- Coverage — the agent should still handle 80% of tasks without external lookups
- Accuracy — when the agent does look things up, it should know exactly where to look
- The long tail of obscure flags and edge cases should be accessible but not always loaded

## Considered Options

### Option A: Exhaustive Local Documentation

Write comprehensive knowledge files covering every command, flag, and edge case locally.
Estimated: 18+ files, 50,000+ words.

**Pros**: Everything is local, no external dependency, no WebFetch needed
**Cons**: Massive token cost when loaded, maintenance nightmare as gh CLI evolves, duplicates
official docs, stale within months

### Option B: External-Only (WebFetch Everything)

Minimal local knowledge, rely on WebFetch to official docs for all operations.

**Pros**: Always current, zero maintenance, tiny local footprint
**Cons**: Every operation requires a WebFetch (slow, token-expensive), no offline capability,
can't encode institutional knowledge (gotchas, team patterns)

### Option C: 80/20 Model (Chosen)

Three focused local knowledge files covering the 80% case (common ops, guardrails, decisions),
plus an index of external URLs for the 20% long tail.

**Pros**: Lean local files, covers daily work without lookups, knows exactly where to find the
rest, maintainable (3 files, not 18)
**Cons**: The 20% requires WebFetch, external docs could move/change

## Decision Outcome

**Chosen option**: Option C - 80/20 Knowledge Model

**Rationale**:

An expert doesn't memorize every flag — they know the common stuff cold, know the gotchas by
heart, and know exactly where to look for the rest. The knowledge base follows this principle:

- **80% coverage** from 3 local files: common operations, guardrails, decision frameworks
- **20% long tail** via indexed URLs: obscure flags, advanced API patterns, edge cases
- Total: ~6,000 words locally vs ~50,000 words for exhaustive coverage — 88% reduction

### Consequences

**Positive**:

- 3 knowledge files instead of 18 — dramatically less to maintain
- Local knowledge focuses on what official docs don't cover well: gotchas, anti-patterns,
  decision frameworks, institutional knowledge
- External URL index means the agent knows exactly where to look for the long tail
- Knowledge stays current — official docs are the source of truth for flag details
- Token cost is proportional to what's actually needed per conversation

**Negative**:

- 20% of operations require a WebFetch round-trip
- **Mitigation**: These are rare operations; the cost is amortized
- External URLs could break
- **Mitigation**: URLs point to stable official doc paths (cli.github.com/manual/*)

## Knowledge File Structure

| File | Content | Words |
| ---- | ------- | ----- |
| `operations.md` | Top 30-40 commands with correct flags | ~2,200 |
| `guardrails.md` | 23 anti-patterns and gotchas | ~1,800 |
| `decisions.md` | 5 decision frameworks with matrices | ~1,600 |
| `index.md` | File catalog + external URL index | ~500 |
| **Total** | | **~6,100** |

## External URL Index Categories

- gh CLI Manual: pr, issue, repo, project, release, run, workflow, search, label, api, secret
- GitHub Platform: Actions syntax, branch protection, rulesets, Projects v2, GraphQL API
- Git Reference: git-scm.com/docs, Pro Git book

## References

- `agents/github-expert/knowledge/index.md` — the URL index
- `docs/github-expert-agent-plan.md` — "Knowledge Base Design: The 80/20 Model" section
