# Alternatives Schema

The output schema for the `propose-alternatives` and `codex-propose-alternatives` agents. Returns a structured comparison of the current approach (if any) and genuinely different alternatives.

## Schema

```
AlternativesOutput {
  current_id: id of the existing approach in `alternatives`, or null for greenfield problems with no current approach,
  alternatives: Alternative[],
  recommendation: which alternative id you'd pick and why
}
```

## Alternative

```
Alternative {
  id: sequential number starting from 1,
  name: short name,
  summary: 1 sentence,
  implementation: concrete description with file paths and function names,
  trade_offs: {
    pros: string[],
    cons: string[]
  },
  when_to_use: scenario where this alternative is better than the others,
  confidence: 0.0-1.0
}
```

## Field notes

- `current_id` — points at the entry in `alternatives` representing the status quo. Set to `null` only for greenfield problems with no existing approach. When non-null, the current approach must appear in the `alternatives` array as a peer candidate.
- `alternatives` — when `current_id` is set, the array contains the current approach plus 2-3 new alternatives (3-4 entries total). When `current_id` is null, the array contains 2-3 new alternatives.
- `implementation` — be concrete. Name files, functions, patterns. "Use a queue" is too vague; "Add a BullMQ job in `workers/ingest.ts` that processes batches of 100" is concrete. For the current entry, describe what is in place today.
- `confidence` — for new alternatives: how confident you are this would work well (1.0 = proven pattern, below 0.5 = speculative). For the current entry: how confident you are the status quo should be *kept* (1.0 = clearly the right call to maintain, below 0.5 = current has serious problems even if functional). The score answers "should we use this," not "does this work."
- `when_to_use` — the scenario where this specific entry is the best choice. For the current entry, describe the conditions under which the status quo is the right answer (e.g., "when migration cost outweighs benefits at current scale").
- `trade_offs` — every entry has both pros AND cons, including the current one. If you can't name a con for the status quo, you haven't thought hard enough.
- `recommendation` — must cite the chosen alternative by id. If recommending the current approach, cite `current_id`.
- Propose 2-3 genuinely different new approaches. "Use library A vs library B" is a variation, not an alternative.
