---
name: durable-docs-update
description: "After finishing a coding task or plan, audit code comments and durable docs (CLAUDE.md, architecture.md, ARCHITECTURE.md, .claude/rules) for the changed files; propose scoped adds/updates/trims the user approves. Change-scoped, not a repo-wide doc sweep. TRIGGER when: user asks to update/sync durable docs, code comments, or CLAUDE.md after finishing work."
---

# Durable Docs Update

Audit code comments and durable docs for the files changed by a piece of work, then propose scoped doc changes the user approves.

## Input

Scope resolves via one of two modes (discoveries and context are optional):

| Mode | Invoked | Scope source | Change content |
|---|---|---|---|
| **A — session** | directly, in a working session | files this session's agent created/edited, from its own Edit/Write history | current file state + the agent's knowledge of what it changed |
| **B — range** | with a commit range `A..B` (e.g. `<base-sha>..HEAD`) | `git diff --name-only A..B` | `git diff A..B` |

Plus:
- **discoveries** (optional) — pre-distilled gotcha/coupling bullets. The caller passes its logged `Discovery:` bullets; seed them as high-priority candidates.
- **context** (optional) — what the work was for (goal, criteria). Sharpens the "would a future agent get this wrong?" judgment.

## What belongs in a durable doc

Add a rule only if a future agent would get the wrong answer without it; for code comments, encode a constraint, assumption, or coupling.

**Belongs:**
- Gotchas, anti-patterns, dead-code warnings
- Cross-file couplings not visible from one file alone
- Conventions that contradict the obvious default
- Pointers to source-of-truth ("X lives in Y")
- Design rationale framed as "current behaviour is X; if tempted to change to Y, reason Z still applies"

**Does NOT belong:**
- Anything derivable by reading the code, running `ls`, or checking lint config
- Setup / onboarding (belongs in README)
- Historical breadcrumbs: dates, plan IDs, commit SHAs, test counts, supersedes/originally/renamed-from notes, completion summaries, deferred-items lists
- Restated harness or framework defaults
- Inlined specifics that drift (hex codes, version pins, exact syntax)

## Where each rule lives — most-local home wins

- Visible from one file → **in-file comment**
- Module-specific → module's **`architecture.md`** or nearest **`CLAUDE.md`**
- Cross-module → root **`ARCHITECTURE.md`**
- Reusable, path-scoped coding rule → **`.claude/rules/<name>.md`** (create the dir if absent); otherwise nearest `CLAUDE.md`

## Protocol

### Step 1 — Resolve scope and gather candidates

Determine the scope mode (table above) and build the in-scope code file list. How the research runs depends on the mode:

**Mode A (session) — main agent, serial.** You hold the session memory, so do the research serially. Per file: note what changed and any gotcha/coupling, then read related docs (below). Proceed to Step 2.

**Mode B (range) — fan out.** The diff is stateless, so parallelize the read. Group the changed files by nearest parent `CLAUDE.md`/module and dispatch one subagent per group — assess the change set and spin up as many as the work warrants, up to 6. Each subagent receives its file group, `git diff A..B` for those files, any matching discoveries, and §What belongs + §Where each rule lives as criteria; it runs Step 2 (classify → shape → score) for its group and returns its candidate rows only (no file contents). Merge all rows, dedup overlapping proposals (same target + rule), then present per Step 3.

Related docs per file: walk the homing list in §Where each rule lives (in-file → `CLAUDE.md` up the tree → same-module `architecture.md` → root `ARCHITECTURE.md` if cross-cutting → matching `.claude/rules/*.md`); skip absent ones.

In both modes: if **discoveries** were passed, seed them as high-priority candidates; flag historical breadcrumbs (see §What belongs → Does NOT belong) as TRIM; exclude `.claude/skills/`, `.claude/commands/`, process/handoff/workflow docs, session logs, and any doc unrelated to the code you changed.

### Step 2 — Classify, shape, and score

Classify each potential change:

- **ADD** — new rule or in-file comment
- **UPDATE** — existing rule drifted from the code you just changed
- **TRIM** — keep the rule; cut bloat and historical breadcrumbs, recasting any survivor to present tense
- **DELETE** — rule no longer applies (code removed, convention changed, lint catches it)
- **MOVE** — rule is in the wrong home

Shape each proposal with the `tighten-instruction` skill lens:
- One declarative line: trigger + action, present tense, no history.
- Cut restated-goal, hedge, and explain-why clauses.
- Collapse what the positive form already implies.
- Test cold — must read without surrounding context.

Then score each 0.0–1.0 — confidence it belongs in a durable doc.

### Step 3 — Present and gate

Present candidates ≥ 0.70 in the primary table, sorted by confidence.

```
| # | Confidence | Target | Action | Proposal | Why |
|---|------------|--------|--------|----------|-----|
| 1 | 0.92 | src/foo/views.py:142 | ADD comment | "Trailing slash required — webhook signer drops it otherwise" | Gotcha hit this session; recurs |
| 2 | 0.88 | src/foo/CLAUDE.md §Auth | ADD | "JWT verify runs before request body parse — order matters for HMAC check" | Cross-file coupling not visible from either file alone |
| 3 | 0.84 | ARCHITECTURE.md §Data | UPDATE | Rename `foo_v1` → `foo` | File renamed this session |
| 4 | 0.83 | src/foo/CLAUDE.md §Style | TRIM | Drop "introduced in plan-038, supersedes legacy banner logic" and the 8-line why-paragraph; keep the present-tense rule | Bloat + historical breadcrumb |
```

- Ask which to apply (e.g. "apply 1, 2, 4").
- **Below cutoff (0.50–0.69):** don't drop silently — list them compactly below the table, each defaulted to *dismiss*, so the user can promote any the model under-scored. Score < 0.50: drop.

```
Below cutoff (default: dismiss — say "keep N" to promote):
- 0.62 | src/foo/api.py:88 | ADD comment | "Retry caps at 3 — see backoff config"
- 0.55 | src/foo/CLAUDE.md §Data | UPDATE | widen "ints only" to "ints/decimals"
```

- If nothing qualifies in either tier, say so and stop.

### Step 4 — Apply

Group the approved edits by target file and dispatch one subagent per file, up to 6 in parallel. Each applies its file's approved proposals in a single pass and returns a one-line summary:

`src/foo/CLAUDE.md: +1 rule under §Auth, TRIM §Style`

## Rules

- **Never auto-apply.** Always present the scored table and let the user pick — even at confidence 1.0.
- **Stay change-scoped.** Only audit docs tied to the in-scope files. No repo-wide sweeps.
- **Most-local home wins.** Prefer an in-file comment over a CLAUDE.md rule over a root doc.
- **No `git status` for scope.** Use session memory (mode A) or the passed range (mode B) — the working tree is process-global, so a parallel session would contaminate it.
- **One subagent per file on apply.** Give each target file to its own subagent so edits apply in parallel without same-file races; pass the approved proposal text verbatim so it can't drift.
