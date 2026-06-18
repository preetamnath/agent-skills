---
name: refine-file
description: "Audit one instruction file by composing the durable-instruction lenses over it — vet-fact (WORTH: does each fact earn a line?), place-fact (PLACE: is it in the right home?), tighten-instruction (SHAPE: tighten the line). Pick the subset the file needs: shape-only, worth+shape, or worth+place+shape. A misplaced fact can be relocated to its right home on your approval, or deferred for a durable-docs-update batch. TRIGGER when: user wants a skill file or durable doc (CLAUDE.md, a rule, ARCHITECTURE.md) audited for what to keep, where it belongs, and how it reads; user says 'refine/audit this file', 'prune and tighten this doc', 'what here is worth keeping'. For shape-only tightening, tighten-file is the leaner sibling."
---

# Refine File

Primitive: **WORTH + PLACE + SHAPE** — composes the three durable-instruction lenses over one file, in any real subset (S, W+S, W+P+S).

## When to use

- One file you want audited: a skill/agent prompt, or a durable doc (`CLAUDE.md`, a `.claude/rules/*.md`, `ARCHITECTURE.md`).
- You want more than tightening: judge what to keep (WORTH) and whether it sits in the right home (PLACE), not just how it reads.

NOT for:
- **Pure tightening** — `tighten-file` (SHAPE only) is leaner.
- **A whole change-set after a task** — that's `durable-docs-update` (it scans the diff and adds new facts repo-wide). `refine-file` starts from the one file you name.

## Lenses and composition

The combiner owns ordering; the lenses never chain to each other. Apply the selected lenses **per fact, in WORTH → PLACE → SHAPE order**, referencing each by name (never paraphrased):

| Lens | Primitive | The check | Verdict |
|---|---|---|---|
| `vet-fact` | WORTH | does this fact deserve a line? | keep (+ category), or **cut** |
| `place-fact` | PLACE | is it in the right home? | stay, or **move it** (on approval) |
| `tighten-instruction` | SHAPE | does the line read cold? | keep, or **tighten** the line |

Composition glue (written once, here):

