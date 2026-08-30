# Durable documentation placement and regrowth — investigation

**Date:** 2026-08-28
**Status:** Policy decisions complete; skill codification in progress. This is dated evidence, not a current instruction owner.

## Question

How should reusable agent skills decide whether a fact belongs in a code comment, root or nested `CLAUDE.md`, a path-scoped rule, a maintained project document, a workflow, or nowhere—and how should the system prevent documentation from becoming bloated again?

## Evidence

- AgentChatDeck thread `6b5fe204-fdd8-40d8-b218-d4065424b409`, 2026-08-28 UTC.
- AgentChatDeck documentation commits from `e8c60e9` through `4ed9e68`, including `meta/investigations/001-documentation-system-audit/notes.md`.
- Agent Skills commits `03246bf` through `0e2eeff` and the current `vet-fact`, `place-fact`, `durable-docs-update`, `memory-prune`, `refine-file`, `seed-claude-context`, writing guide, and root `CLAUDE.md` guide.
- Two independent Sol analyses: one reconstructed the cleanup empirically; one reviewed the policy architecture. The parent rechecked their material claims against the transcript, diffs, and current files.

## Decision outcome — 2026-08-30

The analysis below preserves the original evidence and recommendations. These outcomes govern where the walk changed them:

1. **Canonical delivery:** keep one canonical owner and write path. Prefer relative symlinks, native imports, or generated views; use automatically guarded copies only when derivation cannot work. Use `AGENTS.md` as the canonical instruction file and deliver `CLAUDE.md` as a symlink or native import where supported.
2. **Policy shape:** keep WORTH → PLACE → SHAPE. `place-fact` owns trigger, boundary, canonical owner, scope, delivery, upkeep, and retirement; active state and dated evidence remain outside current-guidance WORTH.
3. **Destructive edits:** retain the existing confidence gate for MOVE and DELETE; the proposed separate proof gate was not adopted.
4. **Guides:** keep guides independent. Skills carry their essential operating rules and do not depend on loading a guide.
5. **Anti-regrowth:** choose boundaries before existing files. Create, reuse, or split by trigger and scope; judge bloat by duplicated ownership, mixed scopes, broken routes, and unnecessary eager loading, not file count.
6. **Meta taxonomy:** rename Agent Skills `meta/discussions/` to `meta/investigations/` after the skill updates.

Implementation progress:

- **Done:** `place-fact` now owns the complete placement contract; committed as `b3a2cec`.
- **Done:** `vet-fact` now limits WORTH to current guidance, keeps state/evidence in the separate lane, and was committed as `ba833a6`.
- **Done:** `durable-docs-update` now uses canonical `AGENTS.md`, boundary-first placement, separate state/evidence handling, whole-document coherence reads, and non-quota growth signals; committed as `ad1bbd8`.
- **Done:** `refine-file` now audits placement across all current-guidance instruction types, loads only its selected lenses, consumes the full placement contract for MOVE, and keeps state/evidence in their separate lane; committed as `c099b48`.
- **Done:** `memory-prune` now classifies memory-native material before current-guidance WORTH, routes state/evidence through their separate lane, consumes the full placement contract, preserves partial-source content, and requires confirmation before mutation; committed as `da50a3e`.
- **Ready for user review:** `seed-claude-context` now plans one complete placement contract per artifact, uses canonical `AGENTS.md` with derived provider views, separates state/evidence, removes archetype and line-target admission shortcuts, shapes every changed artifact, and reports growth as a review signal.
- **Pending:** align the remaining guides and direct consumers one file at a time.
- **Last:** migrate AgentChatDeck instruction and project-skill mirrors to the accepted symlink-first layout.

## Original analysis answer

The current **WORTH → PLACE → SHAPE** decomposition is the correct core, but PLACE is underspecified. A future agent can usually choose a plausible home, but it cannot always choose the one canonical owner, distinguish that owner from required delivery mirrors, state the artifact's lifecycle and removal condition, or route dated evidence without treating it as current guidance.

Prevent regrowth by extending the existing lenses rather than adding another doctrine file. Every net-new current fact should name its wrong-answer risk, delivery trigger, canonical owner, scope, required mirrors, guard/update path, and removal trigger. Every MOVE or DELETE should cite direct evidence and cold-read both the source and destination. Growth should trigger explanation and focused review, not fail a universal line quota.

## What today proved

