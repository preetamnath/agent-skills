---
name: refine-file
description: "Audit one current-guidance instruction file for worth, placement, and clarity. TRIGGER when: user says 'refine/audit this file', 'prune and tighten this doc', or 'what here is worth keeping'; a skill, agent prompt, AGENTS.md, Claude path rule, maintained current document, or workflow needs one pass. SKIP when: shape-only tightening with no worth/place question (tighten-file)."
---

# Refine File

Apply the requested subset of WORTH → PLACE → SHAPE to one file: S, W+S, or W+P+S.

## Steps

### Step 0 — Resolve the file and lens subset

Read the named file. This workflow applies WORTH and PLACE only to current guidance. An active-state document or dated investigation can receive S here; use `place-fact` and its owning workflow for separate placement and lifecycle decisions.

Choose the smallest subset that answers the request:

- **S** — the user explicitly invoked this skill for shape-only work.
- **W+S** — the user asks what is worth keeping or requests pruning without a placement audit.
- **W+P+S** — the user asks to refine, audit, re-home, or judge whether material belongs in the file.

State the subset and proceed when the request selects it. Ask only when two subsets would materially change the result.

The named file is the audit scope, not the edit boundary; MOVE may edit its canonical target and required delivery views.

### Step 1 — Load the selected lenses

Invoke only the selected skills via the Skill tool:

| Subset | Skills |
|---|---|
| S | `tighten-instruction`, `structure-prose` |
| W+S | `vet-fact`, `tighten-instruction`, `structure-prose` |
| W+P+S | `vet-fact`, `place-fact`, `tighten-instruction`, `structure-prose` |

This file-level workflow owns the apply gate. The lenses never invoke each other.

### Step 2 — Find and score independent edits

Apply the selected lenses per fact in WORTH → PLACE → SHAPE order:

- **CUT** — the fact fails `vet-fact`; record the current text and a one-line reason.
- **MOVE** — `place-fact` keeps the fact but selects another owner or delivery boundary; record the fact, WORTH category, and target.
- **SHAPE** — the kept, in-place fact or block needs tightening or structure; record current → proposed and the level: whole file, section/block, or line.

A WORTH cut dissolves PLACE and SHAPE work for the same fact. Preserve rationale when its reason is the non-derivable constraint; shape it as `behaviour — constraint`.

For each MOVE:

1. Record `place-fact`'s full placement contract in the analysis; do not paste it into the repository.
2. Inspect the existing target, or confirm the contract for a new artifact, before scoring.
3. Shape the fact for the canonical target, establish any required derived or guarded delivery view, then remove it from the source.
4. If the target already carries the fact, skip the add and classify the source removal as CUT.

Score confidence `0.00–1.00` that the fact assessment, action, and resulting text are correct. A MOVE score also covers the target and delivery contract.

### Step 3 — Gate and apply

Show the ordered plan, then apply every finding at `c ≥ 0.75` and hold lower-confidence findings without changing their text. Apply CUT → MOVE → SHAPE; within SHAPE, apply whole-file → section/block → line. Drop any queued finding that an earlier edit dissolves.

```text
**Refinement plan — <file>:**
- [0.93] CUT: <current> — <reason>
- [0.86] MOVE: <fact> → <canonical target>
- [0.78] SHAPE: <current> → <proposed>
- [0.64] CUT: <current> — <reason> · held (< 0.75)
```

Write `Nothing to refine — every fact is worth keeping, well placed, and clear.` when there are no findings.

### Step 4 — Prove the result cold

Re-read the named file and every MOVE target in full. Confirm every kept fact and load-bearing rationale survived, every edit stayed inside the selected subset, and the result has no contradiction, duplicate ownership, mixed delivery scope, broken route, or unnecessary eager loading. Verify that each moved fact has one canonical owner and that every required delivery view derives from it or has an automatic equality guard.

Revert or fix any edit that fails this proof.

### Step 5 — Report

```text
**Refinement result — <file>:**
- Applied: [N cut, N moved, N shaped | none]
- Held: [finding, score, and reason, one per line | none]
- Dissolved: [finding removed by an earlier edit, one per line | none]
- Delta: [net lines and words removed]
```
