---
name: interview-me
description: "Move from ambiguity to clarity before building. Use when user says 'interview me', asks to be interviewed, or the task has ambiguous scope."
---

# Interview Me

Move from ambiguity to clarity before building. Read the codebase, then interview the user until you could confidently hand this off to be built.

## When to use

When the task is non-trivial and the goal is vague, has multiple valid interpretations, or touches unfamiliar areas.

## Protocol

### 1 — Read context first

Before asking anything, silently explore:
- Architecture docs (ARCHITECTURE.md, CLAUDE.md, DESIGN.md)
- Existing code in the affected area
- Related modules or features

Don't ask questions the codebase already answers.

### 2 — Interview

Ask questions until you could confidently hand this off to be built. Use the `AskUserQuestion` tool for any question with distinct choices — include your recommendation and why. Use plain text only for genuinely open-ended questions.

Cover these concerns in whatever order and depth the task requires:

- **Scope** — What's the goal? What's in, what's out? What's affected?
- **UX and behavior** — Happy path, error states, empty states, user flows
- **Technical approach** — How should this be implemented? Patterns, data shapes, state management
- **Constraints** — Compatibility, performance, dependencies, boundaries
- **Clarity** — Resolve any remaining ambiguity or contradictions

These are starting points, not a closed list — pursue any concern relevant to the task.

### 3 — Confirm summary

Before writing, present a brief summary of the key decisions, scope, and constraints to the user via the `AskUserQuestion` tool with options: "Looks good — write it", "Adjust before writing". Recommended: "Looks good — write it". This catches misunderstandings from a long interview before they're committed to a file.

### 4 — Write handoff artifact

Write the summary to `meta/workflows/interviews/interview-NNN-<topic-slug>.md`. Create the directory if missing. Find the highest existing number in the directory and increment by 1 (start at 001 if empty). Tell the user the file path.

```markdown
## Interview Summary: [topic]

### Goal
[1-2 sentences]

### Decisions made
| Decision | Choice | Rationale |
|---|---|---|
| ... | ... | ... |

### In scope
- [what's included]

### Out of scope
- [what's explicitly excluded]

### Constraints
- [fixed boundaries, compatibility requirements, dependencies]

### Unresolved questions
- [anything still ambiguous, with impact assessment]
- [or "None — ready to proceed"]

### Recommended next step
[create-prd / plan-builder / direct implementation — with reasoning]
```

After writing, use the `AskUserQuestion` tool with options based on the recommended next step (e.g., "Proceed to plan-builder", "Proceed to direct implementation", "Done for now"). Recommended: whichever next step was written in the artifact.

## Rules

- **Always use the `AskUserQuestion` tool for questions with distinct choices.** This is not optional. If you can enumerate the options, use the tool — include your recommendation and why. Plain text is only for genuinely open-ended questions with no enumerable answers.
- **Codebase is context, not constraints.** Existing code shows what IS, not what MUST BE. The user may intentionally want to diverge.
- Reference specific code or docs when asking: "I see X in ARCHITECTURE.md — does that apply here?"
- **Flag bad decisions during the interview, not after.** If a stated requirement or decision seems materially suboptimal (correctness, security, reliability, cost), say so with your reasoning. Respect the user's final call — record their decision in the handoff, not yours.
