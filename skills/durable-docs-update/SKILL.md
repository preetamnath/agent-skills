---
name: durable-docs-update
description: "After a coding task or plan, sweep the changed files' code comments — correcting or deleting stale ones — then turn the facts worth keeping into durable-doc adds/updates/trims (CLAUDE.md, .claude/rules, ARCHITECTURE.md): applies high-confidence ones, asks before relocating a fact. Change-scoped, not a repo-wide sweep. TRIGGER when: user asks to update/sync durable docs, code comments, or CLAUDE.md after finishing work; an executor skill reaches its close-out."
---

# Durable Docs Update

Primitive: **WORTH + PLACE + SHAPE** over a change-set.

Two judgments, in order, never merged:

| Judgment | Asks | Verdict on "no" |
|---|---|---|
| **Sweep** | should this comment exist? | deletes the comment |
| **Docs pass** | does this fact belong in a doc? | drops the fact |

Judge a comment on the docs question instead and a worthless one scores low, drops out of the proposals, and stays in the code.

Callers invoke this skill inline, never as a leaf subagent — it fans out its own subagents.

## Input

Scope resolves via one of three modes (discoveries, context, and spec are optional):

| Mode | Invoked | Scope source | Change content |
|---|---|---|---|
| **A — session** | directly, in a working session | files this session's agent created/edited, from its own Edit/Write history | current file state + the agent's knowledge of what it changed |
| **B — range** | with a commit range `A..B` (e.g. `<base-sha>..HEAD`) | `git diff --name-only A..B` | `git diff A..B` |
| **C — caller-supplied** | by an orchestrator that delegated edits to subagents and made no commits | an explicit changed-file list the caller passes | the caller's working-tree `git diff -- <those files>` |

Never resolve scope from `git status` — the working tree is process-global, so a parallel session would contaminate it. Mode C avoids this by scoping to the caller's named files, never the whole tree.

Plus:
- **discoveries** (optional) — the caller's logged `Discovery:` bullets: pre-distilled gotcha/coupling facts.
- **context** (optional) — what the work was for (goal, criteria). Sharpens the "would a future agent get this wrong?" judgment.
- **spec** (optional) — path to the work's `spec.md`; its `## Decisions` blocks carry locked `D-NNN-XX` decisions (Chosen + Rationale). Step 1 mines them.

## Protocol

### Step 0 — Load lenses

Invoke the Skill tool to load `vet-fact` (WORTH — keep or cut), `place-fact` (PLACE — which home), and `tighten-instruction` with `structure-prose` (SHAPE — how the line reads, and whether a block should be a list). They judge every proposal. Relay their loaded criteria text into every subagent's dispatch brief, in Step 1 and Step 4 alike — subagents don't inherit a parent-loaded skill.

### Step 1 — Sweep the comments, gather the candidates

Determine the scope mode (table above) and build the in-scope code file list. Every file gets both jobs in order — sweep its comments, then gather its doc candidates — so a false comment is fixed before the docs pass can make it durable.

**The sweep covers whole files**, not just the comments the run wrote — a comment the run made false is one it never touched. Never the whole repo.

- **Per comment**, in order:
  1. Contradicts the code it describes → rewrite it to the current fact.
  2. Fails `vet-fact`'s worth test → score that call `0.0–1.0`; `≥ 0.75` deletes the comment, below it leaves the comment and returns it as `left_alone`.
  3. Carries its fact but reads muddy → tighten in place.
  4. States a fact that belongs in a durable doc → hold it as a `doc_candidate` for the gather, and leave a one-line comment behind.
- **Order is the content** — worth runs before shape, so a dead comment isn't tightened before being deleted.
- **Only the worth call is scored** — a contradiction is checkable against the code, and a tighten is cheap either way.
- **Tidy what the sweep wrote** — `tighten-instruction`, then `structure-prose`, over every comment it rewrote or tightened. Nothing else shapes them.
- **Comment id hygiene** — a `D-NNN-XX`/`AC-NNN-XX` id beside its fact is a legitimate label (keep); a task id, wave number, or `F-NNN-XX` finding id is a breadcrumb — cut the id, keep the fact.

