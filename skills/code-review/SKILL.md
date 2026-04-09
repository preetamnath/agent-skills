---
name: code-review
description: "Structured code review with P0-P3 findings, confidence scores, and criteria-based analysis. Use for reviewing code changes, PRs, or specific files."
---

# Code Review

Analyze code changes for correctness, security, edge cases, and quality. Return structured findings in the Finding schema v1.

## When to use

- Reviewing code changes (staged, unstaged, or specific commits)
- Reviewing specific files or file sets
- Quick structured review of a PR or branch

For full two-pass review with adversarial verification, use `/two-pass-review` instead.

## Instructions

### 1 — Gather the artifact

Determine what to review:
- If the user specified files: read those files
- If the user specified a diff range: run `git diff <range>`
- Otherwise: run `git status` and `git diff` to see current changes

For modified files, review the diff. For untracked files, read the full content. For deleted files, check for broken references.

If related files are needed for context (types, interfaces, callers), read them too.

### 2 — Automated checks

If the project supports it:
- Read `package.json` to check available scripts
- If a `lint` script exists, run it
- If `tsconfig.json` exists, run `npx tsc --noEmit`
- Note any failures as P0/P1 findings

### 3 — Analyze

Review the code for:
- **Correctness** — does the code do what it's supposed to?
- **Security** — injection, unauthorized access, data exposure?
- **Edge cases** — unhandled scenarios, boundary conditions?
- **Bugs** — obvious errors, off-by-one, null references?
- **Performance** — inefficient patterns (only flag with evidence)?

Do NOT flag: style preferences, naming opinions, theoretical risks without evidence, or things you'd do differently but aren't wrong.

### 4 — Return findings

Return a `ReviewOutput` envelope conforming to the [Output Schema](#output-schema) below.

- Set `verdict` and `evidence` to `null` on all findings
- Include honest `confidence` scores — 1.0 means certain, below 0.5 means you're guessing
- Populate `checks_run` with what you evaluated (files, criteria, lint/typecheck results)
- If no issues are found, return an empty findings array — don't manufacture problems

## Constraints

- **No fixes.** Do NOT implement fixes unless explicitly asked.
- **Report only.** Present findings for the user to review.

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
