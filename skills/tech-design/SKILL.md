---
name: tech-design
description: "Turn a locked product/UX spec into technical design — the HOW: architecture, data shapes, signatures, file layout. TRIGGER when: user asks how to implement a spec'd feature; user wants architecture, data-shape, or file-layout decisions; user says 'tech design' or 'design the implementation'."
---

# Tech Design

Turn a locked WHAT into a buildable HOW. Gather the constraints first, then decide the technical approach with the facts on the table, and append the design record to the spec: **technical decisions** as `D-NN` blocks (so the architecture *why* survives across sessions), the **Structure Outline** — schemas, signatures, file list — as a design snapshot that freezes once verified, and the **constraints and accepted risks** recon proved (facts must not live only in conversation). Verify the written design against reality before handing off.

## When to use

YES: a feature's product/UX is locked in a spec and now needs implementation decisions (approach, data shapes, file layout) before it can be sequenced into waves.

NO: product scope or UX is still unclear (use `product-interview`); the change is trivial with one obvious implementation (go straight to `write-plan`); you only need wave ordering, not design (use `write-plan`).

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

If either matches, stop and tell the user which product/UX decisions or clarifications are still open — route back to `product-interview`. Do not design on top of an unlocked WHAT.

### Step 2 — Discover (two parallel tracks, before any design)

Bounded by the spec, so parallel — both complete **before** an approach is proposed.

**2A — Context (parent reads):**
- The spec: Requirements, UX, ACs, product decisions (note the highest existing `D-NN` — Step 6 continues the numbering from it), Constraints, Open Questions (items tagged `(for tech-design)` are inputs discovery left for this skill).
- Project conventions: CLAUDE.md and whatever convention docs it references (ARCHITECTURE.md, api-patterns.md, `.claude/rules`). **These are the source of truth for "where things go" — follow them; don't re-decide them here.**
- Existing code in the affected areas: patterns, interfaces, signatures to match — and the test landscape (test file locations, test style — unit/integration/e2e — helpers and fixtures the implementation should follow); nothing downstream re-discovers it.

**2B — Constraint recon (parallel Opus subagents, one per surface):**

Enumerate every external surface the spec's ACs ride on — the enumeration sizes the fan-out: one subagent per surface, merging closely related surfaces (no external surfaces at all → record "2B empty — no external surfaces" and design on 2A alone). Each dispatch carries the surface name plus the AC/Constraint texts riding on it, so the subagent knows which numbers are load-bearing. Pull each surface's hard constraints:

| Surface | Recon |
|---|---|
| External APIs / providers | Hard limits: rate/throughput caps, quotas, batch sizes, latency floors; required fields; capabilities; gotchas |
| Platform (Shopify, extension, etc.) | What the platform permits/forbids for the promised UX; review/approval constraints |
| Existing subsystems | The real interfaces and capacities of internal systems the design will lean on |
| Data / migrations | Current schema shapes and volumes a delta must be compatible with |

Each subagent returns: exists (yes/no), capabilities, hard constraints (with numbers), gotchas, and **`blocks: AC-N | D-NN | none`** — the subagent flags any constraint that makes a cited AC unsatisfiable or contradicts a decision; `none` is a valid, recordable result.

