---
name: durable-docs-update
description: "After finishing a coding task or plan, audit code comments and durable docs (CLAUDE.md, .claude/rules, ARCHITECTURE.md) for the changed files; propose scoped adds/updates/trims the user approves. Change-scoped, not a repo-wide doc sweep. TRIGGER when: user asks to update/sync durable docs, code comments, or CLAUDE.md after finishing work."
---

# Durable Docs Update

Primitive: **WORTH + PLACE + SHAPE** over a change-set.

Audit code comments and durable docs for the files changed by a piece of work, then propose scoped doc changes the user approves.

## Input

Scope resolves via one of two modes (discoveries, context, and spec are optional):

| Mode | Invoked | Scope source | Change content |
|---|---|---|---|
| **A — session** | directly, in a working session | files this session's agent created/edited, from its own Edit/Write history | current file state + the agent's knowledge of what it changed |
| **B — range** | with a commit range `A..B` (e.g. `<base-sha>..HEAD`) | `git diff --name-only A..B` | `git diff A..B` |

Plus:
- **discoveries** (optional) — pre-distilled gotcha/coupling bullets. The caller passes its logged `Discovery:` bullets; seed them as high-priority candidates.
- **context** (optional) — what the work was for (goal, criteria). Sharpens the "would a future agent get this wrong?" judgment.
- **spec** (optional) — path to the work's `spec.md`. Mine its `## Decisions` blocks: each `Status: locked` `D-NN` (Chosen + Rationale) seeds a high-priority candidate, mapped to the in-scope file(s) it constrains — skip any that map to no changed file. A settled decision is often a durable constraint, coupling, or rationale, but it's a candidate for the belongs-filter, not a guaranteed ADD.

## Placement and the content filter

Invoke three lens skills per proposal — reference each by name, don't paraphrase the model; if one isn't installed, fall back to the gist beside it:
- **`vet-fact`** (WORTH) — add a fact only if a future agent would get the wrong answer without it.
- **`place-fact`** (PLACE) — its delivery trigger picks the home; most-local wins (in-file comment → path-scoped rule or nested `CLAUDE.md` → root `ARCHITECTURE.md`). For an in-file comment, encode a constraint, assumption, or coupling visible from that one file.
- **`tighten-instruction`** (SHAPE) — one positive line: trigger + action for an instruction, subject + the non-derivable part for a fact.

Never ADD to a module `architecture.md` / `*-quirks.md` (retired homes, `place-fact`) — TRIM or decompose any you find.

## Protocol

### Step 1 — Resolve scope and gather candidates

Determine the scope mode (table above) and build the in-scope code file list. How the research runs depends on the mode:

**Mode A (session) — main agent, serial.** You hold the session memory, so do the research serially. Per file: note what changed and any gotcha/coupling, then read related docs (below). Proceed to Step 2. (Step 3 runs `triage` only if the triage band is non-empty.)

**Mode B (range) — fan out.** The diff is stateless, so parallelize the read. Group the changed files by nearest parent `CLAUDE.md`/module and dispatch one subagent per group — assess the change set and spin up as many as the work warrants, up to 6. Each subagent receives its file group, `git diff A..B` for those files, any matching discoveries and locked `D-NN` decisions, plus the `vet-fact` (WORTH) and `place-fact` (PLACE) lenses as criteria (see §Placement); it runs Step 2 (classify → shape → score) for its group and returns all rows it scored ≥ 0.70, plus every seeded row regardless of score (no file contents). Merge all rows, dedup overlapping proposals (same target + rule), then present per Step 3.

Related docs per file: walk outward from the changed file (in-file comment → nested `CLAUDE.md` up the tree → matching `.claude/rules/*.md` → root `ARCHITECTURE.md` if cross-module); skip absent ones.

In both modes: seed any passed **discoveries** as high-priority candidates, and — if **spec** was passed — each `Status: locked` `D-NN` block the same way. Collapse the two channels where they name the same fact — a `D-NN` promoted from an `[AC-affecting]` discovery (its close-out marker names the decision), or a discovery that otherwise restates a locked decision, is one candidate: seed once, keeping the decision's rationale phrasing. Every seed still runs Step 2 against the file's current docs — a fact an in-file comment or rule already carries is not a fresh ADD (drop it, or UPDATE if the code drifted from the decision). Flag historical breadcrumbs (see `vet-fact`) as TRIM; exclude `.claude/skills/`, `.claude/commands/`, process/handoff/workflow docs, session logs, and any doc unrelated to the code you changed.

