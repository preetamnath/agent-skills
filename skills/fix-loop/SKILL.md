---
name: fix-loop
description: "Bounded fix-and-verify protocol for resolving findings from a review. Max 2 attempts per finding, adaptive verification, escalates to user on failure."
---

# Fix Loop

A bounded fix-and-verify protocol for resolving confirmed findings from a review pass. Prevents infinite loops by capping attempts and escalating to the user.

## When to use

After a two-pass-review (or any review) produces confirmed P0/P1 findings that need fixing. Also after test failures that need code or test fixes.

## Finding schema (v1)

Read the full schema definition from `references/finding-schema-v1.md`.

Input findings must conform to this schema (same as two-pass-review and code-review output, i.e. Finding schema v1).

**Intake filter:** Only process findings where `verdict = "confirmed"` and `severity in ["P0", "P1"]`. Ignore P2/P3 findings — they are out of scope.

## Protocol

### Input

- **Findings**: confirmed P0/P1 findings conforming to the Finding schema (v1)
- **Artifact paths**: files to fix
- **Criteria**: the original criteria the fix must satisfy

### Round 1 — Fix

For each finding (or batch of related findings that affect the same files):
1. Spawn a fix subagent (Sonnet for scoped fixes, Opus for cross-file fixes)
2. Subagent receives: the finding (full schema), the affected file path(s), the criterion it violates
3. Subagent fixes the code and returns: `{ files_changed: [paths], summary: string, concerns: [string] | null }`
4. Stage the changes (`git add <specific files>`) — do NOT commit. User decides when to commit.

### Round 1 — Verify (targeted)

Deterministic check — confirm the specific finding is resolved without spawning an agent:
- If tests exist: rerun the relevant test(s)
- If code pattern: grep/read the specific lines to confirm the fix
- If behavioral: spot-check the fixed code against the criterion

If the finding is resolved and no obvious new issues: **done**.
If the finding persists or new issues are apparent: proceed to Round 2.
If verification cannot run (flaky test, missing env, tool failure): treat as **inconclusive** and escalate to user with the reason. Do not count as a failed attempt.

### Round 2 — Fix + Verify (full)

1. Fix: spawn another fix subagent with context about what Round 1 attempted and why it didn't work
2. Stage the changes (`git add <specific files>`)
3. Verify: spawn the `verifier` agent with:
   - **Artifact**: the staged diff scoped to this finding's files (`git diff --staged -- <files_changed>`)
   - **Findings**: the original finding being fixed
   - **Criteria**: the original criterion the finding violated + "no new P0/P1 regressions introduced"
   - **Scope**: files changed in the fix
   - **Output contract**: "Return a ReviewOutput envelope (see Finding schema v1 at `references/finding-schema-v1.md`). Set verdict to confirmed/demoted/rejected with evidence on all findings."
4. If the verifier finds new P0/P1 issues: **escalate** (do not attempt Round 3)

### Escalation

If Round 2 still has unresolved P0/P1:
- **STOP.** Do not attempt Round 3.
- Present to the user:
  1. The original finding
  2. What was attempted in Rounds 1 and 2
  3. What's still broken and why
  4. Ask the user to decide: manual fix, different approach, or defer

## Rules

- Max 2 fix attempts per finding. Never loop beyond Round 2.
- Fix subagents must NOT edit files outside the scope of their finding without pre-approval. If a fix requires additional files, the subagent must FIRST return `{ needs_scope_expansion: true, additional_files: [paths], justification: string }` instead of making edits. The parent approves and re-dispatches with expanded scope. Additional files are included in verification.
- Every fix must be verified. Don't assume a fix worked — check.
- Group related findings into one fix pass when they affect the same file(s).
- For test failures: determine if it's a code bug or test bug first, then fix the right one.
  - Code bug: fix implementation, rerun test
  - Test bug: fix test, rerun test
