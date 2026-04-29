---
name: propose-alternatives
description: "Propose 2-3 genuinely different approaches to a problem with concrete trade-offs. Use when evaluating design choices, exploring options, or challenging the current approach. Do NOT use for validating a chosen approach, code review, or implementation."
---

# Propose Alternatives

Evaluate the current approach and propose genuinely different alternatives with concrete trade-offs.

## When to use

- Evaluating design choices before implementation
- Challenging whether the current approach is optimal
- Exploring options for a non-trivial technical decision
- Comparing frameworks, patterns, or architectures

## Instructions

### 1 — Understand the problem

Gather context:
- What problem is being solved?
- What is the current approach (if any)?
- What files or code are relevant?

If any of these are unclear, use the `AskUserQuestion` tool to clarify before proceeding. Present what you understand and what's missing.

### 2 — Analyze and propose

- If a current approach exists, include it in `alternatives` as a peer candidate and set `current_id` to its id. Otherwise set `current_id` to null.
- Propose 2-3 genuinely different new approaches (not minor variations).
- Evaluate every entry — including the current one — with the same shape: pros, cons, when_to_use, confidence.
- Be concrete: name files, functions, patterns.

### 3 — Return output

Return an `AlternativesOutput` conforming to the [Output Schema](#output-schema) below.

## Rules

- **No trivial variations.** Don't propose minor differences (e.g., different variable names, library A vs library B for the same pattern).
- **Implementably different.** Each alternative must be a genuinely different approach.
- **Cite evidence.** Read relevant code before claiming an alternative is feasible. Be concrete — name files, functions, patterns.
- **Don't validate.** Propose options with trade-offs; the sanity-check skill handles validation of a chosen approach.
- **Honest confidence.** Include honest confidence scores — speculative ideas get low confidence.
- **Current may be best.** If the current approach is already optimal, say so in the recommendation.

---

## Output Schema

<!-- source: references/alternatives-schema.md -->

### AlternativesOutput

```
AlternativesOutput {
  current_id: id of the existing approach in `alternatives`, or null for greenfield problems with no current approach,
  alternatives: Alternative[],
  recommendation: which alternative id you'd pick and why
}
```

### Alternative

```
Alternative {
  id: sequential number starting from 1,
  name: short name,
  summary: 1 sentence,
  implementation: concrete description with file paths and function names,
  trade_offs: {
    pros: string[],
    cons: string[]
  },
  when_to_use: scenario where this alternative is better than the others,
  confidence: 0.0-1.0
}
```

### Field notes

- `current_id` — points at the entry in `alternatives` representing the status quo. Set to `null` only for greenfield problems with no existing approach. When non-null, the current approach must appear in the `alternatives` array as a peer candidate.
- `alternatives` — when `current_id` is set, the array contains the current approach plus 2-3 new alternatives (3-4 entries total). When `current_id` is null, the array contains 2-3 new alternatives.
- `implementation` — be concrete. Name files, functions, patterns. "Use a queue" is too vague; "Add a BullMQ job in `workers/ingest.ts` that processes batches of 100" is concrete. For the current entry, describe what is in place today.
- `confidence` — for new alternatives: how confident you are this would work well (1.0 = proven pattern, below 0.5 = speculative). For the current entry: how confident you are the status quo should be *kept* (1.0 = clearly the right call to maintain, below 0.5 = current has serious problems even if functional). The score answers "should we use this," not "does this work."
- `when_to_use` — the scenario where this specific entry is the best choice. For the current entry, describe the conditions under which the status quo is the right answer (e.g., "when migration cost outweighs benefits at current scale").
- `trade_offs` — every entry has both pros AND cons, including the current one. If you can't name a con for the status quo, you haven't thought hard enough.
- `recommendation` — must cite the chosen alternative by id. If recommending the current approach, cite `current_id`.
- Propose 2-3 genuinely different new approaches. "Use library A vs library B" is a variation, not an alternative.
