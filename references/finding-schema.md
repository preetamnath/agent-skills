# Finding Schema v1

The canonical schema for structured review findings. Used by code-reviewer, reviewer, verifier, two-pass-review, and fix-verify-loop.

## Inlined schema

<!-- fragment: output-schema -->

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
  validated_by: "reviewer" | "verifier" | "machine" | null,
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
- `verdict` — initial reviewers set `null`; verifiers populate it after adjudication. A caller may set `confirmed` when routing an observed failure with honest `validated_by` and `evidence` values.
- `validated_by` — `reviewer` means initial review only; `verifier` means independent verification; `machine` requires the exact check and observed failure. Missing or `null` means unverified.
- A machine result proves only the observed failure, not an inferred cause.
- `evidence` — reasoning or an exact observed result supporting the verdict; use `null` before adjudication.
- `checks_run` — list every criterion evaluated, file path checked, or acceptance criterion verified. For ACs, use `AC-NNN-XX: PASS — [evidence]` or `AC-NNN-XX: FAIL — [reason]`.

<!-- /fragment: output-schema -->
