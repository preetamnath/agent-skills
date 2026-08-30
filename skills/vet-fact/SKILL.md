---
name: vet-fact
description: "Judge whether a candidate current-guidance fact earns a durable instruction line: keep only what prevents a likely wrong answer; cut derivable, historical, setup, or default restatements. TRIGGER when: user asks 'does this belong in AGENTS.md / a rule / the docs', 'is this worth keeping/writing down', or 'should this be a comment'; vetting or pruning current guidance before placement or shaping. SKIP when: evaluating or placing active state or dated evidence (place-fact)."
---

# Vet Fact

Primitive: **WORTH** — does this candidate fact deserve a current-guidance line at all?

## Steps

1. **State the fact in one line, then apply the gate:** would a capable future agent likely get the wrong answer without it? Cut it when code, configuration, or live help reveals it reliably; lookup cost alone does not justify current guidance.
2. **Keep WORTH inside current guidance:**
   - **Exclude state and evidence records.** Do not run an active-state document or dated investigation through this lens; apply WORTH only to conclusions proposed for current guidance.
   - **Preserve freshness provenance.** Keep a per-entry `Discovered: YYYY-MM (sha)` stamp only when it lets a future agent judge whether a current workaround's premise is stale; a trim must preserve it.
3. **Cut a current-guidance candidate on any hit:**
   - **Setup.** Put setup and onboarding in the README.
   - **History.** Cut dates, plan IDs, commit SHAs, superseded/originally notes, completion summaries, and deferred-item lists.
   - **Defaults.** Cut restated framework or harness defaults.
   - **Drift-prone literals.** Cut hex codes, version pins, and exact syntax unless the literal is itself load-bearing.
4. **Keep only a recognized category:**

   | Category | Keep when |
   |---|---|
   | Gotcha | A non-obvious trap, anti-pattern, or dead-code warning can cause a wrong change. |
   | Coupling | A cross-file constraint is invisible from any single file. |
   | Convention | The required choice contradicts the obvious default. |
   | Rationale | A tempting wrong alternative exists; keep the reason as the constraint. |
   | Pointer | The agent must follow the target before touching the governed work. |
5. **Cut facts already carried elsewhere.** WORTH is corpus-relative: an existing comment, rule, or document makes the same fact a duplicate. Catch duplicates visible in scope; flag cross-document deduplication when the needed sources are outside scope.
6. **Return the verdict:** keep or cut, with a one-line reason; on a keep, include the category (gotcha / coupling / convention / rationale / pointer).
