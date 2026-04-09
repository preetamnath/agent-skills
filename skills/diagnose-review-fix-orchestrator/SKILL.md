---
name: diagnose-review-fix-orchestrator
description: "End-to-end pipeline for uncertain bugs: diagnose root cause, review the fix, then verify and harden. Chains parallel-diagnosis → two-pass-review → fix-loop."
---

# Diagnose → Review → Fix

An orchestration protocol that chains three skills into a single pipeline: find the root cause, write the fix, review it, and harden it. The human stays in the loop at every stage transition.

## When to use

- **YES:** Uncertain bugs where root cause is unknown, multi-layer issues, high-risk changes needing diagnosis + review
- **NO:** Known bugs (skip to fix-loop), code review of existing changes (use two-pass-review directly), trivial fixes
- If you already know the root cause, skip Stage 1 and start at Stage 2

## Pipeline

Four stages. Every stage transition requires human approval via `AskUserQuestion` with structured options and a recommended choice. Never auto-proceed.

### Stage 1: Diagnose

Load the `parallel-diagnosis` skill. Pass it the problem statement and relevant file paths.

Receive: `DiagnosisOutput` with `status`, `root_cause`, `confidence`, `agreement`, `affected_files`, `fix_direction`.

**Checkpoint:** Present diagnosis to the human. Check `status` first, then evaluate `confidence` and `agreement`.
- If `status` is `"not_a_bug"` → report findings and stop. No fix needed.
- If `status` is `"inconclusive"` → stop or gather more context before proceeding.
- If `status` is `"diagnosed"`: evaluate `confidence` and `agreement` to decide next steps.
  - `confidence: "low"` or human disagrees → stop or re-run with more context.
  - `confidence: "medium"` + `agreement: "escalated"` warrants more caution than `"medium"` + `"converged"` — surface the disagreement context to the human.
- Only proceed to Stage 2 on human approval.

### Stage 2: Fix

No sub-skill — the parent LLM writes the fix directly.

Using the diagnosis output (`root_cause`, `affected_files`, `fix_direction`), read the affected files and make the code changes. This is a normal coding task.

**Checkpoint:** Show the changes to the human. Proceed on approval.

### Stage 3: Review

Load the `two-pass-review` skill. Pass it:
- **Artifact**: the files changed in Stage 2
- **Criteria**: "Does this fix address the diagnosed root cause? Are there regressions, edge cases, or incomplete handling?"
- **Scope**: the files changed in Stage 2 and their immediate callers/dependents

Receive: `ReviewOutput` with findings (P0–P3, confirmed/demoted/rejected).

**Checkpoint:** Present review findings to the human.
- No confirmed P0/P1 findings → recommend shipping. Skip Stage 4.
- Confirmed P0/P1 findings → recommend proceeding to Stage 4.

### Stage 4: Harden

Load the `fix-loop` skill. Pass it:
- **Findings**: the confirmed P0 and P1 findings from Stage 3
- **Artifact paths**: the files changed in Stage 2
- **Criteria**: derived from the original diagnosis (`root_cause` + `fix_direction`) and the review criteria from Stage 3

fix-loop will attempt fixes (max 2 per finding) and verify each one.

Receive: fix-loop output with per-finding results: resolved in Round 1, resolved in Round 2, or escalated with attempt history.

**Checkpoint:** Present final state to the human.

## Shortcutting

Before applying any shortcut, confirm with the user via the `AskUserQuestion` tool. Present the detected condition and the proposed skip as a structured option alongside "Run all stages".

| Condition | Action |
|---|---|
| Root cause already known | Skip Stage 1, start at Stage 2 |
| Fix is trivial after diagnosis | Skip Stages 3–4 — apply directly after human confirms the fix is trivial |
| Review finds no P0/P1 issues | Skip Stage 4, recommend shipping |
| Human says stop at any checkpoint | Present what you have and halt |

## Constraints

- Every stage transition requires human approval. Never silently proceed.
- Never auto-proceed from diagnosis to fix without the human seeing the diagnosis.
- Never auto-proceed from fix to review without the human seeing the changes.
- If any stage fails or the human says stop, present what you have and halt gracefully.
- This skill does not define its own output schema — it uses the schemas of the skills it chains (`DiagnosisOutput`, `ReviewOutput`, Finding schema v1).

## Output

Present a final summary to the human:

1. **Root cause** — from Stage 1 (or user-provided if Stage 1 was skipped)
2. **Changes made** — from Stage 2
3. **Review findings and resolution** — from Stages 3–4
4. **Deferred items** — any P2/P3 findings from review (FYI only)
