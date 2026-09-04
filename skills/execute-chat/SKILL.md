---
name: execute-chat
description: "Execute work already agreed in the current chat without a plan.md. TRIGGER when: the user explicitly asks to use execute-chat."
---

# Execute Chat

## Protocol

### Step 0 — Readiness gate

Judge the chat and verified evidence against two lenses without reopening settled points.

**WHAT is clear (product lens):**
- **Outcome:** what changes for the user or system.
- **Scope:** what is in and out.
- **Behavior:** the user-visible behavior and material edge cases.

**HOW is decided (tech lens):**
- **Approach:** chosen, with alternatives rejected for stated reasons.
- **Fit:** follows the existing architecture and patterns; deviations are justified.
- **Decisions:** data shapes, code locations, and affected interfaces are locked.
- **Evidence:** load-bearing claims are verified against source.
- **Risks:** mitigated or explicitly accepted.

Route by gap size:
- **All settled** — confirm in one line each and proceed.
- **Small gaps** — ask 1–3 targeted questions via `AskUserQuestion`, then proceed.
- **WHAT genuinely open** — stop; confirm with the user, then invoke the `product-interview` skill via the Skill tool.
- **HOW genuinely open** — stop; confirm with the user, then invoke the `tech-design` skill via the Skill tool.
- **Both open** — `product-interview` first.

```
**Readiness:**
- WHAT: [settled — one line | gaps: …]
- HOW: [settled — one line | gaps: …]
- Proceeding | Asking | Routing to [skill]
```

### Step 1 — Plan from the chat

1. Create one task per agreed item; add nothing else.
2. Group tasks into dependency-ordered, file-disjoint waves; put consumers in later waves.
3. Review once after all waves unless the user objects. Review each wave when later work depends on its untested output or shared contracts.
4. Use `TaskCreate` for each wave, review, working gate, comments + durable docs, and commit. Do not create entries for build subagents or the done report.

```
**Plan:**
- Tasks: [n], waves: [wave → tasks, one line per wave]
- Review cadence: [at end | per wave] — [one-line reason]
```

### Step 2 — Build waves

Use the requested model; otherwise select one per logical task:

- **Sonnet — only when every condition holds:**
  - The edit is fully specified and follows an existing pattern.
  - Assigned files are known and bounded.
  - Behavior, architecture, and contracts require no unresolved choice.
  - It touches no schema, migration, auth, security, concurrency, payments, destructive data, or public, shared, or external interface.
  - The dispatch includes a verification check.
- **Opus — otherwise.**
- **Grouped work:** classify a subagent's full assignment; any Opus condition selects Opus.
- **Escalation:** upgrade Sonnet to Opus when new scope, coupling, or ambiguity appears; never downgrade the task.

For each wave, launch one subagent per logical task in parallel. Give each subagent its task, file paths, and these rules:

- Before the first write, resolve each target path and read its governing repository instructions and Claude path rules in `.claude/rules/` whose quoted `paths:` globs match it; use the intended path for a new file.
- Edit assigned files only; report any needed extra file before editing.
- Scope Git reads and mutations to assigned files; never run `git stash`, `git checkout -- .`, `git reset`, or another whole-tree mutation.
- Read a committed baseline without changing shared state with `git show HEAD:<path>`.
- Write a comment only for what the code cannot say: a constraint, assumption, or coupling.
- Run the narrowest check that proves the assigned change, plus directly affected tests; reserve broader checks for Step 4.
- Do not commit.
- Return `{ files_changed, summary }`.

Accept each wave in order:

1. Read its actual working-tree diff: `git diff -- <reported files>`.
2. Add its `files_changed` to the running scope for later diffs and the docs pass.
3. If it needs another file, rerun that task serially with the file included.

### Fix-loop packet

Every `fix-verify-loop` invocation in Steps 3–4 passes:

- **Findings:** Confirmed P0/P1 findings with their `validated_by` value and verdict evidence.
- **Artifact paths:** The run's collected files. A finding or its evidence may identify another path, but editing it requires the fix-loop scope-expansion gate.
- **Criteria:** Each finding's criterion plus the relevant settled WHAT and HOW facts from the readiness gate. A working-gate failure also includes the expected verification or live-test result.

### Post-fix review

After all fixes for one review or working-gate failure are accepted, union their returned `files_changed` as `<fix files>` and select one regression scope:

| Scope | Use when | Action |
|---|---|---|
| **Bounded** | Every condition holds: at most 5 fix files and 400 changed lines in their working-tree diff from `HEAD`; no schema, migration, auth, security, concurrency, payment, destructive-data, or shared-interface change; clear affected WHAT/HOW facts, callers, and consumers. | Invoke the `two-pass-review` skill via the Skill tool over `git diff HEAD -- <fix files>`, licensed to inspect affected callers and consumers. |
| **Whole run** | Any Bounded condition fails or its evidence is unclear. | Invoke the `two-pass-review` skill via the Skill tool over `git diff HEAD -- <run files>`. |

