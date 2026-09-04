---
name: durable-docs-update
description: "After coding work, sweep comments in changed files and sync only related durable guidance through WORTH → PLACE → SHAPE. TRIGGER when: user asks to update/sync durable docs, code comments, or AGENTS.md after work; an executor skill reaches close-out."
---

# Durable Docs Update

Make two judgments in order:

| Judgment | Question | A "no" means |
|---|---|---|
| **Sweep** | Should this comment exist? | Delete the comment. |
| **Docs pass** | Does this fact belong in current guidance? | Drop the fact. |

Callers invoke this skill inline, never as a leaf subagent; it coordinates discovery and application subagents, then checks their combined result.

## Input

Resolve scope through one mode:

| Mode | Use when | Scope and change content |
|---|---|---|
| **A — session** | Run directly in the working session. | Files this agent created or edited, from its Edit/Write history; current state plus session knowledge. |
| **B — range** | A commit range `A..B` is available. | Names from `git diff --name-only A..B`; content from `git diff A..B`. |
| **C — caller-supplied** | An orchestrator delegated uncommitted edits. | Explicit file list plus `git diff -- <those files>`. |

Never derive scope from `git status`; the working tree is process-global. Mode C uses only the caller's named files.

Optional inputs:

- **discoveries** — the caller's `Discovery:` bullets, already reduced to gotchas or couplings.
- **context** — the work's goal and criteria.
- **spec** — the work's `spec.md`; Step 2 mines its locked `D-NNN-XX` decisions.

## Protocol

### Step 1 — Resolve scope and scale

Resolve the mode, build the in-scope changed-file list, and count each file once. Use the count to cap both discovery and application subagents:

| Tier | Scoped files | Subagents per pass |
|---|---:|---:|
| **Small** | 1–3 | Up to 1 |
| **Medium** | 4–8 | Up to 2 |
| **Large** | 9+ | Up to 3 |

Use fewer subagents when files are tightly coupled. Group files by nearest parent `AGENTS.md`, and assign each scoped file to exactly one discovery subagent. With no scoped files, continue to the Step 5 no-op report.

- **Brief.** Give each discovery subagent its files, scoped diff or current content, matching discoveries, locked decisions, and work context.
- **Git safety.** Scope every subagent's Git reads and mutations to its assigned files. Never let a subagent run `git stash`, `git checkout -- .`, `git reset`, or another whole-tree mutation.
- **Discovery boundary.** Discovery subagents make no mutations.
- **Baselines.** Read committed baselines with `git show HEAD:<path>`.

### Step 2 — Discover, judge, and place

Each discovery subagent invokes the Skill tool to load `vet-fact` and `place-fact`, then scans its assigned files and directly related guidance. Read a changed code file in full only when it contains a candidate comment; never read the whole repository.

A full-file read does not expand scope. Consider only comments in or governing changed code, or comments named by a passed discovery or decision. Leave unrelated comments—including test separators and historical notes—untouched unless the caller explicitly expands scope.

Inspect only related sources:

- The file's comments, ancestor `AGENTS.md` files, and Claude path rules in `.claude/rules/` whose quoted `paths:` globs match the file.
- A root-routed task document only when the change purpose matches its route.
- Any target selected by `place-fact`; crossing modules does not choose a document by itself.

- **Gather.** Gather candidates from comments, passed `Discovery:` bullets, locked spec decisions that constrain an in-scope file, and existing guidance that directly names affected behavior.
- **Merge.** Merge a discovery with the decision it restates and keep the decision's rationale wording.
- **Exclude.** Exclude active-state documents, dated investigations, session logs, handoffs, process/workflow documents, `.agents/skills/`, `.claude/skills/`, `.claude/commands/`, and unrelated material.

For every candidate, apply WORTH before PLACE:

1. Use `vet-fact` to decide whether the fact should survive. A comment that contradicts current code becomes an UPDATE; a comment that fails WORTH becomes a DELETE.
2. Use `place-fact` over every surviving fact to select its canonical owner and delivery boundary.
3. Classify the proposed change: ADD a missing fact; UPDATE a stale or unclear fact; TRIM history or bloat while keeping the fact; DELETE a fact that no longer belongs; or MOVE a fact to its canonical owner. Preserve any valid `Discovered:` freshness stamp on a TRIM.
4. Score confidence `0.00–1.00` that the fact, action, and target are all correct.

Keep a `D-NNN-XX` or `AC-NNN-XX` id beside the fact it labels. Cut task ids, wave numbers, and `F-NNN-XX` finding ids while keeping any fact they obscure. Return proposals as `{ source: file:line | input, current_text, fact, action, target, proposed_change, confidence }`; return no file contents beyond a candidate's current text and make no edits.

### Step 3 — Merge, gate, and assign

The main agent merges discovery results, deduplicates by fact and canonical target, and keeps the highest-confidence copy. Resolve conflicting placements before assignment.

- **Gate.** Accept every proposal with confidence `≥ 0.75`; drop every proposal below it without asking, regardless of source or action.
- **Report retention.** Keep dropped comment proposals only for the Step 5 `left alone, unsure` report.
- **Triage.** Skip triage because all accepted edits are scoped and reversible.

Group accepted proposals by target file within the Step 1 subagent cap. Assign each target file to exactly one application subagent, and assign both sides of a MOVE to the same subagent. If none qualify, continue to Step 5.

### Step 4 — Apply, shape, and check coherence

Pass each application subagent its accepted proposals verbatim and the Step 1 Git-safety rules. Each subagent:

1. Applies all assigned proposals before shaping their text.
2. For every instruction document created or materially reshaped, invokes the `compress-file` skill via the Skill tool. A document is materially reshaped when the changes add, remove, or move a section, or span at least three sections.
3. Invokes the `tighten-instruction` skill, then the `structure-prose` skill, via the Skill tool over only the comments and instructions this run changed.
4. Scores every independent lens edit `0.00–1.00`, applies it at `c ≥ 0.75`, and holds it below the threshold.
5. Returns one line per file, a comment tally (`corrected`, `deleted`, `tightened`), and deleted-comment details as `{ file, line, text, confidence }`.

After all application subagents return, the main agent:

1. Invokes the `check-coherence` skill via the Skill tool on each changed durable document.
2. Confirms that the final combined diff applies every accepted proposal and contains no unrelated changes.

### Step 5 — Report

The caller does not repeat this report.

```text
**Docs sync:**
- Comments: [n] corrected, [m] deleted, [k] tightened
  - deleted: [file:line — "text" (0.NN), one per line | none]
  - left alone, unsure: [file:line — "text" (0.NN), one per line | none]
- Docs: [file — what changed, one per line | none needed]
- Dropped: [K] candidates below 0.75
- Instruction delta: [net lines], [artifacts added], [artifacts removed], [always-loaded lines]; review signal only, never a quota
```
