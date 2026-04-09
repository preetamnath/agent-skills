---
name: parallel-diagnosis
description: "Parallel independent root-cause diagnosis for uncertain bugs. Two agents investigate independently, then converge on a unified diagnosis."
---

# Parallel Diagnosis

Two independent agents investigate a bug in parallel, then converge on a single unified diagnosis. Produces structured output that downstream skills (two-pass-review, fix-loop) can act on.

## When to use

- **YES:** Multi-layer bugs (schema + router + model), framework quirks, uncertain library behavior, high-risk deploys, intermittent failures
- **NO:** Trivial bugs, typos, issues where root cause is already known, zero blast radius

## Instructions

### 1 — Parallel diagnosis

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

### 2 — Consensus

Compare both diagnosis reports.

- **If they agree:** High confidence. Set `agreement: "converged"`. Proceed to Step 3.
- **If they disagree:** Read the contested files yourself and resolve. If still ambiguous, escalate to the human with both reports. Set `agreement: "resolved"` (orchestrator resolved) and proceed to Step 3, or `agreement: "escalated"` (human needed).
- **If both conclude not a bug:** Report findings to the human and stop.
- **If one found an extra detail:** Include it only if it concerns the same root cause and does not contradict the other agent's findings.
- **Outcome:** Produce exactly 1 unified diagnosis.

### 3 — Return output

1. Produce a `DiagnosisOutput` conforming to the [Output Schema](#output-schema) below.
2. Present to the human with a recommended next step:
   - If the diagnosis points to a clear fix → recommend fix-loop
   - If the fix needs review before applying → recommend two-pass-review
   - If the diagnosis is uncertain → recommend the human investigate further, citing the specific uncertainty
3. **If `agreement` is "escalated":** Wait for the human to resolve. After the human provides direction, produce the `DiagnosisOutput` incorporating the human's input, set `agreement: "resolved"`, and proceed with the recommended next step.

## Constraints

- **Agent cap.** Max 2 subagents per run.
- **No reuse.** Never reuse agents across retries. Spin up fresh agents each time.
- **Human in the loop.** At disagreements, ambiguity, or escalation — use `AskUserQuestion` with structured options and a recommended choice. Never silently proceed on assumptions.
- **Retry limit.** Max 1 retry of Step 1 if both agents fail. After that, escalate.

## Handoff

This skill is composable. Its structured output feeds directly into:

- **fix-loop** — to fix confirmed issues. The `affected_files` and `fix_direction` fields give fix-loop enough context to act.
- **two-pass-review** — to review a proposed fix. The `root_cause` and `confidence` fields inform what the reviewer should validate.

The `DiagnosisOutput` preserves both raw agent reports for transparency, so downstream skills or the human can trace reasoning back to source.

---

## Output Schema

<!-- source: references/diagnosis-schema.md -->

### DiagnosisOutput

```
DiagnosisOutput {
  schema_version: string, always "v1",
  status: "diagnosed" | "not_a_bug" | "inconclusive",
  root_cause: string, unified root cause (1-3 sentences),
  confidence: "high" | "medium" | "low",
  affected_files: string[], file paths involved in the root cause,
  fix_direction: string, what should be fixed and how, in prose — NOT code,
  agreement: "converged" | "resolved" | "escalated",
  agent_reports: AgentReport[]
}
```

### AgentReport

```
AgentReport {
  agent_id: number, 1 | 2,
  root_cause: string, this agent's root cause assessment,
  affected_files: string[], file paths this agent identified,
  fix_direction: string, this agent's proposed fix direction,
  confidence_notes: string, any caveats or uncertainties this agent noted
}
```

### Field notes

- `status` — `"diagnosed"`: normal case, root cause found and actionable. `"not_a_bug"`: both agents concluded the reported behavior is not a bug — terminal, no downstream skills needed. `"inconclusive"`: couldn't determine root cause, escalated to human for further investigation.
- `confidence` — `"high"`: both agents agreed on root cause. `"medium"`: orchestrator resolved a disagreement. `"low"`: significant uncertainty remains (e.g., one agent failed, or orchestrator resolution was shaky).
- `agreement` — `"converged"`: agents independently reached the same conclusion. `"resolved"`: agents disagreed but the orchestrator reconciled. `"escalated"`: human input was needed to resolve.
- `root_cause` — the unified assessment, not a copy of either agent's report. When agents disagreed and the orchestrator resolved, this reflects the orchestrator's judgment.
- `fix_direction` — prose description of what to change and where. Enough detail for fix-loop or a human to act on, but no code.
- `affected_files` — union of files from both agents, filtered to those relevant to the unified root cause.
- `agent_reports` — both raw reports preserved for transparency. Downstream consumers can trace reasoning back to source.
- `confidence_notes` — per-agent field. Agents should be honest about what they're unsure of. Empty string if no caveats.
