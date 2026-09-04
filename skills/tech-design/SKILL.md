---
name: tech-design
description: "Turn a locked product/UX spec into technical design — the HOW: architecture, data shapes, signatures, file layout. TRIGGER when: user asks how to implement a spec'd feature; user wants architecture, data-shape, or file-layout decisions; user says 'tech design' or 'design the implementation'. SKIP when: product scope or UX is unclear; implementation is trivial and obvious; only wave ordering remains."
---

# Tech Design

## Protocol

### Input

- **Spec folder**: `meta/specs/NNN-slug/` (or a path to either file in it, or a feature name to match against existing folder slugs). If more than one folder plausibly matches, list the candidates via `AskUserQuestion` — never glob-and-pick. The resolved `NNN-slug` is the one Step 6 commits.

### Step 1 — Gate: the WHAT must be locked

Refuse to proceed if the spec (`meta/specs/NNN-slug/spec.md`) is not ready:

```
grep -nE '^[[:space:]]*-[[:space:]]*\*\*Status:\*\*[[:space:]]*open' spec.md   # any hit ⇒ blocked
grep -n '\[NEEDS CLARIFICATION:' spec.md                                       # any hit ⇒ blocked
```

(Exact forms are load-bearing — defined under **Gate anchors** in `skills/product-interview/SKILL.md` beside the canonical template. POSIX ERE only; don't "fix" the patterns.)

If either matches, stop and report in this exact shape — never design on top of an unlocked WHAT:

```
**Blocked — the WHAT isn't locked:**
- Open decisions: [D-NNN-XX — title, one per line | none]
- Unresolved markers: [each clarification marker, verbatim | none]
Next: resolve these in product-interview (it resumes at the open items, not a fresh interview), then re-run tech-design.
```

### Step 2 — Discover (two parallel tracks, before any design)

Bounded by the spec, so parallel — both complete **before** an approach is proposed.

**2A — Context (parent reads):**
- The spec: Requirements, UX, ACs, product decisions (note the highest existing `XX` across this spec's `D-NNN-XX` blocks — Step 5 continues the counter from it), Constraints, Open Questions (items tagged `(for tech-design)` are inputs discovery left for this skill).
- Project conventions: root and relevant ancestor `AGENTS.md` files, Claude path rules in `.claude/rules/` whose quoted `paths:` globs match affected files, and task documents the project instructions require. **Use these sources to decide where things go.**
- Existing code in the affected areas: patterns, interfaces, signatures to match — and the test landscape (test file locations, test style — unit/integration/e2e — helpers and fixtures the implementation should follow); nothing downstream re-discovers it.

**2B — Constraint recon (parallel Opus subagents, one per surface):**

Enumerate every external surface the spec's ACs ride on — the enumeration sizes the fan-out: one subagent per surface, merging closely related surfaces (no external surfaces at all → record "2B empty — no external surfaces" and design on 2A alone). Each dispatch carries the surface name plus the AC/Constraint texts riding on it, so the subagent knows which numbers are load-bearing. Recon targets per surface type:

| Surface | Recon |
|---|---|
| External APIs / providers | Hard limits: rate/throughput caps, quotas, batch sizes, latency floors; required fields; capabilities; gotchas |
| Platform (Shopify, extension, etc.) | What the platform permits/forbids for the promised UX; review/approval constraints |
| Existing subsystems | The real interfaces and capacities of internal systems the design will lean on |
| Data / migrations | Current schema shapes and volumes a delta must be compatible with |

Each subagent returns these fields — **read `blocks` and `volatility` first; they drive the gate, the rest informs the design:**

| Field | Value |
|---|---|
| `blocks` | `AC-NNN-XX` \| `D-NNN-XX` \| `none` — a constraint that makes a cited AC unsatisfiable or contradicts a decision; `none` is valid and recordable |
| `volatility` | `stable` \| `changing` — set `changing` (with what/when) whenever the user has named a pending change to the surface |
| exists | yes / no |
| capabilities | what the surface can do |
| hard constraints | the limits, with numbers |
| gotchas | traps the design must avoid |

**The gate — resolve before designing.** A `blocks` or `changing` finding stops you; pick a choice via `AskUserQuestion`. A surface flagged both takes the `blocks` choice first — a current blocker outranks a future one.

| Finding | Choices (via `AskUserQuestion`) |
|---|---|
| `blocks: AC-NNN-XX \| D-NNN-XX` | Revise the AC / decision now (rec. when the finding tightens a bound or detail without changing scope or UX) · Route back to `product-interview` (scope or UX itself changes) · Record as accepted risk · Abort |
| `volatility: changing` | Design against the anticipated state (rec.) · Design against the current state · Block until it settles |
| `blocks: none`, `stable` | none — continue |

Mechanics for the choices that touch the spec:
- **Route back to `product-interview`** (the WHAT itself is affected) — first write `[NEEDS CLARIFICATION: <the 2B evidence>]` beside the affected AC/requirement; the marker re-blocks the lock gates, so an interrupted route-back resumes from the file, not memory — then stop. Tell the user: product-interview resumes at this marker only, not a fresh interview.
- **Return from `product-interview`** — when the affected 2B surfaces remain clear in the current chat, re-run only those surfaces; when the scope is unavailable or uncertain, re-run all of 2B.
- **Revise the AC / decision now** (user-sanctioned WHAT edit) — revise the AC and the decision it rests on per the spec template's Revising rule (adding a decision if none exists — drafted now, written at Step 5 with the shared counter), citing the 2B evidence; it rides Step 6's commit, continue.
- **Record as accepted risk** — lands in `## Accepted risks (knowingly carried)` at the Step-5 Draft write; continue.
- **Design against the anticipated state** — existing code is the starting state, never the target (the WHAT may diverge); record the assumption as a `D-NNN-XX` (drafted now, written at Step 5) citing what changes and when; a not-yet-built dependency it leans on lands in `## Accepted risks` as a sequencing dependency.
- **Design against the current state** — note why the pending change is out of scope, continue.
- **Block until it settles** — write `[NEEDS CLARIFICATION: <surface> pending change — confirm the target state before lock]` beside the affected AC/requirement; the lock greps refuse to lock until it's resolved.

**Before leaving Step 2:** state the load-bearing assumptions you *are* making (named pending changes are caught above; this catches the rest) in this exact shape, so the user can correct them before any design exists:

```
**Assumptions I'm carrying into the design:**
- [assumption] — [what breaks if it's wrong]
```

(Write `None — 2A/2B covered everything load-bearing` when the list is empty.)

### Step 3 — Design: approach, then structure

**Select approach** — with 2B's constraints on the table:

- **Single obvious path** — note it briefly and continue. Most features land here.
- **Multiple viable paths with real tradeoffs** — the parent owns the judgment of *whether* multi-path applies; the agent owns the analysis. Spawn the `propose-alternatives` agent (`agents/propose-alternatives.md`) with three inputs: **Problem** (the spec's goal plus the specific decision point that forks), **Current approach** (the existing implementation if any, else "no current approach — greenfield"), **Context** (2A's relevant files and conventions + 2B's constraints). Present its `AlternativesOutput` via `AskUserQuestion` with a recommendation — flag when confidence is low or the tradeoff depends on priorities you don't know. Do not continue until the user selects. If the user proposes an approach not in the list, validate it against 2A's conventions and 2B's constraints — adopt it if it holds; otherwise explain why and re-ask.

Record the chosen approach (and rejected alternatives + why, distinguishing *rejected-forever* from *deferred*) as a **technical `D-NNN-XX` block** destined for the spec, citing the 2B finding that drove it where load-bearing. A genuinely load-bearing fork is a *decision* (spec), not detail — capture it here, don't let it leak silently into the plan.

**Cite complete records only.** Before a `D-NNN-XX` cites an audit or research record, confirm every named table, list, and count exists there. Add each missing artifact verbatim to the record before citing it. If the record cannot be corrected, carry the artifact in the decision or relevant spec section and omit the citation.

**Structure outline** — the concrete shape the locked decisions imply. Scale depth to scope. This is a design snapshot bound for the spec's `## Structure Outline` section — written `Status: Draft` for review, frozen once locked:

```markdown
## Structure Outline
<!-- Written `Status: Draft` for review (### Files touched withheld until lock); FROZEN once `Status: Locked`. Before build, replacement requires a tech-design re-run scoped to the change; during build, deviations live as [Implementation] entries in plan.md's Execution Log. -->

### Before → after
[ASCII call-graph: affected module/flow today → what it becomes.
 module → function → return-shape, with caller lists.]

### File map
[Annotated create/modify tree (✨ create · ✏️ modify) of the affected dirs, with a one-line *why* on each load-bearing or convention-establishing/deviating placement; where an existing convention dictates the location, cite the convention doc instead of re-arguing it. Add the import DAG when cross-module direction is a rule. Scale to scope — a one-file change is one line.]

### Per-file walk
- `path/to/file.py`
  - `[load-bearing signature](args) -> ReturnType` — [one-line purpose]
  - [load-bearing data shape / schema delta: field, type, nullability, constraint]

### Files touched
- create: [paths]
- modify: [paths]
```

- **Include design boundaries where the goal touches them:** public or shared interfaces, serialization or persistence schemas, cross-task shapes or values, and component boundaries that determine ownership or task/file slicing; skip skeleton sections irrelevant to the change.
- **Leave private mechanics open:** keep private one-task helpers, records, and testkit mechanics out of the outline unless at least two planned tasks depend on them or they encode a locked decision.
- **Always map changed files:** include the create/modify file list and File map; give each load-bearing placement one rationale line and provide a deeper walk only on request.
- **Trace serialization consumers:** when a return shape or exported signature changes, trace direct consumers across serialization boundaries that symbol search cannot recover, such as frontend fetches, IPC/queue messages, GraphQL fields, routes, and serialized storage. Add each affected consumer as a `modify` entry for write-plan; treat deeper chains as accepted runtime scope expansion.
- **Own shared literals and defaults:** when two or more files or components consume one value, name its exact value and one canonical owner or source in the outline. If no existing source fixes the value, resolve it before lock.
- **Keep downstream work out:** leave implementation logic, wave sequencing, and test strategy to planning or implementation.

The `### Files touched` heading is write-plan's buildable signal — its outline-present gate greps `^### Files touched` (**Gate anchors**, `skills/product-interview/SKILL.md`). Withheld from the Step-5 Draft and appended at lock, so a mid-design Draft reads as in-progress, never finished or stale. Never rename or omit it.

**Pressure-test the shape** — before handing the design to verify, read the outline as architecture and invoke the `deep-modules` skill via the Skill tool for the lens — the deletion test and deepening-move table it carries. Then settle a verdict on each axis below for the Step-5 review: a clean outline clears all four in one line; a smell names its axis, and the loaded table gives the reshape. Fold any reshape into the outline first; record a `D-NNN-XX` only if it changes the chosen approach itself.

- **Depth** — does each module earn its interface? Settle it with the deletion test.
- **Interface** — is the common case one obvious call, with the hard cases hidden rather than pushed onto callers?
- **Seam only where it varies** — is every swap point backed by a real second adapter, not a hypothetical one?
- **Coupling** — would changing one decision force edits across several files? Reshape so the knowledge lives in one place.

### Step 4 — Verify the design

2B answered "what is possible"; this step answers "does this *specific* design hold." Verify runs before the Draft is written — on the drafted outline, not yet on disk. Launch Opus subagents split by file cluster (related files and interfaces share a subagent):

- Signatures/interfaces the outline references exist as written.
- The schema delta is compatible with current models.
- Named components exist with the assumed props/composition.
- Every outline claim that *names a real file or symbol* resolves to it — file-location and attribution claims ("X lives in `a.js`"), not just signatures and props.
- Every literal or default shared by two or more outlined files or components has one exact value and canonical owner or source.
- Nothing in the outline contradicts a 2B finding; any surface the *chosen approach* implies that 2B didn't cover (e.g., a specific endpoint of a recon'd provider) gets checked now.

Each subagent returns a verdict per outline claim it checked: **confirmed** / **broken (with evidence)** / **not checkable** — "breaks the outline" is the subagent's finding to make, not parent improvisation. Step 4 is mandatory for every outline and replacement bound for the spec; write-plan must not build on guesses.

If a finding breaks the outline, present via `AskUserQuestion`: "Amend outline" (recommended — a verified break means the design is wrong; back to Step 3; one amend→re-verify lap per finding — if the same claim breaks again, re-present this question with the new evidence rather than amending again silently) / "Record as a known risk and proceed" (written into the spec's `## Accepted risks (knowingly carried)` at the Step-5 Draft write — never left in conversation) / "Route back to product-interview" (the WHAT is affected — first write `[NEEDS CLARIFICATION: <evidence>]` beside the affected AC, as in 2B's gate) / "Abort". A finding that merely needs an AC downgrade rather than a re-interview takes 2B's "Revise the AC / decision now" path.

### Step 5 — Write the Draft, then review the file

Write the verified design into `meta/specs/NNN-slug/spec.md` as `Status: Draft` so the user reviews the file. One Draft write, the design-fact duties:

1. **Technical `D-NNN-XX` blocks** under `## Decisions`, continuing the spec's shared `XX` counter (one counter across product and tech decisions); stamp `[tech]` after the colon (discovery stamps `[product]` — advisory, no gate greps it). Write lowercase `Status: locked` — the Capitalized header staying `Draft` is what keeps the design reviewable yet unlocked (the case split; see Gate anchors). Canonical block:

```markdown
### D-NNN-07: [tech] [technical decision title]
- **Status:** locked
- **Chosen:** [approach/structure]
- **Rejected:** [alt — why it lost]; [alt — *deferred*, not rejected forever — why]
- **Rationale:** [the constraint that drove it; cite the 2B/verify finding if load-bearing]
- **Supersedes:** —
- **Superseded-by:** —
```

2. **The Structure Outline** into `## Structure Outline`, replacing the section wholesale (discovery's placeholder comment included) — but **withhold the `### Files touched` heading** (appended at lock, Step 6).

3. **Constraints and accepted risks**: append load-bearing 2B numbers (cited in a `blocks` verdict or bounding an AC) to `## Constraints`; append every Step-4 risk the user accepted to `## Accepted risks (knowingly carried)`. Both append-by-both — discovery seeds them; this skill adds what recon and verify proved.

4. **Confirm the AC gating tags**: discovery's `[code-gated]`/`[human-gated:]` tags were provisional — confirm or flip each against the chosen design. A tag flip is a tag-only edit, exempt from the supersession protocol; the only other sanctioned AC edit is a user-approved revision from the 2B/Step-4 gates.

5. **Dispose of `(for tech-design)` Open Questions**: strike each with `→ resolved per D-NNN-XX`, or escalate to a real decision or clarification marker — the tag must be absent at lock.

Then point the user at the file — `spec.md`, or `git diff` — and give the review its context in this exact shape:

```
**Design ready for review:**
- What verify changed: [claim → what broke → how the outline was amended | none — all claims confirmed]
- Accepted risks carried: [risk — why accepted | none]
- Shape checks: [clear | [check]: [smell] → [reshape]]
```

Use `AskUserQuestion` to collect the choice: "Lock & commit" / "Adjust" / "Find gaps first". Recommended: lock & commit once the file matches the goal and clears the four shape checks. This is the design-lock gate — any reply that isn't explicit approval is **Adjust**; never proceed on an implied yes.

- **Adjust** — edit the Draft in place, re-run Step 4's verify on the change (an unverified outline is a guess), then re-point the user at the file.
- **Find gaps first** — opt-in, at most once, for a complex design or when you doubt the outline is complete — invoke the `find-gaps` skill over the written Draft, paired with the affected code paths so checkers read real files. Fence lenses to design-level absences only — data integrity, interface coverage, rollback/migration; leave error-path and concurrency *logic* to code review, and never re-check what Step 4's verify confirmed (checkers verify what's written; find-gaps hunts what's not). Applied gaps amend the Draft, which re-enters Step 4's verify. Then re-point and re-ask without the Find-gaps option — it runs at most once.

### Step 6 — Lock and commit

On **Lock & commit**:

1. **Re-run the two lock greps** (Step 1 forms) over the spec. If either hits, lock fails — append nothing, leave the header `Draft`, and report the open decisions/markers in Step 1's block shape, headed `**Lock failed — still open:**`; the outline body stays on disk as a mid-design Draft (resumability reads it as in-progress).
2. **On clean greps, lock in one edit** — append `### Files touched` to the Structure Outline *and* flip the header to `Status: Locked` in a single write, so the "Files touched present + `Draft` header" state never lands on disk (that signature must mean only a reopen — see Resumability). The `### Files touched` heading under a `Locked` header is the signal that tells write-plan the design is ready to sequence. (Header values are Capitalized — `Locked`, not `locked`; the case split is load-bearing, see Gate anchors rule 2 in `skills/product-interview/SKILL.md`.) The outline is now frozen.
3. **Commit** — stage only spec.md; the locked design must not live uncommitted across sessions:

```
git add meta/specs/NNN-slug/spec.md && git commit -m "spec(NNN-slug): tech design — decision blocks + structure outline"
```

(Use the slug resolved at Input. Run `git status --porcelain meta/specs/NNN-slug/`; if anything other than spec.md is staged or dirty, unstage it and commit spec.md alone. Never fold another file — a plan.md, a doc — into this commit, even when write-plan runs in the same session.)

Tell the user the design is locked and committed at `meta/specs/NNN-slug/spec.md` and ready for `write-plan`; plan.md does not exist yet because write-plan creates it. No routing question is needed because every WHAT-level gap detector already ran.

### Resumability

On re-entry, read the spec's state — it encodes where a prior session stopped. "Outline present" means the `### Files touched` heading is on disk (the lock-completion signal); a Draft outline *body* without it is a mid-design state, not a finished one.

- **`### Files touched` present and header `Status: Locked`** → this skill finished; route to `write-plan` — *unless the user explicitly asks to redesign* (following bullets).
- **`### Files touched` present, header `Locked`, user asks to redesign, and plan.md's `Base SHA:` is set** → keep the outline frozen; handle the change in the active `execute-plan` session, updating spec decisions, plan tasks, or the Execution Log as the change requires, then resume execution.
- **`### Files touched` present, header `Locked`, user asks to redesign, and plan.md is absent or its `Base SHA:` is unset** → confirm the re-open, flip the header to `Draft`, revise the affected `D-NNN-XX` blocks in place per the spec template's Revising rule, and re-run from Step 2 scoped to the change: re-run 2B only for the surfaces the change rides on; recompute only the affected outline sections, carrying the rest forward (the Step-5 write still replaces the section wholesale and withholds `### Files touched`); Step 4's verify covers the changed claims — every claim, if code has moved since the last lock — then write a fresh Draft and re-lock. The one sanctioned path to replace a frozen outline.
- **`### Files touched` present but header `Draft`** → a reopen flipped a previously-locked design (product-interview on a WHAT reopen, or a prior tech-design re-open) — the outline is stale; establish the change first — diff spec.md against its last locked commit (`git log -- spec.md`), and if the delta can't be established, re-run wholesale — then re-run from Step 2 scoped to it: revise the affected `D-NNN-XX` blocks per the Revising rule, re-run 2B only for the surfaces the changed WHAT rides on, recompute only the affected outline sections (Step-5 write mechanics unchanged).
- **Outline body present, no `### Files touched`, header `Draft`** → a Step-5 Draft write landed but Step 6 never locked; the design is on disk. First re-read the WHAT sections (Requirements/UX/ACs/product decisions) and confirm the outline still matches them — an edit in this review window flips no header, so drift is silent; on drift, re-run from Step 2 on the changed scope. Otherwise re-run Step 4's verify against it, then resume Step 5's review. Don't reconstruct from memory.
- **Technical `D-NNN-XX` blocks present but no outline body** → a Step-5 write was interrupted between the decision blocks and the outline; rebuild the outline body, re-run Step 4's verify, resume Step 5.
- **Neither** → any prior design lived only in conversation (interrupted before the Step-5 write); start from Step 2 — redo, don't reconstruct from memory.

## Rules

- **Constraints before approach.** The only pre-approach user questions are 2B's own `blocks`/`changing` gates, which fire after recon completes — facts inform decisions, they don't invalidate them afterwards.
- **Decisions are live; the outline is a snapshot.** A choice whose *why* you'd want next session is a `D-NNN-XX` (supersedable mid-build). Before plan.md's `Base SHA:` is set, replace a frozen outline only through a scoped re-run of this skill; during build, keep it frozen and record deviations in plan.md's Execution Log.
- **Don't re-decide project conventions.** Follow loaded project instructions. Record a `D-NNN-XX` only for a deviation or new convention; flag any new convention for durable placement.
- **Cite decisions by full stable id** (`per D-NNN-07`), never by line number. Cross-spec revisions always supersede, never edit — a prior spec's decisions may already be in code; a later spec's decision may supersede this spec's, mechanics in execute-plan Step 2.5.
- **Note off-scope finds; don't chase them.** When discovery or recon surfaces an out-of-scope problem (a stale doc, an unrelated bug, a tempting fix), record it as a one-line follow-up and continue — unless it changes a load-bearing constraint of this design, then fold it into 2B. Never spawn investigation or write code mid-skill.
