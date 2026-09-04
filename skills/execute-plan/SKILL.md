---
name: execute-plan
description: "Implement a feature by executing its wave-grouped plan.md. TRIGGER when: user says 'run the plan', 'execute the plan', or 'implement it'; a plan.md has unchecked waves ready to build."
---

# Execute Plan

## When to use

YES: `meta/specs/NNN-slug/` has a `plan.md` with wave-grouped `[ ]` tasks (from write-plan) ready to execute; resuming a partially executed plan.

NO: no waves yet (use `write-plan`); design undecided (use `tech-design`); plan Status is already FROZEN.

## Protocol

### Input

- **Spec folder**: `meta/specs/NNN-slug/` (or a path to either file in it). Reads both `plan.md` (waves, log) and `spec.md` (ACs, D-NNN-XX decisions, Structure Outline).

### Execution model

**Parent agent (orchestrator):**
- Reads plan + spec, dispatches subagents, runs review gates, commits.
- Never reads source code files or writes code itself (the Step 5 docs sync is the exception — durable-docs-update runs inline and manages its own reading).
- Edits `spec.md` ONLY in Step 2.5 (promotion) and Step 6 (ship gate).

**Use the model the user requests. Otherwise, choose the implementer model per logical task:**

- **Sonnet — only when every condition holds:**
  - The edit is fully specified and follows an existing pattern.
  - Its assigned files are known and bounded.
  - It requires no unresolved choice about behavior, architecture, or contract.
  - It touches no schema, migration, auth, security, concurrency, payments, destructive data, or public/shared/external interface.
  - The dispatch names a check that can verify the result.
- **Opus — otherwise.** Use Opus when any Sonnet condition fails or is unclear.
- **Grouped work:** classify all work assigned to one subagent together; any Opus condition selects Opus.
- **Escalation:** when the orchestrator selected Sonnet, upgrade to Opus if new scope, coupling, or ambiguity appears. Never downgrade during the same task.
- **Authority:** model choice never bypasses decision gates or reduces review and verification.