How the work runs depends on the mode:

**Mode A (session) — main agent, serial.** You hold the session memory, so do the work serially. If the edited-file set is too large to handle serially and a commit range exists, run it as Mode B instead. Per file: sweep, then note what changed and any gotcha/coupling, then read related docs (below). Proceed to Step 2.

**Mode B (range) or Mode C (caller-supplied) — fan out.** The diff is stateless, so parallelize:
- **Dispatch** — group the changed files by nearest parent `CLAUDE.md`; up to 3 **Sonnet** subagents, each covering one or more groups. One file is swept by exactly one subagent.
- **Each subagent receives** — its files and their diff (`git diff A..B`, or the caller-supplied working-tree diff in Mode C), any matching discoveries and locked `D-NNN-XX` decisions, and the lens criteria text from Step 0. Its brief draws the line hard: the sweep **edits** its files; the gather **proposes only**.
- **Git safety** — include these rules in every editing-subagent brief:
  - Keep Git mutations scoped to assigned files: never run `git stash`, `git checkout -- .`, `git reset`, or another command that changes the whole tree.
  - Read a committed baseline without changing shared state with `git show HEAD:<path>`.
- **Each returns** — its sweep tally (`corrected`, `deleted`, `tightened`, plus the `deleted` and `left_alone` lists as `{ file, line, text, confidence }`), and, after running Step 2 (classify → shape → score) over its files, all rows it scored ≥ 0.75 plus every seeded row regardless of score. No file contents.
- **Merge** — join the sweep tallies and lists; dedup overlapping doc proposals (same target + rule), keeping the max confidence — path-scoped rules and `ARCHITECTURE.md` span groups, so several subagents may target one shared doc. Present per Step 3.

Related docs per file: walk outward from the changed file (in-file comment → nested `CLAUDE.md` up the tree → matching `.claude/rules/*.md` → root `ARCHITECTURE.md` if cross-module); skip absent ones.

In all modes, seed and filter:
- **Seed the sweep's `doc_candidate`s** — a fact a comment was carrying is a high-priority candidate.
- **Seed discoveries** — each passed `Discovery:` bullet is a high-priority candidate.
- **Seed locked decisions** — if **spec** was passed, each `Status: locked` `D-NNN-XX` block is a high-priority candidate, mapped to the in-scope file(s) it constrains — skip any that map to no changed file. A settled decision is often a durable constraint, coupling, or rationale, but it's a candidate for the lens filter, not a guaranteed ADD.
- **Collapse the channels where they name the same fact** — a `D-NNN-XX` promoted from an `[AC-affecting]` discovery (its close-out marker names the decision), or a discovery that otherwise restates a locked decision, is one candidate: seed once, keeping the decision's rationale phrasing.
- **Every seed still runs Step 2** against the file's current docs — a fact an in-file comment or rule already carries is not a fresh ADD (drop it, or UPDATE if the code drifted from the decision).
- **Flag historical breadcrumbs** (see `vet-fact`) as TRIM.
- **Exclude** `.claude/skills/`, `.claude/commands/`, process/handoff/workflow docs, session logs, and any doc unrelated to the code you changed.

### Step 2 — Classify, shape, and score

Classify each potential change:

- **ADD** — new rule or in-file comment. Never ADD to a module `architecture.md` / `*-quirks.md` — they are `place-fact` non-homes; classify their facts as MOVE (decompose per the lens).
- **UPDATE** — existing rule drifted from the code you just changed
- **TRIM** — keep the rule; cut bloat and historical breadcrumbs — but keep per-entry `Discovered:` provenance stamps (`vet-fact` provenance carve-out)
- **DELETE** — rule no longer applies (code removed, convention changed, lint catches it)
- **MOVE** — rule is in the wrong home

