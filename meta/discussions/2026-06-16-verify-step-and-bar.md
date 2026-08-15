# Verify Step + Walk Bar — validate-answer & find-gaps

**Date:** 2026-06-16
**Status:** Shipped. `triage` built and wired into both `validate-answer` and `find-gaps`.
**Scope:** Whether to add a finding-verification step to `validate-answer` and `find-gaps`, and how a repo-wide ≥0.70 bar interacts with it. (`best-answer` keeps its clean-room `judge`; not in scope.)

---

## Update (2026-06-18) — triage simplified to consider/skip + bar-free

Everything below describes the **superseded** 4-verdict (`drop`/`demote`/`keep`/`promote`) + bar model. What actually shipped:

- **`triage` returns 2 verdicts: `consider` / `skip`** (+ `adjusted_confidence` + one-line `reason`). `keep`/`promote` were a fake split — both meant "walk," and the position-vs-bar that distinguished them is already in `adjusted_confidence`. `drop`/`demote` collapsed into `skip`.
- **`triage` is bar-free and score-blind.** Input = findings (id + claim) + artifact path(s); no prior score (clean-room), no bar. The bar was caller policy that didn't belong in a verification primitive — once it left, `promote` vanished on its own.
- **Callers own all banding** (the cost lever):
    - **validate-answer:** all 3 ≥0.80 → walk · (≥1 ≥0.80 OR ≥2 ≥0.70) → triage · else → drop. `consider`→walk, `skip`→drop. Solo observations walk at ≥0.80.
    - **find-gaps:** `c ≥0.80` → walk · `[0.70,0.80)` → triage · `c <0.70` → drop. `consider`→walk, `skip`→park (shown in table), `c<0.70` listed under the table. No `promote` — floor-0.70 leaves nothing below the bar to rescue.
- **Source of truth: the SKILL files, not this doc.**

---

## The three skills (settled, shipped)

| Skill | Workers (Knob A) | Output (Knob B) | Confidence means |
|---|---|---|---|
| `best-answer` | diverse mandates | one synthesized answer | per-panelist self-report; clean-room `judge` maps disagreement |
| `validate-answer` | **identical** reviewers | per-decision trust verdict | **cross-reviewer agreement** |
| `find-gaps` | **diverse** lenses | scored findings list | **one lens's self-report** (uncalibrated) |

No `judge` for validate-answer / find-gaps — confirmed.

---

## Proposed verify step (before synthesize)

A verifier of findings, two outcomes:
1. **≥0.75 findings** — confirm real & correct → keep or demote/drop.
2. **0.50–0.75 findings** — triage materiality → promote (to walk) or leave parked.

**Reframe agreed:** correctness and materiality are two **axes**, not two **bands**. One verifier pass over findings ≥0.50, checking *real?* + *material?* → four verdicts: **drop / demote / keep / promote**. Re-score, then apply the walk bar to post-verify scores. Band still useful as a *cost* lever (deep check on ≥0.75, lighter triage on the tail). Same protocol/agent/contract in both skills; only the entry band differs.

---

## Key principle: the bar can't replace the verify step

- **Bar** = static sorting line (where the cutoff is).
- **Verify** = rescoring (moves findings across the line).
- The human walks **only what's above the bar** → parked findings are invisible. Only a rescoring pass can **promote** a real-but-parked finding. Lowering the bar 0.75→0.70 doesn't rescue a real 0.60 finding.

**Promotion is the irreplaceable job**, and it splits by Knob A:

| | Parked-but-real finding likely? | Drop the sweep? |
|---|---|---|
| `validate-answer` (agreement) | unlikely — identical reviewers converge on real ones | **Yes — safe** |
| `find-gaps` (self-report) | likely — a cautious lens under-scores a real gap | **No — keep verify** |

---

## Recommendation (mine)

- Adopt **≥0.70 bar repo-wide** — independent, fine on its own. (0.75)
- `validate-answer`: **drop the upfront Step-2 Sweep** — bar + convergence + human walk suffice. (0.72)
- `find-gaps`: **keep a lightweight verify-for-promotion pass** — bar can't substitute. (0.80)
- Keep **on-pushback `second-opinion`** in both (Step 3/4) — fires only on disagreement, near-zero standing cost. Don't conflate with the upfront sweep. (0.80)

Agent: existing `verifier` is code-centric with no promotion path → likely a **new** agent, not a reuse. (open)

---

## Resolved architecture

**Two layers** — a reusable skill that fans out, and the workers it dispatches:

- **`triage` skill** — owns the count logic: take the findings that need checking, dispatch general-purpose checkers in parallel, **1–3 findings each sized by complexity** (no `triager` agent — precise prompt lives in the skill), collect verdicts, return them. Reused by both `validate-answer` and `find-gaps`.
- **Checker** (per finding) — clean room, reads the artifact fresh, judges **real?** + **material?** → one of `drop` / `demote` / `keep` / `promote` + adjusted confidence + reason.

**`validate-answer` logic (per question, by its 3 reviewer scores):**

| Reviewers ≥ 0.70 | Outcome |
|---|---|
| all three | walk, no triage |
| split (≥1 ≥0.70 AND ≥1 <0.70) | `triage` → `keep`/`demote` walk · `drop` removes |
| none | drop, list in summary |

- **No PARK tier in validate-answer** — convergence across identical reviewers makes all-low (max < 0.70) safe to drop outright. `find-gaps` keeps PARK (promotion lives there).
- **PROMOTE is dormant in validate-answer** — only above-bar splits reach triage, so nothing sits below the bar to lift. It runs in `keep`/`demote`/`drop` mode. PROMOTE fires in `find-gaps`.
- **On-pushback `second-opinion`** stays in the walk (Step 3/4) — fires only on user disagreement, near-zero standing cost.

## find-gaps adoption — precise plan (DONE 2026-06-18)

`find-gaps` is the consumer where `promote` and PARK both fire (diverse lenses → uncorroborated self-reported scores). Shipped edits to `skills/find-gaps/SKILL.md` (Steps 3–4):

1. ~~**Insert a triage step**~~ **Done** — Step 3 ("Synthesize and triage") runs `triage` once on the deduped findings: id, claim = finding text, current confidence = dedup confidence; plus artifact path(s) and walk bar 0.70. One pass so its 1–3 batching engages. No remap — find-gaps already speaks "findings."
2. ~~**Apply verdicts**~~ **Done** — route by verdict: `drop` removes (marked in table) · `keep`/`promote` walk · `demote` parks. `promote` is the prize — lifts a real but under-scored finding out of park into the walk.
3. ~~**Align the surface bar** 0.75 → 0.70~~ **Done.**
4. ~~**Keep PARK**~~ **Done** — `demote` is the park home; the old "sub-threshold parked" tier is gone in favor of verdict routing.
5. **Reconcile — RESOLVED: REPLACE.** Triage verdicts *replace* the band tiers in find-gaps: walk = `keep` ∪ `promote`, park = `demote`, drop = `drop`. The 0.70 bar is a triage **input** (keep-vs-promote) and the walk sort key — no second post-triage banding pass. Chosen over LAYER because under a consistent checker the two converge, and REPLACE has one routing mechanism with no `keep`@0.62-style contradiction.
6. ~~**Sync + verify**~~ **Done** — README find-gaps line updated (now names the `triage` verify step); `validate-skills.sh` passes (26 manifests); `tighten-file` run (no finding crossed 0.75; one PARK→park casing fix applied).
