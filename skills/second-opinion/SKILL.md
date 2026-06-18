---
name: second-opinion
description: "Second opinion on one concrete proposal: stress-test it, rank alternatives, or both. TRIGGER when: user says 'second opinion', '2nd opinion', 'rate my fix', or 'weigh in on my approach'; user wants a candidate edit/decision evaluated. SKIP when: multiple decisions on a larger artifact — use `validate-answer`."
---

# Second Opinion

## Steps

### Step 1 — Anchor, then route

When there's no concrete anchor (a specific edit, chosen option, or phrasing under review), ask the user for one.

Route by what the proposal needs:

| The proposal needs | Run | Pass it as |
|---|---|---|
| "Is this worth doing? what am I missing?" | `sanity-checker` | **Subject** |
| "Is there a better option, and how does mine rank?" | `propose-alternatives` | **Current approach** |
| Want both, or high-stakes and unsure | both, in parallel | as above |

When ambiguous, default to `sanity-checker` — the cheaper, more common need.

Brief each agent with: the file path / surrounding context and constraints; the proposal verbatim and the problem it solves; alternatives the user already ruled out, with reasons.

### Step 2 — Synthesize only what ran

- **Table** (only if `propose-alternatives` ran) — proposal plus alternatives in one confidence frame, ordered by confidence:

  | # | Option | Tradeoff | Conf. |
  |---|---|---|---|
  | 1 | Proposal — [content] | … | 0.xx |
  | 2 | Alt — [content] | … | 0.xx |

- **Worth-it verdict + blind spots** (only if `sanity-checker` ran) — lead with its verdict, then blind spots and open concerns; omit if none.
- **Disagreement** (only if both ran) — surface it when they split on keep-vs-replace: `propose-alternatives` ranks an alternative above the proposal while `sanity-checker`'s verdict calls it sound (or the reverse).
- **Recommendation** — spot-check the load-bearing claims behind your pick against the cited code, then give your pick, brief reasoning, and your own confidence (0.xx, distinct from the agents').
- **Checkpoint** — call `AskUserQuestion` with the top 2–3 options.
