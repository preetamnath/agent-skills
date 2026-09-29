# Durable-Instruction Primitives — skill-family redesign

Started 2026-06-12. Decomposes what "write a durable instruction" means into primitives, then repackages the `tighten-*` / `durable-docs-update` / `seed-claude-context` family around them. Sibling to `2026-06-12-context-tiers-redesign.md` (which owns the placement model itself).

**Status: complete (2026-06-12/13).** All units shipped — lenses `vet-fact` / `place-fact` / `tighten-instruction`, applier `refine-file`, workflows `durable-docs-update` + `seed-claude-context` rewired to the lenses, `context-tiers.md` retired. Deferred: re-home / prune triggers (see Open gaps).

## The 3 primitives

"Durable" is not one test. It is three distinct primitives, evaluated in order — **WORTH gates → PLACE routes → SHAPE writes**. Not orthogonal: a precedence binds them, and two shared sub-properties (write-path, redundancy) couple WORTH↔PLACE.

| Primitive | Test | Nature | Lens skill |
|---|---|---|---|
| **WORTH** | Should this fact exist at all? A future agent gets the wrong answer without it; not derivable from code/ls/lint; not setup; not a breadcrumb. | Mostly intrinsic — single-file-visible facts judge alone; coupling/dedup worth needs the other file(s) | `vet-fact` |
| **PLACE** | Which home? Trigger→home, most-local-wins; only homes a workflow maintains ("Survives"/write-path folds in here). | Routing judges from one file (trigger→home); only dedup + executing a move are reach-bound — execution policy is the caller's, not the primitive (§7) | `place-fact` |
| **SHAPE** | How to write the line: one positive line that reads cold — imperative (trigger+action) or declarative (fact). | Intrinsic — judged on the line alone | `tighten-instruction` |

"Survives" is not a 4th primitive — it is a constraint *on* PLACE (route only to write-path-backed homes).

## The load-bearing axis: context-span gradient

```
            INTRINSIC (one line / one file)     CROSS-FILE (needs many files)
  WORTH     ✓  should it exist?
  SHAPE     ✓  how to write it
  PLACE                                          ✓  which home
```

A gradient, not a binary: **SHAPE (the line) ⊂ WORTH (the fact + any coupled/duplicate files) ⊂ PLACE (the fact + any homes it must dedup against or move between).** Cheaper primitives run at smaller scope — the payoff driving the redraw. The gradient describes *reach, not resolvability* — execution policy is a *caller* constraint, not a property of PLACE (see §7).

## Refinements (stress-test, 3 agents)

1. **WORTH is corpus-relative, not purely intrinsic.** A single-file pass catches single-file-visible WORTH only; coupling + dedup ("a fact a rule already carries is not a fresh ADD") need the other file(s).
2. **Freshness = WORTH over time.** UPDATE/TRIM/DELETE are WORTH re-judged against drifted code; provenance stamps are the freshness anchor. Not a 4th primitive.

## Final architecture

Three layers — **lenses → applier → workflows** — and every unit records the primitive(s) it embodies (one-line `Primitive:` note in its SKILL.md; authoritative map here).

