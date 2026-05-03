# Sanity Check Schema

The output schema for the `sanity-checker` and `codex-sanity-checker` agents. Returns a structured validation of a plan, design, or decision.

## Schema

```
SanityCheckOutput {
  verdict: "sound" | "concerns" | "rethink",
  confirmation: what's good about this approach,
  concerns: Concern[],
  blind_spots: string[],
  reframe: string | null
}
```

## Concern

```
Concern {
  id: sequential number starting from 1,
  severity: "P0" | "P1" | "P2",
  issue: description of the concern,
  why_it_matters: impact if not addressed,
  confidence: 0.0-1.0
}
```

## Field notes

- `verdict` — "sound" means proceed. "concerns" means fixable issues exist. "rethink" means the approach has fundamental problems (must populate `reframe`).
- `confirmation` — always say what's good, even when the verdict is "rethink." This prevents the user from throwing out the baby with the bathwater.
- `concerns` use P0-P2 only (no P3). Plan-level issues are either blocking or not — "nice to have" doesn't apply to plan validation.
- `blind_spots` — things the plan doesn't address. Not necessarily problems — the user may have intentionally excluded them. List them so the user can confirm.
- `reframe` — required (non-null) when verdict is "rethink"; null when verdict is "sound" or "concerns". The "you're solving the wrong problem" field — populate with a concrete alternative direction, not just "reconsider".
- `confidence` — how confident you are that this concern is real. 1.0 = certain failure mode, below 0.5 = speculative risk.
