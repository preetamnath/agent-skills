---
name: write-plan
description: "Sequence a locked spec into dependency-ordered, wave-grouped tasks. TRIGGER when: user says 'build the plan' or 'sequence this'; a spec needs slicing into parallel-safe waves."
---

# Write Plan

Slice a locked spec and its Structure Outline into atomic, dependency-ordered, wave-grouped tasks in `plan.md`.

## When to use

YES: `meta/specs/NNN-slug/spec.md` is locked with a populated Structure Outline (from tech-design), and the work needs sequencing into waves.

NO: requirements or UX unclear (use `product-interview`); approach, data shapes, or file layout undecided (use `tech-design`); plan already has waves and you want to execute (use `execute-plan`).

## Protocol

### Input

- **Spec folder**: `meta/specs/NNN-slug/` (or a path to either file in it).

### Step 1 — Gate: spec locked, outline present

Four checks, all machine-checkable:

```
grep -nE '^[[:space:]]*-[[:space:]]*\*\*Status:\*\*[[:space:]]*open' spec.md   # any hit ⇒ blocked
grep -n '\[NEEDS CLARIFICATION:' spec.md                                       # any hit ⇒ blocked
grep -n '^### Files touched' spec.md                                           # no hit ⇒ outline missing
grep -nE '^[[:space:]]*-[[:space:]]*\*\*Status:\*\*[[:space:]]*Draft' spec.md  # + outline present ⇒ stale outline (reopened after design)
```

(Lock-gate forms are load-bearing — defined under **Gate anchors** in `skills/product-interview/SKILL.md`. POSIX ERE only.)

If a lock grep hits, stop and name the open decisions/clarifications — route to `product-interview` (product/UX) or `tech-design` (technical). If the outline check misses, route to `tech-design`. If both `### Files touched` and the `Draft` grep hit, the WHAT was reopened after design and the outline is stale — route to `tech-design` (its resume re-runs from Step 2, scoped to the change). (A fresh `Draft` has no outline, so `Draft` + an outline means reopen — capitalized, header-only; case-split rule 2.)

Trivial-skip exception: for a trivial change with one obvious implementation, offer via `AskUserQuestion` — "Skip tech-design — trivial" / "Route to tech-design". On Skip, put `- **Outline:** skipped (trivial; user-approved)` as plan.md's last header line — reviewer criterion S2 then auto-passes.

### Step 2 — Read context

Read `spec.md` (Requirements, Acceptance Criteria, Decisions, Structure Outline, Constraints). Skim the affected files only to size and split the work — don't redo the design; it's already in the spec. On the trivial-skip path there is no Structure Outline: read Requirements + ACs and skim the affected files instead.

### Step 3 — Identify work items