File count is not bloat. AgentChatDeck's instruction surface grew from 49 to 71 files as facts moved closer to their triggers, while total instruction lines fell from 1,320 to 951. Root and nested `CLAUDE.md` content fell from 833 to 410 lines; path-rule content grew from 473 to 522 lines because broad eager guidance became narrow conditional guidance.

| Surface | Start of 2026-08-28 | End of audit | What happened |
|---|---:|---:|---|
| Root `CLAUDE.md` | 96 lines | 36 lines | Became a repository briefing, task router, verification entry point, and rare universal safeguard layer. |
| `meta/ARCHITECTURE.md` | 303 | removed | Its last valid facts all had narrower delivery homes. |
| `meta/PRODUCT.md` | 78 | 8 | Kept four reversal-preventing product decisions with a selective task trigger. |
| `meta/DESIGN.md` | 285 | 35 | Kept only context needed for material visual work. |
| `meta/GLOSSARY.md` | 69 | removed | Remaining terms were already owned beside their mechanisms. |
| `meta/OPERATIONS.md` + `meta/SERVERS.md` | 360 | removed | Replaced by smaller operator files split by task trigger. |
| Investigation notes | 247 | 50 | Closed progress history into outcome, decisions, and remaining guards. |
| Project-authored skills | 357 | 121 | Kept workflow and safety boundaries; removed live CLI syntax, schemas, flags, defaults, and inventories. |

The cleanup exposed six recurring causes:

1. **Derivable prose.** Documents repeated code, tests, schemas, file layouts, defaults, and command help.
2. **Topic-owned documents.** A cross-module topic was assumed to need an architecture file; a folder was assumed to need a `CLAUDE.md`; related operations were assumed to need one operations monolith.
3. **Missing narrowest-home test.** The thread first proposed a defensible 25-line architecture file. Event `276178` added “no narrower delivery home,” after which the file had no remaining owner role and commit `2fe20cf` removed it.
4. **Indexes that copied their entries.** The broad cross-boundary mirror index repeated rules that already loaded on their paths. Splitting it was only an intermediate step: rules with complete guards or local owners were then deleted in `e33c1da` and `f4c7eb8`.
5. **Live-interface duplication.** Project skills copied CLI syntax and executable behavior instead of routing readers to live help and keeping only non-discoverable workflow branches.
6. **Records without closure.** Investigation notes retained interim conclusions, completed agenda items, stale hashes, and warnings after current owners had absorbed their conclusions.

## What survives

The current skills already supply the right foundation: `vet-fact` asks the wrong-answer question; `place-fact` routes by delivery trigger, rejects folder symmetry and cross-module scope as owners, prefers executable guards, and handles the new-file gap; the root guide has a strong admission and cold-read procedure; `durable-docs-update` remains change-scoped; and `refine-file` proves MOVE targets cold.

Five principles survived every cleanup revision:

1. Keep only non-derivable facts that prevent a likely wrong answer.
2. Deliver each fact at the narrowest trigger that needs it.
3. Prefer generation, derivation, or an executable guard over prose coordination.
4. Keep rationale only when it blocks a tempting wrong reversal.
5. Cold-read the complete resulting artifact, not only changed lines.

## Gaps in the current policy

| Gap | Evidence and consequence |
|---|---|
| PLACE is incomplete | `place-fact` handles trigger and scope, but canonical ownership, mirrors, lifecycle, guards, update paths, and removal conditions are uneven or scattered across the root guide and repository-specific `meta/` rules. |
| “One fact, one home” is too absolute | The valid invariant is **one canonical owner, with only guarded delivery mirrors required by a different loader or trigger**. AgentChatDeck's byte-identical provider skill copies and code-owned contracts delivered through path rules are legitimate mirrors, not competing authors. |
| Root versus unscoped rule is ambiguous | “Root `CLAUDE.md`, or rarely an unscoped rule” does not define the rare case. Root should own portable repository-wide guidance; an unscoped provider rule should only mirror it when that provider needs another delivery path. |
| Dated evidence has no clean lane | `vet-fact` correctly cuts history from current instructions, while the root guide recognizes dated research and investigations. Raw evidence needs a separate non-auto-loaded lane that closes by promoting accepted conclusions and remaining work. |
| The root guide is outside the skill execution path | `durable-docs-update` loads lens skills, not repository guides. Stable admission rules must live in `place-fact`, or root-file work must invoke an installed skill/reference that carries them. |
| Confidence alone cannot prove destructive edits | `durable-docs-update` applies MOVE and DELETE at the same self-scored `0.75` gate as wording edits. Today's audit revised high-confidence placements after stricter source checks, so destructive actions need direct evidence and stronger proof. |
| Existing-file cold reads are inconsistent | `refine-file` reads the named file and MOVE targets cold; `durable-docs-update` reserves full tidy passes for new documents. Every changed durable artifact needs a whole-file coherence and duplication read. |
| Creation and maintenance can drift | `seed-claude-context` retains separate archetypes and line targets, while `memory-prune`, `refine-file`, `handoff`, and the writing guide restate parts of placement. All must consume one placement contract. |

