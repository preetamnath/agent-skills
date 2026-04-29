---
name: plan-runner
description: "Executes wave-grouped markdown plans via parallel subagents. Orchestrates implementation, per-wave review, fix cycles, and final two-pass-review. Resumable across conversations."
---

# Plan Runner

Executes a wave-grouped markdown plan file via parallel subagents. The parent agent orchestrates — reading the plan, dispatching subagents, running review gates, and committing. All code work happens in subagents.

## When to use

When you have a plan file (`.md`) with wave-grouped `[ ]` checkbox items (produced by plan-builder) and want to execute them with parallel implementation, review gates, and checkpointing. Resumable across conversations.

## Protocol

### Input

- **Plan file path**: the markdown file containing the wave-grouped plan

### Execution model

**Parent agent (orchestrator):**
- Reads the plan file and orchestrates execution
- Never reads source code files or writes code itself
- Launches subagents for all code work
- Invokes review/fix protocols after each wave
- Commits after each wave

**Subagents (implementers):**
- Receive: plan file path (to read their assigned items + structure outline), criteria from the plan header
- Read existing code in affected areas
- Implement the assigned work
- Return structured summary: `{ files_changed: [paths], summary: string, deviations: [string] | null, discoveries: [string] | null }`
- If a subagent needs to modify a file assigned to another subagent in the same wave, it must NOT edit it. Instead return: `{ needs_scope_expansion: true, additional_files: [paths], justification: string }`. The parent reassigns and re-dispatches.
- No file contents in return — paths and summaries only

### Step 1 — Wave execution loop

1. Read the plan file. Extract `PLAN_SLUG` from the filename (e.g., `plan-010-tanstack-query-migration.md` → `010-tanstack-query-migration`). On first wave, record `PLAN_BASE_SHA=$(git rev-parse HEAD)` and write `**Base SHA**: <sha>` into the plan file header (after the `**Created**` line) for final review diff range.
2. Find the next `## Wave N` section with any `[ ]` items. If resuming mid-wave (some items `[x]`, some `[ ]`), dispatch only the remaining unchecked items.
3. If no waves with unchecked items: proceed to final review (Step 4).
4. Launch up to 3 **Sonnet subagents** in parallel for the wave's items (plan-builder caps waves at 3 items).
   - Each subagent receives: plan file path, its assigned item ID(s), criteria from plan header.
   - If a wave has items marked "must land together", assign them to the same subagent.
5. Collect results from all subagents. If a subagent crashes or times out (no result returned):
   - Surface immediately via `AskUserQuestion` with options: "Retry this item", "Skip and mark dependents blocked", "Abort plan". Recommended: "Retry this item".
   - If other subagents in the wave succeeded: do NOT commit the partial wave. Resolve the crashed item first.
6. If any subagent reports a blocking issue (returned a result but flagged a problem): pause, present to user via the `AskUserQuestion` tool with options: "Resolve and retry", "Skip and mark dependents blocked", "Override and proceed", "Abort plan". Recommended: "Resolve and retry".
7. Stage and commit the wave: `git add [wave files] && git commit -m "plan(<PLAN_SLUG>): Wave N complete — [brief summary]"`
8. Mark all wave items `[x]`, append discoveries inline if any.
9. Per-wave review (Step 2).
10. Return to step 1.

### Step 2 — Per-wave review

After each wave commit, invoke the **code-review** skill against the wave diff. In addition to its standard analysis (correctness, security, edge cases, bugs), evaluate the diff against the plan's criteria scoped to this wave's items.

- **Artifact**: wave diff (`git diff HEAD~1..HEAD`)
- **Criteria**: the plan's criteria from the header, scoped to this wave's items
- **Scope**: files changed in this wave only

Single review pass, no verifier. Findings have `verdict: null`.

| Finding | Action |
|---|---|
| No findings | Append `- Review: 0 findings — clean`. Do NOT present review output or pause — proceed directly to the next wave |
| P0/P1 | Set `verdict: "confirmed"` and `evidence: "Orchestrator-confirmed — per-wave review, no verifier pass"`, then invoke fix-loop (Step 3) |
| P2/P3 | Log as discovery inline with the wave's items |

After review completes, append a review summary as an inline note under the wave's last item: `- Review: N findings (M fixed, K deferred)`. This captures the review outcome for resumability without a separate log section.

