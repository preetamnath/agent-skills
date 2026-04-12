---
name: interview-me
description: "Move from ambiguity to clarity before building. Use when user says 'interview me', asks to be interviewed, or the task has ambiguous scope."
---

# Interview Me

Move from ambiguity to clarity before building. Read the codebase, then Socratically interview the user — surfacing hidden assumptions and testing their framing — until you could confidently hand this off to be built.

## When to use

When the task is non-trivial and the goal is vague, has multiple valid interpretations, or touches unfamiliar areas.

## When NOT to use

- User has a specific request with file paths, function names, or exact behavior
- Quick fix, typo, or single obvious change
- User says "just do it" or "skip the questions"
- User already has a PRD or detailed spec

## Protocol

### 1 — Read context first

Before asking anything, silently explore:
- Architecture docs (ARCHITECTURE.md, CLAUDE.md, DESIGN.md)
- Existing code in the affected area
- Related modules or features

Don't ask questions the codebase already answers.

### 2 — Interview

Surface what the user is assuming, not just what they're requesting. Target the least-clear concern with each question. Continue until you could confidently hand this off to be built. Use the `AskUserQuestion` tool for any question with distinct choices — include your recommendation and why. Use plain text only for genuinely open-ended questions.

Cover these concerns in whatever order and depth the task requires:

- **Scope** — What's the goal? What's in, what's out? What's affected?
- **UX and behavior** — Happy path, error states, empty states, user flows
- **Technical approach** — How should this be implemented? Patterns, data shapes, state management
- **Criteria** — What are the acceptance criteria? How will we know it's done?
- **Constraints** — Compatibility, performance, dependencies, boundaries
- **Clarity** — Resolve any remaining ambiguity or contradictions

These are starting points, not a closed list — pursue any concern relevant to the task.

If the interview runs long, check in — summarize current clarity and offer to continue or proceed. If the user exits early, note what's still unresolved in the artifact but don't block.

When a load-bearing assumption surfaces, test it once: "Does this constraint actually exist?" or "What's the simplest version that would still be valuable?" Challenge the framing, not the person.

### 3 — Feasibility check

After the interview establishes what to build, validate that the planned components, APIs, and patterns are available and usable. Launch **1–4 Sonnet subagents** in parallel, split by topic. Always run — at minimum, check existing codebase patterns in the affected area.

| Area | When relevant | How |
|---|---|---|
| UI components | Feature uses specific UI components or libraries | Check component existence, props, composition constraints |
| External APIs | Feature needs external API data | Verify API capabilities, available fields, rate limits |
| Extension/plugin targets | Feature includes an extension or plugin | Verify target capabilities and constraints |
| Existing codebase patterns | Always | Read existing code in affected areas, extract reusable patterns, verify interfaces match assumptions |

Each subagent returns: exists (yes/no), capabilities, constraints, gotchas.

If issues found: feed back into the interview — resolve with user before proceeding to confirm summary. Example: "I checked and component X doesn't support Y natively, here are our options."

### 4 — Confirm summary

Before writing, present a brief summary of the key decisions, scope, constraints, and feasibility results to the user via the `AskUserQuestion` tool with options: "Looks good — write it", "Adjust before writing". Recommended: "Looks good — write it". This catches misunderstandings from a long interview before they're committed to a file.

### 5 — Write handoff artifact

Write the summary to `meta/workflows/interviews/interview-NNN-<topic-slug>.md`. Create the directory if missing. Find the highest existing number in the directory and increment by 1 (start at 001 if empty). Tell the user the file path.

```markdown
## Interview Summary: [topic]

### Goal
[1-2 sentences]

### Decisions made
| Decision | Choice | Rationale |
|---|---|---|
| ... | ... | ... |

### Assumptions exposed
| Assumption | Resolution |
|---|---|
| ... | ... |

### In scope
- [what's included]

### Out of scope
- [what's explicitly excluded]

### Criteria
- [acceptance criteria or success conditions — what must be true for this to be done]

### Constraints
- [fixed boundaries, compatibility requirements, dependencies]

### Feasibility results
| Area | Status | Findings |
|---|---|---|
| [area checked] | Available / Partial / Unavailable | [capabilities, constraints, gotchas] |

### Unresolved questions
- [anything still ambiguous, with impact assessment]
- [or "None — ready to proceed"]

### Recommended next step
[grill-me / plan-builder / direct implementation — with reasoning]
```

After writing, use the `AskUserQuestion` tool with options based on the recommended next step (e.g., "Proceed to grill-me", "Proceed to plan-builder", "Proceed to direct implementation", "Done for now"). Recommended: whichever next step was written in the artifact.

## Rules

- **One question per round.** Tightly coupled follow-ups are fine; shotgunning unrelated questions is not.
- **Always use the `AskUserQuestion` tool for questions with distinct choices.** This is not optional. If you can enumerate the options, use the tool — include your recommendation and why. Plain text is only for genuinely open-ended questions with no enumerable answers.
- **Codebase is context, not constraints.** Existing code shows what IS, not what MUST BE. The user may intentionally want to diverge.
- Reference specific code or docs when asking: "I see X in ARCHITECTURE.md — does that apply here?"
- **Flag bad decisions during the interview, not after.** If a stated requirement or decision seems materially suboptimal (correctness, security, reliability, cost), say so with your reasoning. Respect the user's final call — record their decision in the handoff, not yours.
