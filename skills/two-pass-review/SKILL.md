---
name: two-pass-review
description: "Two-pass code review — a review pass hardened by an adversarial verification pass that suppresses false positives. TRIGGER when: user wants final review of completed code changes; any review where a false positive would cost real time. SKIP when: reviewing a non-code artifact (reviewer); a quick spot-check during iteration."
---

# Two-Pass Review

## Protocol

### Pass 1 — Review

Spawn the `code-reviewer` agent with:
- **Artifact**: the file(s) or diff to review
- **Criteria**: what to review against
- **Scope**: what's in-bounds
- **Output**: Return a `ReviewOutput`; set every finding's `verdict` and `evidence` to null, and list evaluated criteria and paths in `checks_run`.

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
- **Findings**: the reviewer's full `Finding` array
- **Criteria**: same as Pass 1
- **Output**: Return a `ReviewOutput` with the full findings array and populated `checks_run`.
  - **Verdicts**: Set every finding to `confirmed`, `demoted`, or `rejected` and provide evidence.
  - **Severity**: Adjust severity up under `confirmed` or down under `demoted`.
  - **Boundary**: Verify only Pass 1 findings; do not add findings.

### Present to user

Report in this shape:

```
**Two-pass review results:**
- P0/P1 findings: [id: title — confirmed | demoted Px→Py | promoted Px→Py — evidence]
- Summary: [X] of [Y] P0/P1 confirmed, [W] demoted, [Z] rejected
- P2/P3 (FYI): [id: title — verdict]
- Disagreement: [none | reviewer/verifier split — rejected findings and verifier reasoning]
```

- **Empty result:** Write `None — zero P0/P1 findings after both passes` when the P0/P1 list is empty.
- **Severity changes:** Mark each demotion (`demoted P0 → P1`) and promotion (`promoted P2 → P1`).
- **All rejected:** Report zero confirmed P0/P1 findings, populate Disagreement with the rejected findings and verifier reasoning, and stop without another automatic review.
- **Visibility:** Hide rejected findings outside the all-rejected case and unverified P2/P3 findings unless the user asks.

---

## Output Schema

<!-- source: references/finding-schema.md#output-schema -->

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

<!-- /source: references/finding-schema.md#output-schema -->