**Flow control**: Only pause for user input when the action table explicitly requires it (P0/P1 → fix-loop escalation, or `AskUserQuestion` calls elsewhere). Clean reviews and P2/P3-only reviews do not pause — log the outcome and continue to the next wave immediately.

### Step 3 — Per-wave fix-loop

If the per-wave review produces P0/P1 findings, invoke the **fix-loop** skill:

- **Findings**: P0/P1 findings with `verdict: "confirmed"` and `evidence` populated (set by orchestrator — per-wave review has no verifier pass)
- **Artifact paths**: files changed in this wave
- **Criteria**: the plan's criteria

Fix-loop runs max 2 attempts per finding. After 2 failed rounds, escalate to user via the `AskUserQuestion` tool with options: "Retry with guidance", "Accept current state and defer", "Skip finding", "Abort plan". Recommended: "Retry with guidance".

After fix-loop completes, commit the fixes separately: `git add [fixed files] && git commit -m "plan(<PLAN_SLUG>): Wave N fixes — [summary]"`

### Step 4 — Final review

After all waves complete, invoke the **two-pass-review** skill:

- **Artifact**: full diff from plan start to current HEAD (`git diff $PLAN_BASE_SHA..HEAD`)
- **Criteria**: complete criteria list from plan header
- **Scope**: all files changed across all waves

two-pass-review runs the reviewer agent (Pass 1) and, if any P0/P1 findings, auto-progresses to the verifier agent (Pass 2). Receive a `ReviewOutput` with verdicts populated.

If confirmed P0/P1 findings: invoke **fix-loop** with those findings. Fix subagents use **Opus** for cross-file fixes at this stage.

Present: "Final review: N criteria checked. K findings fixed."

### Step 5 — Discovery triage

After final review, review all discoveries logged during execution. For each:

| Type | Action |
|---|---|
| Criteria-affecting | Present to user via the `AskUserQuestion` tool — approve change or defer |
| Implementation detail | Note in plan file |
| Future work | Leave in plan file for reference |

### Step 6 — Completion summary

After discovery triage, append a `## Completion Summary` section to the plan file:

```markdown
## Completion Summary
**Status**: Complete | Partial — [date]

### Criteria
| Criterion | Result |
|---|---|
| [from plan header] | PASS / FAIL / PARTIAL — [1-line evidence] |

### Deferred
- [P2/P3 findings from reviews that weren't fixed]
- [Unresolved discoveries from triage]
- [or "None"]
```

Evaluate each criterion from the plan header against the final state. Be honest — mark FAIL or PARTIAL when warranted, not just PASS. The Deferred section collects P2/P3 findings and unresolved discoveries into one place so they don't silently disappear.

### Coupling detection

Items within a wave are committed together — wave grouping from plan-builder handles most coupling. Cross-wave coupling should not exist if plan-builder did its job correctly.

If a subagent returns `{ needs_scope_expansion: true, ... }`, the parent reassigns overlapping items to a single subagent and re-dispatches.

### Resumability

Resumable via `[x]` checks at wave granularity. On resume: find the first wave with any `[ ]` items, dispatch only those unchecked items.

If resuming means `PLAN_BASE_SHA` is lost, read it from the `**Base SHA**` line in the plan file header. Fallback: recover from the first wave's commit parent via `git log --format=%H --grep="plan(<PLAN_SLUG>): Wave" --reverse | head -1`, then `git rev-parse <that-commit>~1`.

## Rules

- **Parent NEVER reads source code or writes code.** All code work via subagents.
- **Always read the plan file fresh before each wave.** It may have been modified by fix-loop or externally.
- **`PLAN_BASE_SHA` recorded before the first wave** — used for final review diff range.
- Execute ONE wave per cycle. Don't batch waves — each wave needs its own commit and review gate.
- If an item is blocked or unclear, DON'T skip it. Use `AskUserQuestion` with options: "Clarify and proceed", "Skip this item", "Reorder plan", "Abort plan". Recommended: "Clarify and proceed".
- If an item requires a decision the plan doesn't specify, use `AskUserQuestion` with the enumerated options and a recommended choice. Do not proceed on assumptions.
- Discoveries go inline with the item that found them, not in a separate section.