### Step 2 — Classify, shape, and score

Classify each potential change:

- **ADD** — new rule or in-file comment
- **UPDATE** — existing rule drifted from the code you just changed
- **TRIM** — keep the rule; cut bloat and historical breadcrumbs, recasting any survivor to present tense — but keep per-entry `Discovered:` provenance stamps (`vet-fact` provenance carve-out)
- **DELETE** — rule no longer applies (code removed, convention changed, lint catches it)
- **MOVE** — rule is in the wrong home

Shape each proposal with the `tighten-instruction` skill lens:
- One positive line in the shape the content wants — trigger + action for an instruction, subject + the non-derivable part for a fact; present tense, no history.
- Cut restated-goal, hedge, and explain-why clauses.
- Collapse what the positive form already implies.
- Test cold — must read without surrounding context.

Score each on two axes: confidence (0.0–1.0) it belongs in a doc, and impact — render `Label (value)`: Minimal (0.25) · Low (0.5) · Medium (1) · High (2) · Massive (3).

### Step 3 — Triage, present, and gate

**Seeds bypass the bands.** Discovery- and locked-`D-NN`-seeded candidates present directly at any score — a caller-asserted fact isn't filtered by the skill's own confidence; you decide.

Band every other candidate by its confidence `c` — the bands are a cost lever:
<!-- source: references/confidence-bands.md (Mode F) -->
- **keep** (no triage) — `c ≥ 0.80`.
- **triage** — `0.70 ≤ c < 0.80`.
- **drop** — `c < 0.70`.

Run `triage` once on the triage band (skip if empty) — each finding: id = row #, claim = the proposal; plus the target file path(s). Route the verdicts: `consider` → keep · `skip` → drop. **MOVE candidates skip triage — present them directly** (`consider`/`skip` can't carry a corrected target home, and this skill has no walk step to recheck one).

Present the resulting set in the primary table, sorted by confidence — post-triage `adjusted_confidence` where triage ran, else the candidate's score.

```
| # | Confidence | Impact | Target | Action | Proposal | Why |
|---|------------|--------|--------|--------|----------|-----|
| 1 | 0.92 | High (2) | src/foo/views.py:142 | ADD comment | "Trailing slash required — webhook signer drops it otherwise" | Gotcha hit this session; recurs |
| 2 | 0.88 | Massive (3) | src/foo/CLAUDE.md §Auth | ADD | "JWT verify runs before request body parse — order matters for HMAC check" | Cross-file coupling not visible from either file alone |
| 3 | 0.84 | Low (0.5) | ARCHITECTURE.md §Data | UPDATE | Rename `foo_v1` → `foo` | File renamed this session |
| 4 | 0.83 | Minimal (0.25) | src/foo/CLAUDE.md §Style | TRIM | Drop "introduced in plan-038, supersedes legacy banner logic" and the 8-line why-paragraph; keep the present-tense rule | Bloat + historical breadcrumb |
| 5 | 0.76 | Medium (1) | src/foo/CLAUDE.md §Cache | ADD | "Cache key omits tenant id — scope it per tenant" | Triaged `consider` (0.76 adjusted) — real coupling, checker confirmed |
```

- Ask which to apply (e.g. "apply 1, 2, 4").
- After the table, if the triage band was non-empty, report it in one line: `N triaged → M considered, K dropped`.
- If nothing qualifies, say so and stop.

### Step 4 — Apply

Group the approved edits by target file and dispatch one subagent per file, up to 6 in parallel. Each applies its file's approved proposals in a single pass and returns a one-line summary:

`src/foo/CLAUDE.md: +1 rule under §Auth, TRIM §Style`

## Rules

- **Never auto-apply.** Always present the scored table and let the user pick — even at confidence 1.0.
- **Stay change-scoped.** Only audit docs tied to the in-scope files. No repo-wide sweeps.
- **Most-local home wins.** Prefer an in-file comment over a CLAUDE.md rule over a root doc.
- **No `git status` for scope.** Use session memory (mode A) or the passed range (mode B) — the working tree is process-global, so a parallel session would contaminate it.
- **One subagent per file on apply.** Give each target file to its own subagent so edits apply in parallel without same-file races; pass the approved proposal text verbatim so it can't drift.
