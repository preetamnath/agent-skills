---
name: two-pass-review
description: "Two-pass code review — a review pass hardened by an adversarial verification pass that suppresses false positives. TRIGGER when: user wants final review of completed code changes; any review where a false positive would cost real time. SKIP when: reviewing a non-code artifact (reviewer); a quick spot-check during iteration."
---

# Two-Pass Review

A reusable review protocol that produces high-confidence findings on code changes by running a `code-reviewer` pass followed by an adversarial `verifier` pass. All output conforms to the [Output Schema](#output-schema) below.

## When to use

For code review where you'd present findings to the user and a false positive costs real time (final review of a completed change, pre-merge audit). Don't present unverified findings for non-trivial code reviews — always run both passes.

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
- Zero P0/P1 findings → terminate after Pass 1 and present the clean result in this shape:
  ```
  **Review result — clean:**
  - Checks run: [criterion / file path checked, one per line]
  - P0/P1 findings: none
  ```
- One or more P0/P1 findings → proceed automatically to Pass 2. No user prompt.

### Pass 2 — Verify

Spawn the `verifier` agent with:
- **Artifact**: same as Pass 1
- **Findings**: the reviewer's full output (Finding array)
- **Criteria**: same as Pass 1
- **Output contract**: "For each finding, set verdict to confirmed/demoted/rejected and provide evidence. Severity may be adjusted up under `confirmed` or down under `demoted`. Return a ReviewOutput envelope with the full findings array (verdicts populated). Add any new observations as new findings with their own IDs (continuing the sequence) — but first check whether the observation is a re-discovery of an existing finding; if so, modify the existing finding instead of appending. Populate checks_run."

Collect its output (ReviewOutput with verdicts + new observations).

### Present to user

Report in this shape:

```
**Two-pass review results:**
- P0/P1 findings: [id: title — confirmed | demoted Px→Py | promoted Px→Py — evidence]
- Summary: [X] of [Y] P0/P1 confirmed, [W] demoted, [Z] rejected
- P2/P3 (FYI): [id: title — verdict]
- New observations: [id: title — severity — evidence]
- Disagreement: [none | reviewer/verifier split — sanity-check the verifier's rejections before treating as clean]
```

(Write `None — zero P0/P1 findings after both passes` when the P0/P1 list is empty.) Mark each demotion ("demoted P0 → P1") and promotion ("promoted P2 → P1") so the user sees the verifier's adjustment. **All-rejected case:** if the verifier rejected every reviewer finding, do not present it as clean — populate Disagreement with the rejected findings + verifier reasoning. Do NOT show rejected findings (other than the all-rejected case) or unverified P2/P3s unless the user asks.

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
- `checks_run` — list every criterion evaluated, file path checked, or acceptance criterion verified. For ACs, use `AC-NNN-XX: PASS — [evidence]` or `AC-NNN-XX: FAIL — [reason]`.
