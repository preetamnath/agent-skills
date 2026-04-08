---
name: sanity-check
description: "Validate or challenge a plan, design, or decision. Confirms what's good, flags realistic concerns, and identifies blind spots."
---

# Sanity Check

Validate a plan, design, or decision. Confirm good choices, flag real concerns, and identify blind spots.

## When to use

- Before implementing a plan
- After designing an approach
- When making a non-trivial technical decision
- When you want your thinking challenged

## Instructions

### Step 1 — Read the output schema

Read `references/sanity-check-schema.md` to understand the required output format.

### Step 2 — Understand what's being checked

Gather context:
- The plan, design, or decision text
- Relevant files or code
- Any constraints or requirements

If the plan is vague or missing key details, ask for specifics before proceeding.

### Step 3 — Evaluate

- Confirm what's good about the approach — don't skip this even if there are concerns
- Check for realistic failure scenarios (not theoretical edge cases)
- Identify blind spots — things not addressed that should be
- Assess whether the whole approach should be reconsidered

### Step 4 — Return structured output

Return the `SanityCheckOutput` conforming to the schema in `references/sanity-check-schema.md`.

## Constraints

- Be honest. If the plan is sound, say so — don't manufacture concerns
- Focus on realistic risks, not theoretical edge cases
- If it needs rethinking, say so directly with a concrete alternative in the `reframe` field
- Concerns use P0-P2 only — plan-level issues are either blocking or not, "nice to have" doesn't apply
