---
name: jtbd
description: "Frame a vague goal as the job to be done, so the outcome is explicit before you build or choose. TRIGGER when: user says 'what's the job', 'JTBD', 'frame the outcome', 'what are we actually trying to do'; or a goal, feature, or decision is stated as a solution with the progress underneath it unnamed."
---

# JTBD — Job To Be Done

Primitive: **JTBD** — name the job the user is hiring for, then judge every option by job-fit.

People hire a product to make progress in a situation — the **job** is that progress, not the feature they ask for or who they are.

## The lens — a job is one story:

> *when [situation], I want to [motivation], so I can [outcome], without [constraint].*

- **Situation** — the trigger and context they're in.
- **Motivation** — what they reach for; the core desire.
- **Outcome** — the progress that ends the story.
- **Without** — the pain or constraint they're avoiding; often where the real insight sits. Name it when it sharpens the job.

## Steps

1. **Find and draft the job.** Read the thread for the job in play. If several are live, list them and ask which — or name the primary; don't silently pick. Write it in the lens format, marking any unsupported part `[unclear]` — never fill a slot with a guess.
2. **Check the outcome is progress, not a restated feature.** Test: could a completely different solution deliver the same outcome? If not, it's a feature — ask "so they can *what*?" until it lands on progress.
3. **Score the options by job-fit, then state it back** in the format below. If only the asked-for path is live, add 1–2 alternatives. Rank by job-fit — not elegance, effort, or novelty; the *without* usually separates them.

**Job frame** — the shape to state back:

```
Job:        when [situation], I want to [motivation], so I can [outcome], without [constraint]
            (any unsupported part → [unclear])
Confidence: 0.00–1.00 — how well the thread supports the job; blanks and assumptions lower it
Options (when choosing):
  | Option | Job-fit 0–1 | Serves the without? |
  |---|---|---|
Winner:     the option that best gets the job done — one line
```

(Write `Job unclear — [which parts are blank and why]` when the thread doesn't support a job.)

## Examples

### Job statements — the format filled across domains

- **Milkshake** — *when I face a long, boring commute, I want a thick, filling treat, so I can keep a hand busy and my stomach full, without making a mess in the car.*
- **Spotify Discover Weekly** — *when I want music while I work, I want fresh tracks I'll probably like, so I can stay in flow, without stopping to curate a playlist.*
- **PayPal** — *when I'm buying online, I want a fast, trusted way to pay, so I can check out in seconds, without re-entering my card or fearing fraud.*

### A worked reframe — from a solution-shaped ask to the output format

Ask: "Add a bulk-export button to the orders page."

- **Job** — *when I'm reconciling last month's sales in my accounting tool, I want my order data out of the app, so I can close the books, without having to remember to pull it every month.*
- **Confidence** — 0.6: the thread gave the ask and the reconciling context, but the monthly *without* is inferred, not stated.
- **Options** —

  | Option | Job-fit 0–1 | Serves the *without*? |
  |---|---|---|
  | Export button (asked for) | 0.5 | No — relies on remembering to click each month |
  | Scheduled CSV email | 0.9 | Yes — arrives monthly, no memory needed |
- **Winner** — scheduled CSV email: gets the job done without the user remembering, so the asked-for feature loses to a better fit.
