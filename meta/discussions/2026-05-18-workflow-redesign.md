# Workflow Redesign — Problem Statement & Working Hypothesis

**Date:** 2026-05-18
**Status:** Discussion / pre-decision
**Owner:** Preetam

## Purpose

Redesign the skill/agent pipeline that takes a solo developer from "I want to do some work" to "it's done well." This is a from-scratch rebuild, not a tweak of existing skills. The existing pipeline is the starting point; we are free to delete, merge, split, or rename anything.

## Current pipeline

```
chat discussion  →  interview-me (optional)  →  "plan draft" (informal)  →  plan-builder  →  plan-runner
                                                                                      \
                                                                                       two-pass-review / fix-verify-loop
```

Supporting skills: `grill-me`, `panel-review`, `second-opinion`, `tighten-*`, `simplify`.

## Failure modes (all four confirmed present)

1. **Discovery happens too late.** Mid-wave, plan-runner hits blockers and "there was a better approach" realizations that should've surfaced before execution.
2. **Decisions don't stick.** Choices get re-litigated mid-build; rationale is lost across sessions. "Discussed" ≠ "locked." Only the artifact remains, not the *why*.
3. **No clean ready-to-build moment.** Unclear when discussion ends and planning begins. Either jumping to plan-builder too early, or over-discussing without convergence. Scope creeps mid-build.
4. **Post-build review is shallow.** Build ships, but no capture of what the plan got wrong, what surprised, or what to do differently next time. No learning loop.

## What "done well" means for this user

- **Solo throughput is the bottleneck.** Not stakeholder alignment. Avoid PRD bloat.
- **Decisions must be machine-checkable as locked vs open**, not just "we talked about it."
- **Cross-session memory must survive context compaction.** The *why* of choices must be retrievable in a new session.
- **Recovery loops matter.** When execution discovers a planning error, the route back must be cheap.
- **Skill proliferation has a cost.** Each new skill is friction; consolidate where possible.

## Research-grounded patterns surveyed

(See `meta/discussions/` notes; sources verified.)

| Source | Strongest steal | What it proves |
|---|---|---|
| **GSD (gsd-build/get-shit-done)** | D-IDs (`D-01`…) in `CONTEXT.md`, planner refuses to advance unless every ID appears in a plan's `must_haves`/`truths` | Machine-enforced decision lock-in is feasible and grep-able. |
| **addyosmani/agent-skills** | Committed `SPEC.md` between intent and plan; SPEC gates PLAN, PLAN gates code; ADRs in `docs/decisions/` | The "plan draft" stage IS a separate committed artifact. Not implicit. |
| **mattpocock/skills** | `CONTEXT.md` (project glossary) + `docs/adr/*` (decisions); `to-prd` explicitly forbids interviewing — clean lock-in | Durable cross-session artifacts beat conversation memory. |
| **github/spec-kit** | `[NEEDS CLARIFICATION]` blocking marker in spec; Complexity Tracking table with "Simpler Alternative Rejected Because" column | A literal in-file token is the cleanest readiness gate. |
| **Boris Tane's workflow** | Annotation cycle on committed `plan.md` + sentinel phrase `"don't implement yet"` | Decisions are captured inline as you reject approaches, not just finalize them. |
| **obra/superpowers** | Two-gate human approval (section-by-section, then full spec commit) | Chunked human sign-off prevents rubber-stamping. |
| **gstack** | Multi-perspective verdicts (CEO / Design / Eng); `VERDICT: CLEARED` token | Different reviewer lenses surface different gaps. |
| **OpenSpec** | Diff-style spec deltas; Given/When/Then scenarios | Spec changes are themselves first-class artifacts. |

## Working hypothesis (to be challenged by panel)

A five-stage pipeline with **three durable artifacts per feature** and **one append-only project-level artifact**.

### Stages

