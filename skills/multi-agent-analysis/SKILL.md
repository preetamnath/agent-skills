---
name: multi-agent-analysis
description: "Divergent analysis: parallel subagents each apply a distinct lens to an in-progress artifact, surfacing scored findings. TRIGGER when: user says 'use subagents on different lenses/angles/dimensions', 'multi-agent analysis', 'analyze from multiple angles'; user has an artifact and an open mandate to find what could improve. SKIP when: user brings a fixed list of focused questions on a near-final artifact, or one concrete proposal to rate."
---

# Multi-Agent Analysis

Many parallel lenses on one in-progress artifact to surface what could improve — then synthesize, scored, and walk one at a time.

## Steps

### Step 1 — Frame and derive lenses

- **Derive lenses** from the artifact's risk surface — orthogonal angles that together cover what could be wrong or improvable (for a skill: resumability, failure-modes, coherence-with-siblings, UX; for a spec: scope, architecture, edge cases). One lens per subagent; merge near-duplicates — overlap re-raises one finding and wastes the fan-out.
- **Count:** default 3–5 lenses; scale up only for a broad audit. If the user named the exact lenses, honor them and skip the checkpoint; if partial, honor those and fill any gap.
- **Checkpoint:** print the lens list (one line each) and confirm via `AskUserQuestion` ("Run these" / "Adjust").

### Step 2 — Dispatch

- **Readers:** R0 (you, concurrent) takes the integrative lens; R1…RN are parallel `general-purpose` subagents, one focused lens each.
- **Prompt (per lens):** artifact path(s), the lens and what it must scrutinize, and the return contract.
- **Return contract:** `finding` · `recommended action` · `reasoning (pro/con)` — whichever are relevant — plus two scores, always: `impact` (0.25 minimal · 0.5 low · 1 medium · 2 high · 3 massive) and `confidence` (0.00–1.00).

### Step 3 — Synthesize

- **Dedup across lenses:** the same finding raised by two lenses is one row — keep the max confidence.
- **Table:**

| # | Finding | Lens(es) | Recommended action | Impact | Conf. |
|---|---|---|---|---|---|
| 1 | … | resumability, failure-modes | … | 2 | 0.xx |

- **Order** by confidence descending.
- **Surface ≥ 0.75:** mark which findings cross the bar.
- **Sub-threshold:** keep findings under 0.75 in the table, marked parked — name them to the user, but don't walk unless asked.
- **Dependency override:** if acting on one finding invalidates a later one, walk it first.

### Step 4 — Walk findings one at a time

For each finding (≥ 0.75 first, then the rest the user wants):
- **Present:** the finding, the lens(es) that raised it, the recommended action, the impact and confidence — quote the artifact span when the finding is location-specific.
- **Decide:** `AskUserQuestion` — apply / defer / drop. Drop later findings an applied decision invalidates, with a one-line reason.
- **On pushback:** spawn `second-opinion` on the contested action.
