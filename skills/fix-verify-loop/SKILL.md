---
name: fix-verify-loop
description: "Bounded resolver for confirmed P0/P1 findings — for each: fix, verify the fix resolved it, up to 2 attempts, then escalate. TRIGGER when: a review or fan-out skill needs confirmed findings driven to resolution; user says 'fix these findings' or 'resolve the P0s'. Scoped to per-finding resolution; regressions are the caller's job."
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

**Intake filter:** Only process findings where `verdict = "confirmed"` and `severity in ["P0", "P1"]`. Ignore P2/P3 findings — they are out of scope. Note: findings with `verdict: "confirmed"` are accepted regardless of source — the caller is responsible for confirmation quality (e.g., an orchestrator may set this as an escape hatch for review findings that have no verifier pass).

**Pre-gate phase (findings without an independent verifier pass):** Collect every finding that requires independent verification before Round 1. A finding requires the pre-gate when:
- `evidence` field is null or missing, OR
- `evidence` field starts with "Orchestrator-confirmed".

Confidence is the reviewer or verifier's honest signal — it does not by itself trigger pre-gate. Pre-gate's job is to catch findings that haven't been independently verified, not findings that the verifier already vouched for at low confidence.

Run one pre-gate phase before any mutation:

1. **Batch.** Group findings that share files, symbols, call chains, or a reported root cause. Put at most four findings in one batch; keep unrelated findings in separate batches.
2. **Dispatch.** Run at most four `verifier` agents concurrently and queue additional batches. Repository rules that forbid overlapping checks override this concurrency. Give each verifier:
   - **Artifact**: the files or surrounding context for its batch.
   - **Findings**: every finding in its batch.
   - **Criteria**: "Is each finding real?"
   - **Output contract**: a `ReviewOutput` envelope with one verdict per finding.
3. **Collect.** Wait for every batch before starting Round 1. Treat a missing or unparseable verdict as inconclusive only for that finding; keep other returned verdicts.
4. **Route.** Apply each finding's verdict independently:
   - `rejected` → add to `dropped` and skip the fix loop.
   - `confirmed` → proceed to Round 1.
   - `demoted` to P0/P1 → proceed to Round 1.
   - `demoted` to P2/P3 → add to `demoted` and skip the fix loop.
   - inconclusive → proceed to Round 1 without consuming a fix attempt.

Findings that pass the intake filter and either skip or survive the pre-gate proceed to Round 1 after every batch finishes.

### Conflict-group loop

After the pre-gate phase, group surviving findings that share files, symbols, call chains, tests, mutable artifacts, behavior, or a root cause. Keep ordinary groups to four findings; exceed four only when splitting one root cause would make the fix unsafe.

- **Fix in parallel.** Run one fixer per group. Dispatch all groups concurrently when their files, behavior, checks, and mutable artifacts are proven disjoint; queue groups when overlap is known or uncertain. Repository concurrency rules and available agent capacity override dispatch size.
- **Verify in parallel.** As soon as a group is fixed, verify it while unrelated fixers continue. Batch up to four related findings per verifier and run verifier batches concurrently unless their checks share mutable resources or repository rules forbid overlap. Wait when an active fixer could change the files, behavior, or checks being verified.
- **Account separately.** Keep each finding's verdict, attempt count, bucket, and escalation state independent even when one fixer or verifier handles the group.
- **Stage serially.** The parent stages one group at a time. Fixers never stage files.

For each finding, run Round 1; if it remains P0/P1, run Round 2; if it remains unresolved, escalate. Different conflict groups may be in different rounds concurrently when they remain proven disjoint.

Include these rules in every fix-subagent brief:

- Keep Git mutations scoped to assigned files: never run `git stash`, `git checkout -- .`, `git reset`, or another command that changes the whole tree.
- Do not run `git add` or otherwise change the Git index; the parent stages each group for verification.
- Scope every Git read to assigned paths.
- Read a committed baseline without changing shared state with `git show HEAD:<path>`.

### Staging safety

Apply this check to each group in each round:

1. **Snapshot.** Before dispatching the fixer, record `git diff --staged --binary -- <group's approved artifact paths>`.
2. **Detect index changes.** After the fixer returns, compare the same staged diff with the snapshot. On mismatch, report the unexpected index change and ask how to proceed; do not stage over it.
3. **Check existing hunks.** When the snapshot contains staged hunks in `files_changed`, proceed without asking only when every hunk belongs to an earlier resolved finding in this invocation or matches the exact staged record from this group's earlier attempt. Otherwise, inspect the hunks and ask the user:
    - No overlap with the fix's likely lines, hunks small, look unrelated → recommend "Commit pre-existing first"
    - Overlap with the fix's lines, OR hunks large/sprawling → recommend "Stash pre-existing"
    - Hunks clearly continue the fix's logical change → recommend "Proceed (treat as part of this fix)"
    - Use the `AskUserQuestion` tool with options "Commit pre-existing first", "Stash pre-existing", "Proceed (treat as part of this fix)". Include a one-line summary of what was found (e.g., "3 hunks in auth.js totaling 18 lines, no overlap with fix's edits"). Surface the heuristic recommendation as the first option labeled "(Recommended)".
4. **Stage.** After the checks pass, the parent runs `git add <files_changed>` for one group at a time and records the exact path-scoped staged binary diff for the group's next round.

