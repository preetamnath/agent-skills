---
name: triage
description: "Verify a panel's findings against their artifact: each gets a consider / skip verdict and a confidence. TRIGGER when: a fan-out skill needs its findings verified before walking them with the user; user says 'triage these findings', 'verify which of these are real', 'which are worth acting on'."
---

# Triage

Verify a list of findings: fan out independent checkers, each judging whether a finding is real and worth acting on, and returning a per-finding verdict and a confidence. The caller decides what to do with them.

## Instructions

### Step 1 — Receive the inputs

The caller passes: the **findings** (each with an id and its claim) and the **artifact path(s)**. If the findings or the artifact are missing, ask before proceeding.

### Step 2 — Batch the findings and fan out

- **Batch:** **1–3 findings per checker, sized by complexity** (more than 3 degrades independence and quality) — a finding needing deep ground-truth checking goes alone; simple or closely-related ones can share.
- **Dispatch:** one `general-purpose` subagent per batch, in parallel — cap ~6 concurrent and wave the rest.
- **Each checker gets only:** its finding(s), the artifact path(s), the return contract below, and the instruction not to fan out checkers of its own.

For each finding it holds, the checker reads the artifact fresh and:
- **real?** — is the finding correct, or a misread? Ground it in the artifact.
- **material?** — does it warrant the user's attention?
- maps the two axes to one **verdict**:
    - real AND material → `consider`
    - not real, or real but trivial → `skip`
    - can't be checked against the given artifact (claim rests on runtime behavior or files outside it) → `skip` with reason `unverifiable`
- returns: `verdict`, `adjusted_confidence` (0.00–1.00, the checker's fresh score), one-line `reason` — on a `skip`, say which: false positive, real-but-trivial, or unverifiable.

### Step 3 — Return output conforming to the [Output Schema](#output-schema) below.

Collect the checkers' results verbatim — don't re-judge or override a verdict.

## Rules

- **Clean room.** A checker didn't produce the finding it judges — don't pass it the panel's reasoning, prior score, or your expected verdict.
- **Score from the read, don't re-rank by fiat.** Verdict and confidence come from the checker's read, not the caller's preference.
- **Bar-free.** Judge `consider`/`skip` on the finding's own merits; the caller owns any confidence bar and applies it after.

---

## Output Schema

```
TriageResult {
  verdicts: [
    {
      finding_id: string,
      verdict: "consider" | "skip",
      adjusted_confidence: number,   // 0.00–1.00, the checker's fresh score
      reason: string                 // one line; on skip: false positive, real-but-trivial, or unverifiable
    }
  ]
}
```
