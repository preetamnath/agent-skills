---
name: write-plan
description: "Sequence a locked spec into dependency-ordered, wave-grouped tasks. TRIGGER when: user says 'build the plan' or 'sequence this'; a spec needs slicing into parallel-safe waves."
---

# Write Plan

Slice a locked spec and its Structure Outline into atomic, dependency-ordered, wave-grouped tasks — create `plan.md` with its `## Waves`. Sequencing only: the WHAT and the design live in the spec; this skill decides order and parallelism.

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

If a lock grep hits, stop and name the open decisions/clarifications — route to `product-interview` (product/UX) or `tech-design` (technical). If the outline check misses, route to `tech-design`. If both `### Files touched` and the `Draft` grep hit, the WHAT was reopened after design and the outline is stale — route to `tech-design` (its resume re-runs from Step 2). (A fresh `Draft` has no outline, so `Draft` + an outline means reopen — capitalized, header-only; case-split rule 2.)

Trivial-skip exception: for a trivial change with one obvious implementation, offer via `AskUserQuestion` — "Skip tech-design — trivial" / "Route to tech-design". On Skip, put `- **Outline:** skipped (trivial; user-approved)` as plan.md's last header line — reviewer criterion S2 then auto-passes.

### Step 2 — Read context

Read `spec.md` (Requirements, Acceptance Criteria, Decisions, Structure Outline, Constraints). Skim the affected files only as needed to size and split work — the design thinking is already done; don't redo it. On the trivial-skip path there is no Structure Outline: read Requirements + ACs and skim the affected files instead.

### Step 3 — Identify work items

