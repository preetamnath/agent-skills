---
name: second-opinion
description: "Anchored second-opinion on one concrete proposal: dispatch a subagent to rate the fix, generate ranked alternatives, and flag blind spots, then synthesize back. TRIGGER when: user says 'second opinion', 'rate my fix', 'weigh in on my approach', 'what alternatives am I missing', or wants their candidate edit/decision evaluated against alternatives. SKIP when: multiple decisions on a larger artifact — use `panel-review`."
---

# Second Opinion

## Steps

### Step 1 — Brief the subagent

If there's no concrete anchor (specific edit, chosen option, phrasing under review), stop and ask the user for one.

Otherwise, spawn one subagent with a briefing containing exactly:
- **Context** — file path(s), surrounding code/prose, constraints.
- **Problem statement** — what the proposal is trying to solve and why this approach.
- **The proposed fix** — verbatim.
- **What's already ruled out** — alternatives the user has considered and rejected, with the reason.
- **The 3-part ask.** The subagent returns:
  1. **Rate the proposal.** Pros, cons, and a confidence score (0.00–1.00) that it improves on the current state.
  2. **Generate 2–4 alternatives.** Each with proposed option, reasoning, and a confidence score (0.00–1.00) that it beats the user's proposal.
  3. **Flag additional issues.** Anything the proposal does not address — scope ambiguity, missing trigger classes, downstream impact.

### Step 2 — Synthesize back

- **Table:**

| # | Option | Tradeoff | Reviewer conf. |
|---|---|---|---|
| 1 | User's proposal — [content] | … | 0.xx (vs. status quo) |
| 2 | Alt 1 — [content] | … | 0.xx (vs. proposal) |
| … | up to 4 alternatives, ordered by reviewer confidence | | |

- **Additional issues flagged:** reviewer-surfaced blind spots not addressed by any alternative (omit if none).
- **Recommendation:** your synthesized pick with brief reasoning and your own confidence (0.xx, distinct from the reviewer scores above).
- **Checkpoint:** call `AskUserQuestion` with the top 2–3 options.