## Proposed policy: two lanes, one canonical placement contract

### Lane A — current guidance

Keep the existing primitive order, but make PLACE answer the complete placement contract:

1. **WORTH — wrong-answer risk.** What specifically would a capable future agent get wrong without this fact? If the answer is “it would need to look it up,” cut it; lookup cost alone does not justify current guidance.
2. **DELIVERY TRIGGER.** At what moment must the agent already know it: any task, one mechanism, a subtree including future files, an exact distributed path set, a named task, or a repeatable procedure?
3. **CANONICAL OWNER AND SCOPE.** Which narrowest source is allowed to change the fact? Which paths, subtree, task, or procedure does it govern?
4. **DELIVERY MIRRORS.** Does another supported loader need an equivalent copy or pointer? If yes, name the sync mechanism and keep one canonical author.
5. **LIFECYCLE AND GUARD.** What keeps the fact current, what detects drift, and what event removes or re-homes it?
6. **SHAPE.** Write the smallest cold-readable instruction or fact that preserves the constraint.

### Lane B — state and evidence

Do not force these records through the current-instruction WORTH gate:

- **Active state** records what is underway or queued. A workflow owns updates and retirement.
- **Dated evidence** records a scoped question, sources, provisional findings, decisions reached, and open questions. It is not current truth and should not auto-load for ordinary work.
- **Closure** promotes accepted conclusions to one current owner, routes unfinished work to the active-state owner, removes stale progress prose, and retains only unique evidence or rationale worth revisiting.

This separation prevents “historical breadcrumbs are bad” from becoming “delete the evidence,” while also preventing investigation diaries from becoming permanent instruction layers.

## Artifact admission and removal tests

| Artifact | Admit only when | Remove or re-home when |
|---|---|---|
| Code comment or docstring | One mechanism needs a non-derivable constraint, assumption, coupling, or tempting-wrong-path warning exactly where it is edited. | The mechanism disappears, code or a guard expresses the fact, or another owner now delivers it at the same trigger. |
| Root `CLAUDE.md` | Any repository task may need the vocabulary, safeguard, verification entry point, or read-when-relevant route. | The fact becomes local, derivable, historical, task-specific, or owned by an auto-loading narrower source. |
| Nested `CLAUDE.md` | A real subtree boundary has a rule that applies to every current and future file below it. | The boundary disappears, the rule applies only to a subset, or local code/rules fully carry it. |
| Path-scoped rule | One distributed coupling has no useful common subtree; the rule can name complete affected paths, canonical owner, mirrors, guard status, and same-change action. | The coupling localizes or disappears, or an executable guard plus source-adjacent rationale fully replaces prose coordination. |
| Maintained current document | A named product, design, operations, or decision task needs cross-cutting context before work; an instruction routes to it and a workflow updates it. | The task trigger, inbound route, or maintenance path disappears; facts can be decomposed into narrower owners. |
| Repository workflow | A repeatable local multi-step procedure must be run on demand. | It becomes one step, obsolete, or duplicates a reusable skill. |
| Reusable skill | A repeatable procedure or external-platform workflow applies across repositories and has a reliable trigger. | It becomes repository-specific, one-step, obsolete, or duplicates another skill. |
| Active-state document | A workflow actively reads and updates the queued or in-progress state. | Work completes, is rejected, or moves to its durable result. |
| Dated investigation | A scoped question has unique internal or external evidence, provisional findings, or unresolved decisions worth preserving. | Closure has promoted every conclusion and task, and no unique evidence or provenance remains. |

## Anti-regrowth controls

### At every change close-out

