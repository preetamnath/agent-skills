---
name: vet-fact
description: "Judge whether a candidate fact earns a durable-doc line: keep only what a future agent would get the wrong answer without; cut anything derivable from code, setup, breadcrumb, or a restated default. TRIGGER when: user asks 'does this belong in CLAUDE.md / a rule / the docs', 'is this worth keeping/writing down', 'should this be a comment'; vetting or pruning a fact before it's filed or shaped."
---

# Vet Fact

Primitive: **WORTH** — does this candidate fact deserve a durable-doc line at all?

## Steps

1. **State the fact in one line, then apply the gate:** would a future agent get the *wrong* answer without it? If the agent could recover it from the code, `ls`, or lint config, it fails — don't write it.
2. **Run the does-NOT-belong filter — cut on any hit:**
   - Setup / onboarding (belongs in README).
   - Historical breadcrumbs: dates, plan IDs, commit SHAs, supersedes/originally notes, completion summaries, deferred-item lists.
   - Restated framework or harness defaults.
   - Drift-prone literals: hex codes, version pins, exact syntax — unless the literal is itself load-bearing.
3. **Confirm it matches a belongs category:**
   - Gotcha, anti-pattern, or dead-code warning.
   - A cross-file coupling invisible from any single file.
   - A convention that contradicts the obvious default.
   - Design rationale that clears Step 5's selection filter.
   - A pointer carrying a must-know-before-you-touch obligation.
4. **Provenance carve-out — don't mistake evidence for breadcrumb.** A quirk's `Discovered: YYYY-MM (sha)` stamp is a freshness anchor (how stale the workaround's premise is), not historical narrative. Keep it; a TRIM must never strip per-entry provenance.
5. **If it's rationale ("why"), keep it only when a tempting wrong alternative existed.** That rejected alternative is the *selection filter*: no tempting wrong path → the choice is self-evident → don't record it. (E.g. "polls every 60s — webhooks drop silently during bulk ops" earns a line because webhooks were the tempting wrong path.) A kept rationale is a *constraint* — the reason is the fact itself; emit it as the `rationale` category (Step 7).
6. **Check it isn't already carried.** WORTH is corpus-relative: a fact an existing doc, rule, or comment already states is not a fresh keep. Single-file-visible duplication you catch alone; coupling and cross-doc dedup need the other file(s) — flag, don't force.
7. **Verdict:** keep or cut, with the one-line reason — and, on a keep, the fact's category (gotcha / coupling / convention / rationale / pointer).