```
1. FRAME & INTERVIEW   (extends interview-me)
   ├─ Includes: framing, option-exploration, risk/feasibility surfacing
   ├─ Output: docs/intent/<feature>.md  (disposable, drives spec)
   └─ Gate: human says "draft the spec"

2. SPEC                (NEW skill — `draft-spec` or `spec-it`)
   ├─ Output: docs/specs/<feature>.md  (committed, durable)
   ├─ Sections: Outcome / Decisions (with D-IDs, status, rationale, rejected-alts) /
   │            Constraints / Non-goals / Open Questions ([NEEDS CLARIFICATION] markers)
   └─ Gate: refuses to advance if any [NEEDS CLARIFICATION] remains OR any Decision is open

3. PLAN                (existing plan-builder, enhanced)
   ├─ Output: docs/plans/<feature>.md  (committed; disposable post-ship)
   ├─ Wave-grouped, dep-ordered, vertical slices
   ├─ Every task traces to a Decision ID, Constraint, or AC
   └─ Refuses to run if SPEC has open decisions / clarifications

4. EXECUTE             (existing plan-runner)
   ├─ Per-wave review + fix-verify-loop (existing)
   ├─ Discoveries that affect ACs force re-entry to SPEC (not silent override)
   └─ Final two-pass review on full diff

5. CAPTURE             (NEW skill — `capture` or extension of plan-runner's final review)
   ├─ Promote locked decisions worth keeping → docs/decisions/ADR-NNN.md
   ├─ Surface learnings: what changed during execution, what to do differently
   └─ Optional: promote project-level invariants to CLAUDE.md
```

### Artifacts

| Path | Lifecycle | Purpose |
|---|---|---|
| `docs/intent/<feature>.md` | Disposable | Captures interview output; drives the spec |
| `docs/specs/<feature>.md` | Committed, kept | Decisions + constraints + ACs for the feature |
| `docs/plans/<feature>.md` | Committed, disposable post-ship | Wave-grouped tasks; reviewable history |
| `docs/decisions/ADR-NNN.md` | Append-only, cross-feature | Durable project memory; numbered, never deleted |
| `CONTEXT.md` (root) | Append-only, project-level | Glossary + cross-feature invariants (à la Pocock) |

### Lock-in mechanism (proposed)

- Each Decision in the spec has a structured block:
  ```
  ### D-01: <decision title>
  - **Status:** locked | tentative | open
  - **Chosen:** <choice>
  - **Rejected:** <alternatives + reason>
  - **Rationale:** <why>
  ```
- Plan-builder greps for `Status: open` in the spec; refuses to run if any.
- Plan-builder greps for `[NEEDS CLARIFICATION]`; refuses if any.
- Locked decisions are immutable mid-execution; changes route back to SPEC + re-trigger plan.

### Recovery loop

- If plan-runner discovers a locked decision is wrong: it halts the affected wave, writes a `Discovery` entry referencing the D-ID, and prompts the user. The user either confirms the change (which updates the spec and re-runs plan-builder for affected waves) or rejects (which forces an alternative path in execution).

## Key open questions for the panel

1. **Is SPEC → PLAN as two committed files the right answer to the "plan draft is underspecified" problem?** Or is one unified document with internal sections (à la lightweight conversation arch) better for a solo dev?

2. **Should decision lock-in be machine-enforced** (GSD-style D-IDs with grep gates) **or human-soft-gate** (Tane-style sentinel + commit)? Which fails better when the user is moving fast?

3. **Where should durable cross-feature memory live** — per-decision ADR files, a single `CONTEXT.md` glossary, distributed inline in specs, or some combination? Which gets read back vs. just-written-and-forgotten?

4. **Is a separate `capture` / retro skill needed**, or can promotion-to-ADR happen as a side-effect of plan-runner's final review? Does the user actually need a learning-loop step, or is that an aspiration that won't get used?

5. **What's the right number of skills/artifacts per feature for a solo dev?** Two? Three? Four? Above what threshold does the overhead exceed the value, given that the user's pain is throughput?

6. **What stays vs. goes from the current pipeline?** `interview-me` extends, but does `grill-me` survive? `panel-review`? `second-opinion`? Or are those absorbed into the spec-draft stage's review pass?

## Non-goals for this discussion

- Naming skills / files / commands (downstream).
- Exact frontmatter formats for skill files.
- Whether to support Cline/Roo/Gemini multi-runtime (this is Claude Code only).
- Team-collaboration features (this is solo).
