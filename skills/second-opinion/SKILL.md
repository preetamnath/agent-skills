---
name: second-opinion
description: "Anchored second-opinion on a concrete proposal: dispatch a subagent to rate the fix, generate ranked alternatives, and flag blind spots, then synthesize back. TRIGGER when: user says 'second opinion', 'rate my fix', 'weigh in on my approach', 'what alternatives am I missing', or wants their candidate edit/decision evaluated against alternatives."
---

# Second Opinion

## Protocol

### 1 — Brief the subagent

If there's no concrete anchor (specific edit, chosen option, phrasing under review), stop and tell the user this skill needs a candidate to critique.

Otherwise, spawn one subagent — or more if the user explicitly asks for multi-reviewer (R0/R1/R2) — with a briefing containing exactly:
- **Context** — file path(s), surrounding code/prose, constraints.
- **Problem statement** — what the proposal is trying to solve and why this approach.
- **The proposed fix** — verbatim.
- **What's already ruled out** — alternatives the user has considered and rejected, with the reason.
- **The 3-part ask**.

### 2 — The 3-part ask

The subagent returns:
1. **Rate the proposal.** Pros, cons, and a confidence score (0.00–1.00) that it improves on the current state.
2. **Generate 2–4 alternatives.** Each with the proposed phrasing/option, the reasoning, and a confidence score *vs. the user's proposal* (not absolute) — i.e., how confident the agent is this alternative beats the anchor.
3. **Flag additional issues.** Anything the proposal does not address — scope ambiguity, missing trigger classes, downstream impact.

### 3 — Synthesize back

Return to the user with:
- A comparison table: rows = (user's proposal + each alternative), columns = phrasing, confidence vs. proposal, key tradeoff.
- The subagent's additional flagged issues.
- Your own ranked recommendation with your confidence score.
- A focused `AskUserQuestion` with the top 2–3 options for the user to pick.
