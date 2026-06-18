---
name: tighten-file
description: "File-level tightening pass on an instruction file (CLAUDE.md, skill, agent prompt, style guide) using `tighten-instruction` as the lens. TRIGGER when: user says 'tighten/simplify this file/skill/CLAUDE.md', 'cut this down'; user points at a verbose instruction file and wants it leaner."
---

# Tighten File

Apply `tighten-instruction` at three levels: whole file, section, instruction.

## Steps

### Step 1 — Dispatch

- **Reviewers:** R0 (you) + R1, R2 (`general-purpose` subagents, parallel) with the file path and `tighten-instruction` as the lens.
- **Output per finding:** numbered; quoted current text; proposed text (or "cut entirely"); level (whole-file / section / instruction); confidence 0.00–1.00.

### Step 2 — Triage, synthesize, and confirm

- **Band each finding by its three reviewer scores** — the bands are a cost lever, only the contested middle gets a checker:
    <!-- source: references/confidence-bands.md (Mode V) -->
    - **keep** (walk, no triage) — all three ≥ 0.80. Unanimous agreement across identical reviewers; re-checking spends a checker for nothing.
    - **triage** — ≥1 reviewer ≥ 0.80 **OR** ≥2 reviewers ≥ 0.70. Real support, not consensus.
    - **drop** — ≤1 reviewer ≥ 0.70 and none ≥ 0.80. Too thin to walk or check.
- **Run `triage` once** on the collected findings — each finding: id = finding #, claim = the proposed tightening; plus the file path. Then route the verdicts:
    - **`consider`** → walk · **`skip`** → drop (list in Step 4).
- **Order:** whole-file → section → instruction, then confidence descending — post-triage `adjusted_confidence` where triage ran, else max.
- **Table:**

| # | Level | Finding | R0 | R1 | R2 | Triage |

  `Triage` = `consider` + its `adjusted_confidence` where triage ran (e.g. `consider 0.78`), else `—` for the all-three-≥0.80 keep band.

- **Checkpoint:** use `AskUserQuestion` to confirm the list before walking.

### Step 3 — Walk findings one at a time

**Walk order:** whole-file → section (structural pass), then re-sort remaining instruction findings by confidence desc and walk.

**Queue rule:** drop any queued finding dissolved by an approved edit, with a one-line reason.

**For each finding:**
- **Present:** quote current text, name each line's purpose (per `tighten-instruction` Step 2), propose tightened version, then show the R0/R1/R2 split (plus the triage verdict and its reason, if triage ran).
- **Decide:** Use `AskUserQuestion` with options: apply / alternative / keep. On approval, Edit.
    - **On pushback:** run `second-opinion` anchored on the finding.

### Step 4 — Summary

- **Applied** — what tightened.
- **Skipped** — walked but kept as-is, or dissolved by an approved edit; one-line reason each.
- **Dropped** (Step 2 band, or triage `skip`) — finding + score/reason.
- **Net compressed** — clauses, lines, words.

## Rules

- **Never auto-apply.** Confirm each finding — even at confidence 1.0.
- **Keep load-bearing rationale.** When a line's reason IS its non-derivable content (a rationale, a gotcha's failure mode), shape it to "behaviour — constraint" (`tighten-instruction` Step 4); don't cut it as explain-why.
