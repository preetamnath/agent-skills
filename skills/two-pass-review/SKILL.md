---
name: two-pass-review
description: "Two-pass code review: a `code-reviewer` pass followed by an adversarial `verifier` pass. Use for final review of completed code changes (e.g., end of plan-runner) or any code review where a false positive would cost the user real time. Do NOT use for non-code artifacts or for quick spot-checks during iteration."
---

# Two-Pass Review

A reusable review protocol that produces high-confidence findings on code changes by running a `code-reviewer` pass followed by an adversarial `verifier` pass. All output conforms to the [Output Schema](#output-schema) below.

## When to use

For code review where you'd present findings to the user and a false positive costs real time (final review at end of plan-runner, pre-merge audit). Don't present unverified findings for non-trivial code reviews — always run both passes.

For non-code artifacts (PRDs, plans, prose), spawn `reviewer` directly — this skill is hard-wired to `code-reviewer` for Pass 1.

## Protocol

### Pass 1 — Review

Spawn the `code-reviewer` agent with:
- **Artifact**: the file(s) or diff to review
- **Criteria**: what to review against
- **Scope**: what's in-bounds
- **Output contract**: "Return a ReviewOutput envelope (see [Output Schema](#output-schema)). Set verdict and evidence to null on all findings. Populate checks_run with what you evaluated (e.g., criteria names, file paths checked)."

Collect its output (ReviewOutput with P0-P3 findings + checks_run).

**Auto-progression:**
- Zero P0/P1 findings → terminate after Pass 1. Present the clean result with `checks_run` so the user can see what was evaluated.
- One or more P0/P1 findings → proceed automatically to Pass 2. No user prompt.

### Pass 2 — Verify

Spawn the `verifier` agent with:
- **Artifact**: same as Pass 1
- **Findings**: the reviewer's full output (Finding array)
- **Criteria**: same as Pass 1
- **Output contract**: "For each finding, set verdict to confirmed/demoted/rejected and provide evidence. Severity may be adjusted up under `confirmed` or down under `demoted`. Return a ReviewOutput envelope with the full findings array (verdicts populated). Add any new observations as new findings with their own IDs (continuing the sequence) — but first check whether the observation is a re-discovery of an existing finding; if so, modify the existing finding instead of appending. Populate checks_run."

Collect its output (ReviewOutput with verdicts + new observations).

### Present to user

Show:
1. **P0/P1 findings** — confirmed and demoted-to-P0/P1. Mark demotions clearly (e.g., "demoted from P0 → P1") and promotions clearly (e.g., "promoted from P2 → P1") so the user can see the verifier's adjustment.
2. **Summary count** — "X of Y P0/P1 confirmed, W demoted, Z rejected"
3. **P2/P3 findings** — confirmed and demoted-to-P2/P3 (briefly, as FYI)
4. **New observations** from the verifier (if any)

**All-rejected case:** If the verifier rejected every reviewer finding, do not present this as a clean review. Surface it explicitly: show the rejected findings with verifier reasoning, flagged as "reviewer/verifier disagreement — sanity-check the verifier's rejections before treating this as clean."

Do NOT show rejected findings (other than the all-rejected case) or unverified P2/P3s unless the user asks.

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
