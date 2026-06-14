---
name: panel-review
description: "Multi-reviewer panel on N focused questions about a near-final artifact (plan, design, code, prose). R0 (you) plus two parallel reviewer subagents, per-question table with disagreement preserved, walk decisions one at a time. TRIGGER when: user says 'panel review'; user has a mostly-done artifact and focused micro-decisions to validate. SKIP when: only one proposal under review — use `second-opinion`."
---

# Panel Review

Three parallel reads on N focused questions, with disagreement preserved.

## Steps

### Step 1 — Dispatch

- **Reviewers:** R0 (you, concurrent) + R1, R2 (two `general-purpose` subagents in parallel).
- **Prompt (identical for all three):** artifact path(s), the questions, a confidence (0.00–1.00) and impact score per recommendation.
- **Preflight:** if any question is vague, sharpen via `AskUserQuestion` first.
- **Output schema per question:** recommendation, confidence (0.00–1.00), impact — render `Label (value)`: Minimal (0.25) · Low (0.5) · Medium (1) · High (2) · Massive (3) — 1-2 sentence reason.
- **Unprompted observations (any reviewer):** 1-sentence claim, raising reviewer(s), confidence 0.00–1.00, impact; merge duplicates.

### Step 2 — Synthesize and confirm

- **Sweep:** for questions with max < 0.80 AND any reviewer < 0.70, run `second-opinion` on the highest-confidence reviewer's pick and raise Max to the synthesized score if higher.
- **Order:** sort by max confidence descending (post-sweep).
- **Dependency override:** if a decision can invalidate later questions, walk it first.
- **Table:**

| # | Question | R0 | R1 | R2 | Max | Impact |

- **Low-consensus filter:** drop questions where post-sweep max < 0.60 AND no reviewer ≥ 0.75; list in Step 5.
- **Checkpoint:** use `AskUserQuestion` to confirm the walk order before walking.

### Step 3 — Walk questions one at a time

**Queue rule:** drop later questions invalidated by an approved decision, with a one-line reason.

**For each question:**
- **Present:** restate the question, quote the artifact span if location-specific, and show R0/R1/R2 side-by-side (plus second-opinion's synthesized recommendation, if Sweep ran).
- **Decide:** `AskUserQuestion` with options: apply / alternative / defer. Apply if actionable; otherwise record.
    - **On pushback:** run `second-opinion` on the challenged pick.

### Step 4 — Walk unprompted observations

List all observations. Walk those with confidence ≥ 0.70 using Step 3's sub-procedure (skip R0/R1/R2 split).

### Step 5 — Summary

One line each:
- **Decisions applied** — question # + pick.
- **Decisions deferred** — reason.
- **Questions skipped** (upstream invalidation) — reason.
- **Questions dropped** (low panel consensus) — question + max score.
- **Unprompted observations** — applied / deferred / dropped.
