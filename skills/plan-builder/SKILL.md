---
name: plan-builder
description: "Creates dependency-ordered, wave-grouped executable plans from a goal + context. Produces markdown plans with parallel execution waves compatible with plan-runner. Use when you need to break a goal into sequenced, atomic work items before execution."
---

# Plan Builder

Creates dependency-ordered, wave-grouped executable plans from a goal description. Produces markdown plans with `[ ]` checkboxes organized into parallel execution waves that plan-runner can execute.

## When to use

When you have a goal (feature, migration, refactor, cleanup) and need to break it into sequenced work items before starting. Not for requirements gathering — use the `interview-me` skill first if the goal is vague.

## Protocol

### Input

- **Goal**: what needs to be achieved (feature description, refactor objective, migration target)
- **Constraints**: any fixed boundaries (timeline, compatibility, dependencies)
- **Criteria**: acceptance criteria or success conditions (from an interview output, spec, or user statement)

If the goal is ambiguous or missing constraints, stop and use the `interview-me` skill to clarify before building the plan.

### Step 1 — Read context

Before planning, read:
- Architecture docs (ARCHITECTURE.md, relevant CLAUDE.md files)
- Existing code in affected areas (patterns, interfaces, conventions)
- Any referenced interview output or spec

Identify: what exists today, what needs to change, what's fixed vs flexible.

### Step 2 — Select approach

After reading context, determine whether there are multiple viable implementation paths.

**Single obvious path** — one natural way to implement given existing code and constraints. Note it briefly and skip to Step 3. Most tasks land here — don't force exploration when there's nothing to explore.

**Multiple viable paths** — genuinely different approaches with real tradeoffs. Analyze the problem yourself (this is not a subagent call — you do the analysis directly) and produce an `AlternativesOutput` conforming to the schema in `references/alternatives-schema.md` (`AlternativesOutput` with `Alternative[]`). Be concrete: name files, functions, patterns. Include honest confidence scores and real tradeoffs.

Present the structured output to the user via `AskUserQuestion`. Include a recommended choice with reasoning, but flag if confidence is low or tradeoffs depend on priorities you don't know.

**Do not proceed to Step 3 until the user selects an approach.** If the user proposes a different approach not in your list, validate it against the constraints from Step 1. If feasible, adopt it. If not, explain why and re-ask.

### Step 3 — Structure outline

After approach selection, produce a concrete technical design that separates **architectural decisions** (types, schemas, signatures) from **execution sequencing** (waves). Scale depth to scope — a single-endpoint change needs less detail than a full-stack feature.

Output (include only sections relevant to the goal):
- **DB schema changes** — model names, field names, types, constraints, relationships (if applicable)
- **API endpoint signatures** — method, path, request shape, response shape, auth (if applicable)
- **Component tree** — component names, props, state shape, parent-child relationships (if applicable)
- **Type definitions** — new types, enums, or interfaces introduced (if applicable)

Must NOT include: implementation logic, wave sequencing, test strategy.

Present to user via `AskUserQuestion` with options: "Approve structure", "Adjust". Recommended: "Approve structure". Do not proceed until approved. This becomes the reference for subagents during execution.

### Step 4 — Identify work items

Break the goal into atomic items **for the chosen approach**. Each item should be:
- **One commit's worth of work** — completable in a single focused session
- **Self-contained** — includes file paths, what to change, and why
- **Verifiable** — you can tell when it's done

### Step 5 — Order by dependency + wave grouping

For each item, determine:
- What must exist before this item can start?
- What files does it touch?
- Can it run in parallel with other items?

Order items so dependencies are satisfied. Then group into waves:

**Wave assignment rules:**
1. No dependencies + no file overlap → same wave (parallel execution)
2. Depends on another item → later wave
3. Same file modified by multiple items → different waves (serialize)
4. Maximum **3** items per wave (matches plan-runner's subagent concurrency limit)
5. Prefer fewer, fatter waves over many single-item waves

**Checkpoint:** Present the wave-grouped item list to the user via the `AskUserQuestion` tool with options: "Approve and write plan", "Adjust items". Recommended: "Approve and write plan". Include item titles, file paths, wave assignments, and dependency links so the user can verify before the file is written.

### Step 6 — Write the plan

Write a markdown file to `meta/workflows/plans/plan-NNN-<topic-slug>.md`. Create the directory if missing. Find the highest existing number in the directory and increment by 1 (start at 001 if empty). Tell the user the file path.

```markdown
# Plan: [goal summary]

**Goal**: [1-2 sentence description]
**Criteria**: [acceptance criteria or success conditions — preserved from input for downstream review/fix]
**Created**: [date]

## Constraints
- [fixed boundaries, assumptions, out-of-scope items]

## Approach
[1-2 sentences: what approach was chosen and why. Omit this section entirely if there was only one obvious path.]

## Structure Outline
[Types, schemas, signatures produced in Step 3. Subagents reference this during execution.]

## Wave 1: [short description]

- [ ] **T1: [short title]** — [what to change, which files, why]
- [ ] **T2: [short title]** — [what to change, which files, why]

## Wave 2: [short description]

- [ ] **T3: [short title]** — [what to change, which files, why]
  - Depends on: T1
- [ ] **T4: [short title]** — [what to change, which files, why]
  - Must land together with: T5
- [ ] **T5: [short title]** — [what to change, which files, why]
  - Must land together with: T4

## Out of scope
- [things explicitly not included and why]
```

### Item ID format

Use stable IDs (`T1`, `T2`, ...) not ordinal positions. These survive edits, discoveries, and reordering. Reference dependencies by ID.

## Rules

- Each item must name the file(s) it touches. Plan-runner needs this for wave execution and coupling detection.
- Preserve criteria/constraints metadata at the top — downstream review and fix-verify-loop need them.
- Don't include review, test, or verification steps in the plan. Those are handled by other skills (two-pass-review, fix-verify-loop). Plan items are implementation work only.
- If a goal needs more than ~15 items, decompose into a parent roadmap + child plans. Each child plan should be independently executable.
- Mark dependencies explicitly using item IDs. Don't rely on ordering alone.
- Include an "Out of scope" section. Preventing scope creep is half the value of a plan.
- Wave assignments follow the five rules above — no exceptions. If an item can't be parallelized, it goes in its own wave.
