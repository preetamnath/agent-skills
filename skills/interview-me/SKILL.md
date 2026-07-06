---
name: interview-me
description: "Socratically interview the user to move an open question — a decision, strategy, trade-off, or research direction — from ambiguity to clarity. TRIGGER when: user says 'interview me' or asks to be interviewed; user wants to think a decision or trade-off through Socratically; the topic is ambiguous and not a buildable feature meant to produce a spec."
---

# Interview Me

Socratically interview the user — surfacing hidden assumptions and testing their framing — until an open question is clear enough to act on. Any topic; no codebase or buildable feature assumed.

## When to use

YES: the goal is vague, has multiple valid interpretations, or hinges on assumptions worth testing; user says "interview me" or asks to be interviewed; user wants to think a decision or trade-off through out loud.

NO: user has a specific request with exact intent and no ambiguity (just do it); the topic is a buildable feature that should produce a spec (use `product-interview`); the user wants a finished plan stress-tested (use `grill-me`) or one concrete proposal rated (use `second-opinion`).

## Protocol

### Step 1 — Read context first

When the topic touches existing code, docs, or files, skim the affected area before asking — don't ask what the material already answers. For purely external or open-ended topics, skip to Step 2.

### Step 2 — Interview

Target the least-clear concern with each question.

When decisions depend on each other, sketch the decision space as a compact nested list once you can name two or more distinct branches, and share it as a hypothesis: "Here's what I think we need to figure out — does this match?" Seed the tree beyond the user's framing: add any load-bearing branch they didn't raise — from the Step-1 skim, or from domain knowledge when the topic has no material — saying where it came from. If you can't yet name two branches, ask open-ended questions until you can — aim to sketch within 2–3 rounds. If the topic is one or two flat questions, skip the tree and ask directly.

Every node carries a trailing status — `- [branch] — [resolved: choice] | [open] | [deferred: why] | [blocked by branch] | [collapsed: why]` — and blocking branches sort first. Resolve one branch at a time. When a branch depends on another, surface the dependency, resolve the blocking branch first, then return; when several block, resolve the one that unblocks the most others first. Update the tree inline as branches resolve, collapse, split, or defer, noting what changed. As each branch resolves, record the decision, its choice, and the rationale — don't reconstruct them from memory at the end. Propose deferral — for the user to confirm — when a branch needs information unavailable now.

Use these dimensions as a completeness lens, not a required structure — adapt them to the topic and verify nothing load-bearing is missing:

- **Goal** — the outcome wanted; what's in, what's out
- **Options** — the distinct paths and their trade-offs
- **Assumptions** — what's being taken for granted
- **Constraints** — fixed boundaries, dependencies, non-negotiables
- **Criteria** — how you'll know the decision is right or the question is settled
- **Clarity** — remaining ambiguity or contradictions

When the topic turns out to involve building or changing software, extend the lens with **UX & behavior** (flows, error and empty states) and **Technical approach** (patterns, data shapes, state).

Test a load-bearing assumption once when it surfaces — "Does this constraint actually exist?" or "What's the simplest version that still works?" — challenging the framing, not the person. Continue until every branch is resolved or deferred and you could confidently act on the outcome. If the interview runs long, summarize current clarity and offer to continue or stop; if the user exits early, record what's unresolved and don't block.

### Step 3 — Verify before resolving (optional)

Run a verification subagent only when it would change a decision. Two generalized checks, either or both:

- **External fact** — a decision hinges on an unknown you can check (a real constraint, a number, prior art, an API capability). Dispatch a subagent to verify it; it returns the fact plus source and any caveat.
- **Existing patterns** — the conversation is inside a repo of files or code and the decision should build on what's already there. Dispatch a subagent to read the affected area and report the existing patterns, conventions, and interfaces as they are — for any repo, code or docs.

Feed findings back into Step 2: update the tree if a branch changed, resolve with the user, then continue. Cap re-entry at one follow-up round per finding; capture anything still unresolved under Open questions.

### Step 4 — Confirm the summary

Before writing, print the summary in chat in this exact shape — it catches misunderstandings from a long interview before they reach the file:

```
**Interview summary (pre-write):**
- Decisions: [decision → choice]        (one per line)
- Assumptions exposed: [assumption → resolution]
- Open questions: [each | none]

**Assumptions I'm carrying (never discussed):**
- [assumption] — [what rests on it]
```

(Write `None — everything load-bearing was discussed` when the assumptions list is empty.) Then use `AskUserQuestion` only for the choice: "Looks good — write it" / "Adjust before writing" (recommend the former).

### Step 5 — Write the interview file

Write the summary to `meta/interviews/NNN-interview-<topic-slug>.md`, creating the directory if missing and incrementing `NNN` from the highest existing number (start at `001`). Tell the user the path.

```markdown
## Interview Summary: [topic]

### Goal
[1–2 sentences]

### Decisions made
| Decision | Choice | Rationale |
|---|---|---|
| ... | ... | ... |

### Assumptions exposed
| Assumption | Resolution |
|---|---|
| ... | ... |

### Decision tree
[If a tree was used, the final version in Step 2's node format. Omit for simpler interviews.]
- Branch — [resolved: choice]
  - Sub-branch — [collapsed: user confirmed X]
  - Sub-branch — [deferred: needs data unavailable now]

### Constraints and criteria
[Fixed boundaries and how we'll know the decision is right. Omit either if not applicable.]

### Verified facts
[Findings from Step 3 — fact, source, caveat. Omit if Step 3 didn't run.]

### Unverified load-bearing assumptions
[ALWAYS present — the gap between what this interview concluded and what was checked. Every assumption the outcome leans on that nothing verified, with what rests on it. Write "None — every load-bearing assumption was verified or tested" when empty.]
- [assumption] — [what rests on it]

### Open questions
- [anything still ambiguous, with its impact]
- [or "None — ready to proceed"]

### Recommended next step
Derive 2–4 next-step options from what THIS interview surfaced, naming the specific area each acts on (e.g. "Pressure-test <the unresolved assumption> with grill-me", "Spec this feature with product-interview", "Act on it now", "Done"). Cite the row(s) above that drove each, and mark one recommended. Reach for a canonical handoff when it fits — `product-interview` (turned out buildable), `grill-me` (an open question or untested assumption remains), `second-opinion` (a resolved decision wants an external rating) — as candidates, not a required menu.
```

After writing, print the next-step options from the artifact in chat, then use `AskUserQuestion` for the choice — "What do you want to do next?" — recommending the one the artifact marked.

### End condition

Stop when every branch is resolved or deferred, the user has confirmed the summary, and the interview file is written.

## Rules

- **One question per round.** Tightly coupled follow-ups, and a tree sketch alongside a question, count as one round.
- **Always use `AskUserQuestion` for enumerable choices.** Include your recommendation and why; reserve plain text for genuinely open-ended questions.
- **Produce clarity, not a build contract.** If the topic turns out buildable, hand off to `product-interview` rather than drifting into spec-writing here.
- **Play back concrete scenarios, not abstract questions.** Confirm intent by walking one specific case in the shape `[trigger]: [what happens] — right?` ("The contract renews in month 3 at double the price: you stay — right?") — a wrong detail draws the correction an abstract question won't.
- **Existing material is context, not constraints.** What exists shows what IS, not what MUST BE — the user may intentionally diverge.
- **Flag bad decisions during the interview, not after.** If a stated choice seems materially suboptimal, say so with your reasoning, then record the user's final call in the artifact — not yours.
