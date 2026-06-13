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

- **Spec folder**: `meta/specs/NNN-slug/` (or a path to either file in it). Reads both `plan.md` (waves, log) and `spec.md` (ACs, D-NN decisions, Structure Outline).

### Execution model

**Parent agent (orchestrator):**
- Reads plan + spec, dispatches subagents, runs review gates, commits.
- Never reads source code files or writes code itself.
- Edits `spec.md` ONLY in Step 2.5 (promotion) and Step 5 (ship gate).

**Subagents (implementers):**
- Receive: plan file path + their assigned task IDs; the `AC-N` texts their tasks cite and the relevant Structure Outline excerpt (both copied from spec.md into the dispatch — they don't hunt the spec); any prior `[Implementation]` log entries touching their files (the outline is frozen — the log is where reality lives).
- Implement the assigned work; read existing code in affected areas.
- Return: `{ files_changed: [paths], summary: string, discoveries: [{ type: "[Implementation]" | "[AC-affecting]" | "[Future]", note: string }] | null }`
- A deviation from the Structure Outline IS an `[Implementation]` discovery — there is no separate channel. If the task body conflicts with a copied current `AC-N` text, the AC text is authoritative: implement to the AC and return the conflict as an `[AC-affecting]` discovery — never silently reconcile it.
- A file assigned to another subagent in the same wave must NOT be edited — return `{ needs_scope_expansion: true, additional_files: [paths], justification: string }` instead; the parent reassigns and re-dispatches. Once per wave: a second `needs_scope_expansion` in the same wave stops the reshuffle — collapse the colliding tasks into ONE subagent and run them serially (the same escape wave rule 3 uses for declared overlap).
- No file contents in returns — paths and summaries only.

### Step 1 — Wave execution loop

1. Read the plan fresh. Extract `PLAN_SLUG` from the folder name (`meta/specs/014-daily-digest/` → `014-daily-digest`). Before the first wave: check `git status --porcelain` excluding the spec folder's files (they fold into the Wave 1 commit); if dirty, `AskUserQuestion`: "Stash and proceed (Recommended)" / "Commit and proceed" / "Abort". Then record `PLAN_BASE_SHA=$(git rev-parse HEAD)` and set the plan header's `**Base SHA:**` line.
2. Find the next `### Wave N` with any `[ ]` tasks. Resuming mid-wave → dispatch only unchecked tasks.
3. No unchecked tasks anywhere → final review (Step 4).
4. Launch up to 5 **Opus subagents** in parallel for the wave's tasks (the wave cap in write-plan matches this dispatch budget). `Must land together with:` tasks go to one subagent.
5. Collect results. Crash/timeout → `AskUserQuestion`: "Retry this item (Recommended)" / "Skip and mark dependents blocked" / "Abort plan". Don't commit a partial wave.
6. Append each returned discovery to the plan's `## Execution Log` under a `### Wave N — [date]` heading, with its type tag. **Any `[AC-affecting]` discovery → run Step 2.5 now, before committing the wave.** Other blocking issues → `AskUserQuestion`: "Resolve and retry (Recommended)" / "Skip and mark dependents blocked" / "Override and proceed" / "Abort plan".
7. Flip the wave's tasks to `[x]` — the flip must land IN the wave commit (it's the resume state).
8. Stage and commit: `git add [wave files + plan] && git commit -m "plan(<PLAN_SLUG>): Wave N complete — [brief summary]"`
9. Per-wave review (Step 2).
10. Return to 1.

### Step 2 — Per-wave review + Drift check

Check the wave's actual size first: `git diff HEAD~1..HEAD --stat`. **At or under 5 files and 200 changed lines** → spawn one `code-reviewer` agent against the wave diff. **Over either bound** → spawn one `code-reviewer` per task in parallel, each scoped to that task's returned `files_changed` (same criteria + Drift question per slice), and merge findings before applying the table below — review load is bounded by diff size, not task count.

- **Criteria**: the code-gated `AC-N` texts cited by this wave's tasks (copied from the spec). `[human-gated:]` ACs are excluded — they can't be verified against a diff (the ship gate routes them to Post-ship verification). Plus standard correctness/security/edge-case analysis.
- **Drift question** (explicit instruction to the reviewer): *"Does this diff contradict any locked `D-NN` in spec.md? Cite the decision ID and the contradicting hunk."*
- **Scope**: files changed in this wave only. Single pass, no verifier; findings have `verdict: null`.

