---
name: execute-plan
description: "Implement a feature by executing its wave-grouped plan.md. TRIGGER when: user says 'run the plan', 'execute the plan', or 'implement it'; a plan.md has unchecked waves ready to build."
---

# Execute Plan

Execute a wave-grouped `plan.md` via parallel subagents. The parent orchestrates — dispatching subagents, running review gates, promoting contract-affecting discoveries to the spec, committing — and never writes code itself. Ends by writing the spec's Completion record and freezing the plan.

## When to use

YES: `meta/specs/NNN-slug/` has a `plan.md` with wave-grouped `[ ]` tasks (from write-plan) ready to execute; resuming a partially executed plan.

NO: no waves yet (use `write-plan`); design undecided (use `tech-design`); plan Status is already FROZEN.

## Protocol

### Input

- **Spec folder**: `meta/specs/NNN-slug/` (or a path to either file in it). Reads both `plan.md` (waves, log) and `spec.md` (ACs, D-NNN-XX decisions, Structure Outline).

### Execution model

**Parent agent (orchestrator):**
- Reads plan + spec, dispatches subagents, runs review gates, commits.
- Never reads source code files or writes code itself (Step 6.2's docs sync is the post-ship exception — durable-docs-update runs inline and manages its own reading).
- Edits `spec.md` ONLY in Step 2.5 (promotion) and Step 5 (ship gate).

**Subagents (implementers):**
- Receive: plan file path + their assigned task IDs; the `AC-NNN-XX` texts their tasks cite and the relevant Structure Outline excerpt (both copied from spec.md into the dispatch — they don't hunt the spec); any prior `[Implementation]` log entries touching their files (the outline is frozen — the log is where reality lives).
- Implement the assigned work; read existing code in affected areas.
- Code comments and test names:
  - Write a comment only for what the code can't say — a constraint, assumption, or coupling; the comment carries the fact in prose.
  - The dispatch's `D-NNN-XX`/`AC-NNN-XX` ids may label a comment beside its fact.
  - Never cite task ids, wave numbers, or finding ids in code — use a date if "when" matters.
  - A test that satisfies an AC carries the id in its name: `test_acNNN_XX_...`.
- Return: `{ files_changed: [paths], summary: string, discoveries: [{ type: "[Implementation]" | "[AC-affecting]" | "[Future]", note: string }] | null }`
- A deviation from the Structure Outline IS an `[Implementation]` discovery — there is no separate channel. If the task body conflicts with a copied current `AC-NNN-XX` text, the AC text is authoritative: implement to the AC and return the conflict as an `[AC-affecting]` discovery — never silently reconcile it.
- A file assigned to another subagent in the same wave must NOT be edited — return `{ needs_scope_expansion: true, additional_files: [paths], justification: string }` instead; the parent reassigns and re-dispatches. Once per wave: a second `needs_scope_expansion` in the same wave stops the reshuffle — collapse the colliding tasks into ONE subagent and run them serially (the same escape wave rule 3 uses for declared overlap).
- No file contents in returns — paths and summaries only.

### Autonomy gate — resolve before asking

This gate governs any mid-run `AskUserQuestion` on a **reversible code decision**. Out of scope (always ask): crash/timeout retry, verification-fail, contract amendment (→ Step 2.5), new-feature placement (→ Step 5.2), any destructive act. Auto-resolve only when the decision is **grounded** — it traces to a named source (a `D-NNN-XX`, `AC-NNN-XX`, cited spec line, or existing code at a `file:line`), never your reasoning alone — and you are **≥ 0.80 confident** it fits this case. Then apply the disposition you'd otherwise recommend — the spec-mandated action (Tier 1) or the solver's fix (Tier 2) — and log it (below). A human-gated or not-diff-provable concern (a visual `D-NNN-XX`) never auto-fixes: log it as a `- P2`/`P3 [deferred]: F-NNN-XX — ...` entry in `## Wave Reviews` (the anchor form on the P2/P3 row of Step 2) with the recommendation — Step 5.2 triages it at the ship gate.

Ground the decision in tiers; stop at the first that resolves:

- **Tier 1 — Spec (parent, no subagent).** The answer sits in a cited `AC-NNN-XX`, locked `D-NNN-XX`, plan task, or the frozen Structure Outline. A literal match is ~1.0 confident; applying a *principle* to this case is a judgment — score it honestly. ≥ 0.80 → proceed; below it, fall to Tier 2, don't ask yet.
- **Tier 2 — Investigation (two read-only subagents, serial).** Dispatch a **finder** (Sonnet): *"Does a source directly answer this — a `D-NNN-XX`/`AC-NNN-XX`, another spec line, or existing code? Return `{ source, excerpt }` only if it directly answers; merely related → `source: none`."* `source: none` → escalate. Else dispatch a **solver** (Opus): *"From that source + the spec, return `{ fix, confidence, needs_decision_change }` — the simplest fix consistent with the locked decisions. Set `needs_decision_change` if the fix contradicts the `D-NNN-XX`'s rationale, needs a decision changed, re-architects, or invents a default for behavior no source specifies."* `confidence ≥ 0.80` and not `needs_decision_change` → proceed; else escalate. The solver only proposes — the fix runs through the normal wave / fix-verify-loop path.
- **Tier 3 — Escalate.** The step's `AskUserQuestion`, options with a recommendation, carrying the spec ref + finder/solver notes so the user decides fast.

Log every auto-resolve to `## Execution Log` under the wave's `### Wave N — [date]` heading: `- [auto-resolved]: <decision> — per <source>, conf 0.NN`. These are code-only and still pass Step 2/4 review — the backstop for a mis-scored proceed.

### Step 1 — Wave execution loop

1. Read the plan fresh — fix-verify-loop or a promotion may have changed it. Extract `PLAN_SLUG` from the folder name (`meta/specs/014-daily-digest/` → `014-daily-digest`). If the plan header's `**Base SHA:**` is already set (a resume), adopt it as `PLAN_BASE_SHA` and skip the rest of this item. Fresh start only: check `git status --porcelain` excluding the spec folder's files (they fold into the Wave 1 commit); if dirty, `AskUserQuestion`: "Stash and proceed (Recommended)" / "Commit and proceed" / "Abort". Then record `PLAN_BASE_SHA=$(git rev-parse HEAD)` and set the plan header's `**Base SHA:**` line.
2. Find the next `### Wave N` with any `[ ]` tasks. Resuming mid-wave → dispatch only unchecked tasks.
3. No unchecked tasks anywhere → final review (Step 4).
4. Launch one **Opus subagent** per task in the wave, in parallel. `Must land together with:` tasks go to one subagent.
5. Collect results. Crash/timeout → `AskUserQuestion`: "Retry this item (Recommended)" / "Skip and mark dependents blocked" / "Abort plan". Don't commit a partial wave.
6. Append each returned discovery to the plan's `## Execution Log` under a `### Wave N — [date]` heading, with its type tag (`[Future]` entries take the next `F-NNN-XX` — Plan anchors, skills/write-plan/SKILL.md). **Any `[AC-affecting]` discovery → run Step 2.5 now, before committing the wave.** Other blocking issues → run the **Autonomy gate**; on escalation, `AskUserQuestion`: "Resolve and retry (Recommended)" / "Skip and mark dependents blocked" / "Override and proceed" / "Abort plan".
7. Flip the wave's tasks to `[x]` — the flip must land IN the wave commit (it's the resume state).
8. Stage and commit: `git add [wave files + plan] && git commit -m "plan(<PLAN_SLUG>): Wave N complete — [brief summary]"`. On Wave 1, also `git add` any uncommitted spec.md (Step 1.1's fold-in); if `git status --porcelain` on the spec folder shows anything but spec.md/plan.md, leave those unstaged and tell the user.
9. Per-wave review (Step 2) through the review-fixes check (Step 3.5).
10. Return to 1.

### Step 2 — Per-wave review + Drift check

Spawn every `code-reviewer` against the **whole wave diff** (`git diff HEAD~1..HEAD`), never per-task slices — so a bug spanning two tasks stays visible. Reviewer count scales with size and risk:

- **R1 — contract & correctness** — always. Criteria below.
- **R2 — cross-task & regression** — add when the diff exceeds 4 files or 200 changed lines (`git diff HEAD~1..HEAD --stat`). Charter: *"Find bugs from how this wave's changes interact — a signature, shared state, or config one task changed that another task or an existing caller now depends on. An empty result is valid."*
- **R3 — data integrity** — add whenever the diff touches schema, migrations, or concurrent writes (any size). Charter: transactions, races, partial writes, migration reversibility — Step 4's data-integrity seat runs these plan-wide.

Merge findings (dedup by file + line-span + root cause, keep max severity) before the table below; at most three reviewers.

- **Criteria (R1)**: the code-gated `AC-NNN-XX` texts cited by this wave's tasks (copied from the spec). `[human-gated:]` ACs are excluded — they can't be verified against a diff (the ship gate routes them to Post-ship verification). Plus standard correctness/security/edge-case analysis.
- **Drift question** (posed to R1, whose dispatch also carries the wave's Structure Outline excerpts — the same ones the implementers got): *"Does this diff contradict any locked `D-NNN-XX` in spec.md, or deviate from the Structure Outline excerpt? Cite the decision ID or outline element and the contradicting hunk."* The outline half is the independent net — implementers self-report only the deviations they notice.
- **Scope**: this wave's diff only, not the whole plan. Single pass, no verifier; findings have `verdict: null`.

| Finding | Action |
|---|---|
| None | Append `- Review: 0 findings — clean` to `## Wave Reviews`. Don't pause — next wave. |
| **Drift hit** (diff contradicts a `D-NNN-XX`) | Run the **Autonomy gate**. Grounded + reversible (the `D-NNN-XX` is the source) → conform without asking: confirmed P1 → Step 3, log `[auto-resolved]`. A human-gated/visual `D-NNN-XX` isn't diff-provable → log it as a `- P2`/`P3 [deferred]:` entry (P2/P3 row below), don't ask. Only if the gate escalates (not confident, or the reviewer challenges the decision) → `AskUserQuestion`: "Fix code to conform to the D-NNN-XX (Recommended)" / "The decision is wrong — supersede it" (→ Step 2.5) / "Accept with risk note in Wave Reviews". |
| **Outline-drift hit** (diff deviates from the outline; no `D-NNN-XX` or AC contradicted) | A detail delta the implementer didn't self-report: append it as an `[Implementation]` entry to the Execution Log and continue — no pause. (A deviation that also contradicts an `AC-NNN-XX` or locked `D-NNN-XX` takes the Drift-hit / Step 2.5 path instead.) |
| P0/P1 | Set `verdict: "confirmed"`, `evidence: "Orchestrator-confirmed — per-wave review, no verifier pass"` → fix-verify-loop (Step 3). |
| P2/P3 not fixed | Log in `## Wave Reviews` as `- P2 [deferred]: F-NNN-XX — ...` / `- P3 [deferred]: F-NNN-XX — ...` with the why — line-leading `- ` required: the ship-gate anchor is `^- P[0-9]+ \[deferred\]:`, and the F id follows the colon (Plan anchors, skills/write-plan/SKILL.md). |

Append the wave's review block to `## Wave Reviews` once Step 3 outcomes are known: findings tally `N findings: M fixed, D dropped by pre-gate, E demoted` — the dropped/demoted counts come from fix-verify-loop's return buckets — plus Drift result and deferred entries. Only pause where the table says so.

### Step 2.5 — Promote an [AC-affecting] discovery (user-gated)

Triggered the moment an `[AC-affecting]` discovery is logged (Step 1.6) or a Drift hit resolves to "the decision is wrong" (Step 2). Never auto-apply — this amends the contract.

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

### Step 3 — Per-wave fix-verify-loop

P0/P1 findings (incl. confirmed Drift fixes) → invoke the **fix-verify-loop** skill: findings with `verdict: "confirmed"` + evidence, artifact paths = this wave's files, criteria = the wave's cited ACs. On a returned escalation, `AskUserQuestion`: "Retry with guidance (Recommended)" / "Accept and defer" (→ log `[deferred]` in Wave Reviews) / "Skip finding" / "Abort plan".

Commit fixes separately: `plan(<PLAN_SLUG>): Wave N fixes — [summary]`.

### Step 3.5 — Review fixes commit (regression check)

If Step 3 produced a fixes commit, spawn `code-reviewer` scoped to its diff when the fix reached outside the wave commit's files (`git show --name-only --format= HEAD` vs `HEAD~1`) or the diff is sizeable — directionally 2+ files or ~50 lines; otherwise skip the review. Clean or P2/P3-only → continue (deferred entries logged as in Step 2). P0/P1 → orchestrator-confirm → fix-verify-loop → commit as `Wave N regression fixes`. Regression-fix commits are not re-reviewed per-wave; Step 4's full-diff review is the backstop.

### Step 4 — Final review

All waves done → final review over `git diff $PLAN_BASE_SHA..HEAD`, all files changed across waves.

**Single-wave plan** → invoke the **two-pass-review** skill as a single review: Artifact = the diff; Criteria = every code-gated `AC-NNN-XX`, selected mechanically: `grep -E '^- \*\*AC-[0-9]+' spec.md | grep -F '[code-gated]'`. (No second wave, so no seam for the regression and drift seats to find — and the wave's own review already covered this diff.)

**Multi-wave plan** → run the review panel inline. The two-pass-review skill is not invoked (its Pass 1 is hard-wired to one reviewer) but its protocol rules apply: zero P0/P1 across all seats → skip the verifier and present the clean result with `checks_run`; if the verifier rejects every finding, do NOT treat the review as clean — surface the reviewer/verifier disagreement.

Dispatch in parallel — every seat is a `code-reviewer` agent receiving the full `$PLAN_BASE_SHA..HEAD` diff:

- **Seat A — contract.** Criteria: every code-gated `AC-NNN-XX` (mechanical selection grep above) + standard correctness/security/edge-case analysis.
- **Seat B — regression / blast radius.** Scope: the changed files PLUS their unchanged callers/consumers — explicitly licensed to read outside the diff. Criteria: "Find behavior outside this feature that the diff breaks — callers and consumers of changed signatures, shared state or config, existing behavior no AC describes. Whether the feature's own ACs pass is Seat A's job, not yours. An empty result is a valid result."
- **Seat C — decision & outline drift.** Receives ALL `D-NNN-XX` blocks from spec.md (including superseded, to catch reversion) + the frozen Structure Outline. Criteria: "Does the whole diff contradict any locked `D-NNN-XX` or deviate from the frozen Structure Outline? Cite the decision or outline element and the contradicting hunk. A contract-level contradiction is a Step 2.5 promotion, not just a fix. An empty result is a valid result."
- **Conditional — AC clusters.** If code-gated ACs ≥ 12: partition them into clusters of ≤ 8 and dispatch one Seat-A-style reviewer per cluster (its AC subset + the full diff); Seat A then carries only the correctness/security mandate, no ACs.
- **Conditional — data integrity.** If the diff touches schema, migrations, or concurrent writes: one more reviewer chartered on transactions, races, partial writes, and migration reversibility.

**Merge** (parent): dedup by file + line-span + root cause; keep the max severity; note which seats flagged each finding.

**Verify**: ONE `verifier` agent over the merged finding set — never one per seat. If the deduped P0/P1 findings exceed 4, batch the verification by relatedness (shared files, symbols, or call chains — never split findings that reference the same code path) and stitch the verdicts back into one envelope.

Confirmed P0/P1 → **fix-verify-loop**. A finding that *contradicts* an `AC-NNN-XX` or locked `D-NNN-XX` (not just fails it) is a contract break: log it as an `[AC-affecting]` Execution Log entry and run Step 2.5 — final review has no wave commit, but promotion works the same.

**Verification run (conditional).** After the panel's fixes land, the parent runs the project's test/verification command once over the final state, if one exists — reading PASS/FAIL only, never source.

- **No command** → skip.
- **Pass** → note `verification: passed`.
- **Fail, or can't run** → `AskUserQuestion`: "Fix" / "Accept (pre-existing or intended)" / "Abort". You classify; the parent never reads the test to guess why. "Fix" → fix-verify-loop as a confirmed finding; "Accept" → log an accepted risk in the `### Final review` block, carried into the completion record.

Record per-AC PASS/FAIL evidence and the verification-run outcome in a `### Final review` block appended to `## Wave Reviews` — file-backed so it survives a session boundary; Step 5.3 copies it into the spec.

### Step 5 — Ship gate

Run the plan's `## Ship Gate` checklist; every box must be resolved before freezing.

1. **Promotion check (count-compare, Execution-Log-scoped)**: `sed -n '/^## Execution Log/,/^## Wave Reviews/p' plan.md | grep -c '^- \[AC-affecting\]'` must equal the same slice piped to `grep -ci 'promoted-to-spec'`. Any shortfall → run Step 2.5 for the unmarked entries now; an unpromoted contract break fails the gate.
2. **Triage every `[Future]` and `[deferred]` entry** (walk them via `AskUserQuestion`, batched): hole in the shipped thing → spec "Deferred / what this does NOT close"; new feature → surface to the user to place manually — no automatic destination exists; it must not die silently; noise → dies with the plan. The promoted text's new home opens with `promoted from F-NNN-XX`; the finding id never appears in code.
3. **Write the spec's Completion record** (format canonical in `skills/product-interview/SKILL.md`'s spec template; copy, don't move — the plan keeps its log):
   - `Shipped: [date]`, Status Complete/Partial.
   - **Criteria results**: per-AC PASS/PARTIAL/FAIL with 1-line evidence from Step 4. Honest — FAIL/PARTIAL when warranted.
   - **Post-ship verification**: manual test cases covering the whole feature (happy path, edges, error/empty states), derived from the spec's `## UX` section + ACs, each an unchecked `- [ ]` line written `steps → expected result`. Every human-gated `AC-NNN-XX` MUST appear as a `steps → expected` line led by `AC-NNN-XX:` — owed, not orphaned (the diff never verified them). Confirm coverage mechanically: `grep -E '^- \*\*AC-[0-9]+' spec.md | grep -F '[human-gated:'` (grep the open `[human-gated:` form — it carries the inline "how" text; a closed bracket matches nothing and silently drops every human-gated AC) — every hit needs a matching `AC-NNN-XX:` line. If nothing is human-observable: write `None — nothing manually observable`.
   - **Deferred / what this does NOT close**: the triaged debt from 5.2, with severity.
   - **Review filter stats**: one line aggregating the Wave Reviews tallies — findings dropped by fix-verify-loop's pre-gate and findings demoted, across all waves — so what the filter rejected stays visible.
4. Flip spec `Status:` → `Shipped`. Check the plan's Ship Gate boxes, set plan `Status: FROZEN [date]`.
5. Commit: `git add [spec folder] && git commit -m "plan(<PLAN_SLUG>): ship — completion record, plan frozen"`.

After this commit the plan is frozen — the shipped record.

### Step 6 — Code comments and durable docs update

**6.1 — Comment sweep.** Always runs — answering Skip at 6.2 does not skip it. Sweep the code comments in the files the plan's commits changed (`git diff --name-only $PLAN_BASE_SHA..HEAD`) — never the whole repo. Dispatch ONE Sonnet subagent; when the file list is too large for one, split it across up to 3 in parallel, each file assigned to exactly one subagent.

- **Brief:** load `vet-fact` and `tighten-instruction` via the Skill tool and relay their criteria text (subagents don't inherit loaded skills), plus the implementers' comment rules above.
- **Per comment:** fails the worth test → delete; carries its fact but reads muddy → tighten in place; states a fact that belongs in a durable doc → return it as a `doc_candidate` for 6.2, leave a one-line comment behind.
- **Boundary check:** the files grep clean of task ids, wave numbers, and finding ids.
- **Return:** `{ files_changed: [paths], deleted: N, tightened: N, doc_candidates: [{ file, fact }] | null }` — merging shards: join their `doc_candidates` lists, de-duplicate `files_changed`.
- **Commit:** `plan(<PLAN_SLUG>): comment sweep` — skip the commit when clean.

**6.1 stays separate from 6.2:** durable-docs-update scores a candidate on whether its fact belongs in a doc, so a worthless comment scores low and drops out of its proposal list instead of being deleted from the code.

**6.2 — Durable docs sync.** `AskUserQuestion`: "Run docs sync (Recommended)" / "Skip — go to summary". If run, invoke the **durable-docs-update** skill: scope = `$PLAN_BASE_SHA..HEAD` (mode B); discoveries = the typed Execution Log entries plus 6.1's `doc_candidates` (seeds bypass durable-docs-update's 0.75 gate — a comment-borne fact scoring below it would otherwise be dropped); context = the spec's Background + ACs; spec = the `spec.md` path (mines locked `D-NNN-XX` decisions as candidates). Commit any edits: `plan(<PLAN_SLUG>): durable docs sync`.

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
- Post-ship verification (you verify): [each item, one per line | none]
```

(Counts write `0` when empty — a zero is information, not noise. A field with two or more items nests them as sub-bullets.)

### Resumability

- **Wave-granular via `[x]` checkboxes** — on resume, find the first wave with `[ ]` tasks, dispatch only those.
- **`PLAN_BASE_SHA`** recovers from the plan header's `**Base SHA:**` line; fallback: take the first `plan(<PLAN_SLUG>): Wave` commit (`git log --format=%H --grep="plan(<PLAN_SLUG>): Wave" --reverse | head -1`), then walk to its parent, skipping past any `plan(<PLAN_SLUG>): promote` commits — a Wave-1 promotion lands BEFORE the Wave-1 commit, and the base is the commit before all of them.
- **Promotion commits (Step 2.5) interleave safely** — wave state lives in the checkboxes, not the git history.
- **The flips are the resume authority** — checkbox flips land in their own wave's commit (Step 1.7-8); Wave-Review blocks and deferred entries are written to disk immediately and ride the next commit (fixes, next wave, or ship) — that lag is fine.

## Rules

- **One wave per cycle.** Each wave gets its own commit and review gate.
- **Typed tags are line-anchored grep targets.** `[Implementation]` / `[AC-affecting]` / `[Future]` / `[auto-resolved]` in the Execution Log, `[deferred]` in Wave Reviews — the tag STARTS the entry line (`- [Tag] ...`), exact forms per Plan anchors in skills/write-plan/SKILL.md. Never log a discovery untagged; never start a narrative line with a bracketed tag.
- **The spec's Structure Outline is frozen.** Never edit it — deviations are `[Implementation]` log entries, and later-wave dispatches carry those entries so subagents trust log over outline. A true mid-build redesign goes back through `tech-design` (re-verify + recommit); this skill never rewrites the outline.
- **`*(revised per D-NNN-XX)*` is a human-readable convention, not a gate anchor** — nothing greps it; don't build checks on it.
- **ACs are verified by reviewers against diffs, never self-certified** by the implementing subagent.
- **Post-ship learnings route onward.** After the ship commit, new learnings go to the spec or durable docs, not back into the plan.
