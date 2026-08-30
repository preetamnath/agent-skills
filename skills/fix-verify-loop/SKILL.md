---
name: fix-verify-loop
description: "Resolve confirmed P0/P1 findings in at most two fix-and-verify attempts, then escalate. TRIGGER when: review findings or test failures need resolution; user says 'fix these findings' or 'resolve the P0s'. Per-finding resolution only; the caller owns regressions."
---

# Fix-Verify Loop

Resolve confirmed P0/P1 findings in at most two fix-and-verify attempts. Leave fixes staged, and return their paths plus one outcome per finding.

The caller owns regression detection, new-issue discovery, and whole-diff review.

## Protocol

### Input

- **Findings:** Confirmed P0/P1 findings conforming to the [Output Schema](#output-schema).
- **Artifact paths:** Files the resolver may edit.
- **Criteria:** Original requirements each fix must satisfy.

**Intake filter:** Process only findings with `verdict = "confirmed"` and `severity in ["P0", "P1"]`. The caller owns confirmation quality; finding source does not affect intake. Leave P2/P3 findings with the caller.

**Pre-gate:** Before mutation, independently verify any finding whose `evidence` is missing, null, or starts with `Orchestrator-confirmed`.

Confidence reports certainty, not validation history; it never triggers the pre-gate.

Complete the pre-gate before any mutation:

1. **Batch.** Group findings by shared files, symbols, call chains, or reported root cause. Put at most four findings in each batch.
2. **Dispatch.** Run up to four `verifier` agents concurrently and queue the rest. Repository rules that forbid overlapping checks override this limit. Give each verifier:
   - **Artifact**: the files or surrounding context for its batch.
   - **Findings**: every finding in its batch.
   - **Criteria**: "Is each finding real?"
   - **Output contract**: a `ReviewOutput` envelope with one verdict per finding.
3. **Collect.** Wait for every batch before Round 1. A missing or unparseable verdict makes only that finding inconclusive.
4. **Route.** Route each finding independently:
   - `rejected` → add to `dropped` and skip the fix loop.
   - `confirmed` → proceed to Round 1.
   - `demoted` to P0/P1 → proceed to Round 1.
   - `demoted` to P2/P3 → add to `demoted` and skip the fix loop.
   - inconclusive → proceed to Round 1 without consuming a fix attempt.

### Conflict-group loop

Group surviving findings by shared files, symbols, call chains, tests, mutable artifacts, behavior, or root cause. Keep groups to four findings unless one root cause cannot split safely.

- **Fix in parallel.** Run one fixer per group. Dispatch every proven-disjoint group concurrently up to agent capacity; queue known or uncertain overlap. Repository concurrency rules override dispatch.
- **Verify in parallel.** Verify a completed group while unrelated fixers continue. Give each verifier up to four related findings, and run verifier batches concurrently unless their checks share mutable resources or repository rules forbid overlap. Wait when an active fixer could affect the files, behavior, or checks under verification.
- **Account separately.** Keep each finding's verdict, attempt count, bucket, and escalation state independent even when one fixer or verifier handles the group.
- **Stage serially.** The parent stages one group at a time. Fixers never stage files.

Give each finding at most two attempts. Proven-disjoint groups may occupy different rounds concurrently.

Include these rules in every fix-subagent brief:

- **Git writes.** Keep Git mutations within assigned files; never run `git stash`, `git checkout -- .`, `git reset`, or another whole-tree command.
- **Git index.** Do not run `git add` or otherwise change the Git index; the parent stages each group for verification.
- **Git reads.** Keep Git reads within assigned paths.
- **Committed baseline.** Read a committed baseline without changing shared state with `git show HEAD:<path>`.
- **Edit scope.** Do not edit outside the group's approved paths.
- **Expansion request.** When a fix needs more files, return `{ needs_scope_expansion: true, additional_files: [paths], justification: string }` before editing them.
- **Expansion decision.** Use `AskUserQuestion` with "Approve expanded scope", "Reject — fix within original scope only", and "Defer this finding"; recommend approval with the justification and file list.
- **Approved expansion.** After approval, add the files to verification, regroup any overlapping findings, and re-dispatch the fixer.
- **Test failures.** For a test failure, inspect the code and test, decide which is wrong, and fix that side.

### Staging safety

Apply this check to each group in each round:

1. **Snapshot.** Before dispatching the fixer, record `git diff --staged --binary -- <group's approved artifact paths>`.
2. **Detect index changes.** After the fixer returns, compare the staged diff with the snapshot. On mismatch, report the change and ask how to proceed; do not stage over it.
3. **Validate paths.** Confirm every path in `files_changed` belongs to the group's approved artifact paths. On mismatch, report the out-of-scope paths and ask how to proceed; do not stage them.
4. **Check existing hunks.** When the snapshot contains hunks in `files_changed`, proceed only if every hunk belongs to an earlier resolved finding in this invocation or exactly matches this group's recorded earlier attempt. Otherwise, inspect the hunks and ask the user:
    - Small unrelated hunks without line overlap → recommend "Commit pre-existing first".
    - Large, sprawling, or overlapping hunks → recommend "Stash pre-existing".
    - Hunks that continue the fix → recommend "Proceed (treat as part of this fix)".
    - Use `AskUserQuestion` with those three options, put the recommendation first with `(Recommended)`, and summarize the hunks in one line.
5. **Stage.** After the checks pass, run `git add <files_changed>` for one group at a time. Record the exact path-scoped staged binary diff for the group's next round.

### Round 1 — Fix + Verify

1. **Fix.** Apply staging-safety Step 1, then spawn one fix subagent per conflict group with every finding, approved path, and violated criterion in that group. It edits the working tree and returns `{ files_changed: [paths], summary: string, finding_summaries: [{ id: Finding.id, summary: string }], concerns: [string] | null }`.
2. **Stage.** Apply staging-safety Steps 2–5 without committing.
3. **Verify.** Dispatch the group's findings in related batches of at most four. Each verifier receives:
   - **Artifact**: the exact staged diff captured for the group's files after staging
   - **Findings**: every finding in its verification batch
   - **Criteria**: "Is each finding resolved?" and no broader review
   - **Output contract**: a `ReviewOutput` envelope with one verdict per finding
4. **Decide.** Map each finding's verdict independently:

   | Verdict | Action |
   |---|---|
   | `confirmed` | Still P0/P1 → **proceed to Round 2**. |
   | `rejected` | Add to `resolved` → **done**. |
   | `demoted` to P0/P1 | **Proceed to Round 2**. |
   | `demoted` to P2/P3 | Add to `demoted` → **done**. |
   | Inconclusive — crash, malformed output, or no verdict for this finding | Count the attempt → **proceed to Round 2**. |

### Round 2 — Fix + Verify

Regroup the P0/P1 findings that survive Round 1 using the same conflict test. Proven-disjoint groups may enter Round 2 while other groups finish Round 1.

1. **Fix.** Apply staging-safety Step 1, then spawn one fixer per surviving group with each finding's Round 1 attempt, failure reason, and verifier evidence. Use the Round 1 return shape.
2. **Stage.** Apply staging-safety Steps 2–5 without committing.
3. **Verify.** Use the Round 1 verification dispatch for the surviving findings.
4. **Decide.** Map each finding's verdict independently:

   | Verdict | Action |
   |---|---|
   | `confirmed` | Add to `escalated` → **escalate**. |
   | `rejected` | Add to `resolved` → **done**. |
   | `demoted` to P0/P1 | Add to `escalated` → **escalate**. |
   | `demoted` to P2/P3 | Add to `demoted` → **done**. |
   | Inconclusive | Count the attempt, add to `escalated`, and **escalate**. |

### Escalation

For each finding still unresolved after Round 2:
- **Stop.** Do not attempt Round 3 for this finding.
- Present its `finding_summaries` entries in this shape; derive the staged line with `git diff --staged --stat -- <files_changed>`:
  ```
  **Escalated — finding not resolved after 2 attempts:**
  - Finding: [ID — title]
  - Attempted: [Round 1 summary] → [Round 2 summary]
  - Still unresolved: [verifier's evidence | verifier inconclusive]
  - Currently staged: [e.g. "R2's changes to auth.js, +12/-4 lines" | nothing staged]
  ```
  Then use `AskUserQuestion` with "Manual fix", "Try a different approach", "Defer this finding", and "Discard R2 changes and revert"; recommend "Defer this finding".

After all findings are processed, return a [`FixVerifyLoopOutput`](#fixverifyloopoutput) envelope. Set `files_changed` to the deduplicated validated paths whose fix-loop changes remain staged.

---

## Output Schema

### FixVerifyLoopOutput

The skill returns this envelope after all findings are processed:

```
{
  files_changed: [string, ...],           // validated paths with fix-loop changes still staged
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
