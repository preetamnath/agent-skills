---
description: Seed a layered Claude-context surface across the current repo — root CLAUDE.md, per-subsystem nested CLAUDE.md, file-scoped .claude/rules/*.md, and a living root ARCHITECTURE.md. Maps the repo with parallel agents, plans placement and single ownership, drafts in waves, tightens, and reviews for coherence. Works with or without a reference repo. Use when a repo has no structured agent context or only a single sprawling CLAUDE.md.
---

# Seed Claude Context

Primitive: **WORTH + PLACE + SHAPE** over a whole repo.

Roll out a four-tier Claude-context surface across the current repo so future agents stop re-mapping it each session. You orchestrate: dispatch parallel subagents per phase, hold the task list, own every decision checkpoint.

## When to use

- The target repo has no structured agent context, or only a single sprawling root `CLAUDE.md`.
- It has at least one non-obvious subsystem or one file-level invariant worth documenting.

Skip for a single-purpose repo of a few files — write one root `CLAUDE.md` directly.

## Inputs

1. **Target repo** — defaults to the current working directory.
2. **Reference repo** (optional) — a repo whose context layering you trust, to mine for patterns. Absent one, derive structure from the tier lens below.

## Tier decision lens

Invoke two lens skills through every phase — reference each by name, don't paraphrase; if one isn't installed, fall back to its gist:
- **`place-fact`** (PLACE) — each fact's delivery trigger picks its home; one fact, one home; no home restates another. Owns the triggers→homes table, loading mechanics, and pointer rule.
- **`vet-fact`** (WORTH) — seed a fact only if a future agent would get the wrong answer without it.

Two command-specific notes:
- If the harness predates `.claude/rules/`, fold each file-scoped invariant into the nearest `CLAUDE.md` instead.
- Never seed a module `architecture.md` / `*-quirks.md` — retired homes (`place-fact`).

## Cross-reference rule

Follow `place-fact`'s pointer rule. Context loads progressively, so a pointer that re-announces an auto-loading target is dead weight — emit one only to a target that won't auto-load on the reader's current trigger, carrying a must-know-before-you-touch obligation:

- **Justified:** root `CLAUDE.md` → an `ARCHITECTURE.md` section or a skill — neither auto-loads.
- **Narrow:** `CLAUDE.md` → a rule, only when the rule's glob is deliberately narrower than the set of files the obligation touches (a cross-layer audit contract, or the new-file-`Write` gap). If the glob already covers the reader's files, it auto-loads — no pointer.
- **Never:** a `CLAUDE.md` that delegates to other `CLAUDE.md` files, or a folder→owner map. Those auto-load; the map only rots.

## ARCHITECTURE.md content rule

Bias to **non-inferable** content: data/control flow, subsystem boundaries, design decisions and their rationale, cross-cutting invariants, known constraints and tech debt. Do not dump the file tree — an agent reads that faster than your prose, and a stale tree actively misleads. It is a **living doc**: Phase 8 proposes a mechanism to keep it current. Without that mechanism it has no write-path and drifts fastest — say so when offering.

## Writing lens

If the `tighten-instruction` skill is installed, use it. Otherwise apply this inline:
- Each line = trigger + action ("Use X for Y." / "When X, do Y." / "Do X — Y breaks.").
- Cut any line whose job is to restate the goal, hedge, or explain why — unless the why IS the constraint.
- Lead with the rule, not the rationale. No emoji, no "IMPORTANT:", no marketing prose.
- Test cold: read each line out of context. If a future agent can't act on it, retighten.
- Keep every file within its per-tier length target.

---

## Workflow

### Phase 1 — Map the repo (parallel)

Size the mapping pool to the repo: 2–10 read-only agents (`Explore`, or `general-purpose` where unavailable) running simultaneously — one per major subtree on a large repo, a couple on a small one. Each returns a structured, self-contained report; none proposes file placement yet. Partition by:

- **Structure & conventions** (scale to repo size). Per-directory purpose, conventions, coupling, gotchas; framework and versions; build/test/lint commands; inventory of every existing context file (`CLAUDE.md`, `.claude/rules/*`, `ARCHITECTURE.md`) with its current content.
- **Architecture & flows** (one or more, split by subsystem). Entry points; data and control flow; subsystem boundaries; cross-cutting concerns (auth, state, caching, jobs); key design decisions; hot spots where a fresh agent would make mistakes. Feeds `ARCHITECTURE.md`.
- **Reference repo** (one agent, only if one is supplied). How it splits content across tiers and what earns a rule vs a `CLAUDE.md`. Map any `architecture.md`/`*-quirks.md` patterns it uses to the current model (rules / nested `CLAUDE.md`) — never replicate retired kinds.

### Phase 2 — Plan placement + ownership

Combine the reports into two tables.

**Placement:**

| # | Path | Tier | Owns | Does NOT cover | Confidence |

**Single ownership:**

| Fact / invariant | Sole owner | Inbound pointer (only if owner won't auto-load) |

Below them: explicit non-proposals — directories considered and skipped, one-line reason each.

Reconcile existing context files in the same table: mark each keep, merge, or rewrite. A file already present and correct is a keep — Phase 5 drafts only new and rewrite rows, so a re-run converges instead of overwriting good files. If a sprawling root `CLAUDE.md` exists, plan to carve its facts into the right tiers — never drop a fact on the way to a thinner root. A legacy module `architecture.md`/`*-quirks.md` is a retired kind, not a tier: note it as a deferred non-proposal for a separate decomposition pass — don't reconcile, draft from, or delete it.

### Phase 3 — Sanity-check the plan (parallel)

Dispatch `sanity-checker` agents with non-overlapping focus:
- **Granularity & necessity.** Which proposed files are too thin, duplicative, or just paraphrase the root? Which are missing?
- **Coverage & staleness.** For each hot spot, which file owns it? Where is duplication risk? Which file will go stale first?
- **Boundary.** Is the `ARCHITECTURE.md`/root-`CLAUDE.md` split clean, with single ownership held?

Synthesize their P0/P1 findings into one table.

### Phase 4 — Clarify, confirm, build task list

Apply consensus findings. Bundle load-bearing decisions into one `AskUserQuestion` (≤4 questions): naming conflicts, borderline keep/drop files, the ARCHITECTURE/CLAUDE boundary, anything agents flagged ambiguous. Name any file you propose dropping or adding so the user can push back.

Present the revised placement + ownership tables for confirmation. Then `TaskCreate` one task per file, plus tasks for tighten pass, coherence review, and final summary.

### Phase 5 — Draft in waves (parallel)

A pointer target must exist before the file that points at it (per the cross-reference rule). Only non-auto-loaded docs are link targets, so:
- **Wave 1** — `ARCHITECTURE.md` and all `.claude/rules/*.md`.
- **Wave 2** — all `CLAUDE.md` (root + nested), in parallel; order among them doesn't matter, since CLAUDE.md files don't reference each other.

Draft only the rows the plan marks new or rewrite; leave keeps untouched. Each drafter is a `general-purpose` subagent given a self-contained brief (template below). Accept drafter corrections over your brief.

If a `Write` under `.claude/rules/` is blocked as self-modification, write a frontmatter-only placeholder yourself, then re-dispatch the drafter to fill the body.

### Phase 6 — Tighten every file

If the `tighten-file` skill is installed, run it on the generated files. Otherwise apply the writing lens above at three levels per file: whole file (does it earn its existence?), section (does each heading earn its place?), line (trigger + action, cold-read test). Flag any file over its length target by >30% as a tightness fix, not polish.

### Phase 7 — Review coherence (parallel) + fix

Dispatch `reviewer` agents:
- **Rules audit.** Every `paths:` glob is quoted and resolves on disk; body is tight and scoped; the new-file-`Write` caveat is acceptable for this rule's purpose.
- **CLAUDE.md audit.** Spot-check ≥5 claims per file against source; scope discipline; length sane; no folder→owner map; every pointer targets a non-auto-loaded doc and resolves.
- **ARCHITECTURE.md audit.** Non-inferable bias held (no file-tree dump); accurate vs code; reachable via a root pointer.
- **Cross-file consistency.** One owner per fact (use the ownership table); no contradictions; no CLAUDE→CLAUDE delegation or redundant pointers; remaining pointers resolve and are justified by the cross-reference rule.

Fix all P0 (dead links, contradictions, duplicated ownership, bad `paths:`) and high-value P1 (tightness, weak cross-refs). Collapse duplicated content into a one-line pointer to the owner. Apply via parallel `Edit` calls.

### Phase 8 — Wire, validate, summarize

- Confirm root `CLAUDE.md` points to `ARCHITECTURE.md` (and any other non-auto-loaded doc), holds no folder→owner map, and stays lean.
- Verify every rule `paths:` entry exists on disk.
- Propose a mechanism to keep `ARCHITECTURE.md` living: a `Stop` hook that reviews each session for architecture drift, or a PR check mapping changed paths to doc sections. Offer; don't install unprompted.
- Report: inventory (every file written, line counts); single-ownership table; corrections caught during drafting; open decisions deferred; anything misplaced or dead you noticed but didn't touch.

---

## Drafting brief template

```
# Format
[Rule frontmatter template with quoted paths: globs, OR "plain markdown CLAUDE.md (no frontmatter)", OR "ARCHITECTURE.md, non-inferable content only"]

# Lens
[The writing lens, inlined — concrete points, not a pointer]

# Scope (single ownership)
[What this file owns; what it must NOT restate because that fact's owner auto-loads]

# Inspect first
[Exact paths to read before writing]

# Content to encode
[Bullet list of facts — verify each against the code]

# Verification mandate
For each bullet: inspect the cited code. If a bullet is wrong, DROP it and report the
correction. Do not soften a wrong bullet — drop and report. Encode only what is true today.

# What NOT to cover
[Facts that auto-load elsewhere — omit them; add a pointer only to a non-auto-loaded doc]

# Length target
~N body lines.

# Action
Inspect → Write → reply with confirmation + any factual deviation found.
```

## Output shape

Line targets per tier (guidelines, not ceilings): root `CLAUDE.md` ~80; nested `CLAUDE.md` ~150; `.claude/rules/*.md` ~100; root `ARCHITECTURE.md` ~60–80. Each file holds:

- Root `CLAUDE.md` — durable repo-wide conventions, decisions, quirks, gotchas; a pointer to `ARCHITECTURE.md`. No folder→owner map — nested files auto-load; a map only goes stale.
- `ARCHITECTURE.md` (root) — system narrative, non-inferable content, living.
- Nested `CLAUDE.md` per subsystem — one subsystem owned per file, self-contained.
- `.claude/rules/*.md` — file/glob-scoped invariants, quoted `paths:`; split if over target.
- Single-ownership table: every load-bearing fact has one owner.
- Every pointer targets a non-auto-loaded doc and resolves; all rule `paths:` exist on disk.

## Pitfalls

- **Cargo-culting the reference repo.** A reference's `scripts/CLAUDE.md` for 10 scripts doesn't justify one when the target has 1 — fold up or skip.
- **Folder map in root.** A directory→owner table re-describes what auto-loads and rots on any rename. Keep durable semantics ("`core/` is shared infra — no feature code"), not a census.
- **Triple-owned facts.** Pick the one owner before drafting; the others stay silent — the owner auto-loads — unless it won't, then a single pointer.
- **Restating the goal in a file's intro.** Cut any "This file documents X" opener.
- **Drafters inflating rule scope.** They add extra files to `paths:` for "completeness" — check the arrays in review.
- **Relying on a rule to govern new files.** Path-scoped rules don't fire on `Write`. If a new-file convention must hold, put it in the directory's `CLAUDE.md` too.
