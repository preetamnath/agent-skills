# browser-use org tools vs. agent-browser — should we adopt one?

Started 2026-07-09, during live SPEC-005 testing in OakPostPurchase. **Not a decision — a captured finding.** No adoption yet; current call is to keep `agent-browser` and hand-write the glossary (see Decision below).

## Problem that triggered this

Live-testing OakPostPurchase's admin app with `agent-browser`, the same UI elements (Create-funnel wizard, Style Editor panels, checkout flow) had to be re-discovered from scratch — snapshot, grep, find ref — every time, across a single session and would again next session. Wanted: a way to persist "what a screen looks like and how to drive it" so future sessions look it up instead of rediscovering it.

## What we looked at

Three separate products under `github.com/browser-use/*` — same company, **not a pipeline, not stacked dependencies**:

```
browser-use ─┐
             ├─ workflow-use DEPENDS on browser-use (uses it as fallback
workflow-use ┘  when a replayed step's selector breaks). This pair is coupled.

browser-harness ── standalone. Verified via pyproject.toml: deps are
                    cdp-use, fetch-use, pillow, websockets — NOT
                    browser-use or workflow-use.
```

| Tool | What it is | Relevant here? |
|---|---|---|
| `browser-use` | A full autonomous agent — runs its own LLM loop, decides every click for a natural-language task. Competes with Claude driving the browser, doesn't compose with it. | No |
| `workflow-use` | Record-once → replay-deterministically, falls back to `browser-use`'s agent when a step's selector no longer matches. This *is* the "record a workflow" idea, but scoped to step-sequences, which break the moment a step count/order changes. | No — wrong shape for "element glossary," and pulls in `browser-use` as a dependency |
| `browser-harness` | Thin, unopinionated CDP wire (~1k lines). No fixed verb surface (no `click`/`fill`) — the driving agent (their `browser-use`, or *us*, since its setup prompt literally says "paste into Claude Code") writes ad hoc code against the raw socket, then **saves what worked** as reusable files: `agent_helpers.py` + per-site `domain-skills/`. | **Yes — validates the glossary idea** |

All three run locally by default (attach to your own Chrome the same `chrome://inspect` toggle-and-approve flow `agent-browser` already uses); the org's cloud product is an optional upsell for stealth/proxies/scale, not a requirement.

## The validating insight

`browser-harness`'s own README: *"Skills are written by the harness, not by you... teach the agent the selectors, flows, and edge cases it would otherwise have to rediscover."* That is, near word-for-word, the glossary idea — except they built tooling so the **agent self-authors it automatically** (a skill file gets written the moment the agent figures out something non-obvious), instead of a human/agent hand-maintaining a prose doc.

`agent-browser` has no equivalent — no record/replay, no self-authored memory. Confirmed via `agent-browser skills get core --full` and `--help`; the closest built-ins are video recording (pixels, not actions) and `state save/load` (auth cookies only, not UI knowledge).

## Decision (for now)

Don't adopt any of the three. Keep `agent-browser`, and hand-write the equivalent of a "domain skill" for OakPostPurchase: extend `meta/workflows/automated-testing/automated-testing-instructions.md`'s existing "Interaction quirks — by scope" section (already a per-screen element/gotcha glossary — this need isn't new, we already had the right shape) rather than introducing a second file or format. Reasoning: switching automation tools mid-project has real migration cost, and the actual gap was "the doc doesn't cover today's new screens yet," not "the doc's format is wrong."

## Open for future investigation

Is `browser-harness`'s self-authoring loop (agent writes the skill file itself, the moment it learns something) worth adopting as *the* pattern across repos, replacing the manual "remember to update the gotchas doc" step test-completed-plan currently relies on? Would need: a trial run on one repo, comparing agent-authored skill quality against our hand-curated one, and checking whether `browser-harness`'s no-fixed-verbs model (agent writes raw CDP code) is a net win or a net loss of reliability vs. `agent-browser`'s structured `snapshot`+`@eN`-ref model.