Break the structure outline (on trivial-skip: the spec's Requirements/ACs) into atomic tasks **for the locked design**. Each task:

- **One commit's worth of work** — completable in a single focused session.
- **Self-contained** — names the file(s) it touches, what to change, and why.
- **Verifiable** — you can tell when it's done.
- **Cited** — names the `AC-N` it satisfies and any `D-NN` it honors, by ID (`satisfies AC-2; per D-09`).

Coverage check both directions: an AC no task satisfies is a gap (add a task or flag it); a task citing nothing is scope creep (justify it against the spec or cut it). Human-gated ACs still get implementation tasks where code must exist for the later live check — note `human-gated: verified post-ship` on the citation. On the trivial-skip path, cite `AC-N` only — no technical `D-NN`s exist; don't invent citations to satisfy M6.

### Step 4 — Order by dependency + wave grouping

For each task: what must exist first, which files it touches, whether it can run in parallel.

**Wave assignment rules:**
1. No dependencies + no file overlap → same wave; mark each such task `[P]` (parallelizable).
2. Depends on another task → later wave.
3. Same file modified by multiple tasks → different waves (serialize), or `Must land together with:` in one subagent's hands.
4. Maximum **5** tasks per wave — it matches execute-plan's parallel-dispatch budget.
5. Prefer fewer, fatter waves over many single-task waves.

### Step 5 — Confirm and create plan.md

If `plan.md` already exists: `Status: FROZEN` → stop (shipped; new work = new spec). `Base SHA:` set or any `- [x]` task → execution has started; route to `execute-plan` — never re-sequence under a running plan. Otherwise (built, never executed) → `AskUserQuestion`: "Recreate from the current spec (overwrites)" / "Keep it; jump to Step 6 review" / "Stop".

Print the wave-grouped task list in chat (titles, files, citations, wave assignments, dependency links), then use `AskUserQuestion` only to collect the choice: "Approve and write the plan" / "Adjust". Recommended: approve.

On approval, create `meta/specs/NNN-slug/plan.md` from the canonical template below, then commit:

```
git add meta/specs/NNN-slug/plan.md && git commit -m "plan(NNN-slug): waves created"
```

(Use the slug from Input — execute-plan's resumability and promotion commits key on the same `plan(<slug>):` prefix; an unsubstituted placeholder breaks that chain.)

**CANONICAL plan.md TEMPLATE** (decision #22 — the one true copy; execute-plan inlines only the formats it appends and points here):

```markdown
# PLAN: [Feature name]

- **Created:** [YYYY-MM-DD]
- **Base SHA:** —          <!-- set by execute-plan before Wave 1; final-review diff range -->
- **Status:** Building     <!-- Building → FROZEN [date]. FROZEN marks the plan shipped; new work starts a new spec. -->
<!-- No Spec:/path back-links — the folder pairs the files (decision #14). Conditional: the trivial-skip path (Step 1) appends ONE more header line here marking the outline as skipped — exact form in Step 1; reviewer criterion S2 keys on it. -->

## Waves
<!-- WRITTEN BY write-plan. ≤5 tasks/wave. [P] = parallelizable within its wave. Every task cites AC-N / D-NN by ID. Task line format is load-bearing: checkbox + bold ID/title on one line (execute-plan flips the `- [ ] ` checkbox to `- [x] ` on each task line); details in indented sub-bullets. -->

### Wave 1: [short description]

- [ ] **T1 [P]: [short title]** — satisfies AC-1; per D-07
  - [what to change, which files, why]
- [ ] **T2 [P]: [short title]** — satisfies AC-3
  - [what to change, which files, why]

### Wave 2: [short description]

- [ ] **T3: [short title]** — satisfies AC-2; per D-09
  - [what to change, which files, why]
  - Depends on: T1

## Execution Log
<!-- APPENDED BY execute-plan; append-only. Discoveries logged at the moment found, one per line, with a type tag STARTING the line — the tags are line-anchored grep targets for the ship gate (see Plan anchors in skills/write-plan/SKILL.md). Types: Implementation = detail delta, stays here; AC-affecting = contradicts an AC or locked decision, STOP, user-gated promotion, entry must carry the promotion marker when resolved; Future = opportunity/limitation, triaged once at the ship gate. Guidance and prose here must NEVER start a line with a bracketed tag. -->

## Wave Reviews
<!-- APPENDED BY execute-plan, one block per wave: findings tally (`N findings: M fixed, D dropped by pre-gate, E demoted`), Drift result, deferred entries (line-anchored: `- P2 [deferred]: ...`); plus one final `### Final review` block (per-AC PASS/FAIL evidence + the verification-run outcome, for the ship gate). -->

## Ship Gate
<!-- RUN BY execute-plan after final review, before freezing. -->

- [ ] Every AC-affecting entry carries the promotion marker (count-compare check — see Plan anchors)
- [ ] Every Future entry triaged: hole-in-shipped-thing → spec "Deferred"; new feature → surfaced to user to place (must not die silently); noise → dies here
- [ ] Every deferred finding triaged: real limitation → spec "Deferred"; P3 noise → dies here
- [ ] Completion record written to spec (criteria results + post-ship verification + deferred + review filter stats), spec Status → Shipped
- [ ] Plan Status → FROZEN [date]
```

Tell the user the path. Use stable task IDs (`T1`, `T2`, ...) — they survive edits and reordering; reference dependencies by ID, never position.

### Plan anchors (load-bearing — exact forms matter)

Defined here beside the canonical template; written and grepped by execute-plan. POSIX ERE only.

```
^- \[AC-affecting\]            # execution-log entry, tag starts the line
^- \[Implementation\]          #   "
^- \[Future\]                  #   "
^- P[0-9]+ \[deferred\]:       # wave-review deferred finding
promoted-to-spec               # promotion marker, ALWAYS lowercase + hyphenated; case-insensitive grep
```

Rules: tags start the line — narrative prose and template guidance must never start a line with a bracketed tag, and must never contain the hyphenated token `promoted-to-spec` outside a real marker (the hyphen exists so natural prose — "promoted to spec" — can never collide with the anchor; write the unhyphenated phrase freely). Ship-gate promotion check is a count-compare: number of `^- \[AC-affecting\]` lines must equal the number of (case-insensitive) promotion-marker hits in the Execution Log — consumers scope BOTH counts to that section via `sed -n '/^## Execution Log/,/^## Wave Reviews/p'`.

### Step 6 — Plan review

Spawn the `reviewer` agent (`agents/reviewer.md`) against `plan.md` + `spec.md`. Always runs.

**Criteria** (instruct the reviewer to tag each finding with the exact ID — dispatch logic keys on the `M*`/`S*` prefix; untagged findings default to semantic):

Semantic:
- **S1**: Every `AC-N` in the spec is satisfied by ≥1 task (or explicitly marked post-ship-only).
- **S2**: The spec's Structure Outline covers every schema, signature, and component a task references. EXEMPT when the plan header carries the `- **Outline:** skipped` line — then S2 auto-passes.

Mechanical:
- **M1**: Every task names its file(s).
- **M2**: Every `Depends on:` points to an existing task in an earlier wave.
- **M3**: No file touched by multiple tasks in the same wave (unless `Must land together with:`).
- **M4**: No wave exceeds 5 tasks.
- **M5**: No task appears in multiple waves.
- **M6**: Every task cites ≥1 `AC-N` or `D-NN`, and every cited ID exists in the spec.

| Finding | Action |
|---|---|
| None | Append `- Plan review: 0 findings — clean` under `## Waves`. Proceed silently. |
| Mechanical (`M*`) | Auto-edit the plan to fix; re-run reviewer once. Still failing → escalate via `AskUserQuestion`: "Edit manually and re-review" / "Accept defect with risk note" / "Abort". |
| Semantic (`S*`) | `AskUserQuestion`: "Add tasks to close the gap" (loop Steps 3–5 for the gap — at Step 5's existing-plan guard, choose "Recreate from the current spec": regenerate including the gap tasks and commit again, a second `waves created` commit is fine; re-review once) / "Flag the AC back to the spec owner" / "Accept and note as known gap" / "Abort". Recommended: add tasks — a semantic finding is missing coverage, not noise. |

Cap auto-fix and gap-loop at 1 retry each.

### Next step

Route via `AskUserQuestion` to **`execute-plan`** (default — waves are ready to execute) or "Stop here".

## Rules

- **Sequencing only.** No approach selection, no structure design, no feasibility checks — if those look undone, route to `tech-design` rather than improvising.
- **Cite by stable ID** (`AC-2`, `per D-07`), never by line number or copied text.
- **Task line format is load-bearing.** Checkbox + bold ID/title on one line; details in indented sub-bullets. execute-plan flips the checkbox substring — keep it short and stable.
- **No review/test/verification tasks.** Those belong to execute-plan's gates (per-wave review, two-pass-review, fix-verify-loop).
- **Out-of-scope lives in the spec.** Don't restate it in the plan; cite the spec section if a boundary matters to sequencing.
- **Wave rules bend only where they say they bend.** Rule 3's `Must land together with:` is the one escape; never exceed 5 tasks/wave, never split a task across waves. A task that can't be parallelized gets its own wave.
