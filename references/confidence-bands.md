# Confidence Bands v1

Shared gating bands for the fan-out skills (`tighten-file`, `validate-answer`, `refine-file`, `find-gaps`, `durable-docs-update`, `multi-agent-analysis`). Two breakpoints — **0.80** (keep threshold) and **0.70** (drop floor) — sort scored findings into three buckets:

- **keep** — act on it: walk one at a time, or present in a table — the consuming skill decides.
- **triage** — contested; route through the `triage` skill before acting: `consider` → keep · `skip` → drop (or park).
- **drop** — below the floor; list it, don't act.

The bands are a cost lever: only the contested middle pays for a checker. After triage, sort the keep set by confidence descending — `adjusted_confidence` where triage ran, else the finding's own score.

Two gating **modes** assign the bucket; the buckets and breakpoints are identical, only the count rule differs. Each consumer inlines the one block for its mode (`references/` isn't installed — follow the [Shared schema workflow](../WRITING-GUIDE.md#shared-schema-workflow)).

## Mode V — voting (three identical reviewers)

Each finding carries three reviewer scores.

- **keep** (walk, no triage) — all three ≥ 0.80. Unanimous agreement across identical reviewers; re-checking spends a checker for nothing.
- **triage** — ≥1 reviewer ≥ 0.80 **OR** ≥2 reviewers ≥ 0.70. Real support, not consensus.
- **drop** — ≤1 reviewer ≥ 0.70 and none ≥ 0.80. Too thin to walk or check.

Consumers: `tighten-file`, `validate-answer`, `refine-file`.

## Mode F — flat (one score)

Each finding carries one confidence `c` (max across lenses if deduped).

- **keep** (no triage) — `c ≥ 0.80`.
- **triage** — `0.70 ≤ c < 0.80`.
- **drop** — `c < 0.70`.

Consumers: `find-gaps`, `durable-docs-update`, `multi-agent-analysis`.

## Consumer notes

- **MOVE findings** (relocate a fact to another home) skip triage — `consider`/`skip` can't carry a corrected target — and a doubted MOVE is rechecked via `second-opinion` instead (`refine-file`; `durable-docs-update` has no recheck step — MOVEs present directly).
- **Seeded candidates** (caller-asserted facts) bypass the bands and present at any score (`durable-docs-update`).
