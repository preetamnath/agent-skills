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

### Step 2 — Synthesize and confirm

- **Sweep:** for any finding where max < 0.80 AND any reviewer < 0.70, run `second-opinion`; update scores.
- **Filter:** keep findings where any reviewer scored ≥ 0.75; rank by max.
- **Order:** whole-file → section → instruction, then max desc.
- **Table:**

| # | Level | Finding | R0 | R1 | R2 | Max | Crossed |

- **Checkpoint:** use `AskUserQuestion` to confirm the list before walking.

### Step 3 — Walk findings one at a time

**Walk order:** whole-file → section (structural pass), then re-sort remaining instruction findings by max desc and walk.

**Queue rule:** drop any queued finding dissolved by an approved edit, with a one-line reason.

**For each finding:**
- **Present:** quote current text, name each line's purpose (per `tighten-instruction` step 2), propose tightened version, then show the R0/R1/R2 split.
- **Decide:** Use `AskUserQuestion` with options: apply / alternative / keep. On approval, Edit.
    - **On pushback:** run `second-opinion` anchored on the finding.

### Step 4 — Summary

- **Applied** — what tightened.
- **Skipped** — one-line reason each.
- **Net compressed** — clauses, lines, words.
