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

### Step 0 — Direct-entry guard

Before doing any planning work, check that the premise is solid. For each of the four preflight questions below, evaluate three sources in order before deciding to ask:

| Source | What counts | Evidence required |
|---|---|---|
| **A. Referenced artifact** | User passed an explicit path to a `meta/workflows/interviews/...` file | The artifact answers the question concretely |
| **B. In-conversation context** | Prior messages in this thread already discussed it | Cite the specific exchange — no "I think we covered this" |
| **C. Ask the user** | Neither A nor B applies | Run the question via `AskUserQuestion` |

If any questions are satisfied via Source A or B, present a single confirmation gate before continuing: *"I'm treating Q1, Q2, Q4 as already answered based on [artifact / our conversation about X]. Does this match, or should I re-ask any of them?"* If the user wants to re-answer one, that question fires now.

#### The 4 preflight questions

1. **Scope** — "Can you name 2–3 things explicitly OUT of scope?" Weak → route to `interview-me`.
2. **Criteria measurability** — "For each criterion, how will you know it's met?" Weak → route to `interview-me`.
3. **Load-bearing assumption** — "Name the assumption that, if wrong, breaks the whole plan." Weak → route to `grill-me`.
4. **Fixed vs. assumed constraints** — "Which constraints are external requirements vs. your preference?" Weak → route to `interview-me`.

A "weak" answer means the user genuinely doesn't know — not one where the user clarifies on a follow-up.

#### Routing rule

- **0 weak** → proceed to Step 1.
- **1 weak** → route to that question's specialist (`interview-me` or `grill-me`).
- **2+ weak** → recommend `interview-me`. **If Q3 (load-bearing assumption) is among the weak answers**, also tell the user: *"After interview-me writes the artifact, follow with `grill-me` to pressure-test the assumption before re-invoking plan-builder."* — interview-me alone doesn't pressure-test assumptions, so Q3's specialist signal must be preserved separately.

When routing out, tell the user explicitly: *"After [interview-me/grill-me] writes the artifact, re-invoke plan-builder with the artifact path."*

### Step 1 — Read context

Before planning, read:
- Architecture docs (ARCHITECTURE.md, relevant CLAUDE.md files)
- Existing code in affected areas (patterns, interfaces, conventions)
- Any referenced interview output or spec

Identify: what exists today, what needs to change, what's fixed vs flexible.

### Step 2 — Select approach

After reading context, determine whether there are multiple viable implementation paths.

**Single obvious path** — one natural way to implement given existing code and constraints. Note it briefly and skip to Step 3. Most tasks land here — don't force exploration when there's nothing to explore.

**Multiple viable paths** — genuinely different approaches with real tradeoffs. Spawn the `propose-alternatives` agent (located at `agents/propose-alternatives.md`) to produce an `AlternativesOutput` conforming to the schema in `references/alternatives-schema.md`. The parent owns the judgment call of *whether* multi-path applies; the agent owns the analysis.

**Inputs to propose-alternatives:**
- **Problem**: the goal description plus the specific decision point that has multiple paths
- **Current approach**: existing implementation if there's one to compare against, else "no current approach — greenfield"
- **Context**: relevant files identified in Step 1, plus constraints from input

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

### Step 4 — Feasibility check

After the structure outline names specific components, schemas, and signatures, verify they exist as expected. Always run.

Launch 1–4 Sonnet subagents in parallel, split by topic:

| Area | When relevant | What to verify |
|---|---|---|
| UI components | Outline references specific UI components or libraries | Component exists, props match outline, composition constraints |
| External APIs | Outline depends on external API data | API capabilities, available fields, rate limits, gotchas |
| Extension/plugin targets | Outline includes extension or plugin work | Target capabilities and constraints |
| Existing codebase patterns | Always | Patterns referenced in outline match what's in the codebase |

Each subagent returns: exists (yes/no), capabilities, constraints, gotchas.

If any subagent flags issues, present to user via `AskUserQuestion` with options:
- "Amend structure outline to match findings" — loops back to Step 3 (recommended)
- "Route to interview-me to re-resolve" — fresh interview-me run with these findings as input
- "Document as known unknown and proceed" — note added to structure outline as a risk
- "Abort"

Do not proceed to Step 5 until feasibility issues are resolved or explicitly accepted.

### Step 5 — Identify work items