1. Sweep comments in whole changed files.
2. Inspect only the trigger-reachable neighborhood: source comments, ancestor instructions, matching rules, and purpose-routed current documents.
3. Try, in order: derive or generate; add an executable guard; update an existing owner; move a misplaced fact; add a new fact; create a new artifact.
4. For every ADD or MOVE, record the placement contract in the analysis. Do not paste the card into the repository unless its fields are themselves useful guidance.
5. For every MOVE or DELETE, cite the current source and the target/derivation/guard that makes removal safe. Cold-read the complete source and destination.
6. Report net instruction lines, new instruction artifacts, removed artifacts, and always-loaded growth. Growth is a review signal, not a failure.

### Gate every new artifact

A new `CLAUDE.md`, rule, maintained document, workflow, or skill must state:

- its delivery trigger or invocation trigger;
- its canonical scope;
- why no current owner suffices;
- how it stays current;
- what would retire or merge it;
- how every supported agent receives equivalent delivery when required.

Reject a new artifact when any field has no answer. A short file without a distinct trigger is still bloat.

### Run a repository-wide audit only on symptoms

Keep ordinary close-out change-scoped. Run a full corpus audit when:

- a loader or agent-provider delivery mechanism changes;
- a broken or stale route is discovered;
- an instruction tier or documentation taxonomy is introduced;
- instruction growth is unexplained by new non-derivable constraints;
- repeated corrections show that placement or delivery is failing;
- the user explicitly requests an audit.

Do not use universal file or line ceilings. Measure eager payload, duplicated ownership, trigger breadth, orphan routes, and unexplained net growth instead.

## Original eventual edit set

This was the proposed edit set before the decision walk; implementation progress is tracked above.

| Target | Change |
|---|---|
| `place-fact` | Own trigger, canonical owner, scope, justified mirrors, lifecycle, guard/update path, removal, and root-versus-unscoped placement. |
| `vet-fact` | State that its history cut governs current guidance; dated evidence is a separate lane, not an instruction exception. |
| `durable-docs-update` | Require the placement contract for ADD/MOVE, evidence-backed MOVE/DELETE, whole-file cold reads, new-artifact admission, and a small corpus-delta report. |
| `refine-file`, `memory-prune` | Align owner/mirror and destructive-proof semantics with the canonical contract. |
| `seed-claude-context` | Consume the same contract; make length a review signal rather than a drafting target; remove archetypes that bypass admission. |
| Root writing guide | Keep the full-file procedure, but move or invoke every admission rule needed by installed skills. |
| `WRITING-GUIDE.md` | Define one canonical owner plus deliberate guarded mirrors. |
| `handoff` | Replace the unowned default `CONTEXT.md` with a state artifact selected by an existing workflow or explicit user choice. |
| README and consumers | Update only descriptions or wording changed by the owners above. |

`product-interview` and `tech-design` already follow routed task documents and do not need another generic placement policy.

## Meta taxonomy

`meta/discussions/` currently contains pre-decision hypotheses, investigations, shipped decision records, superseded designs, and open candidates. “Discussion” names how work happened, not what the artifact is or how it ages.

Rename it to `meta/investigations/` and add a local instruction file that requires each record to declare its question, evidence scope, status, current owners, open decisions, and closure outcome. Keep this file in `meta/discussions/` until that rename is approved; creating both folders now would create two competing homes.

This taxonomy is suitable for Agent Skills itself. Reusable policy should describe the dated-evidence lifecycle without forcing every repository to use the same path name.

## Original decisions proposed

These recommendations preceded the walk; the decision outcome above governs.

| # | Decision | Recommendation | Confidence |
|---:|---|---|---:|
| 1 | Canonical ownership | Replace “one fact, one home” with “one canonical owner; mirrors only for distinct delivery mechanisms and always guarded.” | 0.99 |
| 2 | Policy shape | Keep WORTH → PLACE → SHAPE; make PLACE own trigger, owner, scope, mirrors, lifecycle, guard/update path, and removal. Keep state/evidence as a separate lane. | 0.97 |
| 3 | Destructive edits | Require direct evidence and full source/target cold reads for MOVE/DELETE; do not rely on confidence alone. | 0.97 |
| 4 | Root guide | Keep it as a full-file guide, but move or explicitly invoke its load-bearing admission rules from installed skills. | 0.96 |
| 5 | Anti-regrowth | Add new-artifact admission, targeted neighborhood dedup, corpus-delta reporting, and symptom-triggered full audits; use no universal quotas. | 0.97 |
| 6 | Meta folder | Rename Agent Skills `meta/discussions/` to `meta/investigations/` in one later change and add lifecycle instructions. | 0.96 |

## Open questions

No evidence or policy question remains open. Implementation is proceeding one skill file at a time.
