---
name: memory-prune
description: "Review this project's memory files and route each to its durable home — promote a worth-keeping fact into a comment, CLAUDE.md tier, rule, ARCHITECTURE.md, command, or skill via the WORTH+PLACE+SHAPE lenses, then dispose of the source memory. TRIGGER when: user says 'prune my memories', 'clean up memory', 'what memories should be promoted', 'review my memory dir'. SKIP when: routing one already-extracted fact (place-fact), or auditing a single instruction file or CLAUDE.md (refine-file)."
---

# Memory Prune

Primitive: **WORTH + PLACE + SHAPE** over this project's memory dir, plus source disposition.

## Input

- **Memory dir.** `~/.claude/projects/<slug>/memory/`, where `<slug>` is the absolute cwd with every non-alphanumeric character replaced by `-`. Resolve with `ls ~/.claude/projects/ | grep -Fx -- "$(pwd | sed 's|[^a-zA-Z0-9]|-|g')"`. On zero or multiple matches, print the candidates and ask the user to pick.
- **Memory files.** Every `*.md` in that dir except `MEMORY.md` (the index). If none, stop.

## Protocol

### Step 0 — Load lenses

Invoke the Skill tool to load `vet-fact` (WORTH — promote, keep-as-memory, or cut), `place-fact` (PLACE — which durable home), and `tighten-instruction` (SHAPE — how the promoted line reads). The trio judges each memory in Step 2 and shapes each promoted line in Step 4 — don't restate their criteria here.

### Step 1 — Read

Read each memory's frontmatter (incl. `metadata.type`: user / feedback / project / reference) and body.

### Step 2 — Judge each memory

Run every memory through the lenses in WORTH → PLACE → SHAPE order, then set the source's disposition.

- **WORTH (`vet-fact`).** Interpret its keep/cut verdict in the memory context:
  - **keep** (durable-doc-worthy) → promote; carry the fact's category into PLACE.
  - **cut because stale/derivable** → STALE: the memory is dead.
  - **cut because true but not doc-worthy** (a personal preference, an in-flight project state) → KEEP: the memory dir is its home; leave it.
  - `metadata.type` is a signal: `feedback` / `user` lean KEEP; `project` / `reference` lean promotable.
- **Workflow fork.** If the memory is a repeatable procedure the user invokes rather than a fact, route it to a **command** (on-demand workflow) or a **skill** (external SDK/platform capability fused with procedure) — `place-fact` routes facts, not workflows, so PLACE won't cover this.
- **PLACE (`place-fact`).** For a promote-worthy fact, take its trigger→home verdict: in-file comment · nested `CLAUDE.md` · path-scoped rule · root `CLAUDE.md` · `ARCHITECTURE.md`. A repo-internal fact is never a skill (`place-fact`'s guardrail). If the target's directory doesn't exist in the repo (e.g. no `.claude/rules/`), fall back to the nearest `CLAUDE.md`.
- **Disposition of the source** — what happens to the memory once the target is written:
  - **DELETE** — the target fully absorbs it, or it's STALE: delete the memory file.
  - **TRIM** — the target partly absorbs it: replace the body with a pointer to the target.
  - **NONE** — KEEP, or a STALE you want a record of: leave it, listed for visibility only.

Attach a confidence 0.0–1.0 and one-line reason citing the target file (or what makes it stale).

### Step 3 — Present

Present every recommendation ≥0.70 in one table sorted by confidence; if none qualify, say so and stop.

`| # | Confidence | Memory | Verdict | Target | Disposition | Why |`

### Step 4 — Apply

Confirm which rows to apply — never auto-apply, even at confidence 1.0. Then for each approved row: shape the promoted fact with the `tighten-instruction` lens into one trigger+action line, edit or create the target file, verify the change landed, and dispose of the source per its disposition.

Then update `MEMORY.md`: remove only the lines whose source was DELETE'd; leave every other entry (TRIM, NONE, KEEP, and anything below 0.70). Index line format: `- [Title](file.md) — one-line summary`.
