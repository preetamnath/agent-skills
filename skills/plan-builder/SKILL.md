---
name: plan-builder
description: "Creates dependency-ordered executable plans from a goal + context. Produces markdown checkbox plans compatible with plan-runner. Use when you need to break a goal into sequenced, atomic work items before execution."
---

# Plan Builder

Creates dependency-ordered, executable plans from a goal description. Produces markdown plans with `[ ]` checkboxes that plan-runner can execute.

## When to use

When you have a goal (feature, migration, refactor, cleanup) and need to break it into sequenced work items before starting. Not for requirements gathering — use the `interview-me` skill first if the goal is vague.

## Protocol

### Input

- **Goal**: what needs to be achieved (feature description, refactor objective, migration target)
- **Constraints**: any fixed boundaries (timeline, compatibility, dependencies)
- **Criteria**: acceptance criteria or success conditions (from a PRD, interview output, or user statement)

If the goal is ambiguous or missing constraints, stop and use the `interview-me` skill to clarify before building the plan.

### Step 1 — Read context

Before planning, read:
- Architecture docs (ARCHITECTURE.md, relevant CLAUDE.md files)
- Existing code in affected areas (patterns, interfaces, conventions)
- Any referenced PRD or interview output

Identify: what exists today, what needs to change, what's fixed vs flexible.

### Step 2 — Select approach

After reading context, determine whether there are multiple viable implementation paths (different patterns, data flows, architectures, migration strategies).

**Single obvious path** — one natural way to implement given existing code and constraints. Skip to Step 3. Most tasks land here — don't force exploration when there's nothing to explore.

**Multiple viable paths** — genuinely different approaches with real tradeoffs (e.g., new model vs. JSON field, rebuild component vs. extend existing, webhook vs. polling). Enumerate 2-3 options as:
- **Option name** — 1-line description. Tradeoff: [strength] vs [weakness].

Present the options to the user via AskUserQuestion. Include a recommended choice with a one-sentence reason, but flag if your confidence is low or the tradeoffs depend on priorities you don't know.

**Do not proceed to Step 3 until the user selects an approach.** If the user proposes a different approach not in your list, validate it against the constraints from Step 1. If feasible, adopt it. If not, explain why and re-ask.

### Step 3 — Identify work items

Break the goal into atomic items **for the chosen approach**. Each item should be:
- **One commit's worth of work** — completable in a single focused session
- **Self-contained** — includes file paths, what to change, and why
- **Verifiable** — you can tell when it's done

### Step 4 — Order by dependency

For each item, determine:
- What must exist before this item can start?
- What files does it touch?
- Can it run in parallel with other items?

Order items so dependencies are satisfied. Mark coupling explicitly.

### Step 5 — Write the plan

Output a markdown file with this structure:

```markdown
# Plan: [goal summary]

**Goal**: [1-2 sentence description]
**Criteria**: [acceptance criteria or success conditions — preserved from input for downstream review/fix]
**Created**: [date]

## Constraints
- [fixed boundaries, assumptions, out-of-scope items]

## Approach
[1-2 sentences: what approach was chosen and the deciding reason. Omit this section entirely if there was only one obvious path.]

## Items

- [ ] **P1: [short title]** — [what to change, which files, why]
- [ ] **P2: [short title]** — [what to change, which files, why]
  - Depends on: P1
- [ ] **P3: [short title]** — [what to change, which files, why]
  - Must land together with: P4
- [ ] **P4: [short title]** — [what to change, which files, why]
  - Must land together with: P3

## Out of scope
- [things explicitly not included and why]
```

### Item ID format

Use stable IDs (`P1`, `P2`, ...) not ordinal positions. These survive edits, discovery notes, and reordering. Reference dependencies by ID.

## Rules

- Each item must name the file(s) it touches. Plan-runner needs this for coupling detection.
- Preserve criteria/constraints metadata at the top — downstream review and fix-loop need them.
- Don't include review, test, or verification steps in the plan. Those are handled by other skills (two-pass-review, fix-loop). Plan items are implementation work only.
- If a goal needs more than ~15 items, decompose into a parent roadmap + child plans. Each child plan should be independently executable.
- Mark dependencies explicitly using item IDs. Don't rely on ordering alone.
- Include an "Out of scope" section. Preventing scope creep is half the value of a plan.
