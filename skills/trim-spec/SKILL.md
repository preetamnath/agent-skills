---
name: trim-spec
description: "Trim a spec, ADR set, or design doc down to what a builder needs, without losing a fact. TRIGGER when: user says a spec is 'too long' or 'bloated'; user asks what to remove from it, or wants it cut to 'just what we need to build'."
---

# Trim Spec

A long spec is usually not verbose — it is duplicated. The same rule sits in a decision, in the outline, and in an AC, and the copies have drifted apart. The method is one column, `restated_at`: for every claim, where else is this stated?

### Input

- **Target** — a file path or a spec folder (`meta/specs/NNN-slug/`), trimmed in place.
- **Precondition** — a consistency audit has run on this target. If not, run one first (the `reviewer` agent, criteria: any two statements of one rule that disagree). De-duplicating an unaudited doc can delete the correct copy and keep the stale one.
- **Class** — PIPELINE when another skill greps this file, else STANDALONE. The class decides the shape answer in Step 2 and whether Step 4's anchor pass runs.

## Steps

### Step 1 — Inventory every claim, extract only

Fan out `general-purpose` agents partitioned by section (3 for ~700 lines). Each returns one row per normative claim:

```
claim | at | type | restated_at | conf
```

- `type` — MECHANISM (symbol, signature, constant, formula, state transition — what an implementer types) · CHOICE · WHY · EVIDENCE (measured or live-verified, with its source) · UI-COPY (exact string, style token) · HISTORY.
- `at` — the section heading or decision id the claim lives under.
- `restated_at` — where else in the file the claim is stated, VERBATIM or PARAPHRASE.
- Never cite a line number in either — the cut renumbers every line, so a line-keyed inventory goes stale while you are still using it.
- `conf` — 0.00–1.00 on the `restated_at` call.

Instruct them explicitly: extract only, no recommendations.

### Step 2 — Derive the cut inputs, then confirm the plan

- **Sole homes** — every claim whose `restated_at` is `unique`. Untouchable. Before collapsing any block, confirm each fact in it has a live copy outside it; that copy is the sole home, not the block.
- **Drifted pairs** — copies of one rule that disagree. Reconcile which one is true before choosing a survivor, or the cut silently picks a side.
- **Per-block survivors** — for each replaced decision, every fact stated nowhere else. Do not stop at the first.
- **Partially superseded decisions** — status still `locked`, one clause dead, the rest authoritative. Only the dead clause goes.

A PIPELINE target stays one file: moving a decision out carries its `Status: open` and `[NEEDS CLARIFICATION:` markers out of grep range, so `tech-design` and `write-plan` report a blocked spec as locked (Gate anchors, `skills/product-interview/SKILL.md`). No skill reads a second file.

A STANDALONE target may split builder material (MECHANISM · UI-COPY · live EVIDENCE) from maintainer material (CHOICE · WHY · HISTORY · disproved EVIDENCE).

Group the claims by `type` and total the lines of the sections holding each group — that is how small each shape still open to you could get.

Show the cost-ordered plan and those totals, then `AskUserQuestion`.

### Step 3 — Cut in cost order

Every deletion cites a `restated_at` or a survivor row.

1. **Scaffolding** — uniform status lines and empty `Supersedes:` / `Superseded-by:` fields. Replace with one convention note stating the exact field form a reopened decision re-adds, or the lock gate has nothing to grep.
2. **Superseded blocks → one table** — id, what it was, what replaced it, its survivors quoted. This is the one sanctioned exception to "the only edits to a superseded block are Status + Superseded-by" (canonical template, `skills/product-interview/SKILL.md`), and it holds only because the table quotes every survivor.
3. **Resolved open questions** carrying nothing unique.
4. **Duplicate mechanism** — one home per rule: the Structure Outline. Decisions state the choice and point at it.
5. **Merged views** — a file map, a per-file walk and a "files touched" list are three views of one thing.
6. **Wording**, last — invoke the `tighten-instruction` skill via the Skill tool. Never change a fact, and never a line break: rewrapping a long AC moves its `[tag]` to a second line and silently drops that AC downstream (Gate anchors rule 4).

Keep untouched: exact UI copy and style tokens, ACs, constraints holding live-verified facts, and the Structure Outline's schemas, signatures and file list.

### Step 4 — Prove nothing was lost, at both grains

**Facts.** Give one fresh `general-purpose` agent both versions and one falsifiable task: find facts present in the original and absent from the trimmed file. Not "review the trim".

- **Not a finding** — removed redundancy, shorter wording, reordering, scaffolding removal.
- **Seed it** with the sole homes, the survivors, and every exact string, token and citation.
- **Search the whole file before declaring loss** — facts move sections.
- **Split across two agents** when one context cannot hold both versions.

**Anchors** — PIPELINE only.

- **Canonical greps** — re-run them verbatim from Gate anchors in `skills/product-interview/SKILL.md`; never re-derive them.
- **Other anchors** — the headings a gate greps, id prefixes, marker tokens, one-physical-line ACs.
- **Headings kept only as anchors** — comment them, naming what greps each one, or the next trim removes it.

Fix every finding, then grep each restored string to confirm it landed.

### Step 5 — Report

```
**Trim complete — <file>:**
- lines: [before] → [after] ([net], [%])
- drifted pairs reconciled: [id + which copy was true | none]
- restored by the loss pass: [fact — why it was unique | none]
- anchors kept only as anchors: [anchor — what greps it | none]
- over the Step-2 estimate: [by how much, and why | no]
```

## Rules

- **Never cut to hit a number.** The target is "no fact lost"; size is the byproduct.
