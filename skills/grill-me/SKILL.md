---
name: grill-me
description: "Stress-test a plan, design, or decision — challenge assumptions, expose gaps, force specificity. TRIGGER when: user says 'grill me' or 'stress-test this'; user wants their plan or decision pushed on."
---

# Grill Me

Adversarial review of a plan or design through targeted questioning. The goal is to find gaps, contradictions, and unexamined assumptions before they become bugs or rework.

## When to use

When the user has a plan or design and wants it pressure-tested before committing to build.

## Protocol

### 1 — Read context first

Before asking anything, silently explore:
- The plan or design doc if one exists
- Architecture docs, CLAUDE.md, relevant code in the affected area
- Related modules or prior decisions

Don't ask questions the codebase already answers. Don't ask questions the plan already addresses. When the read surfaces a risk, contradiction, or overlap the user didn't raise, open a thread on it — saying it came from the codebase.

### 2 — Grill

Ask one question at a time. Wait for the answer before continuing.

**How to challenge:**
- Don't accept vague answers. "We'll handle that later" → "What specifically will you handle, and what breaks if you don't?"
- Point out contradictions between decisions. "You said X above but Y here — which wins?"
- For every critical path, ask: "What happens when this fails?"
- Challenge hidden assumptions: "You're assuming Z — is that guaranteed?"
- When the user gives a tradeoff, push on the cost side: "You chose A over B for speed — what do you lose?"
- If an answer reveals a new branch, follow it before returning to the main thread.

**How to calibrate intensity:**
- Challenge things that are risky, ambiguous, or load-bearing. Skip obvious or low-impact decisions.
- If the user's answer is solid and specific, say so and move on. Don't manufacture objections.
- If you'd make the same choice, say "Agreed — that's the right call" and advance. Grilling isn't about disagreeing with everything.

**What to cover** (in whatever order the plan demands):
- Failure modes and error handling
- Edge cases and boundary conditions
- Dependencies and ordering assumptions
- Security and data integrity
- Scalability and performance under load
- User experience gaps (empty states, error states, race conditions)
- Scope creep risks — what looks small but isn't?
- What's explicitly out of scope, and is that safe?

### 3 — End condition

Stop grilling when one of these is true:
- Every load-bearing decision has a specific, defended answer
- Remaining open items are low-impact and the user is aware of them
- The user says stop

### 4 — Confirm before writing

Print this summary in chat:

```
**Grill summary (pre-write):**
- Gaps found: [gap → user's resolution]        (one per line)
- Decisions that held: [decision → why solid]
- Risks accepted: [risk — rationale | none]

**Assumptions the plan carries (never grilled):**
- [assumption] — [what rests on it]
```

(Write `None — every load-bearing assumption was grilled` when the assumptions list is empty.) Then use the `AskUserQuestion` tool only to collect the choice, with options: "Looks good — write it", "Continue grilling on [specific area]", "Adjust before writing". Recommended: "Looks good — write it".

### 5 — Write summary

**If grilling an existing interview file:** Append the grill results to that file under a new `## Grill Results` section. Update any decisions or gaps that were resolved or changed during the grill.

**If grilling a standalone plan or idea:** Write to `meta/interviews/NNN-grill-<topic-slug>.md`, creating the directory if missing and incrementing `NNN` from the highest existing number (start at `001`).

Tell the user the file path either way.

```markdown
## Grill Results: [topic]

### Decisions that held up
| Decision | Why it's solid |
|---|---|
| ... | ... |

### Gaps found
| Gap | Risk | User's resolution |
|---|---|---|
| ... | ... | ... |

### Assumptions to validate
- [things stated as true but not yet verified]

### Remaining risks accepted
- [known risks the user chose to carry, with rationale]
```

After writing, use the `AskUserQuestion` tool with options: "Proceed to building a plan", "Proceed to implementation", "Done for now". Recommended: "Proceed to building a plan" if gaps were resolved and the plan is ready for execution.

## Rules

- **Use the `AskUserQuestion` tool when a challenge has distinct choices.** If you can enumerate the options (e.g., "retry with backoff vs. fail fast"), use the tool with your recommended choice. Plain text for open-ended challenges.
- **Be adversarial, not hostile.** Challenge the plan, not the person. Tone: skeptical colleague, not interrogator.
- **Follow threads to resolution.** Don't raise a concern and drop it. Each thread ends with: a specific answer, an acknowledged risk, or an action item.
- **Your opinion matters.** When you think the user's answer is wrong, say so with your reasoning. But accept their final call.
- **No softening.** Don't preface challenges with "that's a great idea, but..." — go straight to the concern.
