---
name: place-fact
description: "Route a kept fact to its durable home by delivery trigger and most-local-wins — comment, CLAUDE.md tier, path-scoped rule, maintained task doc, or workflow. TRIGGER when: user asks 'where should this go', 'which file/rule/home does this belong in', 'is this in the right place', 'should this be a pointer'; placing or re-homing a fact already judged worth keeping."
---

# Place Fact

Primitive: **PLACE** — which durable home does this fact belong in?

## Steps

1. **Name the delivery trigger — the moment a future agent must already hold the fact.** A cross-module topic does not choose a home; the trigger does.
2. **Map the trigger to the narrowest reliable home:**

   | Trigger | Home |
   |---|---|
   | Any repository task; must survive compaction | Root `CLAUDE.md`, or rarely an unscoped rule |
   | Reading or editing one existing mechanism | Comment or docstring beside that mechanism |
   | Reading, editing, or creating files in one cohesive subtree | Nearest ancestor `CLAUDE.md` |
   | Touching one coupling interleaved across unrelated folders | One exact path-scoped rule, or an executable guard |
   | Starting a named product, design, operations, or decision task | A maintained task document reached by an intent pointer |
   | Running a repeatable procedure or external-platform workflow | Skill or named workflow document |

   A repository-internal fact is not a skill: it has no reusable procedure or external-platform trigger.
3. **Make every candidate home earn its existence:**
   - **Root `CLAUDE.md`** — keep only repository-wide, non-derivable instructions and intent routes. A local convention, feature inventory, or folder map does not belong here.
   - **In-file comment** — use for one mechanism's constraint, assumption, or tempting wrong implementation. It travels with the code and needs no loader rule.
   - **Nested `CLAUDE.md`** — use when the folder is a real module boundary and one convention must reach every current and future file in it. A folder alone does not justify a file.
   - **Path-scoped rule** — use for one non-derivable coupling whose files lack one useful common subtree. Name the canonical owner, mirror sites, guard status, and same-change action; never turn the rule into a mirror index or feature census.
   - **Maintained task document** — use only when a distinct task must read a cross-cutting narrative or decision set before work, a pointer delivers it, and a workflow keeps it current. A familiar filename does not create a delivery trigger.
4. **Prefer executable detection over prose coordination.** If a guard fully exposes drift and source-adjacent text explains the constraint, cut the duplicate rule. Keep prose only for the decision, rationale, or same-change obligation the guard cannot deliver.
5. **Check loader behavior against the trigger:**
   - Root `CLAUDE.md` and unscoped rules load eagerly and re-inject after compaction.
   - Nested `CLAUDE.md` and path-scoped rules load on matching reads and re-arm after compaction on the next read.
   - A new-file write may not trigger a path rule; put a convention that governs not-yet-written files in the directory's `CLAUDE.md`.
   - Store each file-matching rule once in `.claude/rules/`, with quoted `paths:` globs; ensure every supported agent has an equivalent delivery path.
6. **Emit a pointer only when its target will not already load on the reader's trigger and the reader must know it before work:**
   - Root or nested `CLAUDE.md` → a maintained task document or skill when the task starts outside that target.
   - `CLAUDE.md` → a narrower rule only for a cross-layer obligation or the new-file-write gap; otherwise let the rule fire or widen its paths.
   - Never point one `CLAUDE.md` to another auto-loading `CLAUDE.md`, and never maintain a folder-to-owner map.
7. **Confirm one owner and one write path.** If two homes tempt you, split the fact or correct the trigger; do not restate it.
