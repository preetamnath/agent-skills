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

### Step 1 — Read the output schema

Read `references/alternatives-schema.md` to understand the required output format.

### Step 2 — Understand the problem

Gather context:
- What problem is being solved?
- What is the current approach (if any)?
- What files or code are relevant?

If any of these are unclear, ask before proceeding.

### Step 3 — Analyze and propose

- Evaluate the current approach honestly — including when it's already the right call
- Propose 2-3 genuinely different approaches (not minor variations)
- Be concrete: name files, functions, patterns
- For each alternative, assess pros, cons, and when it's the better choice

### Step 4 — Return structured output

Return the `AlternativesOutput` conforming to the schema in `references/alternatives-schema.md`.

## Constraints

- Don't propose trivial variations (e.g., different variable names, library A vs library B for the same pattern)
- Each alternative must be implementably different
- Include honest confidence scores — speculative ideas get low confidence
- If the current approach is already optimal, say so in the recommendation
