---
name: multi-agent-analysis
description: "Dispatch 1–3 subagents to analyze or verify something, then judge their findings yourself. TRIGGER when: user says 'multi-agent analysis', 'use subagents to analyze/verify', or 'dispatch subagents' to look into something."
---

# Multi-Agent Analysis

## Steps

### Step 1 — Frame the problem

- **Frame:** restate the problem in a line or two and name its type — verify a claim/fix · which answer is correct · architecturally correct + simplest · how something works.
- **Task list:** if the ask has independent parts, list them first (TaskCreate) so none is dropped.

### Step 2 — Size and dispatch (parallel)

- **Size:** 1 for a focused question, 2–3 when it splits into independent angles or surfaces. Cap at 3.
- **Dispatch:** one message, multiple `Agent` calls. Model per task — `opus` for architectural/design judgment, `sonnet` for mapping, code-tracing, or doc/web research.
- **Brief each:**
    - **What to pass:** the problem statement, its own angle, and file paths (not pasted contents).
    - **Ground every claim** in source it read.
    - **Return the [Findings schema](#output-schema)**, not a raw dump.
    - **Flag anything material** it notices outside the question.
    - **Don't fan out** — no subagents of its own; keep the tree one level deep.

### Step 3 — Ground and apply your verdict

Collapse duplicates first — the same finding from 2+ subagents is one, keep its highest confidence. Then judge every finding at `c ≥ 0.70` yourself: read the cited code or doc, and don't act on a summary you haven't verified. List anything below 0.70 without acting on it.

Then apply your own verdict on top: agree, correct, or overrule each with reasoning — never relay verbatim. Where findings conflict, resolve deliberately against source; don't average.

### Step 4 — Present for decision

Lead with the answer, then report in this shape:

```
**Analysis result:**
- Answer: [one-line plain-language answer]
- Findings: [claim — your verdict (agree / correct / overrule) — confidence 0.00–1.00, one per line]
- Observations: [material finding outside scope | none]
- Open questions: [unresolved item | none]
```

Add a tree / ASCII map or table where it aids understanding — current vs proposed, file map, or flow. Stop there — analyze and recommend only; the user or a build skill decides what to apply.

---

## Output Schema

```
Findings {
  problem: string,                 // the framed problem statement
  findings: [ {
    claim: string,                 // discovery or recommended action, one line
    reasoning: string,             // why — or pro/con — as appropriate
    evidence: string,              // file:line, or doc/URL it's grounded in
    confidence: number             // 0.00–1.00
  } ],
  observations: string[],          // material findings outside the framed question
  open_questions: string[]         // what could not be resolved from source
}
```
