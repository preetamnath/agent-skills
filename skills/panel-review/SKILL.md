---
name: panel-review
description: "Multi-reviewer panel on N focused questions about a near-final artifact (plan, design, code, prose). R0 (you) plus two parallel reviewer subagents, per-question table with disagreement preserved, walk decisions one at a time. TRIGGER when: user says 'panel review', 'multi-agent review'; user has a mostly-done artifact and focused micro-decisions to validate."
---

# Panel Review

Three parallel reads on N focused questions, with disagreement preserved.

## Steps

### Step 1 — Dispatch

- **Reviewers:** R0 (you, concurrent) + R1, R2 (two `general-purpose` subagents in parallel).
- **Prompt (identical for all three):** artifact path(s), the questions, confidence score 0.00–1.00 per recommendation.
- **Preflight:** if any question is vague, sharpen via `AskUserQuestion` first.
- **Output schema per question:** recommendation, confidence, 2-sentence reason; plus any unprompted observations.

### Step 2 — Synthesize and confirm

- **Order:** sort by max confidence descending.
- **Table:**

      | # | Question | R0 | R1 | R2 | Max |

- **Observations:** below the table, list unprompted observations any reviewer raised.
- **Checkpoint:** use `AskUserQuestion` to confirm the walk order before walking.

### Step 3 — Walk one at a time

For each question:
1. Restate the question.
2. Show R0/R1/R2 recommendations side-by-side with reasoning highlights.
3. Use `AskUserQuestion` with the recommended pick, alternatives, and "defer" as options.
4. Apply the decision if it requires action; otherwise record and continue.
5. If a decision invalidates a later question, skip it with a one-line reason.
6. If the user challenges the recommendation, invoke the `second-opinion` skill with the question as anchor.

### Step 4 — Walk unprompted observations

For each unprompted observation, run step 3's sub-procedure.