Break the structure outline (on trivial-skip: the spec's Requirements/ACs) into atomic tasks **for the locked design**. Each task:

- **One commit's worth of work** — completable in a single focused session.
- **Self-contained** — names the file(s) it touches, what to change, and why.
- **Verifiable** — you can tell when it's done.
- **Cited** — names the `AC-NNN-XX` it satisfies and any `D-NNN-XX` it honors, by full id (`satisfies AC-NNN-02; per D-NNN-09`).

Coverage check both directions: an AC no task satisfies is a gap (add a task or flag it); a task citing nothing is scope creep (justify it against the spec or cut it). Human-gated ACs still get implementation tasks where code must exist for the later live check — note `human-gated: verified post-ship` on the citation. On the trivial-skip path, cite `AC-NNN-XX` only — no technical decision blocks exist; don't invent citations to satisfy M6.

**Interface changes pull in their call-sites.** When a task changes a shared interface — a new or changed prop, parameter, exported signature, or return shape — grep for its direct consumers (importers, callers, renderers) and add them to that task's file-set, or to a `Must land together with:` / `Depends on:` task if another wave owns them. Map direct consumers only — a runtime scope-expansion round-trip covers the rare deeper chain. Name the interface change in the task's description (not just the feature it serves) — the S3 review can only check a delta the task states, so one hidden behind feature-level prose ("update the settings panel") slips past.

### Step 4 — Order by dependency + wave grouping

For each task, determine: what must exist first, which files it touches, whether it can run in parallel.

**Wave assignment rules:**
1. No dependencies + no file overlap → same wave; mark each such task `[P]` (parallelizable).
2. Depends on another task → later wave.
3. Same file modified by multiple tasks → different waves (serialize), or `Must land together with:` in one subagent's hands.
4. Maximum **5** tasks per wave — it matches execute-plan's parallel-dispatch budget.
5. Prefer fewer, fatter waves over many single-task waves.

### Step 5 — Create plan.md

If `plan.md` already exists:

1. **Shipped or running:** `Status: FROZEN` → stop (new work = new spec). `Base SHA:` set or any `- [x]` task → route to `execute-plan`; never re-sequence a running plan.
2. **Establish the spec delta:**
   - **Baseline commit:** set `LAST_PLAN=$(git log -1 --format=%H -- meta/specs/NNN-slug/plan.md)`. An empty `LAST_PLAN` takes **Recreate** below.
   - **Spec changes:** run `git diff "$LAST_PLAN" -- meta/specs/NNN-slug/spec.md`; working-tree edits are included.
   - **Reviewed baseline:** grep plan.md for `^- Plan review:`. No hit means Step 6 uses **Full**.
3. **Classify and sync:**
   - **Plan-neutral** — formatting, spelling, or explanatory prose that changes no requirement, UX behavior, AC, decision, constraint, outline claim, path, or cited id: keep plan.md unchanged; Step 6 uses **No review**.
   - **Targeted sync** — the affected tasks and their required edits are clear: update only those task bodies, files, citations, dependencies, or wave placements; preserve stable task ids. Step 6 chooses **Delta** or **Full** from the resulting plan diff.
   - **Recreate** — the affected tasks cannot be identified confidently, or most of the design changed: `AskUserQuestion`: "Recreate from the current spec (Recommended)" / "Stop". Replace plan.md from the current Steps 3–4 output using the canonical template below; Step 6 uses **Full**.

Keep targeted-sync and recreated-plan edits uncommitted until Step 6 finishes, so an interrupted session still compares against the last reviewed plan commit.
After handling an existing plan, point the user at its diff and jump to Step 6; never run the fresh-plan write below.

For a fresh plan, print a terse digest in chat, shaped exactly:

```
**Plan drafted — NNN-slug:** meta/specs/NNN-slug/plan.md · <T> tasks, <W> waves
- Wave 1 — <N> tasks — <what lands>
- Wave 2 — <N> tasks — <what lands>
- … one line per wave
```

The digest is a signpost, not the artifact — review or redirect on plan.md itself. Then create `meta/specs/NNN-slug/plan.md` from the canonical template below, and commit:

```
git add meta/specs/NNN-slug/plan.md && git commit -m "plan(NNN-slug): waves created"
```

(Use the slug from Input — execute-plan's resumability and promotion commits key on the same `plan(<slug>):` prefix; an unsubstituted placeholder breaks that chain.)

**CANONICAL plan.md TEMPLATE** (the only copy — execute-plan fills its own sections and cites the Plan anchors here):

```markdown
# PLAN: [Feature name]

- **Created:** [YYYY-MM-DD]
- **Base SHA:** —          <!-- set by execute-plan before Wave 1; final-review diff range -->
- **Status:** Building     <!-- Building → FROZEN [date]. FROZEN marks the plan shipped; new work starts a new spec. -->
<!-- No Spec:/path back-links — the folder pairs the files. Conditional: the trivial-skip path (Step 1) appends ONE more header line here marking the outline as skipped — exact form in Step 1; reviewer criterion S2 keys on it. -->

## Waves
<!-- WRITTEN BY write-plan. ≤5 tasks/wave. [P] = parallelizable within its wave. Every task cites AC-NNN-XX / D-NNN-XX by full id. Task line format is load-bearing: checkbox + bold ID/title on one line (execute-plan flips the `- [ ] ` checkbox to `- [x] ` on each task line); details in indented sub-bullets. -->

### Wave 1: [short description]

- [ ] **T1 [P]: [short title]** — satisfies AC-NNN-01; per D-NNN-07
  - [what to change, which files, why]
- [ ] **T2 [P]: [short title]** — satisfies AC-NNN-03
  - [what to change, which files, why]

### Wave 2: [short description]

- [ ] **T3: [short title]** — satisfies AC-NNN-02; per D-NNN-09
  - [what to change, which files, why]
  - Depends on: T1

## Execution Log
<!-- APPENDED BY execute-plan; append-only. Discoveries logged at the moment found, one per line, with a type tag STARTING the line — the tags are line-anchored grep targets for the ship gate (see Plan anchors in skills/write-plan/SKILL.md). Types: Implementation = detail delta, stays here; AC-affecting = contradicts an AC or locked decision, STOP, user-gated promotion, entry must carry the promotion marker when resolved; Future = opportunity/limitation, triaged once at the ship gate (takes the next `F-NNN-XX` — see Plan anchors). Plus one parent-written tag: auto-resolved = a grounded decision execute-plan's Autonomy gate took without asking — not a discovery, not count-compared, surfaced only in execute-plan's Step 7 report. Guidance and prose here must NEVER start a line with a bracketed tag. -->

## Wave Reviews
<!-- APPENDED BY execute-plan.
Review unit: one block per one-wave or eligible two-wave unit — range, seats, per-AC evidence, findings, Drift, fix coverage, deferred entries.
Pending unit: starts with the load-bearing `- Review pending:` marker; execute-plan replaces it with the completed block.
Final review: records Integration/Full mode, per-AC PASS/FAIL evidence, and verification outcome for the ship gate.
Deferred anchor: `- P2 [deferred]: F-NNN-XX — ...`.
-->

## Ship Gate
<!-- RUN BY execute-plan after the docs sync, before freezing. -->

- [ ] Final review complete: every seat merged, verified, confirmed P0/P1 resolved
- [ ] Comments swept and durable docs synced
- [ ] Every AC-affecting entry carries the promotion marker (count-compare check — see Plan anchors)
- [ ] Every Future entry triaged: current-contract hole → fix now or spec "Deferred"; new feature → user-placed; noise → dies here
- [ ] Every deferred finding triaged: current-contract issue → fix now or spec "Deferred"; separate feature → user-placed; noise → dies here
- [ ] Completion record written to spec (criteria results + post-ship verification + deferred + review filter stats), spec Status → Shipped
- [ ] Plan Status → FROZEN [date]
```

Use stable task IDs (`T1`, `T2`, ...) — they survive edits and reordering; reference dependencies by ID, never position.

### Plan anchors (load-bearing — exact forms matter)

Defined here beside the canonical template; written and grepped by execute-plan — the Base SHA form is grepped by the spec Revising rule's consumers (product-interview, tech-design). POSIX ERE only.

```
^- \[AC-affecting\]            # execution-log entry, tag starts the line
^- \[Implementation\]          #   "
^- \[Future\]                  #   "
^- \[auto-resolved\]:          # execution-log entry, tag starts the line; Autonomy-gate record, not count-compared
^- P[0-9]+ \[deferred\]:       # wave-review deferred finding
^- Review pending: Waves        # unpaid review-unit marker; resolve before new implementation or final review
promoted-to-spec               # promotion marker, ALWAYS lowercase + hyphenated; case-insensitive grep
^- Plan review:                # reviewed-baseline marker; no hit ⇒ Step 6 Full
^- \*\*Base SHA:\*\* —         # hit, or no plan.md at all ⇒ planning stage: spec decisions/ACs edit in place (spec template's Revising rule); no hit with plan.md present ⇒ build started: supersede, never edit
```

Rules: tags start the line — narrative prose and template guidance must never start a line with a bracketed tag, and must never contain the hyphenated token `promoted-to-spec` outside a real marker (the hyphen exists so natural prose — "promoted to spec" — can never collide with the anchor; write the unhyphenated phrase freely). Ship-gate promotion check is a count-compare: number of `^- \[AC-affecting\]` lines must equal the number of (case-insensitive) promotion-marker hits in the Execution Log — consumers scope BOTH counts to that section via `sed -n '/^## Execution Log/,/^## Wave Reviews/p'`.

**F ids** — every `[deferred]` and `[Future]` entry takes one at append time, whoever writes it:
- **Format:** `F-NNN-XX` — `NNN` = this spec's folder number; `XX` = a zero-padded two-digit counter, ONE counter per plan across both entry types.
- **Next `XX`:** highest `F-NNN-` id anywhere in plan.md + 1 — one scan of the file, so a resumed session recomputes it correctly.
- **Placement:** the id follows the anchor tag — `- P2 [deferred]: F-NNN-04 — ...` / `- [Future] F-NNN-09 — ...` — never before it, so the anchor forms above stay exact.
- **Cite from:** spec, plan, and triage files only — never code. The id is the stable handle for dispatches, triage passes, and promotion records.

### Step 6 — Plan review

Choose the entry mode before dispatch. A fresh plan always uses **Full**. The entry mode starts the review; the [post-amendment gate](#post-amendment-gate) independently sizes any retry.

| Mode | Entry condition | Review |
|---|---|---|
| **No review** | A reviewed baseline exists; Step 5 classified the spec delta as plan-neutral; and plan.md did not change | Skip Step 6 |
| **Delta** | A reviewed baseline exists; the sync changed 1–2 existing tasks; added or removed no task; changed no file-set, wave, dependency, schema, signature, return shape, component boundary, or shared interface; and the affected scope is clear | Run M1–M6 once over the full plan, plus one semantic reviewer on the spec and plan deltas |
| **Full** | No reviewed baseline; fresh or recreated plan; more than 2 tasks changed; any Delta condition fails; or scope/risk is unclear | Run the existing full review below |

**Delta review:**

- **Inputs:** both diffs, the changed tasks and ACs/decisions, and their affected Structure Outline excerpts.
- **Checks:** apply S1–S2 to that surface, then answer: "Does every changed task reflect the changed spec, with no missed task, consumer, or ordering effect?"
- **Escalation:** any shared-interface, cross-wave, or wider-scope effect switches the review to **Full**.
- **Findings:** route them through the same lanes below.

**Full review:** run three layers — a deterministic mechanical pass, a size-scaled semantic panel, then clean-room corroboration. Reviewers are `reviewer` agents (`agents/reviewer.md`) against `plan.md` + `spec.md`; instruct each to tag every finding with the exact criterion ID — routing keys on the `M*`/`S*` prefix; untagged defaults to semantic.

**Criteria**

Mechanical (deterministic — provable from plan.md structure):
- **M1**: Every task names its file(s).
- **M2**: Every `Depends on:` points to an existing task in an earlier wave.
- **M3**: No file touched by multiple tasks in the same wave (unless `Must land together with:`).
- **M4**: No wave exceeds 5 tasks.
- **M5**: No task appears in multiple waves.
- **M6**: Every task cites ≥1 `AC-NNN-XX` or `D-NNN-XX`, and every cited id exists in the spec.

Semantic (judgment):
- **S1**: Every `AC-NNN-XX` in the spec is satisfied by ≥1 task (or explicitly marked post-ship-only).
- **S2**: The Structure Outline covers every public or shared interface, serialization boundary, persisted schema, cross-task shape or value, and ownership-defining component boundary a task changes. Private one-task helpers, records, and testkit mechanics stay in the task unless two or more tasks depend on them or they encode a locked decision. EXEMPT when the plan header carries the `- **Outline:** skipped` line — then S2 auto-passes.
- **S3**: Every task that changes a shared interface (prop, parameter, exported signature, or return shape) has that interface's direct consumers in some task's file-set. Direct consumers only — a deeper chain is an acceptable runtime scope-expansion.

**Full-review panel size** — count total ACs (`grep -cE '^- \*\*AC-[0-9]+' spec.md`):

| ACs | Semantic reviewers (S1–S3) |
|---|---|
| ≤6 | 1 |
| 7–12 | 2 |
| ≥13 | 3 |

- **Partition** — split the ACs evenly across the semantic reviewers; each gets its AC subset + the full plan + the Structure Outline, and checks S1 for its subset, S2 for the shared/cross-task boundaries its tasks change, and S3 for interface changes in those tasks (grepping the codebase for consumers).
- **Every task owned by exactly one reviewer** — a task citing only a `D-NNN-XX` (no `AC-NNN-XX`) maps to no AC subset, so assign it to a reviewer too; otherwise its S2/S3 go unchecked.
- **Mechanical pass runs once** — scaling adds nothing to provable checks: at ≤6 ACs the lone reviewer also carries M1–M6 (one agent total); at ≥7 ACs give M1–M6 their own reviewer so they aren't re-run across the panel.
- **+1 cross-wave reviewer when the plan has ≥4 waves**, chartered: *"Read the waves as a sequence. Find ordering bugs the mechanical checks miss — chiefly a task needing another task's output that declares no `Depends on:`, and whether each wave's prerequisites exist by the time it runs. AC coverage is the other reviewers' job. An empty result is valid."*

Parent merges findings by criterion + task/AC + claim, keeps the highest severity, and starts a settled-finding ledger for this Step 6 run. Each ledger entry carries the finding key, disposition, evidence, and cited plan/spec/outline lines.

**Mechanical lane** (deterministic — no confidence bar):

| Finding | Action |
|---|---|
| None across all layers | Proceed silently. |
| Mechanical (`M*`) | Auto-edit the plan, then run the post-amendment gate. Still failing → `AskUserQuestion`: "Edit manually and re-review" / "Accept defect with risk note" / "Abort". |

**Semantic lane** — first separate direct proof from judgment:

- **Directly provable** — when one literal repository check proves the claim (for example, a cited id, path or symbol claimed to exist, package script, command form, or required task field), record the check in the ledger and route the finding without triage: proved real → fix it; proved false → drop it; not proved by one check → judgmental.
- **Judgmental** — if ≥1 finding remains, invoke the **triage** skill via the Skill tool on those findings; mechanical and directly proved findings skip triage. Triage returns each finding's `consider`/`skip` verdict and `adjusted_confidence`.

Apply the autonomy gate to each routed finding:

- **PROCEED** — the fix is grounded and reversible, and the finding is either directly proved real or triage returned `consider` with `adjusted_confidence ≥ 0.80`: close the gap through Steps 3–5, then run the post-amendment gate. For S1/S3 only, log `- Plan review: auto-closed coverage gap (S1/S3) — <what> (conf 0.NN)` under `## Waves`; use `1.00` for direct proof.
- **ASK** — any real finding that misses PROCEED because confidence is below 0.80, the fix is ungrounded or irreversible, the fix would invent scope, or it contradicts a locked `D-NNN-XX`: `AskUserQuestion`: "Add tasks to close the gap" (same Steps 3–5 loop) / "Flag the AC back to the spec owner" / "Accept and note as known gap" / "Abort". Recommend adding tasks for a coverage gap. A valid S2 gap instead routes to tech-design.
- **DROP** — a directly disproved finding or triage `skip`: record its disposition and evidence in the ledger, then log `- Plan review: noted (<disproved directly | skipped by triage>) — <finding>` under `## Waves`.

### Post-amendment gate

After a review-driven plan, spec, or outline edit, classify only the amendment against the artifact state the review saw. Never inherit the entry mode.

| Gate | Use when | Retry |
|---|---|---|
| **Small** | Meaning did not change: spelling, formatting, an invalid citation, command form, or another literal correction; no task meaning, file-set, dependency, wave, AC/decision coverage, or outline meaning changed | Run only the deterministic checks the amendment can affect |
| **Medium** | Small does not fit; the affected surface is clear; no more than 2 tasks and 2 semantic seats are affected; and no Full condition holds | Run M1–M6 once, then only the affected semantic seats; add the cross-wave seat only when ordering, dependencies, `Must land together with:`, or prerequisites changed |
| **Full** | A contract or shared interface changed; more than 2 tasks or at least 3 semantic seats are affected; the amendment spans multiple plan areas; or its evidence or blast radius is unclear | Re-run Full over the updated plan and spec |

Every retry receives the amendment, affected tasks/ACs/decisions/outline excerpts, and the settled-finding ledger. A reviewer may reopen a settled finding only when its cited lines changed or new evidence contradicts the recorded disposition; it must cite that change or evidence.

Cap the mechanical auto-fix and each semantic gap loop at one retry. A second failure escalates through that lane's `AskUserQuestion`; on a second ASK-lane failure, omit "Add tasks". The 0.80 bar matches execute-plan's Autonomy gate.

Before **Next step**:

1. **Mark the baseline:** append `- Plan review: <Full | Delta> — <N findings: disposition | 0 findings — clean>` under `## Waves`.
2. **Commit an existing-plan sync:** include the Step-5 sync edits and use `git commit -m "plan(NNN-slug): sync to spec changes"`.
3. **Commit any other review:** include its fixes and annotations with `git commit -m "plan(NNN-slug): review fixes"`.

**No review** skips the marker and commit because plan.md did not change.

### Step 7 — Offer to fold the spec/plan commits into one

This phase left several commits (spec, tech design, `waves created`, `review fixes`). Fold them now — once execute-plan sets `Base SHA`, rewriting history breaks it.

1. **Run** = contiguous commits back from HEAD whose subject carries `NNN-slug`/`spec-NNN`, or that touch only `meta/`; `BASE` = the commit before the run. Show the list. Skip the offer if any run commit is a merge or already on `@{upstream}`.
2. `git diff --name-only BASE..HEAD` —
   - **All under `meta/specs/NNN-slug/`** → `AskUserQuestion`: "Fold into one `spec+plan(NNN-slug):` commit (recommended)" / "Keep separate". Fold: `git reset --soft BASE && git commit -m "spec+plan(NNN-slug): <feature> — discovery, tech design, waves"`.
   - **Anything else** (list it) → `AskUserQuestion`: "Fold all" / "Fold only `meta/specs/`, rest as its own commit" / "Keep separate". Split: `git reset BASE`, then `git add meta/specs/NNN-slug/ && git commit`, then `git add -A && git commit`.

### Next step

Route via `AskUserQuestion` to **`execute-plan`** (default — waves are ready to execute) or "Stop here".

## Rules

- **Sequencing only.** No approach selection, no structure design, no feasibility checks — if those look undone, route to `tech-design` rather than improvising.
- **No review/test/verification tasks.** Those belong to execute-plan's review-unit, final-review, and fix-verify gates.
- **Out-of-scope lives in the spec.** Don't restate it in the plan; cite the spec section if a boundary matters to sequencing.
- **Wave rules bend only where they say they bend.** Wave rule 3's `Must land together with:` is the one escape; never split a task across waves. A task that can't be parallelized gets its own wave.