| Finding | Action |
|---|---|
| None | Append `- Review: 0 findings — clean` to `## Wave Reviews`. Don't pause — next wave. |
| **Drift hit** (diff contradicts a `D-NN`) | `AskUserQuestion`: "Fix code to conform to D-NN (Recommended)" (treat as confirmed P1 → Step 3) / "The decision is wrong — supersede it" (→ Step 2.5) / "Accept with risk note in Wave Reviews". |
| P0/P1 | Set `verdict: "confirmed"`, `evidence: "Orchestrator-confirmed — per-wave review, no verifier pass"` → fix-verify-loop (Step 3). |
| P2/P3 not fixed | Log in `## Wave Reviews` as `- P2 [deferred]: ...` / `- P3 [deferred]: ...` with the why — line-leading `- ` required: the ship-gate anchor is `^- P[0-9]+ \[deferred\]:` (Plan anchors, skills/write-plan/SKILL.md). |

Append the wave's review block to `## Wave Reviews` once Step 3 outcomes are known: findings tally `N findings: M fixed, D dropped by pre-gate, E demoted` — the dropped/demoted counts come from fix-verify-loop's return buckets — plus Drift result and deferred entries. Only pause where the table says so.

### Step 2.5 — Promote an [AC-affecting] discovery (user-gated)

Triggered the moment an `[AC-affecting]` discovery is logged (Step 1.6) or a Drift hit resolves to "the decision is wrong" (Step 2). Never auto-apply — this amends the contract.

