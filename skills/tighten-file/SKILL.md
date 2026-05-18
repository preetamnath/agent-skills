---
name: tighten-file
description: "File-level tightening pass on an instruction file (CLAUDE.md, skill, agent prompt, style guide) using `tighten-instruction` as the lens. TRIGGER when: user says 'tighten/simplify this file/skill/CLAUDE.md', 'cut this down'; user points at a verbose instruction file and wants it leaner."
---

# Tighten File

Apply `tighten-instruction` at three levels: whole file, section, instruction.

## Steps

### Step 1 — Dispatch

- **Reviewers:** R0 (you, concurrent) + R1, R2 (two `general-purpose` subagents in parallel).
- **Prompt (identical for all three):** file path + `tighten-instruction` as the lens.
- **Output schema per finding:** numbered; quoted current text; proposed text (or "cut entirely"); level tag (whole-file / section / instruction); confidence 0.00–1.00.

### Step 2 — Synthesize and confirm

- **Filter:** include a finding when any one of R0/R1/R2 scored ≥ 0.75. Take the max.
- **Order:** whole-file → section → instruction, then max desc.
- **Table:**

      | # | Finding | R0 | R1 | R2 | Max | Level |

- **Checkpoint:** use `AskUserQuestion` to confirm the list before walking.

### Step 3 — Walk one at a time

For each finding:
1. Quote current text.
2. Name each line's purpose using `tighten-instruction`'s rules (restated goal / hedge / explain-why → cut; positive form implies negative → collapse).
3. Propose the tightened version.
4. Show the R0 / R1 / R2 split for this finding.
5. Use `AskUserQuestion` with options "apply / alternative / keep". On approval, Edit.
6. If a structural edit dissolves later findings, skip them with a one-line reason.
7. If the user challenges an edit, invoke the `second-opinion` skill with the finding as anchor.
