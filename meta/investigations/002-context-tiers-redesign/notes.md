# Context Tiers Redesign — decision record

Started 2026-06-12. Goal: the right architecture for agent-facing durable docs. **Keystone shipped 2026-06-12.** The model was canonical in `references/context-tiers.md` v2; this file keeps only the decision rationale and what's left.

**Superseded 2026-06-13:** `references/context-tiers.md` is deleted. The model now lives decomposed across three lens skills — `vet-fact` (WORTH / content filter), `place-fact` (PLACE / triggers→homes, loading, pointer rule, retired kinds), and `tighten-instruction` (SHAPE). `durable-docs-update` and `seed-claude-context` reference the lenses by name instead of inlining the appendix; per-tier length targets are now local to `seed-claude-context`. See `2026-06-12-durable-instruction-atoms.md` decision #6.

## Locked decisions

1. **Trigger-based model.** Every fact names its delivery trigger; the trigger picks the home. No nameable trigger → don't write it.

   | Trigger | Home | Delivery |
   |---|---|---|
   | Every session / must always hold | Root CLAUDE.md, unscoped `.claude/rules` | Eager; survives /compact |
   | Agent touches matching file(s) | In-file comment / path-scoped rule / nested CLAUDE.md | On touch; lost on /compact, re-arms on next read |
   | Task type: design/debug across modules | Root ARCHITECTURE.md (~60–80 lines) | Read-steps in pipeline skills (tech-design, explain-deeply); root pointer is a breadcrumb |
   | External SDK/platform work | Skill (bundled with procedure) | Description match; or CLAUDE.md "load skill before X work" |

2. **Module `architecture.md` and `*-quirks.md` die as file kinds.** Content decomposes into path-scoped rules + nested CLAUDE.md + in-file comments.
3. **Skills are NOT a delivery vehicle for repo knowledge** — only external-platform knowledge bundled with procedure (e.g. the OakPostPurchase `post-purchase-ui-extension` skill: fetches Shopify docs, mandates tsc validation).
4. **Rationale capture is one positive line** — "behaviour X — constraint Z." The rejected alternative is the *selection filter* (a fact earns a line only if a tempting alternative exists), never the content; it appears in the clause only when the constraint is a fact about the alternative.
5. **durable-docs-update gains an optional `spec` input** (execute-plan Step 6 passes the spec path) to mine `D-NN` blocks through the belongs-filter. **Done** — only `Status: locked` blocks seed; D-NN↔discovery overlap collapses at seed time (promotion link), and every seed runs the normal classify against current file docs so an already-carried fact is drop/UPDATE, not a fresh ADD.
6. **Shared-schema sync:** `references/context-tiers.md` is source of truth; consumers inline a verbatim copy under `<!-- source: -->` per WRITING-GUIDE. **Done** — both consumers carry the 76-line appendix.

## Why it works (load-bearing insight)

**Write-path integration predicts survival, not the loading mechanism.** OakPostPurchase's abandoned `meta/decisions/` ADR archive (died at 2 files) and its surviving docs were BOTH pointer-loaded — the survivors were the ones a workflow actually wrote. Hence the trigger rule: no fact without a named delivery trigger, no doc without a workflow that writes it. Two structural corollaries, proven during decomposition:
- A feature that interleaves across shared type-folders (`pages/`, `stores/`, `components/`) needs a multi-glob path-scoped rule — nested CLAUDE.md can't reach across folders.
- A clean single-folder module needs only a nested CLAUDE.md — the folder *is* the boundary, and it covers new-file `Write`.

## Shipped (2026-06-12)

- **`references/context-tiers.md` v2** rewritten on the trigger basis; both consumers (`skills/durable-docs-update`, `commands/seed-claude-context`) synced — each carries the verbatim model under `## Context Tiers` + `<!-- source: -->`, model-restating prose collapsed to anchor pointers. Carve-outs folded: the pointer-rule operational test (glob narrower than the obligation's file set) and the `Discovered:`-stamp provenance exemption.
- **Decision #5 (`spec` input)** — durable-docs-update gained the optional `spec` input (mines `Status: locked` `D-NN` blocks through the belongs-filter); execute-plan Step 6 passes the spec path.
- **seed-claude-context gaps pass** — applied C (defer a legacy `architecture.md` to a focused pass), a reference-repo "don't replicate retired kinds" guard, and a length-dedup (point to the appendix); retired-kind footprint minimized to 3 lines (forward guard + reference guard + one-line defer).
- **OakPostPurchase decompositions** (tasks 1–4): funnel-editor + style-editor `architecture.md` → feature-scoped rules; polaris quirks → path-scoped rule; post-purchase extension family → one nested CLAUDE.md; sdk-quirks → folded into the SDK skill. All source `architecture.md`/`*-quirks.md` deleted (git-recoverable). Recurring catch: ~all single-file facts were ALREADY richer comments in source, so decomposition was mostly DELETION (already-owned / duplicate), not relocation.

## Status (agent-skills)

**Closed — seed-claude-context:** A/C nod settled as **C** — the file already defers a legacy `architecture.md` to a focused pass (Phase 2) and never seeds retired kinds. Marginals: #4 (ARCHITECTURE.md weak write-path) → applied a one-line drift caveat on the content rule; #5/#6/#7 → LEAVE (pitfalls pair each prohibition with a positive replacement; ARCHITECTURE.md guidance and the writing-lens↔rationale overlap are distinct altitudes, not restatement).

**Closed — durable-docs-update:** G1/G2 → LEAVE (the change-scoped walk already bounds "any you find"; the `ADD` line is a classifier label, not the home list). G3 → resolved by a Step 3 redesign: the dismiss-defaulted below-cutoff tier became a **rescue band** — `[0.60, 0.70)` candidates get one batched read-only second opinion and present only if it reaches 0.70, `<0.60` drops, Mode-B subagents return rows ≥ 0.60.

**Parked — act only if the symptom appears:**
- Per-session auto-load budget: no accounting of stacked cost (root + nested + matching rules) per file touch.
- Pointer-follow measurement (hook logging ARCHITECTURE.md reads), only if root ARCHITECTURE.md's value is later questioned.

*The agent-skills work is done — only the symptom-gated Parked items remain; the model lives in the three lenses (`vet-fact` / `place-fact` / `tighten-instruction`), see the 2026-06-13 supersede above.*
