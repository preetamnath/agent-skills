---
name: parallel-diagnosis
description: "Parallel independent root-cause diagnosis for uncertain bugs. Two agents investigate independently, then converge on a unified diagnosis."
---

# Parallel Diagnosis

Two independent agents investigate a bug in parallel, then converge on a single unified diagnosis. Produces structured output that downstream skills (two-pass-review, fix-loop) can act on.

## When to use

- **YES:** Multi-layer bugs (schema + router + model), framework quirks, uncertain library behavior, high-risk deploys, intermittent failures
- **NO:** Trivial bugs, typos, issues where root cause is already known, zero blast radius

## Diagnosis schema

Read the full schema definition from `references/diagnosis-schema.md`.

All output must conform to this schema.

---

## Protocol

### Step 1: Parallel Diagnosis

1. Spin up **2 independent subagents** in parallel. Default: Sonnet. Use Opus for complex async/architectural bugs.
2. Give them ONLY the problem statement and relevant file paths.
3. Instruct each agent to:
   - Read the code independently — no communication between agents.
   - Trace the root cause.
   - Propose where the fix should go (not the fix itself).
   - Note any caveats or uncertainties.
4. Collect both reports.

**Failure handling:**
- One agent returns unusable output → treat it as a non-vote. Proceed with the single usable report, noting `confidence: "medium"` (single source, reduced but not absent).
- Both agents return unusable output → retry Step 1 once with fresh agents.
- Both retries fail → abort and escalate to the human.

### Step 2: Consensus

Compare both diagnosis reports.

- **If they agree:** High confidence. Set `agreement: "converged"`. Proceed to Step 3.
- **If they disagree:** Read the contested files yourself and resolve. If still ambiguous, escalate to the human with both reports. Set `agreement: "resolved"` (orchestrator resolved) and proceed to Step 3, or `agreement: "escalated"` (human needed).
- **If both conclude not a bug:** Report findings to the human and stop.
- **If one found an extra detail:** Include it only if it concerns the same root cause and does not contradict the other agent's findings.
- **Outcome:** Produce exactly 1 unified diagnosis.

### Step 3: Output

1. Produce a `DiagnosisOutput` conforming to `references/diagnosis-schema.md`.
2. Present to the human with a recommended next step:
   - If the diagnosis points to a clear fix → recommend fix-loop
   - If the fix needs review before applying → recommend two-pass-review
   - If the diagnosis is uncertain → recommend the human investigate further, citing the specific uncertainty
3. **If `agreement` is "escalated":** Wait for the human to resolve. After the human provides direction, produce the `DiagnosisOutput` incorporating the human's input, set `agreement: "resolved"`, and proceed with the recommended next step.

---

## Constraints

- **Agent cap:** Max 2 subagents per run.
- **No reuse:** Never reuse agents across retries. Spin up fresh agents each time.
- **Human in the loop:** At disagreements, ambiguity, or escalation — use `AskUserQuestion` with structured options and a recommended choice. Never silently proceed on assumptions.
- **Retry limit:** Max 1 retry of Step 1 if both agents fail. After that, escalate.

## Handoff

This skill is composable. Its structured output feeds directly into:

- **fix-loop** — to fix confirmed issues. The `affected_files` and `fix_direction` fields give fix-loop enough context to act.
- **two-pass-review** — to review a proposed fix. The `root_cause` and `confidence` fields inform what the reviewer should validate.

The `DiagnosisOutput` preserves both raw agent reports for transparency, so downstream skills or the human can trace reasoning back to source.
