---
name: propose-alternatives
description: "Propose 2-3 genuinely different approaches to a problem with concrete trade-offs. Use when evaluating design choices, exploring options, or challenging the current approach."
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

- Evaluate the current approach honestly — including when it's already the right call
- Propose 2-3 genuinely different approaches (not minor variations)
- Be concrete: name files, functions, patterns
- For each alternative, assess pros, cons, and when it's the better choice

### 3 — Return output

Return an `AlternativesOutput` conforming to the [Output Schema](#output-schema) below.

## Constraints

- **No trivial variations.** Don't propose minor differences (e.g., different variable names, library A vs library B for the same pattern).
- **Implementably different.** Each alternative must be a genuinely different approach.
- **Honest confidence.** Include honest confidence scores — speculative ideas get low confidence.
- **Current may be best.** If the current approach is already optimal, say so in the recommendation.

---

## Output Schema

<!-- source: references/alternatives-schema.md -->

### AlternativesOutput

```
AlternativesOutput {
  current_approach_assessment: 1-2 sentence evaluation of what exists,
  alternatives: Alternative[],
  recommendation: which approach (including current) you'd pick and why
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

- `implementation` — be concrete. Name files, functions, patterns. "Use a queue" is too vague; "Add a BullMQ job in `workers/ingest.ts` that processes batches of 100" is concrete.
- `confidence` — how confident you are that this alternative would work well. 1.0 = proven pattern, below 0.5 = speculative.
- `trade_offs` — every alternative has both pros AND cons. If you can't name a con, you haven't thought hard enough.
- `when_to_use` — the scenario where this specific alternative is the best choice. Helps the user match alternatives to their actual constraints.
- Propose 2-3 genuinely different approaches, not minor variations. "Use library A vs library B" is a variation, not an alternative.
