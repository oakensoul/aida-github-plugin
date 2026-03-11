---
type: adr
title: "ADR-004: Agent Teaches, Skill Does — Separation of Concerns"
status: accepted
date: "2026-03-10"
deciders:
  - "oakensoul"
context: Software
tags: [architecture, agent-design, skill-design, knowledge]
---

# ADR-004: Agent Teaches, Skill Does — Separation of Concerns

**Status**: Accepted
**Date**: 2026-03-10
**Context**: Software

## Context and Problem Statement

The plugin has two primary components: a `github-expert` agent and a `/github` dispatcher skill.
Both deal with git/GitHub, which raises the question: what does each one do, and where does the
boundary sit?

Without a clear separation, we risk:

- The agent trying to execute commands it should delegate to the skill
- The skill trying to explain concepts it should defer to the agent
- Duplicate knowledge maintained in two places
- Unclear guidance for users on when to use which

## Decision Drivers

- Users with different needs: "do this for me" vs "explain this to me"
- Non-engineers need explanations; engineers need execution
- Token efficiency — don't load execution logic when user wants education, and vice versa
- Knowledge should be authoritative and non-contradictory

## Considered Options

### Option A: Agent Does Everything

The agent handles both explanation and execution. No separate skill.

**Pros**: Single entry point, agent has full context
**Cons**: Agent definition becomes massive, always-loaded knowledge is expensive, no way to invoke
commands without loading educational content

### Option B: Skill Does Everything

The skill handles both execution and education. No agent needed.

**Pros**: Simple architecture, one component
**Cons**: Skills aren't designed for conversational education, can't handle ambiguous multi-step
reasoning, loses the "ask an expert" use case

### Option C: Agent Teaches, Skill Does (Chosen)

The agent is the knowledge expert — it explains concepts, makes recommendations, and helps with
ambiguous decisions. The skill is the executor — it runs commands reliably via the dispatcher.

**Pros**: Clean separation, each component optimized for its role, token-efficient loading,
non-engineers can talk to the agent without triggering commands
**Cons**: Two components to maintain, must coordinate knowledge between them

## Decision Outcome

**Chosen option**: Option C - Agent Teaches, Skill Does

**Rationale**:

- **Agent** (`github-expert`): "What is a cherry-pick?", "Should I rebase or merge?", "Explain
  worktrees", "What went wrong with my CI?" — conversational, educational, advisory
- **Skill** (`/github`): `/github cherry-pick <sha>`, `/github sync`, `/github pr create` —
  imperative, deterministic, config-aware execution
- Non-engineers talk to the agent; engineers use the skill; both benefit from correct behavior
- The agent knows about every `/github` command and can recommend which to use
- The skill references agent knowledge when it needs to explain an error or suggest alternatives

### Consequences

**Positive**:

- Non-engineers can ask "what's the status of the project?" without accidentally running commands
- Engineers can execute `/github pr merge` without loading educational content
- The agent can reason about ambiguous situations ("should I rebase here?") while the skill
  handles unambiguous execution
- Each component's token footprint is optimized for its use case

**Negative**:

- Knowledge must be coordinated between agent knowledge files and skill reference files
- **Mitigation**: Intentional overlap is acceptable — agent covers "why/when", skill covers "how"
- Users may not know whether to use the agent or the skill
- **Mitigation**: Agent recommends skill commands; `/github help` explains the agent

## Knowledge Distribution

| Concern | Agent Handles | Skill Handles |
| ------- | ------------- | ------------- |
| "What is a rebase?" | Explains concept, analogies, when to use | N/A |
| "Rebase my branch" | May advise, then defers to skill | Executes correctly |
| "Should I rebase or merge?" | Gathers context, makes recommendation | N/A (decision, not action) |
| "Why did CI fail?" | Analyzes logs, reasons about cause | Provides `gh run view --log-failed` |
| "Set up this repo" | Multi-step orchestration, asks questions | Individual setup commands |

## Implementation Notes

- Agent definition: `agents/github-expert/github-expert.md`
- Agent knowledge: `agents/github-expert/knowledge/` (operations, guardrails, decisions)
- Skill dispatcher: `skills/github/SKILL.md`
- Skill handlers: `skills/github/handlers/`
- Skill references: `skills/github/references/` (execution-focused recipes)
- Agent should know about all `/github` commands and explain what they do
- Skill error messages should suggest asking the agent for help with concepts

## References

- Issue #27: github-expert agent educational explanations
- Issue #2: /github dispatcher skill
- `agents/github-expert/github-expert.md` — agent definition
- `docs/github-expert-agent-plan.md` — original plan documenting this separation
