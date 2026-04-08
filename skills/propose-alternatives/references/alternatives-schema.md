# Alternatives Schema

The output schema for propose-alternatives. Returns a structured assessment of the current approach and genuinely different alternatives.

## Schema

```
AlternativesOutput {
  current_approach_assessment: 1-2 sentence evaluation of what exists,
  alternatives: Alternative[],
  recommendation: which approach (including current) you'd pick and why
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

- `implementation` — be concrete. Name files, functions, patterns. "Use a queue" is too vague; "Add a BullMQ job in `workers/ingest.ts` that processes batches of 100" is concrete.
- `confidence` — how confident you are that this alternative would work well. 1.0 = proven pattern, below 0.5 = speculative.
- `trade_offs` — every alternative has both pros AND cons. If you can't name a con, you haven't thought hard enough.
- `when_to_use` — the scenario where this specific alternative is the best choice. Helps the user match alternatives to their actual constraints.
- Propose 2-3 genuinely different approaches, not minor variations. "Use library A vs library B" is a variation, not an alternative.