| Layer | Skill | Primitive(s) | Scope | Status |
|---|---|---|---|---|
| Lens | `tighten-instruction` | SHAPE | one line | exists |
| Lens | `vet-fact` | WORTH | one fact | exists |
| Lens | `place-fact` | PLACE | fact → home (judges from 1 file; execution policy is the caller's — §7) | exists |
| Applier | `tighten-file` | SHAPE | one file | exists, untouched |
| Applier | `refine-file` | any subset of {SHAPE, WORTH, PLACE} | one file (skill file *or* durable doc) | exists (shipped 2026-06-12) — coexists with `tighten-file` |
| Workflow | `durable-docs-update` | WORTH+PLACE+SHAPE | change-set | references the lenses |
| Workflow | `seed-claude-context` | WORTH+PLACE+SHAPE | whole repo | references the lenses |

- **Lenses** are read-and-apply primitives invoked on demand (like `tighten-instruction` today). Referenced by name, never paraphrased.
- **`refine-file`** composes a chosen lens subset over one file. Operand-agnostic: a skill file takes WORTH+SHAPE (PLACE doesn't apply — no tier-homes); a durable doc can take all three (PLACE judges the home; on a move, `refine-file` executes it on user approval — write the target, remove from the source — or defers it as a flag for a `durable-docs-update` batch; see §7 supersede 2026-06-13).
- **Workflows** are where PLACE actually resolves (cross-file); they reference the three lenses instead of inlining the model.
- **Composition glue** (lives in appliers/workflows, written once): apply WORTH→PLACE→SHAPE; a rationale line that passed WORTH is a *constraint*, exempt from SHAPE's cut-the-why.

## Locked decisions (2026-06-12)

*Locks are provisional, not permanent — each is the current best call, held until evidence reopens it, and revisable as the discussion evolves. When one is reopened, record the supersede (date + reason) rather than silently overwriting, so the trail stays intact (see §7 for the first instance).*

1. **Primitives are lenses, not modes.** Reject one `durable-instruction` skill with modes — its three combos span three WRITING-GUIDE archetypes (lens / file-artifact / orchestrator) plus a hidden scope axis; one SKILL.md can't be all three.
2. **Only 3 of 7 {W,P,S} subsets are real operations:** S, W+S, W+P+S. The other four are degenerate (e.g. PLACE without WORTH = filing junk). Expose a fixed menu, never a free-form combo selector.
3. **Vary lenses within a fixed scope = fine (that's `refine-file`); collapsing scopes into one skill = the rejected anti-pattern.** Scope = separate units; lenses = composable menu.
4. **Names:** `tighten-instruction` (keep) / `vet-fact` / `place-fact` / `refine-file`. `-fact` over `-instruction` because the model judges/routes *facts* (gotchas, couplings, rationale); only SHAPE acts on an instruction-line. The family coheres on the shared verb-register + lens-shell, not a shared object. (`vet-fact` 0.78, `place-fact` 0.82; runner-ups `justify-fact` / `route-fact`.) *(Re-confirmed 2026-06-12 after SHAPE broadened to declarative facts: SHAPE's object is still the *line* — now command or fact — not the fact, so `-fact` stays wrong; `tighten-line` is the only rename worth weighing if the family grows, never `-fact`.)*
5. **`refine-file` is new and coexists with `tighten-file`** (no rename; additive, low blast radius). It functionally supersedes `tighten-file`, but both stand for now.
6. **`durable-docs-update` + `seed-claude-context` reference the lenses** (single source of truth) instead of inlining `context-tiers.md`. Consequence: **`context-tiers.md` dissolves** — its content filter → `vet-fact`, its triggers→homes / pointer rule / loading mechanics → `place-fact`. Reference-first, with a thin inline fallback (the repo's uninstalled-skill hedge, as `seed-claude-context` already does for `tighten-instruction`).

7. **PLACE flag-only is a combiner constraint, not a primitive property** *(supersedes the "PLACE is cross-file / can only flag at single-file scope" framing in §"The load-bearing axis" and the tables above)*. `place-fact`'s routing judgment (trigger→home) resolves from a single file — Steps 1–6 read the trigger and directory shape, not the candidate home files. Only dedup ("no home restates another") and executing a move need other files in reach. So flag-only belongs to the single-file *combiner* (`refine-file`), which downgrades a move to a flag and routes it to `durable-docs-update`; standalone or inside a multi-file workflow, `place-fact` resolves the move itself (remove from old home, add to new — one fact, one home). **Consequence:** `place-fact` Step 8 removed and frontmatter "flag-only on a single file" dropped (2026-06-12). *(Reopened on the evidence that trigger→home routing needs no second file; the gradient `SHAPE ⊂ WORTH ⊂ PLACE` describes reach, not a definition that makes PLACE un-resolvable at single-file scope.)*

   **Superseded in part (2026-06-13, reopened by the user): the combiner no longer *hard*-flags.** `refine-file` **executes a move on user approval** (open the target home, shape the fact for it, add it, remove it from the source; if the target already carries it, that's a CUT from the source) and only *defers* it as a flag when the user declines — `durable-docs-update` is a *suggested batch executor*, not a mandatory redirect. The reason: the agent running `refine-file` can write the target file, so a blanket "never execute / route to `durable-docs-update`" dressed a self-imposed *audit focus* up as a *capability limit*. The single named file is `refine-file`'s **audit scope, not a sandbox**; a move is the lone action that writes elsewhere, gated by approval. **What still holds (the durable principle):** *execution policy belongs to the **caller**, never the lens.* `place-fact` stays execution-neutral (judges the home, says nothing about moving); each caller layers its own policy — a bare chat and `place-fact` inherit the agent's full scope, `refine-file` adds "audit one file, relocate on approval," `durable-docs-update` batch-executes across a change-set.

## Use cases → which unit fires

| You're doing | Lenses | Unit |
|---|---|---|
| tighten one line | SHAPE | `tighten-instruction` |
| shape a whole file | SHAPE | `tighten-file` or `refine-file` |
| worth + shape a skill file | WORTH+SHAPE | `refine-file` |
| worth + shape (+ flag place) a durable doc | WORTH+SHAPE(+PLACE) | `refine-file` |
| sync docs after a task | WORTH+PLACE+SHAPE | `durable-docs-update` |
| seed a new repo | WORTH+PLACE+SHAPE | `seed-claude-context` |

The single-fact / single-file WORTH-bearing middle (audit one skill file or doc) was the empty cell `refine-file` fills.

## Open gaps (deferred — act when they bite)

- **No trigger for pure re-home (PLACE-only) or pure prune (WORTH-only).** Re-evaluated 2026-06-13 → **leave parked** (symptom-gated; capability already exists — `refine-file` does CUT/MOVE over one named file, `durable-docs-update` over a change-set; both example phrasings are already semantically covered by `refine-file`'s description). If it ever bites, the cheap fix is a one-line trigger-phrasing addition to **`refine-file`** — *not* `durable-docs-update`, whose change-scoped "after finishing work" gate the phrasing fights and which has no scope source for a bare "prune this file." (Supersedes the earlier "route into `durable-docs-update`'s MOVE/TRIM" suggestion, written before §7's `refine-file` MOVE-on-approval supersede made it the natural single-file home.)

*(The earlier execution-policy gap is resolved — execution policy belongs to the caller, never the lens; `refine-file` executes a move on approval else defers a flag, `place-fact` stays execution-neutral. Full rationale in §7.)*

## Design invariants (why the family is shaped this way)

- **Keep the 3-lens split** — don't merge `vet-fact` + `tighten-instruction`. SHAPE has ≥4 standalone non-fact callers (`tighten-file`, `durable-docs-update`, `seed-claude-context`, `memory-prune`); merging would force a WORTH gate onto pure tightening. WORTH is a narrow fact-gate feeding the broader SHAPE, not a co-equal half.
- **Combiner owns composition; lenses never chain.** Appliers/workflows apply WORTH→PLACE→SHAPE; the lenses never call each other. `tighten-instruction` stays WORTH-free; `vet-fact` emits the fact's category (gotcha/coupling/convention/rationale/pointer); `place-fact` stays execution-neutral.
- **SHAPE is fact-complete.** `tighten-instruction` Step 4 shapes declarative fact-lines too, so a kept fact isn't gutted — only rationale needs the combiner's cut-the-why exemption (`rationale` = constraint).

## Build record

- **Shipped 2026-06-12:** lenses `vet-fact` (WORTH) + `place-fact` (PLACE) extracted from `context-tiers.md`; applier `refine-file` (composes a chosen lens subset over one file).
- **Shipped 2026-06-13:** `durable-docs-update` + `seed-claude-context` rewired to reference the lenses by name (thin uninstalled-skill fallback); `context-tiers.md` deleted — content filter → `vet-fact`, placement model → `place-fact`, retired-kinds → `place-fact`, per-tier length targets → local to `seed-claude-context`.
- **Verified 2026-06-13:** post-rewire evaluation (3 parallel agents) — both workflows coherent end-to-end without the appendix, lens calls correct, all old-model elements migrated intact. One fix applied: `durable-docs-update` SHAPE gist broadened from "trigger + action" to instruction-or-fact shape, matching `tighten-instruction` Step 4 and the skill's own fact-shaped example rows.
- **Re-evaluated 2026-06-13 (no change):** `memory-prune` panel-reviewed for a WORTH/PLACE lens-rewire → **stays SHAPE-only** (its Rubric is a promotion-triage superset — adds COMMAND home + DELETE/TRIM/NONE dispositions + promote/KEEP/STALE verdicts the lenses don't model; referencing them would bolt-on, not replace, recreating drift). Confirms invariant: `memory-prune` is a SHAPE caller, not a WORTH/PLACE consumer.
- **Deferred:** re-home / prune triggers (Open gaps — re-evaluated, parked).
