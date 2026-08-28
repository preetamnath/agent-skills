---
name: execute-chat
description: "Execute work already agreed in the current chat without a spec or plan.md. TRIGGER when: user says 'ready to execute', 'let's execute what we discussed', or 'now build it' after an in-chat discussion; multi-task chat-scoped work needs execution without spec ceremony."
---

# Execute Chat

Execute the chat-agreed work through readiness, dependency-ordered waves of parallel subagents, review, verification, durable docs, and commit.

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

- Edit assigned files only; report any needed extra file before editing.
- Scope Git reads and mutations to assigned files; never run `git stash`, `git checkout -- .`, `git reset`, or another whole-tree mutation.
- Read a committed baseline without changing shared state with `git show HEAD:<path>`.
- Write a comment only for what the code cannot say: a constraint, assumption, or coupling.
- Do not commit.
- Return `{ files_changed, summary }`.

Accept each wave in order:

1. Read its actual working-tree diff: `git diff -- <reported files>`.
2. Add its `files_changed` to the running scope for later diffs and the docs pass.
3. If it needs another file, rerun that task serially with the file included.

### Step 3 — Review

- At the Step 1 cadence, invoke the `two-pass-review` skill via the Skill tool over `git diff -- <run files>` or the current wave's files.
- Verify each surviving finding against source; confirm or demote it.
- Invoke the `fix-verify-loop` skill via the Skill tool for confirmed P0/P1 findings.
- Resolve every fix-loop escalation and its staged changes with the user before continuing.
- Fix P2 findings required by the agreed scope; dispatch non-small fixes to a build subagent and defer other P2/P3 findings.
- Add every file changed by review fixes to the run's collected files.
- Send out-of-scope findings to the done report's deferred list.

### Step 4 — Working gate

- Run the project's verification commands unless they already passed on the current state.
- If verification fails, ask the user whether to fix, accept, or abort before continuing.
- If `meta/workflows/automated-testing/automated-testing-instructions.md` exists, use it to test the implemented behavior when relevant.

### Step 5 — Comments and durable docs

Invoke the `durable-docs-update` skill via the Skill tool inline with:

- **scope** — the run's collected `files_changed` (Mode C, caller-supplied);
- **change content** — the working-tree `git diff HEAD -- <those files>`;
- **context** — what the chat agreed this work was for.

### Step 6 — Commit

Commit all files changed by this run.

### Step 7 — Repository instructions

After the commit, read and follow `meta/workflows/execution/execution-instructions.md` if it exists.

### Step 8 — Done report

```
**Execute-chat complete:**
- Shipped: [one line]
- Waves: [n] · review: [clean | P0/P1 fixed: …]
- Verified: [commands + results] · live: [PASS | user-confirmed | not applicable]
- Commit: [hash]
- Deferred (out of scope): [one line each | none]
```

(Write `None — nothing deferred` when the deferred list is empty.)

## Rules

- **The chat is the spec.** Execute only agreed work; defer new ideas.
- **Keep the ledger current.** `TaskUpdate` each entry to `in_progress` when work starts and `completed` when it lands.
- **Verify diffs, not reports.** Read each actual diff before accepting a wave, review fix, or docs pass.
- **Parent role.** The parent plans, dispatches, verifies, adjudicates, and reports; it writes only small confirmed fixes and inline docs.