1. **Log first**: write the `[AC-affecting]` Execution Log entry if none exists — the Drift path arrives without one, and the marker must have an entry to count against. It states the contradiction and evidence.
2. **Present** via `AskUserQuestion`: the contradiction, the evidence, the proposed spec change (revised `AC-N` text and/or `D-NN` supersession with new decision block). Also grep `plan.md` for unchecked `- [ ]` tasks citing the revised `AC-N` or the superseded `D-0X` and list each (title + first body line) in the same question with a disposition: keep / amend / drop — re-pointing a citation updates a label, not the task's instructions. Apply amend/drop edits to `plan.md` as part of step 6's promotion commit. Options: "Promote to spec (Recommended)" / "Adjust the proposal" / "Abort plan".
3. **On approval, edit `spec.md`** (AC line / D-NN block formats are canonical in `skills/product-interview/SKILL.md`'s spec template):
   - Revise the `AC-N` in place, appending `*(revised per D-NN)*` — ACs are the live contract, one current truth; the why lives in the decision trail.
   - Supersede the old `D-NN`: flip `Status: superseded`, add `Superseded-by: D-0Y`. Touch nothing else in the block.
   - Append the new `D-0Y` block (`Supersedes: D-0X`, rationale citing the evidence and `plan Wave N`). Heading type marker: inherit the superseded block's `[product]`/`[tech]`, or `[tech]` if the change is build-originated (marker is advisory — see the canonical Decisions comment).
4. **Re-point stale citations**: grep `plan.md` for `per D-0X` and re-point to `D-0Y`.
5. **Close the log entry**: append `promoted-to-spec [date]: AC-N revised, D-0X superseded by D-0Y.` — ALWAYS lowercase and hyphenated; this is the ship gate's count-compare anchor (Plan anchors, skills/write-plan/SKILL.md). Never write the hyphenated token outside a real marker (unhyphenated prose is safe — the hyphen is what the gate counts).
6. Commit: `git add [spec folder] && git commit -m "plan(<PLAN_SLUG>): promote [AC-affecting] — D-0X superseded by D-0Y"`. Resume where execution stopped.

### Step 3 — Per-wave fix-verify-loop

P0/P1 findings (incl. confirmed Drift fixes) → invoke the **fix-verify-loop** skill: findings with `verdict: "confirmed"` + evidence, artifact paths = this wave's files, criteria = the wave's cited ACs. Max 2 attempts per finding, then `AskUserQuestion`: "Retry with guidance (Recommended)" / "Accept and defer" (→ log `[deferred]` in Wave Reviews) / "Skip finding" / "Abort plan".

Commit fixes separately: `plan(<PLAN_SLUG>): Wave N fixes — [summary]`.

### Step 3.5 — Review fixes commit (regression check)

If Step 3 produced a fixes commit, spawn `code-reviewer` scoped to that commit's diff. Clean or P2/P3-only → continue (deferred entries logged as in Step 2). P0/P1 → orchestrator-confirm → fix-verify-loop → commit as `Wave N regression fixes`. Regression-fix commits are not re-reviewed per-wave; Step 4's full-diff review is the backstop.

### Step 4 — Final review

All waves done → final review over `git diff $PLAN_BASE_SHA..HEAD`, all files changed across waves.

**Single-wave plan** → invoke the **two-pass-review** skill as a single review: Artifact = the diff; Criteria = every code-gated `AC-N`, selected mechanically: `grep -E '^- \*\*AC-[0-9]+' spec.md | grep -F '[code-gated]'`. (The wave's own review just covered this same diff — a panel would re-read the same page twice.)

**Multi-wave plan** → run the review panel inline. The two-pass-review skill is not invoked (its Pass 1 is hard-wired to one reviewer) but its protocol rules apply: zero P0/P1 across all seats → skip the verifier and present the clean result with `checks_run`; if the verifier rejects every finding, do NOT treat the review as clean — surface the reviewer/verifier disagreement.

Dispatch in parallel — every seat is a `code-reviewer` agent receiving the full `$PLAN_BASE_SHA..HEAD` diff:

- **Seat A — contract.** Criteria: every code-gated `AC-N` (mechanical selection grep above) + standard correctness/security/edge-case analysis.
- **Seat B — regression / blast radius.** Scope: the changed files PLUS their unchanged callers/consumers — explicitly licensed to read outside the diff. Criteria: "Find behavior outside this feature that the diff breaks — callers and consumers of changed signatures, shared state or config, existing behavior no AC describes. Whether the feature's own ACs pass is Seat A's job, not yours. An empty result is a valid result."
- **Seat C — decision & outline drift.** Receives ALL `D-NN` blocks from spec.md (including superseded, to catch reversion) + the frozen Structure Outline. Criteria: "Does the whole diff contradict any locked `D-NN` or deviate from the frozen Structure Outline? Cite the decision or outline element and the contradicting hunk. A contract-level contradiction is a Step 2.5 promotion, not just a fix. An empty result is a valid result."
- **Conditional — AC clusters.** If code-gated ACs ≥ 8: partition them into clusters of ≤ 6 and dispatch one Seat-A-style reviewer per cluster (its AC subset + the full diff); Seat A then carries only the correctness/security mandate, no ACs.
- **Conditional — data integrity.** If the diff touches schema, migrations, or concurrent writes: one more reviewer chartered on transactions, races, partial writes, and migration reversibility.

**Merge** (parent): dedup by file + line-span + root cause; keep the max severity; note which seats flagged each finding.

**Verify**: ONE `verifier` agent over the merged finding set — never one per seat. If the deduped P0/P1 findings exceed 4, batch the verification by relatedness (shared files, symbols, or call chains — never split findings that reference the same code path) and stitch the verdicts back into one envelope.

Confirmed P0/P1 → **fix-verify-loop**. A finding that *contradicts* an `AC-N` or locked `D-NN` (not just fails it) is a contract break: log it as an `[AC-affecting]` Execution Log entry and run Step 2.5 — final review has no wave commit, but promotion works the same.

Record per-AC PASS/FAIL evidence in a `### Final review` block appended to `## Wave Reviews` — file-backed so it survives a session boundary; Step 5.3 copies it into the spec.

### Step 5 — Ship gate

Run the plan's `## Ship Gate` checklist; every box must be resolved before freezing.

1. **Promotion check (count-compare, Execution-Log-scoped)**: `sed -n '/^## Execution Log/,/^## Wave Reviews/p' plan.md | grep -c '^- \[AC-affecting\]'` must equal the same slice piped to `grep -ci 'promoted-to-spec'`. Any shortfall → run Step 2.5 for the unmarked entries now; an unpromoted contract break fails the gate.
2. **Triage every `[Future]` and `[deferred]` entry** (walk them via `AskUserQuestion`, batched): hole in the shipped thing → spec "Deferred / what this does NOT close"; new feature → surface to the user to place manually — no automatic destination exists; it must not die silently; noise → dies with the plan.
3. **Write the spec's Completion record** (format canonical in `skills/product-interview/SKILL.md`'s spec template; copy, don't move — the plan keeps its log):
   - `Shipped: [date]`, Status Complete/Partial.
   - **Criteria results**: per-AC PASS/PARTIAL/FAIL with 1-line evidence from Step 4. Honest — FAIL/PARTIAL when warranted.
   - **Post-ship verification**: manual test cases covering the whole feature (happy path, edges, error/empty states), derived from the spec's `## UX` section + ACs, each an unchecked `- [ ]` line written `steps → expected result`. Every human-gated `AC-N` MUST appear as a `steps → expected` line led by `AC-N:` — owed, not orphaned (the diff never verified them). Confirm coverage mechanically: `grep -E '^- \*\*AC-[0-9]+' spec.md | grep -F '[human-gated:'` (grep the open `[human-gated:` form — it carries the inline "how" text; a closed bracket matches nothing and silently drops every human-gated AC) — every hit needs a matching `AC-N:` line. If nothing is human-observable: write `None — nothing manually observable`.
   - **Deferred / what this does NOT close**: the triaged debt from 5.2, with severity.
   - **Review filter stats**: one line aggregating the Wave Reviews tallies — findings dropped by fix-verify-loop's pre-gate and findings demoted, across all waves — so what the filter rejected stays visible.
4. Flip spec `Status:` → `Shipped`. Check the plan's Ship Gate boxes, set plan `Status: FROZEN [date]`.
5. Commit: `git add [spec folder] && git commit -m "plan(<PLAN_SLUG>): ship — completion record, plan frozen"`.

After this commit the plan is frozen — the shipped record.

### Step 6 — Durable docs sync

`AskUserQuestion`: "Run docs sync (Recommended)" / "Skip — go to summary". If run, invoke the **durable-docs-update** skill: scope = `$PLAN_BASE_SHA..HEAD` (mode B); discoveries = the typed Execution Log entries; context = the spec's Background + ACs; spec = the `spec.md` path (mines locked `D-NN` decisions as candidates). Commit any edits: `plan(<PLAN_SLUG>): durable docs sync`.

### Step 7 — Report

The Completion record in `spec.md` is the durable summary — don't duplicate it. Tell the user: AC results (PASS/FAIL counts), open Post-ship verification items (these are now theirs to drive), deferred debt count, accepted risks carried into ship (the count of Drift hits accepted with a risk note — see `## Wave Reviews`; knowingly carried, not fixed), and the spec/plan paths.

### Resumability

Wave-granular via `[x]` checkboxes: on resume, find the first wave with `[ ]` tasks, dispatch only those. `PLAN_BASE_SHA` recovers from the plan header's `**Base SHA:**` line; fallback: take the first `plan(<PLAN_SLUG>): Wave` commit (`git log --format=%H --grep="plan(<PLAN_SLUG>): Wave" --reverse | head -1`), then walk to its parent, skipping past any `plan(<PLAN_SLUG>): promote` commits — a Wave-1 promotion lands BEFORE the Wave-1 commit, and the base is the commit before all of them. Promotion commits (Step 2.5) interleave safely — wave state lives in the checkboxes, not the git history. Checkbox flips land in their own wave's commit (Step 1.7-8); Wave-Review blocks and deferred entries are written to disk immediately and ride the next commit (fixes, next wave, or ship) — that lag is fine, the flips are the resume authority.

## Rules

- **Parent NEVER reads source code or writes code during execution.** All implementation, fix, and review work runs in subagents. (Step 6's docs sync is the post-ship exception: durable-docs-update is user-interactive and runs inline, managing its own reading.)
- **The spec is edited ONLY via Step 2.5 and Step 5**, both user-gated where they amend the contract. Supersede decisions, never edit their bodies; revise ACs in place with the `*(revised per D-NN)*` marker.
- **Always read the plan fresh before each wave** — fix-verify-loop or a promotion may have changed it.
- **One wave per cycle.** Each wave gets its own commit and review gate.
- **Typed tags are line-anchored grep targets.** `[Implementation]` / `[AC-affecting]` / `[Future]` in the Execution Log, `[deferred]` in Wave Reviews — the tag STARTS the entry line (`- [Tag] ...`), exact forms per Plan anchors in skills/write-plan/SKILL.md. Never log a discovery untagged; never start a narrative line with a bracketed tag.
- **The spec's Structure Outline is frozen.** Never edit it — deviations are `[Implementation]` log entries, and later-wave dispatches carry those entries so subagents trust log over outline. A true mid-build redesign goes back through `tech-design` (re-verify + recommit); this skill never rewrites the outline.
- **`*(revised per D-NN)*` is a human-readable convention, not a gate anchor** — nothing greps it; don't build checks on it.
- **ACs are verified by reviewers against diffs, never self-certified** by the implementing subagent.
- **Blocked or unclear task → don't skip silently.** `AskUserQuestion`: "Clarify and proceed (Recommended)" / "Skip this item" / "Reorder plan" / "Abort plan". A decision the plan doesn't specify → enumerate options with a recommendation; don't proceed on assumptions.
- **Post-ship learnings route onward.** After the ship commit, new learnings go to the spec or durable docs, not back into the plan.
