---
name: execute-chat
description: "Execute work agreed in the current chat — no spec or plan.md — through a readiness gate, dependency-ordered subagent waves, review, and closing docs passes. TRIGGER when: user says 'ready to execute', 'let's execute what we discussed', 'now build it' after an in-chat discussion; multi-task chat-scoped work needs wave rigor without spec ceremony."
---

# Execute Chat

Carry work the chat has already agreed, from "ready to execute" to done: a readiness gate, a task list grouped into dependency-ordered waves of parallel subagents, review, then durable-docs and tighten passes. The chat is the spec — the parent orchestrates, verifies, and adjudicates; it does not reopen settled scope.

## Protocol

### Step 0 — Readiness gate

Before planning, check the chat against two lenses. Judge from what was actually said and verified — do not re-interview on settled points.

**WHAT is clear (product lens):**
- The outcome is named — what changes for the user/system when this ships.
- Scope boundaries are drawn — what is explicitly in and out.
- User-visible behavior is agreed, including the edge cases that matter.

**HOW is decided (tech lens):**
- An approach is chosen, and alternatives were rejected with reasons — not just "the first idea we had."
- The approach fits the codebase's existing architecture and patterns; a deviation is named and justified, not accidental.
- Key decisions are locked: data shapes, where the code lives, which contracts/interfaces are touched.
- Load-bearing claims behind the approach were verified against the actual source, not assumed.
- Known risks are named with a mitigation or an explicit acceptance.

Route by gap size:
- **All settled** — confirm in one line each and proceed.
- **Small gaps** — ask 1–3 targeted questions via `AskUserQuestion`, close them, proceed.
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

1. Derive the task list from what the chat agreed (TaskCreate) — every agreed item lands as a task; nothing new enters.
2. Group into dependency-ordered waves: tasks share a wave only if they depend on nothing in that wave and touch no common file; a task consuming another's output goes in a later wave.
3. Recommend the review cadence and apply it unless the user objects: **once after all waves** by default; **after each wave** when a later wave builds on an earlier wave's untested output or waves touch a shared contract, where a defect would propagate.

```
**Plan:**
- Tasks: [n], waves: [wave → tasks, one line per wave]
- Review cadence: [at end | per wave] — [one-line reason]
```

### Step 2 — Build waves

For each wave, launch one **Opus** subagent per task, in parallel, each briefed with its task, the relevant file paths, and these rules: do not touch files outside your task; if you find you need a file outside your assigned set, stop and report it rather than editing it; do not commit. Each returns `{ files_changed, summary }`.

Accept a wave only after reading the **actual working-tree diff** for its files (`git diff -- <the wave's reported files>`), never the subagent's self-report. Collect each wave's `files_changed` into a running set — later diffs and the docs pass scope to it. If a subagent reported it needed a file outside its set, run that task again as a lone serial subagent after the wave, with the file included. Then launch the next wave.

### Step 3 — Review

At the cadence chosen in Step 1, invoke the `two-pass-review` skill via the Skill tool over the run's working-tree diff — `git diff -- <all files the run changed>`, or `git diff -- <the wave's files>` per-wave. Adjudicate every surviving finding against source yourself — confirm, demote, or accept-as-tradeoff — and fix the confirmed ones; findings outside the agreed scope go to the done report's deferred list, not into the diff.

### Step 4 — Working gate

Run the project's verification command (tests/typecheck) over the final state. Where the change has a runtime surface the tests don't reach, hand the user a short live-check recipe (steps → expected) and get their confirmation. Docs passes run only on confirmed-working code.

### Step 5 — Docs pass

Invoke the `durable-docs-update` skill via the Skill tool inline — it fans out its own subagents, so it can't be a leaf subagent; this is the one place the parent runs a dependency itself (docs sync, not feature code). Pass:
- **scope** — the run's collected `files_changed` (Mode C, caller-supplied);
- **change content** — the working-tree `git diff -- <those files>`.

Also tell it to flag the cross-wave hazard: a comment or doc an earlier wave wrote true that a later wave made false — no per-wave record catches this, so the audit must.

### Step 6 — Tighten pass

Dispatch one **Sonnet** subagent briefed to invoke the Skill tool to load `tighten-instruction`, `structure-prose`, then apply both lenses to the docs and code comments the run added or changed (Step 5's edits included). Meaning-preserving only.

### Step 7 — Done report

```
**Execute-chat complete:**
- Shipped: [one line]
- Waves: [n] · review: [clean | P0/P1 fixed: …]
- Verified: [command + result | user live-check confirmed]
- Docs: [files touched | none needed]
- Deferred (out of scope): [one line each | none]
```

(Write `None — nothing deferred` when the deferred list is empty.)

### Step 8 — Commit gate

Ask the user whether to commit.

## Rules

- **The chat is the spec.** Execute what was agreed; a new idea mid-run goes to the deferred list, never into the diff.
- **Verify diffs, not reports.** No wave, review fix, or docs pass is accepted on a subagent's say-so — the parent reads the actual diff.
- **The parent never writes feature code.** It plans, dispatches, verifies, adjudicates, and reports; the only exceptions are small confirmed-finding fixes and the inline docs pass (Step 5) — neither is feature code.
