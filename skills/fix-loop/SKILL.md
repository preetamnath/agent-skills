---
name: fix-loop
description: "Bounded fix-and-verify protocol for resolving findings from a review. Max 2 attempts per finding, adaptive verification, escalates to user on failure."
---

# Fix Loop

A bounded fix-and-verify protocol for resolving confirmed findings from a review pass. Prevents infinite loops by capping attempts and escalating to the user.

## When to use

After a two-pass-review (or any review) produces confirmed P0/P1 findings that need fixing. Also after test failures that need code or test fixes.

## Protocol

### Input

- **Findings**: confirmed P0/P1 findings conforming to the [Output Schema](#output-schema) below
- **Artifact paths**: files to fix
- **Criteria**: the original criteria the fix must satisfy

**Intake filter:** Only process findings where `verdict = "confirmed"` and `severity in ["P0", "P1"]`. Ignore P2/P3 findings — they are out of scope.

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
If verification cannot run (flaky test, missing env, tool failure): treat as **inconclusive**. Use the `AskUserQuestion` tool with options: "Retry verification", "Accept fix without verification", "Revert and escalate". Recommended: "Retry verification". Do not count as a failed attempt.

### Round 2 — Fix + Verify (full)

1. Fix: spawn another fix subagent with context about what Round 1 attempted and why it didn't work
2. Stage the changes (`git add <specific files>`)
3. Verify: spawn the `verifier` agent with:
   - **Artifact**: the staged diff scoped to this finding's files (`git diff --staged -- <files_changed>`)
   - **Findings**: the original finding being fixed
   - **Criteria**: the original criterion the finding violated + "no new P0/P1 regressions introduced"
   - **Scope**: files changed in the fix
   - **Output contract**: "Return a ReviewOutput envelope (see [Output Schema](#output-schema)). Set verdict to confirmed/demoted/rejected with evidence on all findings."
4. If the verifier finds new P0/P1 issues: **escalate** (do not attempt Round 3)

### Escalation

If Round 2 still has unresolved P0/P1:
- **STOP.** Do not attempt Round 3.
- Present to the user:
  1. The original finding
  2. What was attempted in Rounds 1 and 2
  3. What's still broken and why
  4. Use the `AskUserQuestion` tool with options: "Manual fix", "Try a different approach", "Defer this finding". Recommended: "Defer this finding"

## Rules

- **Max 2 attempts.** Never loop beyond Round 2.
- **Scoped fixes.** Fix subagents must NOT edit files outside the scope of their finding without user approval. If a fix requires additional files, the subagent must FIRST return `{ needs_scope_expansion: true, additional_files: [paths], justification: string }` instead of making edits. The parent then uses the `AskUserQuestion` tool with options: "Approve expanded scope", "Reject — fix within original scope only", "Defer this finding". Recommended: "Approve expanded scope" (include the justification and file list). On approval, re-dispatch the subagent with expanded scope. Additional files are included in verification.
- **Always verify.** Every fix must be verified. Don't assume a fix worked — check.
- **Batch related findings.** Group related findings into one fix pass when they affect the same file(s).
- **Test failures.** Determine if it's a code bug or test bug first, then fix the right one.
  - Code bug: fix implementation, rerun test
  - Test bug: fix test, rerun test

---

## Output Schema

<!-- source: references/finding-schema.md -->

### Finding

```
Finding {
  id: sequential number starting from 1,
  severity: "P0" | "P1" | "P2" | "P3",
  title: short title,
  body: detailed explanation with evidence,
  file: file path or null for global issues,
  line_start: number or null,
  line_end: number or null,
  confidence: 0.0-1.0,
  criterion: what was violated,
  verdict: "confirmed" | "demoted" | "rejected" | null,
  evidence: reasoning for verdict | null
}
```

### ReviewOutput

Findings are wrapped in a `ReviewOutput` envelope:

```
ReviewOutput {
  schema_version: "v1",
  findings: Finding[],
  checks_run: string[]
}
```

### Severity calibration

- **P0** — Must fix: breaks functionality, security breach, data loss, or violates criteria
- **P1** — Fix before shipping: correct but incomplete, fragile, or reliability risk
- **P2** — Should fix: quality issue, code smell, not blocking
- **P3** — Nice to have: observation, style, minor improvement

### Field notes

- `confidence` — 1.0 means certain, below 0.5 means you're guessing. Be honest.
- `criterion` — required for P0/P1 findings. Name the specific criterion violated.
- `verdict` — populated by the verifier in two-pass review. Set to `null` when producing findings directly.
- `evidence` — verifier's reasoning for the verdict. Set to `null` when producing findings directly.
- `checks_run` — list every criterion evaluated, file path checked, or acceptance criterion verified. For ACs, use `AC-N: PASS — [evidence]` or `AC-N: FAIL — [reason]`.