**Subagents (implementers):**
- Receive: plan file path + their assigned task IDs; the `AC-NNN-XX` texts their tasks cite and the relevant Structure Outline excerpt (both copied from spec.md into the dispatch — they don't hunt the spec); any prior `[Implementation]` log entries touching their files (the outline is frozen — the log is where reality lives).
- Before the first write, resolve each target path and read its governing repository instructions and Claude path rules in `.claude/rules/` whose quoted `paths:` globs match it; use the intended path for a new file.
- Implement the assigned work; read existing code in affected areas.
- Code comments and test names:
  - Write a comment only for what the code can't say — a constraint, assumption, or coupling; the comment carries the fact in prose.
  - The dispatch's `D-NNN-XX`/`AC-NNN-XX` ids may label a comment beside its fact.
  - Never cite task ids, wave numbers, or finding ids in code — use a date if "when" matters.
  - A test that satisfies an AC carries the id in its name: `test_acNNN_XX_...`.
- Return: `{ files_changed: [paths], summary: string, discoveries: [{ type: "[Implementation]" | "[AC-affecting]" | "[Future]", note: string }] | null }`
- A deviation from the Structure Outline IS an `[Implementation]` discovery — there is no separate channel. If the task body conflicts with a copied current `AC-NNN-XX` text, the AC text is authoritative: implement to the AC and return the conflict as an `[AC-affecting]` discovery — never silently reconcile it.
- A file assigned to another subagent in the same wave must NOT be edited — return `{ needs_scope_expansion: true, additional_files: [paths], justification: string }` instead; the parent reassigns and re-dispatches. Once per wave: a second `needs_scope_expansion` in the same wave stops the reshuffle — collapse the colliding tasks into ONE subagent and run them serially (the same escape wave rule 3 uses for declared overlap).
- Keep Git mutations scoped to assigned files: never run `git stash`, `git checkout -- .`, `git reset`, or another command that changes the whole tree.
- Scope every Git read to assigned paths.
- Read a committed baseline without changing shared state with `git show HEAD:<path>`.
- No file contents in returns — paths and summaries only.

### Autonomy gate — resolve before asking

This gate governs any mid-run `AskUserQuestion` on a **reversible code decision**. Out of scope (always ask): crash/timeout retry, verification-fail, contract amendment (→ Step 2.5), new-feature placement (→ Step 6.2), any destructive act. Auto-resolve only when the decision is **grounded** — it traces to a named source (a `D-NNN-XX`, `AC-NNN-XX`, cited spec line, or existing code at a `file:line`), never your reasoning alone — and you are **≥ 0.80 confident** it fits this case. Then apply the disposition you'd otherwise recommend — the spec-mandated action (Tier 1) or the solver's fix (Tier 2) — and log it (below). A human-gated or not-diff-provable concern (a visual `D-NNN-XX`) never auto-fixes: log it as a `- P2`/`P3 [deferred]: F-NNN-XX — ...` entry in `## Wave Reviews` (the anchor form on the P2/P3 row of Step 2) with the recommendation — Step 6.2 triages it at the ship gate.

Ground the decision in tiers; stop at the first that resolves:

- **Tier 1 — Spec (parent, no subagent).** The answer sits in a cited `AC-NNN-XX`, locked `D-NNN-XX`, plan task, or the frozen Structure Outline. A literal match is ~1.0 confident; applying a *principle* to this case is a judgment — score it honestly. ≥ 0.80 → proceed; below it, fall to Tier 2, don't ask yet.
- **Tier 2 — Investigation (two read-only subagents, serial).** Dispatch a **finder** (Sonnet): *"Does a source directly answer this — a `D-NNN-XX`/`AC-NNN-XX`, another spec line, or existing code? Return `{ source, excerpt }` only if it directly answers; merely related → `source: none`."* `source: none` → escalate. Else dispatch a **solver** (Opus): *"From that source + the spec, return `{ fix, confidence, needs_decision_change }` — the simplest fix consistent with the locked decisions. Set `needs_decision_change` if the fix contradicts the `D-NNN-XX`'s rationale, needs a decision changed, re-architects, or invents a default for behavior no source specifies."* `confidence ≥ 0.80` and not `needs_decision_change` → proceed; else escalate. The solver only proposes — the fix runs through the normal wave / fix-verify-loop path.
- **Tier 3 — Escalate.** The step's `AskUserQuestion`, options with a recommendation, carrying the spec ref + finder/solver notes so the user decides fast.

Log every auto-resolve to `## Execution Log` under the wave's `### Wave N — [date]` heading: `- [auto-resolved]: <decision> — per <source>, conf 0.NN`. These are code-only and still pass Step 2/4 review — the backstop for a mis-scored proceed.

### Review policy — choose the smallest safe gate

The orchestrator chooses each review unit without asking. A review unit changes review timing, not execution state — every wave keeps its own dispatch, checkbox flips, and commit.

- **One wave — default.** Use when any two-wave condition fails or risk is unclear.
- **Two waves — use only when all conditions hold:**
  - Both adjacent waves are low-risk and reversible.
  - Together they name no more than 4 files.
  - Any dependency between them is local and explicit.
  - Neither touches schema, migrations, concurrent writes, auth, permissions, security boundaries, payments, destructive data paths, or a public/shared/external interface.
  - No earlier review debt is pending.

Before dispatch:

- **Marker:** append `- Review pending: Waves N–M — base <SHA>` under `## Wave Reviews`; use `N–N` for one wave.
- **Base:** use `HEAD` before the unit's first implementation commit.
- **Size:** count implementation files and lines; exclude spec-folder bookkeeping unless it changes the contract.

After each wave in a two-wave unit:

- **Close early:** shorten the marker to the completed prefix and review now when the implementation diff exceeds 4 files or 200 changed lines, or the wave produces an AC-affecting discovery, decision/outline drift, scope expansion into the next wave, or any high-risk surface above.
- **Continue:** otherwise execute the second wave before reviewing the unit.

### Step 1 — Wave execution loop

1. Read the plan fresh — fix-verify-loop or a promotion may have changed it. Extract `PLAN_SLUG` from the folder name (`meta/specs/014-daily-digest/` → `014-daily-digest`). If the plan header's `**Base SHA:**` is already set (a resume), adopt it as `PLAN_BASE_SHA` and skip the rest of this item. Fresh start only: first the staleness check — `LAST=$(git log -1 --format=%H -- meta/specs/<slug>/plan.md)`; skip it if `LAST` is empty (plan never committed), else run `git diff $LAST -- meta/specs/<slug>/spec.md` (working tree included, so uncommitted spec edits count); any output means the plan was sequenced against an older spec — stop and route to write-plan. Then check `git status --porcelain` excluding the spec folder's files (they fold into the Wave 1 commit); if dirty, `AskUserQuestion`: "Stash and proceed (Recommended)" / "Commit and proceed" / "Abort". Then record `PLAN_BASE_SHA=$(git rev-parse HEAD)` and set the plan header's `**Base SHA:**` line.
2. On session re-entry, resolve any `Review pending:` marker before new implementation:
   - **Completed wave exists:** shorten the marker to the completed prefix and review it through Step 3.5.
   - **No completed wave; assigned files clean:** resume its first unchecked wave.
   - **No completed wave; assigned files dirty:** `AskUserQuestion`: "Resume from the partial changes (Recommended)" / "Stash them and restart the wave" / "Abort plan". On Resume, dispatch one recovery implementer with the unchecked task IDs and existing diff to reconcile and finish the wave; use the user-requested model, or Opus by default.
3. Find the next `### Wave N` with any `[ ]` tasks. Resuming mid-wave → dispatch only unchecked tasks. No unchecked tasks anywhere → resolve any pending review, then run Step 4; during a Step 6.2 ship-debt phase, return to its **Review coverage** item instead.
4. With no pending unit, choose one or two waves by the Review policy and append its pending marker. With a pending unit, use its first unchecked wave.
5. Launch one subagent per logical task in the wave, in parallel, using the model selected above. `Must land together with:` tasks go to one subagent and are classified together.
6. Collect results. Crash/timeout → `AskUserQuestion`: "Retry this item (Recommended)" / "Skip and mark dependents blocked" / "Abort plan". Don't commit a partial wave.
7. Append each returned discovery to the plan's `## Execution Log` under a `### Wave N — [date]` heading, with its type tag (`[Future]` entries take the next `F-NNN-XX` — Plan anchors, skills/write-plan/SKILL.md). **Any `[AC-affecting]` discovery → run Step 2.5 now, before committing the wave.** Other blocking issues → run the **Autonomy gate**; on escalation, `AskUserQuestion`: "Resolve and retry (Recommended)" / "Skip and mark dependents blocked" / "Override and proceed" / "Abort plan".
8. Flip the wave's tasks to `[x]` — the flip must land IN the wave commit (it's the resume state).
9. Stage and commit: `git add [wave files + plan] && git commit -m "plan(<PLAN_SLUG>): Wave N complete — [brief summary]"`. On Wave 1, also `git add` any uncommitted spec.md (Step 1.1's fold-in); if `git status --porcelain` on the spec folder shows anything but spec.md/plan.md, leave those unstaged and tell the user.
10. If the review unit is complete or an early-close condition fired, run Steps 2–3.5. Otherwise return to Step 1 for its second wave.
11. Return to Step 1 after the review unit closes.

### Step 2 — Review unit + Drift check

Read `REVIEW_BASE` from the pending marker, set `REVIEW_HEAD=$(git rev-parse HEAD)`, and spawn every `code-reviewer` against `git diff $REVIEW_BASE..$REVIEW_HEAD`. Review the whole unit, never task or commit slices, so cross-task and cross-wave bugs stay visible. Reviewer count scales with the unit's actual size and risk:

- **R1 — contract & correctness** — always. Criteria below.
- **R2 — cross-task & regression** — add for every Step 6.2 ship-debt unit, when the unit spans two waves, or when its implementation diff exceeds 4 files or 200 changed lines, counting size by the Review policy. Charter: *"Find bugs from how this review unit's changes interact — a signature, shared state, or config one task changed that another task or an existing caller now depends on. An empty result is valid."*
- **R3 — data integrity** — add whenever the diff touches schema, migrations, or concurrent writes (any size). Charter: transactions, races, partial writes, migration reversibility — Step 4's data-integrity seat runs these plan-wide.

Merge findings (dedup by file + line-span + root cause, keep max severity) before the table below; at most three reviewers.

- **Criteria (R1)**: the code-gated `AC-NNN-XX` texts cited by the unit's tasks (copied from the spec). `[human-gated:]` ACs are excluded — they can't be verified against a diff (the ship gate routes them to Post-ship verification). Plus standard correctness/security/edge-case analysis.
- **Drift question** (posed to R1, whose dispatch also carries the unit's Structure Outline excerpts — the same ones the implementers got): *"Does this diff contradict any locked `D-NNN-XX` in spec.md, or deviate from the Structure Outline excerpt? Cite the decision ID or outline element and the contradicting hunk."* The outline half is the independent net — implementers self-report only the deviations they notice.
- **Scope**: this review unit's diff only, not the whole plan. Single pass, no verifier; findings have `verdict: null` and `validated_by: "reviewer"`.

| Finding | Action |
|---|---|
| None | Record `0 findings — clean` beside the pending marker; continue to Step 3.5. |
| **Drift hit** (diff contradicts a `D-NNN-XX`) | Run the **Autonomy gate**. Grounded + reversible (the `D-NNN-XX` is the source) → conform without asking: confirmed P1 with `validated_by: "reviewer"` → Step 3, log `[auto-resolved]`. A human-gated/visual `D-NNN-XX` isn't diff-provable → log it as a `- P2`/`P3 [deferred]:` entry (P2/P3 row below), don't ask. Only if the gate escalates (not confident, or the reviewer challenges the decision) → `AskUserQuestion`: "Fix code to conform to the D-NNN-XX (Recommended)" / "The decision is wrong — supersede it" (→ Step 2.5) / "Accept with risk note in Wave Reviews". |
| **Outline-drift hit** (diff deviates from the outline; no `D-NNN-XX` or AC contradicted) | A detail delta the implementer didn't self-report: append it as an `[Implementation]` entry to the Execution Log and continue — no pause. (A deviation that also contradicts an `AC-NNN-XX` or locked `D-NNN-XX` takes the Drift-hit / Step 2.5 path instead.) |
| P0/P1 | Set `verdict: "confirmed"`, `validated_by: "reviewer"`, and evidence from the review unit → fix-verify-loop (Step 3). |
| P2/P3 not fixed | Log in `## Wave Reviews` as `- P2 [deferred]: F-NNN-XX — ...` / `- P3 [deferred]: F-NNN-XX — ...` with the why — line-leading `- ` required: the ship-gate anchor is `^- P[0-9]+ \[deferred\]:`, and the F id follows the colon (Plan anchors, skills/write-plan/SKILL.md). |

Write the unit's findings tally and Drift result beside its pending marker once Step 3 outcomes are known. Step 3.5 replaces that marker with the completed review record. Only pause where the table says so.

### Step 2.5 — Promote an [AC-affecting] discovery (user-gated)

Triggered the moment an `[AC-affecting]` discovery is logged (Step 1.7) or a Drift hit resolves to "the decision is wrong" (Step 2). Never auto-apply — this amends the contract.

1. **Log first**: write the `[AC-affecting]` Execution Log entry if none exists — the Drift path arrives without one, and the marker must have an entry to count against. It states the contradiction and evidence.
2. **Present** via `AskUserQuestion`: the contradiction, the evidence, the proposed spec change (revised `AC-NNN-XX` text and/or `D-NNN-XX` supersession with new decision block). Also grep `plan.md` for unchecked `- [ ]` tasks citing the revised `AC-NNN-XX` or the superseded old id and list each (title + first body line) in the same question with a disposition: keep / amend / drop — re-pointing a citation updates a label, not the task's instructions. Apply amend/drop edits to `plan.md` as part of the promotion commit. Options: "Promote to spec (Recommended)" / "Adjust the proposal" / "Abort plan".
3. **On approval, edit the spec(s)** (AC line / decision block formats are canonical in `skills/product-interview/SKILL.md`'s spec template). Worked example: old id `D-014-03`, new id `D-014-11`.
   - Revise the `AC-NNN-XX` in place, appending `*(revised per D-NNN-XX)*` — ACs are the live contract, one current truth; the why lives in the decision trail.
   - Supersede the old decision in the spec file that owns its id — a cross-spec supersession flips a prior spec's block: set `Status: superseded`, add `Superseded-by: <new id>`. Touch nothing else in the block.
   - Append the new block to the current spec's spec.md, with the current spec's `NNN` and the next `XX` (highest existing `XX` in this spec + 1) — `Supersedes: <old id>`, rationale citing the evidence and `plan Wave N`. Heading type marker: inherit the superseded block's `[product]`/`[tech]`, or `[tech]` if the change is build-originated (marker is advisory — see the canonical Decisions comment).
4. **Classify the supersession, then re-point.** Additive = every claim under the old id stays true; behavior-changing = some claim is now false. Either way, grep `plan.md` for the old id and re-point citations to the new id. A behavior-changing supersession also sweeps the repo: grep the old id across code and docs, dispatch ONE subagent with the hit list and the implementers' comment rules; per hit —
   - still true → leave it (the id resolves through the Status line);
   - now false → rewrite the prose to the current fact and re-point the label to the new id;
   - pointless → delete the comment.

   The subagent returns `files_changed` to stage in the promotion commit.
5. **Close the log entry**: append `promoted-to-spec [date]: AC-NNN-XX revised, <old id> superseded by <new id>.` — ALWAYS lowercase and hyphenated; this is the ship gate's count-compare anchor (Plan anchors, skills/write-plan/SKILL.md). Never write the hyphenated token outside a real marker (unhyphenated prose is safe — the hyphen is what the gate counts).
6. Commit: `git add [spec folder(s)] [swept files] && git commit -m "plan(<PLAN_SLUG>): promote [AC-affecting] — <old id> superseded by <new id>"`. Resume where execution stopped.

### Fix-loop packet

Every `fix-verify-loop` invocation in Steps 3–4 passes:

- **Findings:** Confirmed P0/P1 findings with their `validated_by` value and verdict evidence.
- **Artifact paths:** The call's approved base paths below. A finding or its evidence may identify another path, but editing it requires the fix-loop scope-expansion gate.
- **Criteria:** The call's governing criteria below plus each finding's criterion.

| Call | Base artifact paths | Governing criteria |
|---|---|---|
| Review unit — Step 3 | Review-unit files | ACs cited by the unit |
| Regression review — Step 3.5 | Review-unit files plus files in the reviewed fix commit | ACs cited by the unit |
| Final review — Step 4 | Files changed in `$PLAN_BASE_SHA..HEAD` | Code-gated ACs relevant to the findings |
| Verification failure — Step 4 | Files changed in `$PLAN_BASE_SHA..HEAD` | The expected project-verification result and relevant code-gated ACs |

### Step 3 — Review-unit fix-verify-loop

P0/P1 findings (incl. confirmed Drift fixes) → invoke the **fix-verify-loop** skill with the [Fix-loop packet](#fix-loop-packet). On a returned escalation, `AskUserQuestion`: "Retry with guidance (Recommended)" / "Accept and defer" (→ log `[deferred]` in Wave Reviews) / "Skip finding" / "Abort plan".

Commit fixes separately: `plan(<PLAN_SLUG>): Waves N-M fixes — [summary]` (use `Wave N` for a one-wave unit).

### Step 3.5 — Review fixes commit (regression check)

If Step 3 produced a fixes commit, spawn `code-reviewer` scoped to its diff when the fix reached outside the review unit's files (`git show --name-only --format= HEAD` vs the unit file-set) or the diff is sizeable — directionally 2+ files or ~50 lines; otherwise skip the review. Clean or P2/P3-only → continue (deferred entries logged as in Step 2). P0/P1 → set `verdict: "confirmed"`, `validated_by: "reviewer"`, and evidence from the regression review → fix-verify-loop with the [Fix-loop packet](#fix-loop-packet) → commit as `Waves N-M regression fixes` (`Wave N` for one wave). Regression-fix commits are not re-reviewed here; Step 4 therefore selects Full.

Set `Fix coverage` to `none` when Step 3 made no commit, `reviewed through <SHA>` when every fix commit received this regression check, and `unreviewed` when any fix or regression-fix commit did not.

Close the unit by replacing its pending marker and adjacent provisional lines with:

```markdown
### Review unit: Waves N–M
- Range: <REVIEW_BASE>..<REVIEW_HEAD>
- Seats: R1[, R2, R3]
- AC evidence: <AC-NNN-XX PASS — file:line; ... | none>
- Findings: <N findings: M fixed, D dropped by pre-gate, E demoted | 0 findings — clean>
- Drift: <none | disposition>
- Fix coverage: <none | reviewed through <SHA> | unreviewed>
```

Keep every anchored deferred entry directly below the completed block; marker replacement never removes deferred findings.

### Step 4 — Final review

**Land Step-4 fixes.** After any Step-4 `fix-verify-loop` invocation:

- **Resolve.** Resolve every escalation and staged-change choice.
- **Match.** When accepted staged changes remain, confirm the path set from `git diff --staged --name-only` exactly matches the accepted `files_changed`; resolve any mismatch before continuing.
- **Commit.** Before the next review or verification step, commit the matched paths as `plan(<PLAN_SLUG>): final review fixes — [summary]` or `plan(<PLAN_SLUG>): verification fixes — [summary]`. With no accepted staged changes, continue without a commit.

**Review Step-4 fixes.** After **Land Step-4 fixes**, continue when no fix was committed; otherwise classify the commit from its diff:

| Gate | Use when | Action |
|---|---|---|
| **Small** | Every condition holds: at most 2 files and 100 changed lines; one code path; no Review-policy high-risk surface; clear affected criteria, callers, and consumers. | Invoke `two-pass-review` over the fix commit, its affected callers and consumers, and only the ACs or decisions the fix can change. |
| **Medium** | Small does not fit; at most 3 affected final-review seats, including Seat B, can be named; no Full condition holds. | Run the affected seats in parallel over the fix commit and affected surrounding code. Merge P0/P1 findings, then verify them once under the final-review **Verify** rule. |
| **Full** | Any condition holds: more than 5 files or 400 changed lines; a Review-policy high-risk surface; a contract, decision, or outline change; 4 or more affected seats; unclear evidence or blast radius. | Re-run Full over the updated `$PLAN_BASE_SHA..HEAD` diff. |

Small and Medium report only regressions caused by the fix, reuse unaffected final-review evidence, and return confirmed P0/P1 findings to the final-review fix rule below.

After all waves and pending reviews close, select code-gated ACs with `grep -E '^- \*\*AC-[0-9]+' spec.md | grep -F '[code-gated]'`, then choose the final mode over `git diff $PLAN_BASE_SHA..HEAD`:

Use **Integration** only when all conditions hold:

- Every wave belongs to a completed review unit.
- Every fix commit has review coverage.
- Every confirmed P1 was fixed; none was deferred or skipped.
- No P0 occurred; at most two confirmed P1s occurred, all in one review unit.
- No regression review found another P1.
- No decision or outline drift occurred.
- No AC-affecting promotion occurred.
- The build touched none of the Review policy's high-risk surfaces.
- The spec has no more than 11 code-gated ACs.
- The blast radius is clear.

Use **Full** when any Integration condition fails or its evidence is unclear, including any deferred or skipped P1, unreviewed fix, P0, more than two P1s, P1s across units or in regression review, drift, promotion, high-risk work, or unclear blast radius.

**Integration review:** spawn one `code-reviewer` over the full diff, licensed to inspect unchanged callers and consumers. Give it every code-gated `AC-NNN-XX`, every `D-NNN-XX` block, and the Structure Outline. Charter: *"Return per-AC PASS/FAIL evidence, then find cross-wave or caller regressions and whole-build decision/outline drift that review-unit passes could not see. Do not repeat isolated implementation commentary already settled in completed review units. An empty finding set is valid."*

**Full review:** run the panel below. For either mode, the two-pass-review protocol rules apply: zero P0/P1 across all seats → skip the verifier and present the clean result with `checks_run`. If the verifier rejects every finding, record the disagreement and continue with zero confirmed P0/P1 findings; do not start another review automatically.

Dispatch in parallel — every seat is a `code-reviewer` agent receiving the full `$PLAN_BASE_SHA..HEAD` diff:

- **Seat A — contract.** Criteria: every code-gated `AC-NNN-XX` (mechanical selection grep above) + standard correctness/security/edge-case analysis.
- **Seat B — regression / blast radius.** Scope: the changed files PLUS their unchanged callers/consumers — explicitly licensed to read outside the diff. Criteria: "Find behavior outside this feature that the diff breaks — callers and consumers of changed signatures, shared state or config, existing behavior no AC describes. Whether the feature's own ACs pass is Seat A's job, not yours. An empty result is a valid result."
- **Seat C — decision & outline drift.** Receives ALL `D-NNN-XX` blocks from spec.md (including superseded, to catch reversion) + the frozen Structure Outline. Criteria: "Does the whole diff contradict any locked `D-NNN-XX` or deviate from the frozen Structure Outline? Cite the decision or outline element and the contradicting hunk. A contract-level contradiction is a Step 2.5 promotion, not just a fix. An empty result is a valid result."
- **Conditional — AC clusters.** If code-gated ACs ≥ 12: partition them into clusters of ≤ 8 and dispatch one Seat-A-style reviewer per cluster (its AC subset + the full diff); Seat A then carries only the correctness/security mandate, no ACs.
- **Conditional — data integrity.** If the diff touches schema, migrations, or concurrent writes: one more reviewer chartered on transactions, races, partial writes, and migration reversibility.

**Merge** (parent): dedup by file + line-span + root cause; keep the max severity; note which seats flagged each finding.

**Verify**: ONE `verifier` agent over the merged finding set — never one per seat. Set every adjudicated finding's `validated_by` to `verifier`. If the deduped P0/P1 findings exceed 4, batch the verification by relatedness (shared files, symbols, or call chains — never split findings that reference the same code path) and stitch the verdicts back into one envelope.

Confirmed P0/P1 → **fix-verify-loop** with the [Fix-loop packet](#fix-loop-packet). A finding that *contradicts* an `AC-NNN-XX` or locked `D-NNN-XX` (not just fails it) is a contract break: log it as an `[AC-affecting]` Execution Log entry and run Step 2.5 — final review has no wave commit, but promotion works the same.

- **Fix:** apply **Land Step-4 fixes**, then **Review Step-4 fixes**.
- **Promotion:** any Step-2.5 promotion forces the post-fix gate to **Full** because Integration requires a stable contract.
- **Retry limit:** run one post-fix gate automatically. If resolving that gate changes code or the contract again, finish the resolution, then `AskUserQuestion`: "Run another post-fix review (Recommended)" / "Abort plan".
- **Completion:** Small or Medium merges its evidence with the unaffected prior evidence; Full replaces the prior result. Record only a final state covered by that evidence. A later Step 6.2 ship-debt phase keeps the record valid only by merging review evidence for every added code change.

**Verification run (conditional).** After final-review fixes pass their post-fix gate, the parent runs the project's test/verification command once over the final state, if one exists — reading PASS/FAIL only, never source.

- **No command** → skip.
- **Pass** → note `verification: passed`.
- **Fail, or can't run** → `AskUserQuestion`: "Fix" / "Accept (pre-existing or intended)" / "Abort". You classify; the parent never reads the test to guess why. "Fix" → create a confirmed finding with `validated_by: "machine"` and evidence naming the exact command and observed failure; state only what the result proves, invoke fix-verify-loop with the [Fix-loop packet](#fix-loop-packet), apply **Land Step-4 fixes** and **Review Step-4 fixes**, then run verification again. "Accept" → log an accepted risk in the `### Final review` block, carried into the completion record.

Record the selected mode, per-AC PASS/FAIL evidence, and the verification-run outcome in a `### Final review` block appended to `## Wave Reviews` — file-backed so it survives a session boundary; Step 6.3 copies it into the spec.

### Step 5 — Comments and durable docs

Route before the sweep:

- **Already complete.** If the `### Final review` block contains `**Durable-docs phase:** complete`, continue to Step 6 without rerunning the sweep.
- **Untriaged ship debt.** If any `[Future]` or `[deferred]` entry lacks a `**Ship-debt triage:**` disposition, write `**Durable-docs phase:** pending` in the `### Final review` block and enter Step 6.2. Return here after the ship-debt phase closes.
- **Ready.** Otherwise, write `**Durable-docs phase:** pending` unless it already exists, then run one final sweep over the full plan diff.

Invoke the **durable-docs-update** skill via the Skill tool inline. It sweeps the comments, syncs the docs, and reports both. Pass:
- **scope** — `$PLAN_BASE_SHA..HEAD` (Mode B);
- **discoveries** — the typed Execution Log entries;
- **context** — the spec's Background + ACs;
- **spec** — the `spec.md` path, so it mines the locked `D-NNN-XX` decisions as candidates.

Commit only the files durable-docs-update changed: `git add [those paths] && git commit -m "plan(<PLAN_SLUG>): durable docs sync"` — `plan.md` may hold unstaged Wave-Review text that must not ride along. Replace the pending marker with `**Durable-docs phase:** complete`. This step runs once after the last code phase and before the Completion record.

### Step 6 — Ship gate

Run the plan's `## Ship Gate` checklist; every box must be resolved before freezing.

1. **Promotion check (count-compare, Execution-Log-scoped)**: `sed -n '/^## Execution Log/,/^## Wave Reviews/p' plan.md | grep -c '^- \[AC-affecting\]'` must equal the same slice piped to `grep -ci 'promoted-to-spec'`. Any shortfall → run Step 2.5 for the unmarked entries now; an unpromoted contract break fails the gate.
2. **Triage every untriaged `[Future]` and `[deferred]` entry:**

   **Analyze.** An entry is triaged when its `F-NNN-XX` id has a recorded disposition under `**Ship-debt triage:**` in the `### Final review` block. Before asking, write `**Ship-debt phase:** triage` there so an interruption resumes this item. Use one read-only subagent per four untriaged entries, capped at four subagents: `min(4, ceil(entry_count / 4))`. Split the entries evenly. Each subagent verifies its entries against the final code, spec, and review evidence, then returns one `ShipDebtAssessment` per entry. With no untriaged entries and no recorded `fix-now` disposition awaiting a task, replace a `triage` marker with `closed`; a pending durable-docs phase returns to Step 5, otherwise continue to item 3.

   ```
   ShipDebtAssessment {
     id: "F-NNN-XX",
     status: "valid" | "stale" | "unclear",
     evidence: string,
     status_confidence: 0.0-1.0,
     recommendation: "fix-now" | "defer" | "future" | "drop",
     reason: string,
     recommendation_confidence: 0.0-1.0
   }
   ```

   **Ask.** Present the assessments in as few `AskUserQuestion` batches as the tool allows, with one independently selectable question per assessment. Put each recommended choice first and record every disposition in the `### Final review` block:

   ```
   **Ship-debt triage:**
   - <id> — <status> (<status_confidence>): <evidence>
     Recommendation: <recommendation> (<recommendation_confidence>) — <reason>
     Disposition: <fix-now | defer | future: destination | drop>
   ```

   | Choice | Use when | Result |
   |---|---|---|
   | `fix-now` | A valid defect or shipped hole fits the current contract and approved scope. | Add it to the ship-debt phase. |
   | `defer` | A valid shipped limitation will not be fixed now. | Record it under "Deferred / what this does NOT close". |
   | `future` | The item is a separate feature outside the current contract. | Ask the user where to place it; keep it visible and record its destination. |
   | `drop` | The item is stale or noise. | Let it die with the plan. |

   Record each answer immediately. After every entry has a disposition, enter the fix-now phase when any recorded `fix-now` item lacks a task; otherwise replace the phase marker with `**Ship-debt phase:** closed`; a pending durable-docs phase returns to Step 5, otherwise continue to item 3.

   **Fix-now phase.** Run at most one. If it has already run, omit `fix-now` from later questions.

   1. **Plan.** Set `SHIP_DEBT_BASE_SHA=$(git rev-parse HEAD)` and replace the phase marker directly with `**Ship-debt phase:** build — base <SHA>`. Append every recorded `fix-now` item that lacks a task using the canonical task format, the next stable `T` id, its existing `F-NNN-XX` id, and its governing `AC-NNN-XX` or `D-NNN-XX` citations; cite every AC whose outcome the fix can change. Group the tasks into dependency-ordered `### Wave N: Ship debt — <summary>` waves of at most five tasks; run independent tasks in parallel.
   2. **Build.** Run the normal wave dispatch, commit, and Steps 2–3.5 review rules through every appended wave; when no unchecked tasks remain, continue to **Review coverage** instead of Step 4.
   3. **Review coverage.** Re-run Step 4 in Full mode after any Step 2.5 promotion or decision/outline drift; otherwise re-run Step 4 only when a ship-debt review unit ends with `Fix coverage: unreviewed`.
   4. **Verify.** If Step 4 reran, use its verification result; otherwise run the project verification command with Step 4's no-command/pass/fail handling.
   5. **Close.** If Step 4 reran, replace the earlier `### Final review` block with its new record while preserving the phase marker and triage dispositions. Otherwise merge the ship-debt review units' evidence for every cited AC into that block and append the phase's verification result. Replace the phase marker with `**Ship-debt phase:** closed`; a pending durable-docs phase returns to Step 5, otherwise restart Step 6 at item 1. Later questions offer only `defer`, `future`, or `drop`.

   When a `future` item is manually placed in a text home, begin its copied text with `promoted from F-NNN-XX`.
3. **Write the spec's Completion record** (format canonical in `skills/product-interview/SKILL.md`'s spec template; copy, don't move — the plan keeps its log):
   - `Shipped: [date]`, Status Complete/Partial.
   - **Criteria results**: per-AC PASS/PARTIAL/FAIL with 1-line evidence from the `### Final review` block, updated after any Step 6.2 ship-debt phase. Honest — FAIL/PARTIAL when warranted.
   - **Post-ship verification**: manual test cases covering the whole feature (happy path, edges, error/empty states), derived from the spec's `## UX` section + ACs, each an unchecked `- [ ]` line written `steps → expected result`. Every human-gated `AC-NNN-XX` MUST appear as a `steps → expected` line led by `AC-NNN-XX:` — owed, not orphaned (the diff never verified them). Confirm coverage mechanically: `grep -E '^- \*\*AC-[0-9]+' spec.md | grep -F '[human-gated:'` (grep the open `[human-gated:` form — it carries the inline "how" text; a closed bracket matches nothing and silently drops every human-gated AC) — every hit needs a matching `AC-NNN-XX:` line. If nothing is human-observable: write `None — nothing manually observable`.
   - **Deferred / what this does NOT close**: every item selected `defer` in Step 6.2, with severity.
   - **Review filter stats**: one line aggregating the Wave Reviews tallies — findings dropped by fix-verify-loop's pre-gate and findings demoted, across all review units — so what the filter rejected stays visible.
4. **Run one orchestration-prose pass.** Invoke the `tighten-instruction` and `structure-prose` skills via the Skill tool, then relay both lenses to one **Sonnet** subagent. Run this pass once, after all parent-authored prose exists and before changing ship state.
   - **Scope:** only parent-authored prose in the plan's `## Execution Log` and `## Wave Reviews` (including `### Final review`), plus the spec's new Completion record.
   - **Shape only:** improve clarity and structure without changing meaning, evidence, decisions, statuses, or task state. Preserve every ID and checkbox line verbatim.
   - **Anchors:** record each count before the pass and verify it afterward; discard a file's edits if any count or form changes.
     - `[Implementation]`, `[AC-affecting]`, `[Future]`, and `[auto-resolved]` entries must still start `- [Tag]`.
     - `[deferred]` entries must still start `- P<severity> [deferred]:`.
     - Promotion markers must remain lowercase `promoted-to-spec`.
     - Ship-debt state must retain `**Ship-debt phase:** triage`, `**Ship-debt phase:** build — base <SHA>`, or `**Ship-debt phase:** closed`, plus each `Disposition:` line.
     - Durable-docs state must retain `**Durable-docs phase:** pending` or `**Durable-docs phase:** complete`.
5. Confirm every review, verification, docs, and ship-debt decision is resolved; run every applicable project check not already passed on the current state.
6. Flip spec `Status:` → `Shipped`. Check the plan's Ship Gate boxes, set plan `Status: FROZEN [date]`.
7. Commit: `git add [spec folder] && git commit -m "plan(<PLAN_SLUG>): ship — completion record, plan frozen"`.

### Step 7 — Report

The Completion record in `spec.md` is the durable summary — don't duplicate it. Report in this exact shape — a scan of this block is how the user learns what happened, so give substance to what they're knowingly carrying and counts to what was routinely handled:

```
**Build complete: [NNN-slug]**
- Built: [what shipped, one line]
- Tests: [passed | failed — accepted: why | no command]
- ACs: [n] PASS, [m] FAIL/PARTIAL — [name each non-pass | all pass]
- Spec changed mid-build: [old id → new id — what changed, one line each | none]
- Accepted risks (carried, not fixed): [one line each — see Wave Reviews | none]
- Deferred debt: [one line each, with severity | none]
- Handled autonomously: [N] outline deviations, [M] auto-resolved decisions (see Execution Log)
- Docs: [files touched | none needed]
- Post-ship verification (you verify): [each item, one per line | none]
```

(Counts write `0` when empty — a zero is information, not noise. A field with two or more items nests them as sub-bullets.)

### Resumability

- **Wave-granular via `[x]` checkboxes** — on resume, find the first wave with `[ ]` tasks, dispatch only those.
- **Ship-debt resume.** A `**Ship-debt phase:** triage` marker resumes Step 6.2 from the first entry without a recorded disposition. A `build — base <SHA>` marker restores `SHIP_DEBT_BASE_SHA`, materializes any recorded `fix-now` item without a task, then resumes the first unchecked Ship debt wave or **Review coverage**. A `closed` marker never offers another fix-now phase.
- **Durable-docs resume.** A `**Durable-docs phase:** pending` marker resumes Step 6.2 while ship debt is open and Step 5 after ship debt closes. A `complete` marker continues Step 6.
- **Pending review outranks unchecked work.** On session re-entry, close any completed prefix through Step 3.5; when none completed, resume or recover the first unchecked wave by Step 1.2's clean/dirty rule.
- **`PLAN_BASE_SHA`** recovers from the plan header's `**Base SHA:**` line; fallback: take the first `plan(<PLAN_SLUG>): Wave` commit (`git log --format=%H --grep="plan(<PLAN_SLUG>): Wave" --reverse | head -1`), then walk to its parent, skipping past any `plan(<PLAN_SLUG>): promote` commits — a Wave-1 promotion lands BEFORE the Wave-1 commit, and the base is the commit before all of them.
- **Promotion commits (Step 2.5) interleave safely** — wave state lives in the checkboxes, not the git history.
- **The flips are the resume authority** — checkbox flips land in their own wave's commit (Step 1.8-9); Wave-Review blocks and deferred entries are written to disk immediately and ride the next commit (fixes, next wave, or ship) — that lag is fine.

## Rules

- **One wave per commit.** A review unit contains one wave or two eligible adjacent waves; every wave keeps its own commit and resume checkbox state.
- **Typed tags are line-anchored grep targets.** Execution Log entries start `- [Implementation]`, `- [AC-affecting]`, `- [Future]`, or `- [auto-resolved]`; deferred Wave Review entries start `- P<severity> [deferred]:`. Exact forms live under Plan anchors in `skills/write-plan/SKILL.md`. Never log a discovery untagged or start a narrative line with a bracketed tag.
- **The spec's Structure Outline is frozen.** Keep mid-build design changes in this skill: contract changes use Step 2.5; implementation-only changes become `[Implementation]` entries that later-wave dispatches carry so subagents trust the log over the outline.
- **`*(revised per D-NNN-XX)*` is a human-readable convention, not a gate anchor** — nothing greps it; don't build checks on it.
- **ACs are verified by reviewers against diffs, never self-certified** by the implementing subagent.
- **Post-ship learnings route onward.** After the ship commit, new learnings go to the spec or durable docs, not back into the plan.
