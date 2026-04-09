---
name: two-pass-review
description: "Orchestrates a reviewer + verifier agent pair for high-confidence review findings. Use any time you need to review an artifact and present findings to the user."
---

# Two-Pass Review

A reusable review protocol that produces high-confidence findings by running a reviewer pass followed by an adversarial verifier pass. All output conforms to the [Output Schema](#output-schema) below.

## When to use

Any time you need to review an artifact and present findings to the user. Don't present unverified findings for non-trivial reviews — always run both passes.

## Protocol

### Pass 1 — Review

Spawn the `reviewer` agent with:
- **Artifact**: the file(s) or diff to review
- **Criteria**: what to review against
- **Scope**: what's in-bounds
- **Output contract**: "Return a ReviewOutput envelope (see [Output Schema](#output-schema)). Set verdict and evidence to null on all findings. Populate checks_run with what you evaluated (e.g., criteria names, file paths checked)."

Collect its output (ReviewOutput with P0-P3 findings + checks_run).

### Pass 2 — Verify

Spawn the `verifier` agent with:
- **Artifact**: same as Pass 1
- **Findings**: the reviewer's full output (Finding array)
- **Criteria**: same as Pass 1
- **Output contract**: "For each finding, set verdict to confirmed/demoted/rejected and provide evidence. Return a ReviewOutput envelope with the full findings array (verdicts populated). Add any new observations as new findings with their own IDs (continuing the sequence). Populate checks_run."

Collect its output (ReviewOutput with verdicts + new observations).

### Present to user

Show ONLY:
1. Confirmed P0 and P1 findings (with verifier's evidence)
2. Summary count: "X of Y P0/P1 confirmed, Z rejected"
3. Demoted findings (briefly, as FYI)
4. New observations from the verifier (if any)

Do NOT show rejected findings or unverified P2/P3s unless the user asks.

## Variant selection

| Condition | Variant |
|---|---|
| Single file AND explicitly requested as lite | Lite |
| Final build review, architecture, security-critical | Dual-model |
| Everything else | Standard (default) |

### Dual-model review

For high-stakes reviews (final build review, architecture decisions):
1. Run TWO reviewer agents in parallel — one at Sonnet, one at Opus
2. Merge findings. **Dedup rule:** two findings are duplicates only when they share the exact same `(file, line_start, line_end, severity)` tuple. When matched, keep the finding with the longer body. Everything else stays — extra findings are cheaper than lost signal.
3. Renumber IDs sequentially (1, 2, 3, ...) across the merged set. Original IDs from individual reviewers are discarded — the merged sequence is the single source of truth from this point forward.
4. Feed merged findings to a single verifier (Opus)
5. Verifier confirms/demotes/rejects across the combined set

### Lite review

For small-scope reviews:
- Run reviewer only. Skip verifier.
- Use **only** when scope is a single file AND the caller or user explicitly requests lite mode.
- Present reviewer findings directly with a note: "Unverified — lite review."
- Lite findings have `verdict: null` and are not eligible for fix-loop intake (which requires `verdict: "confirmed"`). To fix lite findings, run a full review first or manually confirm them.

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
