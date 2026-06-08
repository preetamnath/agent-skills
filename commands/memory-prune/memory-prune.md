---
description: Review project memories and recommend which should be promoted into a durable doc, rule, slash command, or skill. Confirms before applying.
---

# Memory Prune

Walk every memory file in this project's memory dir. For each, recommend whether it should be promoted into a more durable form, then what to do with the source memory after.

## Inputs

- **Memory dir.** `~/.claude/projects/<slug>/memory/`, where `<slug>` is the absolute cwd with every non-alphanumeric character replaced by `-`. Resolve with `ls ~/.claude/projects/ | grep -Fx -- "$(pwd | sed 's|[^a-zA-Z0-9]|-|g')"`. On zero or multiple matches, print the candidates and ask the user to pick.
- **Memory files.** Every `*.md` in that dir except `MEMORY.md` (the index). If none, stop.

## Protocol

### 1 — Read

Read each memory's frontmatter (incl. `metadata.type`: user / feedback / project / reference) and body.

### 2 — Classify

Classify each against the §Rubric. Attach a confidence 0.0–1.0 and one-line reasoning citing the target file (or what makes it stale). Use `metadata.type` as a signal: `feedback` / `user` lean KEEP; `project` / `reference` lean promotable.

### 3 — Present

Present every recommendation ≥0.70 in one table sorted by confidence; if none qualify, say so and stop.

`| # | Confidence | Memory | Verdict | Target | Disposition | Why |`

### 4 — Apply

For each approved row: edit the target file, verify the change landed, then dispose of the source per its disposition. Never auto-apply — confirm first, even at 1.0.

Then update `MEMORY.md`: remove only the lines whose source was DELETE'd; leave every other entry (TRIM, NONE, KEEP, and anything below 0.70). Index line format: `- [Title](file.md) — one-line summary`.

## Rubric

| Verdict | Promote to | Pick when |
|---|---|---|
| DOC (root) | `CLAUDE.md`, `ARCHITECTURE.md` — always loaded | Cross-cutting fact every contributor needs |
| DOC (scoped) | `<folder>/CLAUDE.md` — loads when the AI opens any file under that folder | Fact only relevant inside that subtree |
| RULE | `.claude/rules/<name>.md` — fires only when its path matcher hits | Behavioral guidance scoped to specific paths |
| COMMAND | `.claude/commands/<name>.md` | Reusable workflow the user invokes on demand |
| SKILL | `.claude/skills/<name>/SKILL.md` | Bounded capability with instructions and assets |
| STALE | — | Outdated or describes shipped/abandoned work |
| KEEP | — | Personal preference, active in-flight project state, or context that fits no durable surface |

If a promotion target's directory doesn't exist in the repo (e.g. no `.claude/rules/`), fall back to the nearest `CLAUDE.md`.

**Verdict → disposition:**
- DOC / RULE / COMMAND / SKILL → **DELETE** if fully absorbed, else **TRIM**
- STALE → **DELETE**, or **NONE** to keep a record
- KEEP → **NONE** (presented for visibility; apply does nothing)

**Disposition:**
- **DELETE** — source fully absorbed into the target
- **TRIM** — replace body with a pointer to the target; keep its `MEMORY.md` line
- **NONE** — leave alone
