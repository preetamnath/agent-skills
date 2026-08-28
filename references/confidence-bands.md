# Confidence Bands v1

Shared gating bands for `find-gaps`. Two breakpoints — **0.80** (keep threshold) and **0.70** (drop floor) — sort scored findings into three buckets:

- **keep** — act on it: walk one at a time, or present in a table — the consuming skill decides.
- **triage** — contested; route through the `triage` skill before acting: `consider` → keep · `skip` → drop (or park).
- **drop** — below the floor; list it, don't act.

The bands are a cost lever: only the contested middle pays for a checker. After triage, sort the keep set by confidence descending — `adjusted_confidence` where triage ran, else the finding's own score.

The consumer inlines this block because `references/` isn't installed; follow the [Shared schema workflow](../WRITING-GUIDE.md#shared-schema-workflow).

## Mode F — flat (one score)

Each finding carries one confidence `c` (max across lenses if deduped).

- **keep** (no triage) — `c ≥ 0.80`.
- **triage** — `0.70 ≤ c < 0.80`.
- **drop** — `c < 0.70`.

Consumers: `find-gaps`.

## Consumer notes

- **`durable-docs-update` opts out of the bands.** It gates flat — apply at `c ≥ 0.75`, drop below — and never calls `triage`. Its edits land in a table the user reads and are reversible in one commit, so the contested middle doesn't earn a checker.
- **`validate-answer` opts out of the bands.** It keeps the three-way vote but gates at **0.75** and never calls `triage`. A split among identical reviewers is the signal it exists to surface, and `triage`'s clean-room rule hides that split from the checker — so a `skip` would discard the finding on grounds unrelated to why it was banded.
- **`compress-file` opts out of the bands.** It self-scores each CUT/FOLD and gates flat — apply at `c ≥ 0.75`, hold below — with no `triage` and no reviewer panel. Its edits land in a reviewable diff and Step 4 re-reads them cold, so the contested middle doesn't earn a checker.
- **`tighten-file` and `refine-file` opt out of the bands.** They self-score independent edits and gate flat — apply at `c ≥ 0.75`, hold below — with no `triage` or reviewer panel. Their edits land in a reviewable diff and a cold-read step proves meaning and placement before completion.
- **`tighten-instruction` and `structure-prose` opt out of the bands.** Each self-scores its independent edit and gates flat — apply at `c ≥ 0.75`, hold below — because the caller may use either lens directly.
- **`multi-agent-analysis` opts out of the bands.** It gates flat — verify at `c ≥ 0.70`, list below — and never calls `triage`. It re-reads every kept finding against source and overrules it in its own voice, so the parent is already the checker the contested middle would buy.
