# Confidence Bands v1

Shared gating bands for the fan-out skills (`tighten-file`, `refine-file`, `find-gaps`). Two breakpoints — **0.80** (keep threshold) and **0.70** (drop floor) — sort scored findings into three buckets:

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

Consumers: `tighten-file`, `refine-file`.

## Mode F — flat (one score)

Each finding carries one confidence `c` (max across lenses if deduped).

- **keep** (no triage) — `c ≥ 0.80`.
- **triage** — `0.70 ≤ c < 0.80`.
- **drop** — `c < 0.70`.

Consumers: `find-gaps`.

## Consumer notes

- **MOVE findings** (relocate a fact to another home) skip triage — `consider`/`skip` can't carry a corrected target — and a doubted MOVE is rechecked via `second-opinion` instead (`refine-file`).
- **`durable-docs-update` opts out of the bands.** It gates flat — apply at `c ≥ 0.75`, drop below — and never calls `triage`. Its edits land in a table the user reads and are reversible in one commit, so the contested middle doesn't earn a checker.
- **`validate-answer` opts out of the bands.** It keeps the three-way vote but gates at **0.75** and never calls `triage`. A split among identical reviewers is the signal it exists to surface, and `triage`'s clean-room rule hides that split from the checker — so a `skip` would discard the finding on grounds unrelated to why it was banded.
- **`compress-file` opts out of the bands.** It self-scores each CUT/FOLD and gates flat — apply at `c ≥ 0.75`, hold below — with no `triage` and no reviewer panel. Its edits land in a reviewable diff and Step 4 re-reads them cold, so the contested middle doesn't earn a checker.
- **`multi-agent-analysis` opts out of the bands.** It gates flat — verify at `c ≥ 0.70`, list below — and never calls `triage`. It re-reads every kept finding against source and overrules it in its own voice, so the parent is already the checker the contested middle would buy.
