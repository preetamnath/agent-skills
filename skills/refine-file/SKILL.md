---
name: refine-file
description: "Audit one instruction file through three durable-instruction lenses — vet-fact (is each fact worth keeping?), place-fact (is it in the right home?), tighten-instruction (does the line read tight?). TRIGGER when: user says 'refine/audit this file', 'prune and tighten this doc', 'what here is worth keeping'; a skill file or durable doc (CLAUDE.md, a rule, ARCHITECTURE.md) needs a keep/place/shape pass. SKIP when: shape-only tightening with no worth/place question (tighten-file)."
---

# Refine File

Primitive: **WORTH + PLACE + SHAPE** — composes the three durable-instruction lenses over one file, in any real subset (S, W+S, W+P+S).

## Lenses and composition

The combiner owns ordering; the lenses never chain to each other. Apply the selected lenses **per fact, in WORTH → PLACE → SHAPE order**. Each lens is loaded as a skill in Step 0; this table maps lens → primitive → verdict for ordering, and is not a substitute for the loaded criteria:

| Lens | Primitive | Verdict |
|---|---|---|
| `vet-fact` | WORTH | keep (+ category), or **cut** |
| `place-fact` | PLACE | stay, or **move it** (on approval) |
| `tighten-instruction` | SHAPE | keep, or **tighten** the line |

Composition glue (written once, here):

- **A WORTH cut dissolves its PLACE/SHAPE work** — don't place or shape a fact you're deleting.
- **MOVE is the only finding that touches a second file.** `place-fact` routes a kept fact to a different home; on approval, open that target file, shape the fact for it, add it there, and remove it here — skip the add if the target already carries the fact (then this is just a CUT here). To defer instead of applying now, flag it for a later `durable-docs-update` batch.
- **The named file is the audit's scope, not an edit boundary** — a MOVE is expected to write outside it.
- **Rationale = constraint (cut-the-why exemption).** A fact `vet-fact` keeps as `rationale` carries its reason *as* the fact — `tighten-instruction` shapes it to "behaviour — constraint" (its Step 4), and must not strip the reason as explain-why (its Step 2). Same for any kept fact whose non-derivable part is a consequence (a gotcha's failure mode).

## Steps

### Step 0 — Load the lenses

Call the Skill tool to load `vet-fact`, `place-fact`, and `tighten-instruction`. Relay each selected lens's criteria verbatim into every reviewer brief in Step 2 — a parent-loaded skill doesn't reach a subagent's separate context.

### Step 1 — Resolve operand + lens subset

- **Classify the operand** by reading the file: a **skill/agent prompt** (internal instructions; no tier-homes → PLACE N/A) or a **durable doc** (`CLAUDE.md` / `.claude/rules/*.md` / `ARCHITECTURE.md`; tier-homed → PLACE applies).
- **Default the subset** from the user's phrasing: "tighten/cut down" → **S**; "prune / worth keeping / audit" → **W+S**; "re-home / does this belong / full audit" on a durable doc → **W+P+S**.
- **Confirm.** If the phrasing pins the subset, proceed and state it. If ambiguous, `AskUserQuestion` with the fixed menu — `{S, W+S}` for a skill/agent prompt, `{S, W+S, W+P+S}` for a durable doc, recommendation first. Never offer a free-form combo.

### Step 2 — Dispatch reviewers

- **Reviewers:** R0 (you) + R1, R2 (Sonnet `general-purpose` subagents, parallel). Brief each with: the file path, the operand type, the selected subset, the Step 0 loaded lens criteria for the selected subset (relayed verbatim), and the composition glue above.
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
- **Triage the collected CUT and SHAPE findings:** invoke the `triage` skill via the Skill tool — each finding: id = finding #, claim = the finding text (for a CUT, name the lens: `CUT — fails vet-fact (WORTH): …`); plus the file path. Then route the verdicts:
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
  - On pushback: invoke the `second-opinion` skill via the Skill tool, anchored on the finding.

### Step 5 — Summary and deferred moves

- **Applied** — N cut, N shaped, N moved; net lines and words removed.
- **Deferred moves** (only those you flagged for later) — table of `fact | this file → target home | category`; to batch them, invoke the `durable-docs-update` skill via the Skill tool, or move them yourself.
- **Skipped** — walked but kept as-is, or dissolved by an approved edit; one-line reason each.
- **Dropped** (Step 3 band, or triage `skip`) — finding + score/reason.

## Rules

- **Never auto-apply.** Confirm the subset, then each finding — even at confidence 1.0.