Run this gate once per review or working-gate failure. Give the reviewer the addressed findings and initial-review evidence; ask only whether the fixes caused regressions. Reuse unaffected initial evidence. Resolve confirmed regressions with the same [Fix-loop packet](#fix-loop-packet) without another automatic post-fix review.

### Step 3 — Review

- At the Step 1 cadence, invoke the `two-pass-review` skill via the Skill tool over `git diff -- <run files>` or the current wave's files.
- Invoke the `fix-verify-loop` skill via the Skill tool with the [Fix-loop packet](#fix-loop-packet) for confirmed P0/P1 findings.
- After every fix-loop run, add its returned `files_changed`—the authoritative path list—to the run's collected files before the next review, docs pass, or commit.
- Resolve every fix-loop escalation and its staged changes with the user before continuing.
- Fix P2 findings required by the agreed scope; dispatch non-small fixes to a build subagent and defer other P2/P3 findings.
- Send out-of-scope findings to the done report's deferred list.
- If the initial review produced fixes, run [Post-fix review](#post-fix-review).

### Step 4 — Working gate

Choose the smallest verification level that covers the current risk:

| Level | When | Scope |
|---|---|---|
| **Focused** | During each task and finding fix. | The narrowest test that proves the change, plus directly affected tests. |
| **Subsystem** | After a coupled wave or fix group when later work depends on it or focused checks cannot prove the interaction. | The smallest relevant subsystem suite. |
| **Full** | Once after review fixes stabilize the run and known overlapping edits to the code or test corpus settle. | Every applicable project-wide verification command. |

- **Early Full:** escalate only for shared test infrastructure, order dependence, or a defect reproducible only in the full suite.
- **Harness exit:** if test bodies pass but the harness fails to exit, stop trying equivalent runner modes unless a new hypothesis distinguishes the rerun; use Fix/Accept/Abort below and record harness debt only on Accept.

After Full passes, classify later edits:

| Later edit | Required verification |
|---|---|
| Documentation or comments only | Reuse the Full evidence. |
| Local code with a clear blast radius | Always rerun Focused; add Subsystem only for a coupled local interaction; reuse the unaffected Full evidence. |
| Shared interface, test infrastructure, order/global state, multiple subsystems, or unclear blast radius | Rerun Focused and Full. |

- If `meta/workflows/automated-testing/automated-testing-instructions.md` exists, use it to test the implemented behavior when relevant.
- If verification or live testing fails, ask the user whether to fix, accept, or abort:
  - **Fix** → create a confirmed finding. Set `validated_by: "machine"` only for an exact automated check and observed failure; otherwise set `validated_by: null`. Invoke `fix-verify-loop` with the [Fix-loop packet](#fix-loop-packet); add its returned files to the collected scope; resolve every escalation and staged-change choice; run [Post-fix review](#post-fix-review); rerun the working gate.
  - **Accept** → carry the risk in the done report.
  - **Abort** → stop.

### Step 5 — Comments and durable docs

Invoke the `durable-docs-update` skill via the Skill tool inline with:

- **scope** — the run's collected `files_changed` (Mode C, caller-supplied);
- **change content** — the working-tree `git diff HEAD -- <those files>`;
- **context** — what the chat agreed this work was for.

### Step 6 — Final gate and commit

1. Read the final scoped diff and confirm every review and docs decision is resolved.
2. Run only applicable checks whose Step 4 evidence was invalidated; reuse evidence under the post-Full table.
3. Commit all files changed by this run.

### Step 7 — Repository instructions

After the commit, read and follow `meta/workflows/execution/execution-instructions.md` if it exists.

### Step 8 — Done report

```
**Execute-chat complete:**
- Shipped: [one line]
- Waves: [n] · review: [clean | P0/P1 fixed: …]
- Verified: [commands + results] · live: [PASS | user-confirmed | not applicable]
- Commit: [hash]
- Deferred: [one line each | none]
```

(Write `None — nothing deferred` when the deferred list is empty.)

## Rules

- **The chat is the spec.** Execute only agreed work; defer new ideas.
- **Keep the ledger current.** `TaskUpdate` each entry to `in_progress` when work starts and `completed` when it lands.
- **Verify diffs, not reports.** Read each actual diff before accepting a wave, review fix, or docs pass.
- **Parent role.** The parent plans, dispatches, verifies, adjudicates, and reports; it writes only small confirmed fixes and inline docs.