Shape each proposal with the `tighten-instruction` and `structure-prose` lenses loaded in Step 0, plus:
- **House rule** — write every kept rule in present tense, no history.
- **Rationale exception** — a fact `vet-fact` keeps as `rationale` carries its reason *as* the fact; shape it to "behaviour — constraint" (lens Step 4), not stripped as explain-why (its Step 3).

Score each on two axes: confidence (0.0–1.0) it belongs in a doc, and impact — render `Label (value)`: Minimal (0.25) · Low (0.5) · Medium (1) · High (2) · Massive (3).

### Step 3 — Present and gate

**Seeds bypass the gate.** Candidates seeded from a `doc_candidate`, a discovery, or a locked `D-NNN-XX` present directly at any score — an asserted fact isn't filtered by the skill's own confidence; you decide. Without the bypass, a fact the sweep demoted to a one-line stub could score under the gate and drop, leaving only the stub.

Gate every other candidate on its confidence `c`: `c ≥ 0.75` applies, `c < 0.75` drops. No triage checker — these edits land in the table below and revert in one commit, so a borderline row isn't worth one.

**MOVE candidates present for your decision instead of applying** — a MOVE names a target home, and sending a fact to the wrong home is worse than leaving it put.

Present the resulting set as a table (template below), sorted by confidence.

```
| # | Confidence | Impact | Target | Action | Proposal | Why |
|---|------------|--------|--------|--------|----------|-----|
| 1 | 0.92 | High (2) | src/foo/views.py:142 | ADD comment | "Trailing slash required — webhook signer drops it otherwise" | Gotcha hit this session; recurs |
| 2 | 0.88 | Massive (3) | src/foo/CLAUDE.md §Auth | ADD | "JWT verify runs before request body parse — order matters for HMAC check" | Cross-file coupling not visible from either file alone |
| 3 | 0.84 | Low (0.5) | ARCHITECTURE.md §Data | UPDATE | Rename `foo_v1` → `foo` | File renamed this session |
| 4 | 0.83 | Minimal (0.25) | src/foo/CLAUDE.md §Style | TRIM | Drop "introduced in plan-038, supersedes legacy banner logic" and the 8-line why-paragraph; keep the present-tense rule | Bloat + historical breadcrumb |
| 5 | 0.76 | Medium (1) | src/foo/CLAUDE.md §Cache | ADD | "Cache key omits tenant id — scope it per tenant" | Coupling invisible from either caller alone |
```

- Auto-apply every row that cleared the gate; ask (`AskUserQuestion`) which seeds and MOVEs to apply.
- After the table, report what the gate filtered in one line: `K candidates dropped below 0.75`.
- If nothing qualifies, say so and go to Step 5 — the sweep still happened and still gets reported.

### Step 4 — Apply and tidy

Group the approved edits by target file and dispatch up to 3 **Sonnet** subagents in parallel, each owning one or more whole files — never split a file across subagents, or same-file edits race. Pass the approved proposal text verbatim so it can't drift. Include the Git-safety brief from Step 1.

Each subagent, per file it owns:
1. Apply that file's approved proposals.
2. Tidy **only the lines it added or changed** — `tighten-instruction`, then `structure-prose`.
3. Return a one-line summary: `src/foo/CLAUDE.md: +1 rule under §Auth, TRIM §Style`.

**You tidy any doc file this run created, not its subagent** — once every subagent has returned, invoke the `compress-file`, `tighten-file`, then `structure-prose` skills via the Skill tool over each. `tighten-file` spawns its own reviewers, which a leaf subagent can't do.

### Step 5 — Report

You own this report; a calling skill repeats none of it.

```
**Docs sync:**
- Comments: [n] corrected, [m] deleted, [k] tightened
  - deleted: [file:line — "text" (0.NN), one per line | none]
  - left alone, unsure: [file:line — "text" (0.NN), one per line | none]
- Docs: [file — what changed, one per line | none needed]
- Dropped: [K] candidates below 0.75
```