Any `blocks` hit gates before design continues — present via `AskUserQuestion`:
- **Route back to `product-interview`** (recommended — the WHAT itself is affected): first write `[NEEDS CLARIFICATION: <the 2B evidence>]` into the spec beside the affected AC/requirement — the marker mechanically re-blocks the lock gates, so an interrupted route-back resumes from the file, not memory — then stop.
- **Revise the AC now** — user-sanctioned WHAT edit: revise the AC in place with the *(revised per D-NN)* marker plus a superseding D-NN citing the 2B evidence; apply it to the spec immediately (it rides Step 6's commit) and continue.
- **Record as accepted risk** — lands in the spec's `## Accepted risks (knowingly carried)` at Step 6; continue.
- **Abort.**

### Step 3 — Design: approach, then structure

**Select approach** — with 2B's constraints on the table:

- **Single obvious path** — note it briefly and continue. Most features land here.
- **Multiple viable paths with real tradeoffs** — the parent owns the judgment of *whether* multi-path applies; the agent owns the analysis. Spawn the `propose-alternatives` agent (`agents/propose-alternatives.md`) with three inputs: **Problem** (the spec's goal plus the specific decision point that forks), **Current approach** (the existing implementation if any, else "no current approach — greenfield"), **Context** (2A's relevant files and conventions + 2B's constraints). Present its `AlternativesOutput` via `AskUserQuestion` with a recommendation — flag when confidence is low or the tradeoff depends on priorities you don't know. Do not continue until the user selects. If the user proposes an approach not in the list, validate it against 2A's conventions and 2B's constraints — adopt it if it holds; otherwise explain why and re-ask.

Record the chosen approach (and rejected alternatives + why, distinguishing *rejected-forever* from *deferred*) as a **technical `D-NN` block** destined for the spec, citing the 2B finding that drove it where load-bearing. A genuinely load-bearing fork is a *decision* (spec), not detail — capture it here, don't let it leak silently into the plan.

**Structure outline** — the concrete shape the locked decisions imply. Scale depth to scope. This is a design snapshot bound for the spec's `## Structure Outline` section — frozen once the verify gate passes:

```markdown
## Structure Outline
<!-- FROZEN design snapshot (tech-design verify gate) — never edited in place; deviations live as [Implementation] entries in plan.md's Execution Log; wholesale replacement only via a tech-design re-run. -->

### Before → after
[ASCII call-graph: affected module/flow today → what it becomes.
 module → function → return-shape, with caller lists.]

### Per-file walk
- `path/to/file.py`
  - `signature(args) -> ReturnType` — [one-line purpose]
  - [data shape / schema delta: field, type, nullability, constraint]

### Files touched
- create: [paths]
- modify: [paths]
```

Must include, where the goal touches them: data shapes, signatures, component trees — skip skeleton sections irrelevant to the change (a backend-only change needs no component tree). The create/modify file list is unconditional. Must NOT include: implementation logic, wave sequencing, test strategy.

The `### Files touched` heading is load-bearing: write-plan's outline-present gate greps for it (`^### Files touched`, listed under **Gate anchors** in `skills/product-interview/SKILL.md`). Never rename or omit it.

Print the drafted technical `D-NN` blocks and the outline verbatim in chat, then use `AskUserQuestion` only to collect the choice: "Approve design" / "Adjust" / "Find gaps first". Recommended: approve once the outline matches the goal. Do not proceed until approved — this is the architecture-lock gate.

On **Find gaps first** — opt-in, for a complex design or when you doubt the outline is complete — invoke the `find-gaps` skill over the drafted outline, paired with the `spec.md` path and the affected code paths so checkers read real files. Fence lenses to design-level absences only — data integrity, interface coverage, rollback/migration; leave error-path and concurrency *logic* to code review (this is design, not implementation). Applied gaps amend the outline, which re-enters Step 4's verify. Then re-print the outline and re-ask.

### Step 4 — Verify the written design

2B answered "what is possible"; this step answers "does this *specific* design hold." Launch Opus subagents against the approved outline, split by `### Files touched` cluster (related files and interfaces share a subagent):

- Signatures/interfaces the outline references exist as written.
- The schema delta is compatible with current models.
- Named components exist with the assumed props/composition.
- Nothing in the outline contradicts a 2B finding; any surface the *chosen approach* implies that 2B didn't cover (e.g., a specific endpoint of a recon'd provider) gets checked now.

Each subagent returns a verdict per outline claim it checked: **confirmed** / **broken (with evidence)** / **not checkable** — "breaks the outline" is the subagent's finding to make, not parent improvisation.

If a finding breaks the outline, present via `AskUserQuestion`: "Amend outline" (recommended — a verified break means the design is wrong; back to Step 3) / "Record as a known risk and proceed" (appended to the spec's `## Accepted risks (knowingly carried)` at Step 6 — never left in conversation) / "Route back to product-interview" (the WHAT is affected — first write `[NEEDS CLARIFICATION: <evidence>]` beside the affected AC, as in 2B's gate) / "Abort". A finding that merely needs an AC downgrade rather than a re-interview takes 2B's "Revise the AC now" path.

### Step 5 — Confirm

Step 3's gate already approved this design. If Step 4 verified clean — no amendments, no accepted risks, no AC revisions — skip the question: state that the approved design is being written and proceed to Step 6. Otherwise print what changed since Step 3's approval in chat, then use `AskUserQuestion` only to collect the choice: "Looks good — write it" / "Adjust". Recommended: write it. "Adjust" loops back to Step 3; any outline change re-runs Step 4's verify before re-confirming (an unverified outline is a guess).

### Step 6 — Write and commit

One file — `meta/specs/NNN-slug/spec.md` — one write pass, five duties:

1. **Technical decisions** under `## Decisions`, continuing the `D-NN` numbering from discovery; stamp `[tech]` after the colon in each heading (discovery stamps `[product]` — the marker is advisory, no gate greps it). Section format is canonical in `skills/product-interview/SKILL.md`'s template — D-NN block with Status/Chosen/Rejected/Rationale/Supersedes/Superseded-by, lowercase status values:

```markdown
### D-07: [tech] [technical decision title]
- **Status:** locked
- **Chosen:** [approach/structure]
- **Rejected:** [alt — why it lost]; [alt — *deferred*, not rejected forever — why]
- **Rationale:** [the constraint that drove it; cite the 2B/verify finding if load-bearing]
- **Supersedes:** —
- **Superseded-by:** —
```

2. **The verified Structure Outline** into the spec's `## Structure Outline` section — replacing the section wholesale, discovery's placeholder comment included. This writes the frozen snapshot from the verify gate: **never edited in place**. Build-time deviations are recorded by execute-plan as `[Implementation]` entries in plan.md's Execution Log; if a mid-build redesign invalidates the outline wholesale, re-run this skill (re-design, re-verify, supersede the affected D-NNs, recommit) — never patch the section. After ship, code is the source of truth for structure.

3. **Constraints and accepted risks**: append load-bearing 2B numbers (anything cited in a `blocks` verdict or bounding an AC) to `## Constraints`; append every Step-4 risk the user accepted to `## Accepted risks (knowingly carried)`. Both sections are append-by-both — discovery seeds them; this skill adds what recon and verify proved.

4. **Confirm the AC gating tags**: discovery's `[code-gated]`/`[human-gated:]` tags were provisional — confirm or flip each against the chosen design. A tag flip is a tag-only edit, exempt from the supersession protocol (like the AC revise-in-place exception); the only other sanctioned AC edit here is a user-approved revision from the 2B/Step-4 gates.

5. **Dispose of `(for tech-design)` Open Questions**: strike each with `→ resolved per D-NN`, or escalate it to a real decision or clarification marker — the tag must be absent at design lock.

Set the header to `Status: Locked` **iff** the two lock greps (Step 1 forms) run clean over the just-written spec — re-run them now. Otherwise leave `Draft` and tell the user which decisions/markers are still open. (Header values are Capitalized — `Locked`, not `locked`; the case split is load-bearing, see Gate anchors rule 2 in `skills/product-interview/SKILL.md`.) Then **commit** — the approved design must not live uncommitted across sessions:

```
git add meta/specs/NNN-slug/spec.md && git commit -m "spec(NNN-slug): tech design — D-NNs + structure outline"
```

(Use the slug resolved at Input. Stage only spec.md — if `git status --porcelain meta/specs/NNN-slug/` shows anything else in the folder, leave it unstaged and tell the user.)

Tell the user the path. (plan.md does not exist yet — creating it is write-plan's job.)

### Next step

No routing question — every WHAT-level gap detector already fired earlier (Step 1's gate, 2B's `blocks` gate, Step 4's verify), so reaching this point means the design holds. State it: design locked and committed at `meta/specs/NNN-slug/spec.md`; next skill is `write-plan`.

### Resumability

On re-entry, read the spec's state — it encodes where a prior session stopped:

- **Outline present** (`grep -n '^### Files touched' spec.md` hits) **and header `Status: Locked`** → this skill already finished; route to `write-plan`.
- **Outline present but header `Draft`** → the WHAT was reopened after design (product-interview flips the header on reopen) — the outline is stale; re-run from Step 2, supersede the affected D-NNs, and replace the outline wholesale through the verify gate.
- **Technical D-NNs present but no outline** → a Step-6 write pass was interrupted after the D-NNs but before the outline and commit; rebuild the outline from the D-NNs already in the spec and re-run Step 4's verify before writing.
- **Neither** → any prior design pass lived only in conversation; start from Step 2 — redo, don't reconstruct from memory.

## Rules

- **Never run on an unlocked WHAT.** The Step 1 grep gate is mandatory.
- **Constraints before approach.** No approach is proposed, and no user approval requested, until 2B's recon is in — facts inform decisions; they don't invalidate them afterwards.
- **Decisions are live; the outline is a snapshot.** A choice whose *why* you'd want next session is a `D-NN` (supersedable mid-build). The outline freezes at the verify gate — deviations go to plan.md's Execution Log, never back into the outline; wholesale replacement via a re-run of this skill is the one sanctioned path.
- **Don't re-decide project conventions.** Folder structure, naming, API patterns live in CLAUDE.md/ARCHITECTURE.md — read and follow them; only record a `D-NN` when you *deviate* or establish a new convention (and flag that it may belong in durable docs).
- **Cite decisions by stable `D-NN` ID**, never by line number.
- **Verify before handoff.** An unverified outline is a guess; write-plan must not build on guesses.
- **This is design, not implementation.** No code, no wave ordering, no test plan in this skill's outputs.
