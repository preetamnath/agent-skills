---
name: best-answer
description: "Build the single strongest answer to one open question — a diverse panel of subagents attacks it, a clean-room judge maps their disagreement, then you synthesize one grounded answer better than any single take. TRIGGER when: user says 'best answer', 'fan out and synthesize', 'give me the strongest answer'; user has a hard question and no answer yet. SKIP when: validating an answer you already have (validate-answer); surfacing problems in a draft (find-gaps)."
---

# Best Answer

Build the single strongest answer to one open question: a diverse panel attacks it, a clean-room judge maps their disagreement, then you synthesize one grounded answer. The engine is diversity of error — independent attempts fail differently, so you resolve the differences deliberately instead of averaging them.

## When to use

You have a hard question and **no answer yet**, and you want the single strongest one.

- NOT this if you already have an answer and want it checked → `validate-answer`.
- NOT this if you want a list of problems in a draft, not an answer → `find-gaps`.
- NOT this if you're grading one concrete proposal → `second-opinion`.

## Instructions

### Step 1 — Frame the question and design the panel

Restate the question in a line or two. Pick a panel size (default 3; range 2–4).

Give each panelist a **distinct mandate** — angles that attack the question from non-overlapping directions:

| Task type | Example panel |
|-----------|---------------|
| Research / analysis | first-principles mechanism · skeptic (what's overstated) · practitioner (how it plays out) |
| Diagnosis | each panelist pursues a different culprit class |
| Design choice | each authors a different approach, then argues its failure modes |

When all panelists share one model (e.g. Opus), diversity must be **manufactured** from the mandates — identical panelists co-vary and the judge's map comes back empty.

### Step 2 — Fan out the panel (parallel)

Dispatch all panelists in one message (multiple `Agent` calls) so they run concurrently. Each gets the same question, its own mandate, and tools (web search, bash, read). Ask each for a structured answer — its position, key claims with evidence, and a confidence — not a raw dump.

### Step 3 — Map the disagreement (clean room)

Dispatch one `general-purpose` subagent as a clean-room judge — give it **only** the panel outputs (verbatim, each labeled by panelist) and the question, never your reasoning or which panelist you trust. Instruct it to:

- map the answers into three buckets — `contradictions` (incompatible positions, with each side), `blind_spots` (relevant points NO panelist raised), `unique_insights` (a point only one panelist made);
- earn each item — only real contradictions and material omissions, no padding;
- **map, don't decide** — pick no winner, write no final answer;
- **surface, don't verify** — don't run code or chase ground truth (that's Step 4);
- **not spawn its own subagents**;
- return the [DisagreementMap](#output-schema) verbatim — the structured map is the whole response, no narrative.

### Step 4 — Verify and synthesize (you)

You hold the original context, so you write the answer:

- Resolve each load-bearing `contradiction` deliberately — check ground truth where it's cheap (read the code, run the check), dispatching a subagent per fork when needed. Don't split the difference.
- Fold in `unique_insights` that survive scrutiny.
- Address `blind_spots`, or flag them as open.

Write one grounded answer, attributing each load-bearing claim to its evidence.

## Rules

- **Recursion guard.** Panelists must not fan out their own panels — keep deliberation to one level.
- **Cost discipline.** Reserve for hard, open-ended questions; answer a cheap or deterministic one directly.

---

## Output Schema

```
DisagreementMap {
  contradictions: [ { topic: string, positions: string[] } ],
  blind_spots: string[],          // each: the gap + why it matters, one line
  unique_insights: [ { insight: string, raised_by: string } ]
}
```
