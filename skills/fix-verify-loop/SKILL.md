---
name: fix-verify-loop
description: "Bounded resolver for confirmed P0/P1 findings. For each finding: fix → verify resolution via the verifier agent → up to 2 attempts → escalate. Scoped to per-finding resolution; regressions are the caller's job."
---

# Fix-Verify Loop

fix-verify-loop is a **bounded resolver**. Input: confirmed P0/P1 findings. Output: staged code where each listed finding is resolved, OR an escalation list of findings it could not resolve in 2 attempts.

It verifies ONLY per-finding resolution. Regression detection, finding new issues, and reviewing the diff as a whole are explicitly NOT its job — those belong to whoever reviews the diff next (caller's choice).

## When to use

After a two-pass-review (or any review) produces confirmed P0/P1 findings that need fixing. Also after test failures that need code or test fixes.

## Protocol

### Input

- **Findings**: confirmed P0/P1 findings conforming to the [Output Schema](#output-schema) below
- **Artifact paths**: files to fix
- **Criteria**: the original criteria the fix must satisfy

**Intake filter:** Only process findings where `verdict = "confirmed"` and `severity in ["P0", "P1"]`. Ignore P2/P3 findings — they are out of scope. Note: findings with `verdict: "confirmed"` are accepted regardless of source — the caller is responsible for confirmation quality (e.g., plan-runner sets this as an orchestrator escape hatch for per-wave review findings that have no verifier pass).

**Pre-gate (findings without an independent verifier pass):** A finding requires a verifier pre-gate BEFORE Round 1 if it has not been verifier-validated. Detect via:
- `evidence` field is null or missing, OR
- `evidence` field starts with "Orchestrator-confirmed".

Confidence is the reviewer or verifier's honest signal — it does not by itself trigger pre-gate. Pre-gate's job is to catch findings that haven't been independently verified, not findings that the verifier already vouched for at low confidence.

For these findings, run this pre-gate first:
1. Spawn the `verifier` agent with: **Artifact** = the finding's file (or surrounding context), **Findings** = the single finding, **Criteria** = "is this finding real?".
2. If verifier returns `rejected` → adds to `dropped` bucket → drop the finding from fix-verify-loop. Skip to next finding.
3. If verifier returns `confirmed` or `demoted` (still real) → proceed to Round 1 normally.
4. If verifier output is inconclusive (no parseable verdict) → treat as a failed attempt. Proceed to Round 1 anyway (this consumes one of the two attempts; see inconclusive rule below).

Findings that pass the intake filter and either don't trigger the pre-gate or pass it proceed to Round 1.

### Per-finding loop

Process findings **sequentially, one at a time**. Do not batch. For each finding, run Round 1; if not resolved, run Round 2; if still not resolved, escalate. Round 1 and Round 2 mirror each other in shape — same fix-then-verify dispatch, same verifier question.

### Preconditions — pre-staged hunk check

This check fires in **Round 1 only**, AFTER the fix subagent declares `files_changed` and BEFORE staging. The fix subagent doesn't know what files it will touch until it runs, so the Round 1 order is: spawn fix → check pre-staged hunks → stage → verify. In Round 2, any pre-existing staged content is from Round 1's prior attempt and not user-authored — the check would fire spuriously, so we skip it. Round 2 order is: spawn fix → stage → verify.

Before staging (Round 1 only):
- Run `git diff --staged -- <files the fix will touch>` (the `files_changed` returned by the fix subagent).
- If non-empty (pre-existing staged hunks exist in those files):
  - Inspect the hunks. Form a heuristic judgment:
    - No overlap with the fix's likely lines, hunks small, look unrelated → recommend "Commit pre-existing first"
    - Overlap with the fix's lines, OR hunks large/sprawling → recommend "Stash pre-existing"
    - Hunks clearly continue the fix's logical change → recommend "Proceed (treat as part of this fix)"
  - Use the `AskUserQuestion` tool with options "Commit pre-existing first", "Stash pre-existing", "Proceed (treat as part of this fix)". Include a one-line summary of what was found (e.g., "3 hunks in auth.js totaling 18 lines, no overlap with fix's edits"). Surface the heuristic recommendation as the first option labeled "(Recommended)".

### Round 1 — Fix + Verify

1. **Fix.** Spawn a fix subagent (Sonnet for scoped fixes, Opus for cross-file fixes). Subagent receives: the finding (full schema), the affected file path(s), the criterion it violates. Subagent edits the working tree and returns `{ files_changed: [paths], summary: string, concerns: [string] | null }`.
2. **Pre-staging check.** Run the [Preconditions](#preconditions--pre-staged-hunk-check) check on `files_changed`.
3. **Stage.** `git add <files_changed>` — do NOT commit. The user decides when to commit.
4. **Verify.** Spawn the `verifier` agent with:
   - **Artifact**: the staged diff scoped to this finding's files (`git diff --staged -- <files_changed>`)
   - **Findings**: the original finding being fixed (single)
   - **Criteria**: ONLY "is this finding resolved?"
   - **Output contract**: "Return a ReviewOutput envelope (see [Output Schema](#output-schema)) with a verdict on the single finding."
5. **Decide.** Map the verifier's verdict on the finding:
   - `confirmed` → still real and still in scope (P0/P1) → not resolved → **proceed to Round 2**.
   - `rejected` → not a real issue → adds to `resolved` bucket → **done**.
   - `demoted` → check the new severity:
     - new severity in [P0, P1] → still in fix-verify-loop scope → **proceed to Round 2**.
     - new severity in [P2, P3] → out of fix-verify-loop scope → adds to `demoted` bucket → **done** (the issue exists at lower severity; hand-off implicit).
   - **Inconclusive** (the verifier subagent fails to return a parseable ReviewOutput — crash, malformed output, no verdict on the finding) → **counts as a failed attempt**. Proceed to Round 2. No retry loop.

### Round 2 — Fix + Verify

Same shape as Round 1. The only difference is the fix subagent gets Round 1 context.

1. **Fix.** Spawn another fix subagent with full Round 1 context (what was attempted, why it didn't work, the verifier's evidence). Subagent returns `{ files_changed: [paths], summary: string, concerns: [string] | null }`.
2. **Stage.** `git add <files_changed>`. (No pre-staging check in Round 2 — see [Preconditions](#preconditions--pre-staged-hunk-check) for why.)
3. **Verify.** Same dispatch as Round 1 — verifier asked "is this finding resolved?" on the single finding.
4. **Decide.** Map the verifier's verdict on the finding:
   - `confirmed` → still real and still in scope (P0/P1) → not resolved → adds to `escalated` bucket → **escalate** (do not attempt Round 3).
   - `rejected` → not a real issue → adds to `resolved` bucket → **done**.
   - `demoted` → check the new severity:
     - new severity in [P0, P1] → still in fix-verify-loop scope → adds to `escalated` bucket → **escalate**.
     - new severity in [P2, P3] → out of fix-verify-loop scope → adds to `demoted` bucket → **done** (the issue exists at lower severity; hand-off implicit).
   - **Inconclusive** (the verifier subagent fails to return a parseable ReviewOutput) → **counts as a failed attempt** → adds to `escalated` bucket → **escalate**. No retry loop.

### Escalation

If Round 2 still has the finding unresolved:
- **STOP.** Do not attempt Round 3.
- Present to the user:
  1. The original finding
  2. What was attempted in Rounds 1 and 2
  3. What's still unresolved and why (verifier's evidence)
  4. A one-line summary of what's currently staged for this finding (derive via `git diff --staged --stat -- <files_changed>`, e.g., "Currently staged: R2's changes to auth.js, +12/-4 lines")
  5. Use the `AskUserQuestion` tool with options: "Manual fix", "Try a different approach", "Defer this finding", "Discard R2 changes and revert". Recommended: "Defer this finding"

After all findings are processed, return a [`FixVerifyLoopOutput`](#fixverifyloopoutput) envelope with four buckets:
- **resolved**: finding IDs marked done in Round 1 or Round 2 (with the staged files)
- **escalated**: findings that hit Round 2 without resolution, with attempt summaries
- **dropped**: findings the pre-gate verifier rejected as not-real
- **demoted**: findings demoted to P2/P3 by the verifier (out of fix-verify-loop scope)

Bucket assignment by verdict path:
- Pre-gate `rejected` → `dropped`
- Pre-gate `confirmed` or `demoted` → proceed to Round 1
- R1 `rejected` → `resolved`
- R1 `confirmed` (still real, P0/P1) → proceed to Round 2
- R1 `demoted` to [P0, P1] → proceed to Round 2
- R1 `demoted` to [P2, P3] → `demoted`
- R2 `rejected` → `resolved`
- R2 `confirmed` (still real, P0/P1) → `escalated`
- R2 `demoted` to [P0, P1] → `escalated`
- R2 `demoted` to [P2, P3] → `demoted`

## Rules

- **Max 2 attempts.** Never loop beyond Round 2.
- **Scoped fixes.** Fix subagents must NOT edit files outside the scope of their finding without user approval. If a fix requires additional files, the subagent must FIRST return `{ needs_scope_expansion: true, additional_files: [paths], justification: string }` instead of making edits. The parent then uses the `AskUserQuestion` tool with options: "Approve expanded scope", "Reject — fix within original scope only", "Defer this finding". Recommended: "Approve expanded scope" (include the justification and file list). On approval, re-dispatch the subagent with expanded scope. Additional files are included in verification.
- **Always verify.** Every fix gets the verifier-on-one-question check. Don't skip — the verifier agent is the only verification mechanism this skill uses.
- **Test failures.** Determine if it's a code bug or test bug first, then fix the right one. This judgment happens during the fix subagent's work — the subagent inspects the failure and the test, decides which is wrong, and fixes the right one. The skill itself does not branch on this; it's part of the fix subagent's task.

---

## Output Schema

### FixVerifyLoopOutput

The skill returns this envelope after all findings are processed:

```
{
  resolved: [Finding.id, ...],            // fixed in R1 or R2
  escalated: [{                           // could not be fixed in 2 attempts
    id: Finding.id,
    attempts: [string, string],           // R1 + R2 summaries
    evidence: string | null,              // verifier's evidence (null if R2 was inconclusive)
    staged_summary: string                // e.g., "R2's changes to auth.js, +12/-4 lines"
  }, ...],
  dropped: [{                             // pre-gate verifier rejected as not-real
    id: Finding.id,
    reason: string                        // verifier's rejection evidence
  }, ...],
  demoted: [{                             // demoted to P2/P3 (out of scope)
    id: Finding.id,
    new_severity: "P2" | "P3",
    evidence: string                      // verifier's demotion reasoning
  }, ...]
}
```

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
