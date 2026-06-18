---
name: validate-answer
description: "Trust-check an answer, plan, or decision you already have — multiple identical independent reads converge per question, agreement signals confidence and splits flag what's contested, then walk each decision. TRIGGER when: user says 'validate', 'trust-check', 'is this right', 'pressure-test my decision'; user has a near-final answer or a few focused decisions to confirm. SKIP when: no answer yet, want one built (best-answer); surfacing what's missing (find-gaps)."
---

# Validate Answer

Trust-check an answer or a few focused decisions.

## When to use

You **have** an answer, plan, or decision and want to know if you can trust it.

- Multiple *identical* independent reads: agreement = confidence, disagreement = contested. The reviewers are deliberately the same — diversity here would destroy the signal.
- NOT this if you have no answer yet and want one built → `best-answer`.
- NOT this if you want to surface what you missed → `find-gaps`.
- NOT this if you're grading one concrete proposal → `second-opinion`.

## Steps

### Step 1 — Dispatch

- **Reviewers:** R0 (you, concurrent) + R1, R2 (two `general-purpose` subagents in parallel).
- **Prompt (identical for all three):** artifact path(s), the questions, a confidence (0.00–1.00) and impact score per recommendation.
- **Preflight:** if any question is vague, sharpen via `AskUserQuestion` first.
- **Output schema per question:** recommendation, confidence (0.00–1.00), impact — render `Label (value)`: Minimal (0.25) · Low (0.5) · Medium (1) · High (2) · Massive (3) — 1-2 sentence reason.
- **Unprompted observations (any reviewer):** 1-sentence claim, raising reviewer(s), confidence 0.00–1.00, impact; merge duplicates.

### Step 2 — Triage, synthesize, and confirm

- **Classify each question by its three reviewer scores** — here unanimous agreement *is* the trust signal:
    <!-- source: references/confidence-bands.md (Mode V) -->
    - **keep** (walk, no triage) — all three ≥ 0.80. Unanimous agreement across identical reviewers; re-checking spends a checker for nothing.
    - **triage** — ≥1 reviewer ≥ 0.80 **OR** ≥2 reviewers ≥ 0.70. Real support, not consensus.
    - **drop** — ≤1 reviewer ≥ 0.70 and none ≥ 0.80. Too thin to walk or check.
- **Run `triage` once** on the collected questions — each finding: id = question #, claim = recommendation text; plus the artifact path(s) from Step 1. Then route the verdicts:
    - **`consider`** → walk · **`skip`** → drop (list in Step 5).
- **Order:** sort the walk set by confidence descending — post-triage `adjusted_confidence` where triage ran, else max.
- **Dependency override:** if a decision can invalidate later questions, walk it first.
- **Table:**

| # | Question | R0 | R1 | R2 | Impact | Triage |

  `Triage` = `consider` + its `adjusted_confidence` where triage ran (e.g. `consider 0.78`), else `—` for the all-three-≥0.80 keep band.

- **Checkpoint:** use `AskUserQuestion` to confirm the walk order before walking.

### Step 3 — Walk questions one at a time

**Queue rule:** drop later questions invalidated by an approved decision, with a one-line reason.

**For each question:**
- **Present:** restate the question, quote the artifact span if location-specific, and show R0/R1/R2 side-by-side (plus the triage verdict and its reason, if triage ran).
- **Decide:** `AskUserQuestion` with options: apply / alternative / defer. Apply if actionable; otherwise record.
    - **On pushback:** run `second-opinion` on the challenged pick.

### Step 4 — Walk unprompted observations

List all observations; walk those at confidence ≥ 0.80 (Step 3's sub-procedure, skip R0/R1/R2 split) — a solo observation is uncorroborated, so it clears a higher bar than a voted question.

### Step 5 — Summary

One line each:
- **Decisions applied** — question # + pick.
- **Decisions deferred** — reason.
- **Questions skipped** (upstream invalidation) — reason.
- **Questions dropped** (Step 2 band, or triage `skip`) — question + score/reason.
- **Unprompted observations** — applied / deferred / dropped.
