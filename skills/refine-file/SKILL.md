---
name: refine-file
description: "Audit one instruction file for worth, placement, and clarity using vet-fact, place-fact, and tighten-instruction. TRIGGER when: user says 'refine/audit this file', 'prune and tighten this doc', 'what here is worth keeping'; a skill, CLAUDE.md, path rule, or maintained task document needs a keep/place/shape pass. SKIP when: shape-only tightening with no worth/place question (tighten-file)."
---

# Refine File

Primitive: **WORTH + PLACE + SHAPE** — composes the three durable-instruction lenses over one file in the requested subset: S, W+S, or W+P+S.

## Lenses and composition

The combiner owns ordering; the lenses never chain to each other. Apply the selected lenses **per fact, in WORTH → PLACE → SHAPE order**. Each lens is loaded as a skill in Step 0; this table maps lens → primitive → verdict for ordering, and is not a substitute for the loaded criteria:

| Lens | Primitive | Verdict |
|---|---|---|
| `vet-fact` | WORTH | keep (+ category), or **cut** |
| `place-fact` | PLACE | stay, or **move it** |
| `tighten-instruction` | SHAPE | keep, or **tighten** the line |

Composition rules:

- **A WORTH cut dissolves its PLACE/SHAPE work** — don't place or shape a fact you're deleting.
- **MOVE is the only finding that edits a second file.** Open the target before scoring. Shape and add the fact there, then remove it here. If the target already carries the fact, skip the add and classify the source removal as CUT.
- **The named file is the audit's scope, not an edit boundary** — a MOVE is expected to write outside it.
- **Rationale carries the constraint.** When `vet-fact` keeps a rationale, its reason is the non-derivable fact. Shape it as `behaviour — constraint`; do not cut it as explanation. Treat a gotcha's non-derivable consequence the same way.

## Steps

### Step 0 — Load the lenses

Invoke the Skill tool to load `vet-fact`, `place-fact`, and `tighten-instruction`. This file-level workflow owns the apply gate.

### Step 1 — Resolve operand + lens subset

- **Classify the operand** by reading the file: a **skill/agent prompt** (internal instructions; PLACE N/A) or a **durable document** (`CLAUDE.md`, path rule, or maintained task document; PLACE applies).
- **Default the subset** from the user's phrasing: "tighten/cut down" → **S**; "prune / worth keeping / audit" → **W+S**; "re-home / does this belong / full audit" on a durable doc → **W+P+S**.
- **Resolve ambiguity.** If the phrasing pins the subset, proceed and state it. Otherwise use the smallest subset that fully answers the request; ask only when two subsets would materially change the result.

### Step 2 — Find and score edits

- Apply the selected lenses per fact in WORTH → PLACE → SHAPE order. Emit independent findings with confidence `0.00–1.00`:
  - **CUT** — fails `vet-fact`: the line + one-line reason.
  - **MOVE** (durable doc + W+P+S only) — kept, but `place-fact` routes it to another home: fact + WORTH category + target home.
  - **SHAPE** — kept and in-place: current → tightened line + level (whole-file / section / line).
  - A worth-keeping, well-placed, well-shaped line yields no finding.
- Score confidence that the fact assessment, action, and resulting text are correct. For MOVE, the score must also cover the target home after reading it.

### Step 3 — Gate and apply

Show the ordered plan, then:

- apply every finding at `c ≥ 0.75`;
- hold lower-confidence findings and leave their text unchanged;
- apply CUT → MOVE → SHAPE;
- within SHAPE, apply whole-file → section → line;
- drop any queued finding an applied edit dissolves.

```
**Refinement plan — <file>:**
- [0.93] CUT: <current> — <reason>
- [0.86] MOVE: <fact> → <target home>
- [0.78] SHAPE: <current> → <proposed>
- [0.64] CUT: <current> — <reason> · held (< 0.75)
```

Write `Nothing to refine — every fact is worth keeping, well placed, and clear.` when no edit qualifies.

### Step 4 — Prove the result

Re-read the named file and every MOVE target cold. Confirm:

- every kept fact and load-bearing rationale survived;
- every moved fact has one durable owner;
- no target gained a duplicate;
- every edit stayed within the selected lens subset.

Revert or fix any edit that fails this proof.

### Step 5 — Report

- **Applied** — N cut, N moved, N shaped; net lines and words removed.
- **Held** — each below-threshold finding with its score and reason.
- **Dissolved** — each queued finding removed by an earlier edit.