### Round 1 — Fix + Verify

1. **Fix.** Spawn one fix subagent per conflict group. Give it every finding in the group, their approved paths, and their violated criteria. It edits the working tree and returns `{ files_changed: [paths], summary: string, finding_summaries: [{ id: Finding.id, summary: string }], concerns: [string] | null }`.
2. **Stage.** Apply [Staging safety](#staging-safety), then stage the group without committing.
3. **Verify.** Dispatch the group's findings in related batches of at most four. Each verifier receives:
   - **Artifact**: the exact staged diff captured for the group's files after staging
   - **Findings**: every finding in its verification batch
   - **Criteria**: ONLY "Is each finding resolved?"
   - **Output contract**: "Return a ReviewOutput envelope (see [Output Schema](#output-schema)) with one verdict per finding."
4. **Decide.** Map each finding's verdict independently:
   - `confirmed` → still real and still in scope (P0/P1) → not resolved → **proceed to Round 2**.
   - `rejected` → not a real issue → adds to `resolved` bucket → **done**.
   - `demoted` → check the new severity:
     - new severity in [P0, P1] → still in fix-verify-loop scope → **proceed to Round 2**.
     - new severity in [P2, P3] → out of fix-verify-loop scope → adds to `demoted` bucket → **done** (the issue exists at lower severity; hand-off implicit).
   - **Inconclusive** (the verifier subagent fails to return a parseable ReviewOutput — crash, malformed output, no verdict on the finding) → **counts as a failed attempt**. Proceed to Round 2. No retry loop.

### Round 2 — Fix + Verify

Regroup only the findings that remain P0/P1 after Round 1 using the same conflict test. Proven-disjoint groups may enter Round 2 while other groups are still fixing or verifying Round 1.

1. **Fix.** Spawn one fixer per surviving conflict group with full Round 1 context for each unresolved finding: what was attempted, why it failed, and the verifier's evidence. Require the same return shape as Round 1.
2. **Stage.** Apply [Staging safety](#staging-safety), then stage the group without committing.
3. **Verify.** Use the Round 1 verification dispatch for the surviving findings.
4. **Decide.** Map each finding's verdict independently:
   - `confirmed` → still real and still in scope (P0/P1) → not resolved → adds to `escalated` bucket → **escalate** (do not attempt Round 3).
   - `rejected` → not a real issue → adds to `resolved` bucket → **done**.
   - `demoted` → check the new severity:
     - new severity in [P0, P1] → still in fix-verify-loop scope → adds to `escalated` bucket → **escalate**.
     - new severity in [P2, P3] → out of fix-verify-loop scope → adds to `demoted` bucket → **done** (the issue exists at lower severity; hand-off implicit).
   - **Inconclusive** (the verifier subagent fails to return a parseable ReviewOutput) → **counts as a failed attempt** → adds to `escalated` bucket → **escalate**. No retry loop.

### Escalation

For each finding still unresolved after Round 2:
- **STOP.** Do not attempt Round 3.
- Present each finding using its `finding_summaries` entries in this shape (derive the staged line via `git diff --staged --stat -- <files_changed>`):
  ```
  **Escalated — finding not resolved after 2 attempts:**
  - Finding: [ID — title]
  - Attempted: [Round 1 summary] → [Round 2 summary]
  - Still unresolved: [verifier's evidence | verifier inconclusive]
  - Currently staged: [e.g. "R2's changes to auth.js, +12/-4 lines" | nothing staged]
  ```
  Then use the `AskUserQuestion` tool with options: "Manual fix", "Try a different approach", "Defer this finding", "Discard R2 changes and revert". Recommended: "Defer this finding".

After all findings are processed, return a [`FixVerifyLoopOutput`](#fixverifyloopoutput) envelope with four buckets:
- **resolved**: finding IDs marked done in Round 1 or Round 2 (with the staged files)
- **escalated**: findings that hit Round 2 without resolution, with attempt summaries
- **dropped**: findings the pre-gate verifier rejected as not-real
- **demoted**: findings demoted to P2/P3 by the verifier (out of fix-verify-loop scope)

Bucket assignment by verdict path:
- Pre-gate `rejected` → `dropped`
- Pre-gate `confirmed` → proceed to Round 1
- Pre-gate `demoted` to [P0, P1] → proceed to Round 1
- Pre-gate `demoted` to [P2, P3] → `demoted`
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
- **Scoped fixes.** Fix subagents must NOT edit files outside their group's approved paths without user approval. If a fix requires additional files, the subagent must FIRST return `{ needs_scope_expansion: true, additional_files: [paths], justification: string }` instead of making edits. The parent then uses the `AskUserQuestion` tool with options: "Approve expanded scope", "Reject — fix within original scope only", "Defer this finding". Recommended: "Approve expanded scope" (include the justification and file list). On approval, re-dispatch the subagent with expanded scope and regroup any finding that now overlaps another group. Additional files are included in verification.
- **Always verify.** Every finding gets its own resolution verdict. A verifier may cover up to four related findings, but it answers only "Is each finding resolved?" for each one.
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
- `checks_run` — list every criterion evaluated, file path checked, or acceptance criterion verified. For ACs, use `AC-NNN-XX: PASS — [evidence]` or `AC-NNN-XX: FAIL — [reason]`.