Break the goal into atomic items **for the chosen approach**. Each item should be:
- **One commit's worth of work** — completable in a single focused session
- **Self-contained** — includes file paths, what to change, and why
- **Verifiable** — you can tell when it's done

### Step 6 — Order by dependency + wave grouping

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

### Step 7 — Write the plan

Write a markdown file to `meta/workflows/plans/plan-NNN-<topic-slug>.md`. Create the directory if missing. Find the highest existing number in the directory and increment by 1 (start at 001 if empty). Tell the user the file path.

**Retry case:** When invoked from Step 8's retry loop on an existing plan, OVERWRITE the existing plan file at its current path. Do NOT increment NNN — preserve the original path so plan-runner consumes the correct artifact.

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

- [ ] **T1: [short title]**
  - [what to change, which files, why]
- [ ] **T2: [short title]**
  - [what to change, which files, why]

## Wave 2: [short description]

- [ ] **T3: [short title]**
  - [what to change, which files, why]
  - Depends on: T1
- [ ] **T4: [short title]**
  - [what to change, which files, why]
  - Must land together with: T5
- [ ] **T5: [short title]**
  - [what to change, which files, why]
  - Must land together with: T4

## Out of scope
- [things explicitly not included and why]
```

### Step 8 — Plan review

After Step 7 writes the plan file, spawn the `reviewer` agent (located at `agents/reviewer.md`) to audit it. Always runs.

**Inputs to reviewer:**
- **Artifact**: the plan file written in Step 7
- **Scope**: the plan file
- **Criteria**: combined semantic + mechanical criteria below

**Combined criteria:**

Semantic (does the plan deliver the goal?):
- **S1**: Each acceptance criterion in the plan header is addressed by at least one wave item.
- **S2**: The structure outline covers all schemas, signatures, and component names referenced in waves.

Mechanical (is the plan well-formed?):
- **M1**: Every wave item names the file(s) it touches.
- **M2**: Every dependency reference (e.g., `Depends on: T3`) points to an item that exists in an earlier wave.
- **M3**: No file is touched by multiple items in the same wave.
- **M4**: No wave has more than 3 items.
- **M5**: No item appears in multiple waves.

**Reviewer tagging instruction:** Instruct the reviewer to populate each finding's `criterion` field with the exact tag from above (e.g., `M3` or `S1`). Step 8's dispatch logic depends on the prefix (`M*` → mechanical, `S*` → semantic). Findings without a recognized tag are treated as semantic by default.

**Action table for findings:**

| Finding type | Action |
|---|---|
| No findings | Append `- Plan review: 0 findings — clean` to the plan file footer. Proceed silently. |
| **Mechanical defect** (`M*`) | Plan-builder auto-edits the plan file to fix. Re-run reviewer once. If still failing, escalate via `AskUserQuestion` with options: "Edit plan manually and re-review", "Accept defect with risk note in plan footer", "Abort". |
| **Semantic gap** (`S*`) | Present to user via `AskUserQuestion` with options: "Add wave items to address gap" (loops to Steps 5–6 for the gap → Step 7 to rewrite the plan with merged item IDs → Step 8 to re-review; cap at 1 retry per gap), "Amend criteria header", "Accept and document as known gap" (adds `## Known Gaps` section to the plan), "Abort". |

Cap mechanical auto-fix at 1 retry per finding.

### Item ID format

Use stable IDs (`T1`, `T2`, ...) not ordinal positions. These survive edits, discoveries, and reordering. Reference dependencies by ID.

## Rules

- Each item must name the file(s) it touches. Plan-runner needs this for wave execution and coupling detection.
- Task line format: checkbox + bold ID/title on one line; description, file paths, and metadata (`Depends on:`, `Must land together with:`) in indented sub-bullets below. Why: keeps the toggleable substring (`- [ ] **Tn: ...**`) short and stable so plan-runner can flip checkboxes without editing wrapped description text.
- Preserve criteria/constraints metadata at the top — downstream review and fix-verify-loop need them.
- Don't include review, test, or verification steps in the plan. Those are handled by other skills (two-pass-review, fix-verify-loop). Plan items are implementation work only.
- If a goal needs more than ~15 items, surface this to the user as a sign scope may be too broad — let them decide whether to narrow or proceed.
- Mark dependencies explicitly using item IDs. Don't rely on ordering alone.
- Include an "Out of scope" section. Preventing scope creep is half the value of a plan.
- Wave assignments follow the five rules above — no exceptions. If an item can't be parallelized, it goes in its own wave.
