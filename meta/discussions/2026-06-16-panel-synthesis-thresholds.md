# Panel Synthesis Thresholds — decision record

Started 2026-06-16. Goal: one confidence-threshold logic across the reviewer-panel skills, replacing the drifted per-skill numbers. **Not yet shipped — design locked, edits pending.**

## Problem

The `0.75` "crosses the bar" threshold and its sweep/drop companions are duplicated and drifted across 7 lines:

| Skill | Current logic |
|---|---|
| `validate-answer` | sweep `max<0.80 AND any<0.70`; surface `any≥0.75`; drop `max<0.60` |
| `tighten-file` | sweep `max<0.80 AND any<0.70`; surface `any≥0.75`; no drop |
| `refine-file` | sweep `max<0.80 AND any<0.70`; surface `any≥0.75`; no drop |
| `find-gaps` | surface `max≥0.75`; park `<0.75`; no sweep (different lenses) |
| `durable-docs-update` | walk `≥0.70`; rescue band `[0.60,0.70)`; drop `<0.60` (single score) |
| `~/.claude/CLAUDE.md` (global) | "surface findings where any reviewer scored ≥ 0.75" |

## Rejected proposal

Three rules: (1) all reviewers ≥0.80 → no sweep; (2) ≥1 ≥0.80 AND any <0.80 → sweep; (3) max<0.70 → drop.

Two fatal flaws (confirmed by 3 parallel subagents):
- **Dead zone** — `max ∈ [0.70, 0.80)` with no reviewer ≥0.80 fires no rule (e.g. `0.78/0.72/0.71`, `0.78/0.50/0.45`).
- **Inverted sweep** — tying sweep to the 0.80 line misses real splits (`0.79/0.72/0.71`) and wastes second-opinions on near-consensus (`0.95/0.82/0.78`). Sweep should fire on *disagreement*, not on a score line.

## Locked design — two orthogonal axes

```
AXIS 1 — Band by max confidence   (all five skills)
   max < 0.60          → DROP
   0.60 ≤ max < 0.70   → PARK   (show in table, walk only if asked)
   max ≥ 0.70          → WALK

AXIS 2 — Sweep modifier            (identical-reviewer panels only)
   will surface AND reviewers split (any reviewer < 0.70)
                       → second-opinion BEFORE presenting
```

Why it works:
- **Total** — every score vector lands in exactly one band; no dead zone.
- **Sweep tied to disagreement**, its actual purpose — not to the 0.80 line. The 0.80 ceiling is dropped on purpose (it suppressed sweeps on `0.95/0.65/0.60`, the exact case worth a second look).
- **Two thresholds** (0.70, 0.60) replace four (0.80/0.75/0.70/0.60); honors the "use 0.70 as the bar" intent.
- **Keeps the PARK tier** that `find-gaps` and `validate-answer` rely on (lost under the rejected proposal).
- **Band numbers unify across all 5.** Only the sweep *mechanism* stays per-family: multi-reviewer dissent (panels) / single-score rescue band (`durable-docs-update`, already does this) / none (`find-gaps`, different lenses).

## Locked design — extraction

Extract the shared core into **`references/panel-synthesis.md`**, cited by consumers (like the existing schema refs). Rejected: a `tighten-instruction`-style lens — wrong layer (a lens is a content judgment a reviewer applies; this is post-return orchestration). Rejected: leave inline — already drifting.

- Extract **only** the narrow core: band defs (Axis 1) + sweep trigger (Axis 2). Leave per-skill table columns, ordering (whole-file→section vs CUT→MOVE→SHAPE), and walk rules inline — they genuinely differ.
- Doc states it covers **identical-reviewer panels**; band thresholds shared, sweep noted as panel-only.
- Inherits CLAUDE.md's "sync all consumers" rule + `validate-skills.sh`.

## Update (2026-06-16) — validate-answer landed as 2-tier + triage

`validate-answer` shipped a **2-tier** band (walk ≥0.70 / drop <0.70 — **no PARK**), a deliberate divergence from the general 3-band Axis 1. Rationale: identical-reviewer convergence makes all-low (max <0.70) safe to drop outright; the PARK tier stays only where promotion matters (`find-gaps`, single-lens self-reports).

The Axis-2 sweep is now the **`triage` skill** (not bare `second-opinion`): on a split (≥1 reviewer ≥0.70 AND ≥1 <0.70) it fans out one independent checker per question → `keep`/`demote`/`drop` verdict. `second-opinion` remains only as the on-pushback escape hatch during the walk.

Open: whether `tighten-file` / `refine-file` (the other identical-reviewer panels) also move from `second-opinion` sweep to `triage`, and whether they keep PARK. Decide when they're touched — see Pending edits.

## Sequencing

Fix the band logic first, then extract — don't enshrine the dead zone in a doc three skills cite. Q1 (logic) and Q2 (extraction) are coupled.

## Pending edits (not yet applied)

- ~~Draft `references/panel-synthesis.md`~~ — **dropped 2026-06-18**: `triage` is the shared home; no thresholds doc needed.
- ~~Rewrite `validate-answer`~~ — done: 2-tier band + `triage` sweep, redundant `no reviewer ≥ 0.75` clause dropped.
- ~~Rewrite `tighten-file`~~ — **done 2026-06-18**: band+triage (mirrors validate-answer), `Max`/`Crossed`→`Triage` column, `Dropped` summary line; on-pushback `second-opinion` kept; no PARK (identical-reviewer convergence). Self-tightened (nothing crossed the bar) + holistic review passed. Also fixed the stale Orchestrator citation for tighten-file in `WRITING-GUIDE.md`.
- ~~Rewrite `refine-file`~~ — **done 2026-06-18**: band+triage for CUT+SHAPE; MOVE skips triage (band-only; corrected target via the on-pushback `second-opinion`) per option **(b)+**; CUT names `vet-fact` in the triage claim. Self-tightened (nothing crossed the bar) + holistic review passed.
- ~~Adopt `triage` in `find-gaps` (where `promote` + PARK fire) and align its surface bar to 0.70~~ — **done 2026-06-18** (REPLACE: verdicts route, bar 0.70 is triage input + walk sort; details in `2026-06-16-verify-step-and-bar.md`). Align `durable-docs-update` to the shared band names — **done 2026-06-18**: bands now `≥0.80` walk / `[0.70,0.80)` triage / `<0.70` drop (mirrors find-gaps); rescue-band `second-opinion` → `triage` (`consider` present, `skip` drop); MOVE candidates + discovery/`D-NN` seeds skip triage, present directly. Floor raised 0.60→0.70 — the old promote-from-below-the-bar rescue path dropped, per user.
- ~~Update `~/.claude/CLAUDE.md` global rule to 0.70~~ — **dropped 2026-06-18** (per user).

## Update (2026-06-18) — triage is now consider/skip + bar-free

The `triage` sweep referenced above shipped, then simplified: 4 verdicts → **`consider` / `skip`**, and the bar left triage entirely (callers own thresholds; `promote` removed). Final per-skill bands:
- **validate-answer:** all 3 ≥0.80 walk · (≥1 ≥0.80 OR ≥2 ≥0.70) triage · else drop.
- **find-gaps:** ≥0.80 walk · [0.70,0.80) triage · <0.70 drop; `skip`→park, sub-0.70 listed under the table.

Source of truth: the SKILL files.
