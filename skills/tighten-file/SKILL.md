---
name: tighten-file
description: "File-level tightening pass on an instruction file (CLAUDE.md, skill, agent prompt, style guide) using `tighten-instruction` as the lens. TRIGGER when: user says 'tighten/simplify this file/skill/CLAUDE.md', 'cut this down', 'titan instruction on this file'; user points at a verbose instruction file and wants it leaner."
---

# Tighten File

Apply `tighten-instruction` at three levels: whole file, section, instruction.

## Steps

### Step 0 — Load

Invoke the `tighten-instruction` skill via the Skill tool. This file-level workflow owns the apply gate.

### Step 1 — Pin meaning

State the file's purpose in one line. List every distinct instruction or fact that must survive, including exact tokens, anchors, output contracts, and load-bearing rationale.

### Step 2 — Find and score edits

Apply the loaded lens at whole-file, section, and instruction level. For each independent edit, record:

- the current text;
- the proposed text, or `cut entirely`;
- the level: whole-file, section, or instruction;
- confidence `0.00–1.00` that the edit improves clarity without changing meaning.

Keep load-bearing rationale. When a reason is the non-derivable fact, shape it as `behaviour — constraint`; do not cut it as explanation.

### Step 3 — Gate and apply

Show the plan, then:

- apply every edit at `c ≥ 0.75`;
- hold lower-confidence proposals and leave their text unchanged;
- apply whole-file and section edits before instruction edits;
- drop any later proposal an applied edit dissolves.

```
**Tightening plan — <file>:**
- [0.92] section: <current> → <proposed>
- [0.61] instruction: <current> → <proposed> · held (< 0.75)
```

Write `Nothing to tighten — already clear.` when no edit qualifies.

### Step 4 — Prove and report

Re-read the changed file cold. Confirm:

- every Step 1 invariant survived;
- every exact token and anchor remains valid;
- every cross-reference still resolves;
- no rationale lost its constraint.

Revert or fix any edit that fails this proof.

Report applied edits, held proposals, dissolved proposals, and net clauses, lines, and words removed.
