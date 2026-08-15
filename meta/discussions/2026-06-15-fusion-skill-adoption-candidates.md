# Fusion Pattern — Skill Adoption Candidates

**Date:** 2026-06-15
**Status:** Naming actioned — the three fan-out skills renamed & shipped (see Final state). Adoption candidates below still open.
**Origin:** Exploration of OpenRouter's "Fusion" feature and how it maps onto this repo's skills.

---

## Final state (2026-06-15) — renamed and shipped

The three fan-out skills were renamed to job-named, self-disambiguating names, and the judge was extracted into a standalone agent. The 2×2 is the settled model.

| Question you'd ask | Skill | was | Knob A · Knob B |
|---|---|---|---|
| "What's the **best** answer?" (no answer yet) | `best-answer` | fusion | diverse · converge |
| "Is this answer **right**?" (have a leaning) | `validate-answer` | panel-review | identical · converge |
| "What did I **miss**?" (open mandate) | `find-gaps` | multi-agent-analysis | diverse · diverge |
| "Grade this one **proposal**" | `second-opinion` | (unchanged) | outside the 2×2 |

- **Two knobs:** Knob A = workers identical vs diverse; Knob B = output one answer vs a findings list. Three live cells (identical + list is empty).
- **`agents/judge.md`** — clean-room mapper (contradictions / blind_spots / unique_insights); maps, never decides. Consumed by `best-answer`; the orchestrator verifies + synthesizes.
- `best-answer` was finalized from the `fusion` draft and wired into README + plugin.json. `validate-answer` keeps identical reviewers on purpose and did NOT adopt the judge — its diversity is already in the questions, not the reviewers, so the agreement signal stays interpretable.

---

## What "Fusion" is (one paragraph)

Fusion is a mixture-of-agents orchestration pattern — not a new model. A request flows:

```
request (parent/orchestrator)
   → FAN-OUT to N parallel panelists, each with a DISTINCT lens + tools (web/bash)
   → JUDGE subagent (clean room: sees only panel outputs) emits a structured
     disagreement map as JSON:
       consensus / contradictions / partial_coverage / unique_insights / blind_spots
   → SYNTHESIZE in the parent thread, grounded in that map (resolve, don't average)
```

Core principle: **diversity of error** is the engine, and **analyze ≠ decide** — the judge maps disagreement, the orchestrator resolves it. With an Opus-only harness this is "self-fusion," where diversity must be *manufactured* via distinct lenses.

This shipped as the `best-answer` skill (formerly `fusion`) at `skills/best-answer/SKILL.md`, with a clean-room `agents/judge.md`.

---

## Headline finding

**This repo has already converged on Fusion as its house pattern.** 8 of 25 skills already implement fan-out → judge/verify → synthesize:

> refine-file, tighten-file, two-pass-review, execute-plan, durable-docs-update, audit-transcripts-for-learnings, plus the two primitives (find-gaps, validate-answer).

So the remaining whitespace is **not** "add fan-out everywhere." It's two specific shapes:
1. **Single-agent judgment/diagnosis skills** that commit to one frame early.
2. **Authoring skills that fan out for recon but not for the creative decision itself.**

---

## Adoption candidates (ranked, with confidence)

| Rank | Skill | Why it fits — what the panel/judge catches that a single pass misses | Caveat | Conf |
|------|-------|----------------------------------------------------------------------|--------|------|
| 1 | **sentry-analysis** | Textbook diversity-of-error: from one stack trace, independent investigators land on different culprits (race vs null-guard vs upstream config vs regression). Judge ranks competing hypotheses instead of anchoring on the first plausible one. High-stakes, currently single-agent. | — | 0.82 |
| 2 | **tech-design** | A locked spec admits many valid architectures; diverse *whole designs* expose different failure modes (one's coupling is another's clean seam; one catches a migration trap another misses). | Already fans out for *recon* — wrap the **approach-selection** step specifically, don't bolt on a second recon fan-out. | 0.78 |
| 3 | **product-interview** | Spec/AC gaps are silent until build, then expensive (execute-plan honors the spec). Diverse readers flag different missing requirements, ambiguous ACs, unhandled UX states. `partial_coverage` / `blind_spots` map directly onto "which ACs are underspecified." | Wrap the **spec-lock gate**, not the live interactive dialogue. | 0.74 |
| 4 | **grill-me** | Already adversarial — but one questioner has one set of blind spots. Diverse attack lenses (security, scale, ops, incentives, recovery) hit angles a single grill won't; the contradiction map shows where lenses disagree on severity. | Adjacent to find-gaps — fits if grill-me stays interactive but *seeds* questions from a parallel attack-lens pass. | 0.68 |
| 5 | **write-plan** | Independent sequencings disagree usefully on what's parallel-safe; judge reconciles missed cross-wave deps into a safer ordering. | Already has a single reviewer gate, so marginal gain over that is moderate, not large. | 0.62 |

---

## Clear non-fits (do NOT add Fusion)

One right answer / mechanical / deliberately cheap or fast:

- **handoff** — mechanical context distillation; single source of truth.
- **place-fact** — deterministic decision-tree routing; one right home.
- **vet-fact** — quick single-criterion keep/cut filter; meant to run cheaply per fact.
- **tighten-instruction** — mechanical single-line collapse; it's the primitive others panel over.
- **explain-deeply** — quality is prose depth over correct grounding, not error-diversity.
- **agent-soul** — personality state-load; no correctness ceiling.
- **post-purchase-ui-extension** / **shopify-dev-mcp** — SDK/MCP reference + schema validation; deterministic, validated by tooling.
- **fix-verify-loop** — already fix→verify; deliberately bounded and cheap per finding.

**Already implement Fusion (skip — redundant/recursive):** find-gaps, validate-answer, refine-file, tighten-file, two-pass-review, execute-plan, durable-docs-update, audit-transcripts-for-learnings.

---

## Suggested order of work

Start with **sentry-analysis** (0.82, clean single-agent → highest, lowest-caveat gain), then **tech-design** and **product-interview** (both need the wrap scoped to a *specific step*, so spec the seam before building).

---

## Telling them apart (plain-language reference)

`best-answer`, `validate-answer`, `find-gaps`, and `second-opinion` look similar (all fan out to subagents) but split by **what you already have** and **what you want back**.

Same topic (adding a caching layer), four intents:

| What you say | What you want | Skill |
|---|---|---|
| "What caching strategy should we use?" | a best answer (you have none) | **best-answer** |
| "I've chosen Redis + write-through + 5-min TTL — is that right?" | your decision trust-checked | **validate-answer** |
| "Is this specific cache-invalidation function correct?" | one artifact graded | **second-opinion** |
| "Here's my whole caching design doc — what's wrong with it?" | problems surfaced, open-ended | **find-gaps** |

The rule, in two questions:

```
1. Do you already have a candidate answer?
      NO  → best-answer        (build the answer)
      YES → go to question 2

2. What do you want back?
      a confidence check on your plan   → validate-answer
      a grade on one specific thing     → second-opinion
      a list of problems you missed     → find-gaps
```

In plain words:
- **No answer yet?** → best-answer *builds* one.
- **Have a plan, nervous about it?** → validate-answer *checks* it.
- **Have one fix, want it judged?** → second-opinion *grades* it.
- **Have a draft, want it stress-tested?** → find-gaps *surfaces* what you missed.
