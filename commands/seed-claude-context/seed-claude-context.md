---
description: Seed a layered Claude-context surface across the current repo — root CLAUDE.md, per-subsystem nested CLAUDE.md files, and exact path-scoped .claude/rules/*.md. Maps the repo with parallel agents, plans placement and single ownership, drafts in waves, tightens, fact-checks the load-bearing instructions, and reviews for coherence. Works with or without a reference repo. Use when a repo has no structured agent context or only a single sprawling CLAUDE.md.
---

# Seed Claude Context

Primitive: **WORTH + PLACE + SHAPE** over a whole repo.

Roll out a layered Claude-context surface across the current repo so future agents stop re-mapping it each session. You orchestrate: dispatch parallel subagents per phase, hold the task list, own every decision checkpoint.

## When to use

- The target repo has no structured agent context, or only a single sprawling root `CLAUDE.md`.
- It has at least one non-obvious subsystem or one file-level invariant worth documenting.

Skip for a single-purpose repo of a few files — write one root `CLAUDE.md` directly.

## Inputs

1. **Target repo** — defaults to the current working directory.
2. **Reference repo** (optional) — a repo whose context layering you trust, to mine for patterns. Absent one, derive structure from the placement lens below.
3. **Decision records** (optional) — authoritative rationale sources: ADR/decision directories, a `spec.md` with `## Decisions` blocks, design documents, or known invariants. Mine them in Phase 1, verify each fact, then let `place-fact` choose its delivered owner.
4. **Transient sources** (optional) — build-state files slated for retirement, such as `CONTEXT.md` or an active `plan.md`, even when auto-loaded. Mine them like decision records, but never reconcile, rewrite, or delete them; list each as a Phase-2 non-proposal.

## Placement lens

Invoke two lens skills through every phase — reference each by name, don't paraphrase; if one isn't installed, fall back to its gist:
- **`place-fact`** (PLACE) — each fact's delivery trigger picks its home; one fact, one home; no home restates another. Owns the triggers→homes table, loading mechanics, and pointer rule.
- **`vet-fact`** (WORTH) — seed a fact only if a future agent would get the wrong answer without it.

Two command-specific notes:
- If the harness cannot load `.claude/rules/`, fold each file-scoped invariant into the nearest `CLAUDE.md` instead.
- Do not seed a catch-all narrative or quirks document. Route each fact by its delivery trigger.

## Rule archetypes

The body shapes that earn a rule (templates, not mandates):

- **Cross-boundary coupling** — one fact re-implemented at sites that cannot share an owner. Name the canonical owner, every mirror, guard status, and same-change action; keep intentional asymmetry in the same rule.
- **Single footgun** — one high-cost invariant across the matching paths plus the one correct pattern.
- **Shared test policy** — one non-derivable test obligation that every matching test file must follow.

## Cross-reference rule

Follow `place-fact`'s pointer rule and record each justified pointer in Phase 2's ownership table. Do not restate an auto-loading target.

## Maintained task documents

Product, design, operations, or decision documents are not automatic instruction tiers. Preserve or propose one only when a named task needs its cross-cutting context before work, a root or workflow instruction names it, and a workflow keeps it current. Keep only non-derivable narrative, decisions, and rationale; never a file tree, feature inventory, mirror index, schema census, or operational procedure owned elsewhere.

## Writing lens

If the `tighten-instruction` skill is installed, use it. Otherwise apply this inline:
- Each line = trigger + action ("Use X for Y." / "When X, do Y." / "Do X — Y breaks.").
- Cut any line whose job is to restate the goal, hedge, or explain why — unless the why IS the constraint.
- Lead with the rule, not the rationale. No emoji, no "IMPORTANT:", no marketing prose.
- Cite code by symbol name (function, constant, docstring heading) — a line number is a bonus, never the anchor. Bare line numbers rot with every edit; names stay greppable.
- Test cold: read each line out of context. If a future agent can't act on it, retighten.
- Keep every file within its per-file length target.
- A fact `vet-fact` keeps whose value is explanatory — a hard-won trap, a why-this-breaks narrative — survives tightening even when it won't compress to one trigger+action line. Tighten its wording, never its substance.

---

## Workflow

### Phase 1 — Map the repo (parallel)

Size the mapping pool to the repo: 2–10 read-only agents (`Explore`, or `general-purpose` where unavailable) running simultaneously — one per major subtree on a large repo, a couple on a small one. Each returns a structured, self-contained report; none proposes file placement yet. Partition by:

- **Structure & conventions** (scale to repo size). Per-directory purpose, conventions, coupling, gotchas; framework and versions; build/test/lint commands; inventory of existing `CLAUDE.md` files, path rules, and root-routed maintained task documents.
- **System flows** (one or more, split by subsystem). Entry points; data and control flow; subsystem boundaries; cross-cutting concerns; key decisions; hot spots where a fresh agent would make mistakes. Return fact candidates with the files and task triggers they constrain; do not choose homes.
- **Reference repo** (one agent, only if one is supplied). How it splits content by delivery trigger and what earns a comment, rule, nested instruction, or maintained task document. Never copy a file kind merely because the reference uses it.
- **Decision records** (one agent, only if supplied). Mine each source for locked decisions (the choice + its rationale) and known invariants; return each as a seed mapped to the subsystem it constrains. These are high-priority candidates — verify each still holds against the code, and drop any the code has outgrown.

### Phase 2 — Plan placement + ownership

Combine the reports into two tables.

**Placement:**

| # | Path | Home | Owns | Does NOT cover | Confidence |

**Single ownership:**

| Fact / invariant | Sole owner | Inbound pointer (only if owner won't auto-load) |

Below them: explicit non-proposals — directories considered and skipped, one-line reason each.

Place each Phase-1 seed as a high-priority row through `place-fact`, preserving non-derivable rationale. A seed already documented correctly is a keep, not a duplicate.

Reconcile existing context files in the same table: mark each keep, merge, or rewrite. A file already present and correct is a keep — Phase 5 drafts only new and rewrite rows, so a re-run converges instead of overwriting good files. A declared transient source (Inputs §4) is never a reconcile row — mine it, list it as a non-proposal, leave it untouched. If a sprawling root `CLAUDE.md` exists, carve its facts into delivered owners without dropping any. Record an unreferenced catch-all document as a deferred `refine-file` candidate; do not reconcile, draft from, or delete it in this command.

### Phase 3 — Sanity-check the plan (parallel)

Dispatch `sanity-checker` agents with non-overlapping focus:
- **Granularity & necessity.** Which proposed files are too thin, duplicative, or just paraphrase the root? Which are missing?
- **Coverage & staleness.** For each hot spot, which file owns it? Where is duplication risk? Which file will go stale first?
- **Boundary.** Does each proposed home match its delivery trigger, with single ownership held?

Synthesize their P0/P1 findings into one table.

### Phase 4 — Clarify, confirm, build task list

Apply consensus findings. Bundle load-bearing decisions into one `AskUserQuestion` (≤4 questions): naming conflicts, borderline keep/drop files, disputed delivery triggers, and anything agents flagged ambiguous. Name any file you propose dropping or adding so the user can push back.

Present the revised placement + ownership tables for confirmation. Then `TaskCreate` one task per file, plus tasks for tighten pass, fact-check + coherence review, and final summary.

### Phase 5 — Draft in waves (parallel)

A pointer target must exist before the file that points at it:
- **Wave 1** — all new or rewritten path rules and maintained task documents.
- **Wave 2** — all `CLAUDE.md` files in parallel; they may point to Wave-1 task documents but never delegate to one another.

Draft only the rows the plan marks new or rewrite; leave keeps untouched. Each drafter is a `general-purpose` subagent given a self-contained brief (template below). Accept drafter corrections over your brief.

If a `Write` under `.claude/rules/` is blocked as self-modification, write a frontmatter-only placeholder yourself, then re-dispatch the drafter to fill the body.

### Phase 6 — Tighten every file

If the `tighten-file` skill is installed, run it on the generated files. Otherwise apply the writing lens above at three levels per file: whole file (does it earn its existence?), section (does each heading earn its place?), line (trigger + action, cold-read test). Flag any file over its length target by >30% as a tightness fix, not polish.

### Phase 7 — Verify facts + review coherence (parallel) + fix

Two read-only lanes run in parallel, then one fix pass merges them.

**Lane 1 — Fact-check load-bearing instructions (`triage`).** Extract each discrete claim from root `CLAUDE.md`, each maintained task document this run changed, and each rule's central invariant. Pair every claim with the code paths it describes. Run `triage` once: `consider` keeps a true, useful claim; `skip` corrects or drops a wrong, derivable, or trivial claim. Nested `CLAUDE.md` files are spot-checked in Lane 2. If `triage` is unavailable, fan out clean-room checkers over 1–3 claims each.

**Lane 2 — Coherence audit (`reviewer`).** Dispatch `reviewer` agents:
- **Rules audit.** Every `paths:` glob is quoted and resolves on disk; body is tight and scoped; the new-file-`Write` caveat is acceptable for this rule's purpose.
- **CLAUDE.md audit.** Spot-check ≥5 claims in each nested file against source (root `CLAUDE.md` is Lane 1's job); scope discipline; length sane; no folder→owner map; every pointer targets a non-auto-loaded doc and resolves.
- **Maintained task-document audit.** Each file has a named task trigger, a justified inbound pointer, a write path, and only non-derivable context; no file tree, feature inventory, mirror index, schema census, or displaced procedure.
- **Cross-file consistency.** One owner per fact (use the ownership table); no contradictions; no CLAUDE→CLAUDE delegation or redundant pointers; remaining pointers resolve and are justified by the cross-reference rule.

**Fix.** Merge both lanes. Fix all P0 (dead links, contradictions, duplicated ownership, bad `paths:`, a triaged `skip`) and high-value P1 (tightness, weak cross-refs). Collapse duplicated content into a one-line pointer to the owner. Apply via parallel `Edit` calls.

### Phase 8 — Wire, validate, summarize

- Confirm each root pointer names the task that requires its non-auto-loading target; keep the root free of folder→owner maps.
- Verify every rule `paths:` entry exists on disk.
- Report: inventory (every file written, line counts); single-ownership table; corrections caught during drafting; facts the Phase-7 fact-check dropped or corrected; open decisions deferred; anything misplaced or dead you noticed but didn't touch.

---

## Drafting brief template

```
# Format
[Rule frontmatter with quoted paths, plain `CLAUDE.md`, or a maintained task document with its purpose and write path]

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

Line targets per instruction tier (guidelines, not ceilings): root `CLAUDE.md` ~80; nested `CLAUDE.md` ~150; `.claude/rules/*.md` ~100. Each file holds:

- Root `CLAUDE.md` — durable repository-wide conventions and read-when-relevant routes. No folder→owner map; nested instructions auto-load.
- Nested `CLAUDE.md` per subsystem — one subsystem owned per file, self-contained. Shapes that earn their lines: a layer-import table (Layer | Holds | Imports, never import upward); a "deliberately looks wrong" note (why the apparent debt is intentional + the revisit condition); a "Not indexed:" line naming non-canonical subdirs (archive/, personal/) so agents don't treat stale files as truth.
- `.claude/rules/*.md` — one exact file/glob-scoped invariant, quoted `paths:`, guard status, and same-change action; split unrelated facts.
- Maintained task documents — optional, non-tier context with a named task trigger, an explicit inbound pointer, and a workflow-backed write path.
- Single-ownership table: every load-bearing fact has one owner.
- Every pointer targets a non-auto-loaded doc and resolves; all rule `paths:` exist on disk.

## Pitfalls

- **Cargo-culting the reference repo.** A reference's `scripts/CLAUDE.md` for 10 scripts doesn't justify one when the target has 1 — fold up or skip.
- **Folder map in root.** A directory→owner table re-describes what auto-loads and rots on any rename. Keep durable semantics ("`core/` is shared infra — no feature code"), not a census.
- **Triple-owned facts.** Pick the one owner before drafting; the others stay silent — the owner auto-loads — unless it won't, then a single pointer.
- **Restating the goal in a file's intro.** Cut any "This file documents X" opener.
- **Drafters inflating rule scope.** They add extra files to `paths:` for "completeness" — check the arrays in review.
- **Relying on a rule to govern new files.** Path-scoped rules don't fire on `Write`. If a new-file convention must hold, put it in the directory's `CLAUDE.md` too.
