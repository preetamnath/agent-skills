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

Not for:

- Reviewing implemented code
- Generating alternative approaches
- Open-ended exploratory analysis
- Interactive adversarial stress-testing

## Instructions

### 1 — Understand what's being checked

Gather context:
- The plan, design, or decision text
- Relevant files or code
- Any constraints or requirements

If the plan is vague or missing key details, use the `AskUserQuestion` tool to ask for specifics before proceeding. Present what's unclear and what you need to evaluate effectively.

### 2 — Evaluate

- Confirm what's good about the approach — don't skip this even if there are concerns
- Check for realistic failure scenarios (not theoretical edge cases)
- Identify blind spots — things not addressed that should be
- Assess whether the whole approach should be reconsidered

### 3 — Return output

Return a `SanityCheckOutput` conforming to the [Output Schema](#output-schema) below.

## Rules

- **Honest.** If the plan is sound, say so — don't manufacture concerns.
- **Realistic risks.** Focus on realistic risks, not theoretical edge cases.
- **Cite evidence.** When making claims about code, read it first. No citation = not a concern.
- **Don't suggest alternatives.** Report what's wrong or missing; the `reframe` field handles the "whole approach is wrong" case.
- **Direct reframes.** If it needs rethinking, say so directly with a concrete alternative in the `reframe` field.
- **P0-P2 only.** Concerns use P0-P2 only — plan-level issues are either blocking or not, "nice to have" doesn't apply.

---

## Output Schema

<!-- source: references/sanity-check-schema.md -->

### SanityCheckOutput

```
SanityCheckOutput {
  verdict: "sound" | "concerns" | "rethink",
  confirmation: what's good about this approach,
  concerns: Concern[],
  blind_spots: string[],
  reframe: string | null
}
```

### Concern

```
Concern {
  id: sequential number starting from 1,
  severity: "P0" | "P1" | "P2",
  issue: description of the concern,
  why_it_matters: impact if not addressed,
  suggestion: what to do instead,
  confidence: 0.0-1.0
}
```

### Field notes

- `verdict` — "sound" means proceed. "concerns" means fixable issues exist. "rethink" means the approach has fundamental problems (must populate `reframe`).
- `confirmation` — always say what's good, even when the verdict is "rethink." This prevents the user from throwing out the baby with the bathwater.
- `concerns` use P0-P2 only (no P3). Plan-level issues are either blocking or not — "nice to have" doesn't apply to plan validation.
- `blind_spots` — things the plan doesn't address. Not necessarily problems — the user may have intentionally excluded them. List them so the user can confirm.
- `reframe` — required (non-null) when verdict is "rethink"; null when verdict is "sound" or "concerns". The "you're solving the wrong problem" field — populate with a concrete alternative direction, not just "reconsider".
- `confidence` — how confident you are that this concern is real. 1.0 = certain failure mode, below 0.5 = speculative risk.