- **A WORTH cut dissolves its PLACE/SHAPE work** — don't place or shape a fact you're deleting.
- **A move is the one finding that reaches a second file.** If `place-fact` routes a kept fact to a *different* home, surface it as a MOVE. On your approval, refine-file executes it — open the target home, shape the fact for it, add it, remove it here (if the target already carries the fact, it's just a CUT here) — or you can defer it as a flag for a `durable-docs-update` batch. The single file you name is the *audit* scope, not a sandbox. Skill/agent prompts have no tier-homes — skip PLACE for them entirely.
- **Rationale = constraint (cut-the-why exemption).** A fact `vet-fact` keeps as `rationale` carries its reason *as* the fact — `tighten-instruction` shapes it to "behaviour — constraint" (its Step 4), and must not strip the reason as explain-why (its Step 2). Same for any kept fact whose non-derivable part is a consequence (a gotcha's failure mode).

## Steps

### Step 1 — Resolve operand + lens subset

- **Classify the operand** by reading the file: a **skill/agent prompt** (internal instructions; no tier-homes → PLACE N/A) or a **durable doc** (`CLAUDE.md` / `.claude/rules/*.md` / `ARCHITECTURE.md`; tier-homed → PLACE applies).
- **Default the subset** from the user's phrasing: "tighten/cut down" → **S**; "prune / worth keeping / audit" → **W+S**; "re-home / does this belong / full audit" on a durable doc → **W+P+S**.
- **Confirm.** If the phrasing pins the subset, proceed and state it. If ambiguous, `AskUserQuestion` with the fixed menu — `{S, W+S}` for a skill/agent prompt, `{S, W+S, W+P+S}` for a durable doc, recommendation first. Never offer a free-form combo.

### Step 2 — Dispatch reviewers

- **Reviewers:** R0 (you) + R1, R2 (`general-purpose` subagents, parallel). Brief each with: the file path, the operand type, the selected subset, the three lens skills by name, and the composition glue above.
- **Each reviewer**, per fact/line in scope, applies the selected lenses in order and emits findings with confidence 0.00–1.00:
  - **CUT** — fails `vet-fact`: the line + one-line reason.
  - **MOVE** (durable doc + W+P+S only) — kept, but `place-fact` routes it to another home: fact + WORTH category + target home.
  - **SHAPE** — kept and in-place: current → tightened line + level (whole-file / section / line).
  - A worth-keeping, well-placed, well-shaped line yields no finding.

### Step 3 — Triage, synthesize, and confirm

- **Band each finding by its three reviewer scores** — cost lever, only the contested middle gets a checker (MOVE findings excepted — see below):
    <!-- source: references/confidence-bands.md (Mode V) -->
    - **keep** (walk, no triage) — all three ≥ 0.80. Unanimous agreement across identical reviewers; re-checking spends a checker for nothing.
    - **triage** — ≥1 reviewer ≥ 0.80 **OR** ≥2 reviewers ≥ 0.70. Real support, not consensus.
    - **drop** — ≤1 reviewer ≥ 0.70 and none ≥ 0.80. Too thin to walk or check.
- **Run `triage` once** on the collected CUT and SHAPE findings — each finding: id = finding #, claim = the finding text (for a CUT, name the lens: `CUT — fails vet-fact (WORTH): …`); plus the file path. Then route the verdicts:
    - **`consider`** → walk · **`skip`** → drop (list in Step 5).
- **MOVE skips triage** — a MOVE walks if it lands in the keep or triage band, drops only in the drop band, and is never checked: `triage`'s `consider`/`skip` can't carry a corrected target home, so a doubted MOVE is checked by the on-pushback `second-opinion` in Step 4 instead.
- **Order (composition order):** CUT → MOVE → SHAPE; within SHAPE, whole-file → section → line, then confidence descending — post-triage `adjusted_confidence` where triage ran, else max.
- **Table:**

  | # | Action | Finding | R0 | R1 | R2 | Triage |

  Finding holds: `current — reason` (CUT), `current → target home` (MOVE), or `current → proposed` (SHAPE). `Triage` = `consider` + its `adjusted_confidence` where triage ran (e.g. `consider 0.78`), else `—` (MOVE, or the all-three-≥0.80 keep band).
- **Checkpoint:** `AskUserQuestion` to confirm the list before walking.

### Step 4 — Walk findings one at a time

**Walk order:** CUT → MOVE → SHAPE. Within SHAPE: whole-file → section (structural pass), then re-sort remaining line findings by confidence desc and walk.

**Queue rule:** any approved edit dissolves a queued finding it subsumes — drop it with a one-line reason. (E.g. a CUT dissolves a same-line MOVE/SHAPE; a MOVE dissolves a same-line SHAPE, since the fact is shaped in its new home.)

**For each finding:**
- **Present:** quote current text; for a kept fact name its WORTH category; for SHAPE name each line's purpose (per `tighten-instruction` Step 2); propose the cut, the move (naming the target home), or the tightened line; then show the R0/R1/R2 split (plus the triage verdict and its reason, if triage ran).
- **Decide:** `AskUserQuestion` — CUT/SHAPE: apply / alternative / keep; MOVE: move / flag for later / keep.
  - On apply: `Edit` — CUT deletes; SHAPE replaces; MOVE adds the target-shaped fact to the target home (after checking it isn't already carried) and removes it here. "Flag for later" records the move to the deferred list instead — no `Edit`.
  - On pushback: run `second-opinion` anchored on the finding.

### Step 5 — Summary and deferred moves

- **Applied** — N cut, N shaped, N moved; net lines and words removed.
- **Deferred moves** (only those you flagged for later) — table of `fact | this file → target home | category`; run `durable-docs-update` to batch them, or move them yourself.
- **Skipped** — walked but kept as-is, or dissolved by an approved edit; one-line reason each.
- **Dropped** (Step 3 band, or triage `skip`) — finding + score/reason.

## Rules

- **Never auto-apply.** Confirm the subset, then each finding — even at confidence 1.0.
