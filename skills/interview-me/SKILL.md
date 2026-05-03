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

Surface what the user is assuming, not just what they're requesting. Target the least-clear concern with each question. Use the `AskUserQuestion` tool for any question with distinct choices — include your recommendation and why. Use plain text only for genuinely open-ended questions.

For tasks where decisions depend on each other, sketch the decision space as a compact nested list once you can name two or more distinct branches. Share it as a hypothesis: "Here's what I think we need to figure out — does this match?" If you can't yet name two branches, ask open-ended questions until you can — aim to sketch within 2–3 rounds. If the task only has one or two flat questions, skip the tree and ask directly.

Resolve one branch at a time. If a question in one branch requires resolving another first, surface the dependency, resolve the blocking branch, then return. When multiple branches block, resolve the one that unblocks the most other branches first. When branches appear, collapse, or split, update the tree inline with your next question and note what changed. When a branch merely resolves, note the decision and continue. Propose deferral when a branch can't be resolved without information unavailable now — the user confirms.

Continue until every branch is resolved or deferred, and you could confidently hand this off to be built.

Use these dimensions as a completeness check — when sketching the tree and as branches resolve, verify nothing is missing:

- **Scope** — What's the goal? What's in, what's out? What's affected?
- **UX and behavior** — Happy path, error states, empty states, user flows
- **Technical approach** — How should this be implemented? Patterns, data shapes, state management
- **Criteria** — What are the acceptance criteria? How will we know it's done?
- **Constraints** — Compatibility, performance, dependencies, boundaries
- **Clarity** — Resolve any remaining ambiguity or contradictions

These are a lens, not a prescribed structure — the task-specific tree (or direct questions for simpler tasks) is the primary navigation.

If the interview runs long, check in — summarize current clarity and offer to continue or proceed. If the user exits early, note what's still unresolved in the artifact but don't block.

When a load-bearing assumption surfaces, test it once: "Does this constraint actually exist?" or "What's the simplest version that would still be valuable?" Challenge the framing, not the person.

### 3 — Feasibility check

After the interview establishes what to build, validate that the planned components, APIs, and patterns are available and usable. Launch **1–4 Sonnet subagents** in parallel, split by topic. Always run — at minimum, check existing codebase patterns in the affected area.

| Area | When relevant | How |
|---|---|---|
| UI components | Feature uses specific UI components or libraries | Check component existence, props, composition constraints |
| External APIs | Feature needs external API data | Verify API capabilities, available fields, rate limits |
| Extension/plugin targets | Feature includes an extension or plugin | Verify target capabilities and constraints |
| Existing codebase patterns | Always | Read existing code in affected areas, extract reusable patterns, verify interfaces match assumptions. Note test file locations, test style (unit/integration/e2e), and any test helpers or fixtures the implementation should follow |

Each subagent returns: exists (yes/no), capabilities, constraints, gotchas.

If issues found: feed back into the interview — update the decision tree if branches changed, resolve with user, then proceed to confirm summary. Limit re-entry to one follow-up round per feasibility issue; if still unresolved, capture it in Unresolved questions. Example: "I checked and component X doesn't support Y natively, here are our options."

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

### Decision tree
[If the interview used a decision tree, include the final version as a compact nested list. Tag each branch inline. Omit for simpler interviews that didn't use a tree.]
- Branch name [resolved]
  - Sub-branch [collapsed: user confirmed X instead]
  - Sub-branch [deferred: blocked on Y]

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
Pick exactly one based on the sections above:
- `grill-me` — if `Unresolved questions` is non-empty, OR `Assumptions exposed` contains load-bearing items not pressure-tested, OR `Feasibility results` shows Partial/Unavailable
- `sanity-checker` agent — if decisions look sound but you want a lighter validation pass before building
- `plan-builder` — if scope spans 3+ work items OR multiple files/modules, no unresolved/feasibility flags
- Direct implementation — if single-file or single-commit change, no unresolved flags

[Pick one with reasoning that cites the specific row(s) above that triggered the choice]
```

After writing, use the `AskUserQuestion` tool with options based on the recommended next step (e.g., "Proceed to grill-me", "Spawn sanity-checker agent", "Proceed to plan-builder", "Proceed to direct implementation", "Done for now"). Recommended: whichever next step was written in the artifact.

### End condition

Stop when every branch in the decision tree is resolved or deferred, the user has confirmed the summary, and the handoff artifact has been written.

## Rules

- **One question per round.** Tightly coupled follow-ups are fine; shotgunning unrelated questions is not. Sketching or updating the tree alongside a question counts as one round — don't burn a separate round just to present the tree.
- **Always use the `AskUserQuestion` tool for questions with distinct choices.** This is not optional. If you can enumerate the options, use the tool — include your recommendation and why. Plain text is only for genuinely open-ended questions with no enumerable answers.
- **Codebase is context, not constraints.** Existing code shows what IS, not what MUST BE. The user may intentionally want to diverge.
- Reference specific code or docs when asking: "I see X in ARCHITECTURE.md — does that apply here?"
- **Flag bad decisions during the interview, not after.** If a stated requirement or decision seems materially suboptimal (correctness, security, reliability, cost), say so with your reasoning. Respect the user's final call — record their decision in the handoff, not yours.
