---
name: find-gaps
description: "Surface what a draft, answer, or code is missing — parallel subagents each apply a different lens, scoring findings by impact and confidence, then walk them one at a time. TRIGGER when: user says 'find gaps', 'what did I miss', 'analyze from multiple angles', 'what am I overlooking'; user has an in-progress artifact and an open mandate. SKIP when: building one answer (best-answer); trust-checking an answer you have (validate-answer)."
---

# Find Gaps

Surface what an in-progress artifact is missing — many parallel lenses, scored findings, walked one at a time.

## When to use

You have a draft, answer, or code and want to surface what you **missed** — blind spots, risks, overlooked angles.

- NOT this if you want one synthesized answer → `best-answer`.
- NOT this if you want a yes/no trust signal on an answer you have → `validate-answer`.
- NOT this if you're grading one concrete proposal → `second-opinion`.

## Steps

### Step 1 — Frame and derive lenses

- **Derive lenses** from the artifact's risk surface — orthogonal angles that together cover what could be wrong or improvable (for a skill: resumability, failure-modes, coherence-with-siblings, UX; for a spec: scope, architecture, edge cases). One lens per subagent; merge near-duplicates — overlap re-raises one finding and wastes the fan-out.
- **Count:** default 3–5 lenses; scale up only for a broad audit. If the user named the exact lenses, honor them and skip the checkpoint; if partial, honor those and fill any gap.
- **Checkpoint:** print the lens list (one line each) and confirm via `AskUserQuestion` ("Run these" / "Adjust").

### Step 2 — Dispatch

- **Readers:** R0 (you, concurrent) takes the whole-artifact view; R1…RN are parallel `general-purpose` subagents, one focused lens each.
- **Prompt (per lens):** artifact path(s), the lens and what it must scrutinize, and the return contract.
- **Return contract:** `finding` · `recommended action` · `reasoning (pro/con)` — whichever are relevant — plus two scores, always: `impact` — render `Label (value)`: Minimal (0.25) · Low (0.5) · Medium (1) · High (2) · Massive (3) — and `confidence` (0.00–1.00).

### Step 3 — Synthesize, band, and triage

- **Dedup across lenses:** the same finding raised by two lenses is one row — keep the max confidence as its confidence `c`.
- **Band each finding by `c`** — the bands are a cost lever, floor at 0.70:
    <!-- source: references/confidence-bands.md (Mode F) -->
    - **keep** (no triage) — `c ≥ 0.80`.
    - **triage** — `0.70 ≤ c < 0.80`.
    - **drop** — `c < 0.70`.
- **Run `triage` once** on the collected findings — each finding: id = finding #, claim = the finding text; plus the artifact path(s). Then route the verdicts:
    - **`consider`** → walk · **`skip`** → park (show in the table, walk only if asked).
- **Table** (walk set + parked skips):

| # | Finding | Lens(es) | Recommended action | Impact | Verdict | Conf. |
|---|---|---|---|---|---|---|
| 1 | … | resumability, failure-modes | … | High (2) | consider | 0.xx |

  `Verdict` is `consider`/`skip` for triaged rows, `—` for the `c ≥ 0.80` keep band. `Conf.` is `adjusted_confidence` where triage ran, else `c`.
- **Order** the walk set by confidence descending.
- **Dependency override:** if acting on one finding invalidates a later one, walk it first.
- **Dropped (`c < 0.70`):** one line each — finding · lens(es) · `c`.

### Step 4 — Walk findings one at a time

For each walk finding (keep band or triage `consider`, confidence descending; then parked findings if the user asks):
- **Present:** the finding, the lens(es) that raised it, the recommended action, the impact and confidence, and — where triage ran — its verdict and reason; quote the artifact span when the finding is location-specific.
- **Decide:** `AskUserQuestion` — apply / defer / drop. Drop later findings an applied decision invalidates, with a one-line reason.
- **On pushback:** spawn `second-opinion` on the contested action.
