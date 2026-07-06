---
name: deep-modules
description: "The deep-module primitive: a small interface hiding lots of behaviour. Apply the lens to judge or shape one interface, or audit a codebase for shallow modules (returns a ranked table). TRIGGER when: user says 'deep modules', 'is this a deep module', 'find shallow modules', 'audit from the deep-module lens'; a skill needs the deep-module vocabulary."
---

# Deep Modules

A **deep module** hides a lot of behaviour behind a small interface. This skill is the shared primitive: a lens other skills load, and an audit that scans code for shallow modules.

## When to use

- **Lens mode** — apply the vocabulary and checks below to judge or shape **one** interface, in a design, a review, or another skill that loads this one. No subagents. A single file or function is always lens mode.
- **Audit mode** — scan **many** modules you can't eyeball in one read for shallow ones, and return a ranked findings table. Dispatches subagents; runs [Audit mode](#audit-mode).

## The lens

Use these terms exactly — don't substitute "component," "service," "API," or "boundary."

- **Module** — anything with an interface and an implementation; scale-agnostic (function, class, package, tier-spanning slice).
- **Interface** — everything a caller must know to use it correctly: the signature, plus invariants, ordering, error modes, required config, performance characteristics. Broader than "API/signature."
- **Implementation** — the body inside the module. Distinct from **Adapter**: a concrete thing satisfying an interface at a seam (a Postgres repo; an in-memory fake).
- **Depth** — leverage at the interface: behaviour a caller or test can exercise per unit of interface it must learn. **Deep** = lots of behaviour behind a small interface; **shallow** = interface nearly as complex as the implementation.
- **Seam** _(Feathers)_ — a place you can change behaviour without editing in place; where the interface lives. Where to put it is its own decision.
- **Leverage** — callers' payoff: one implementation pays back across N call sites and M tests.
- **Locality** — maintainers' payoff: change, bugs, and knowledge concentrate in one place. Fix once, fixed everywhere.

**What shallow looks like** — the signals an audit hunts for:

- Pass-throughs — the interface just forwards and adds nothing.
- Leaked internals — the caller must know implementation details to use it.
- Untestable except by reaching *past* the interface.
- Pure functions extracted only for unit-testability, while the real bugs hide in the uncovered glue that calls them — no locality.

**Principles**

- **The deletion test.** Imagine deleting the module. If its callers get simpler and nothing *substantial* moves into them, it was a pass-through — fold it away or deepen it. If *substantial* hidden work would reappear, spread across callers, it earns its keep. Relocating trivial boilerplate to N callers is not "earning its keep" — that's still shallow.
- **One adapter is a hypothetical seam; two is a real one.** Don't introduce a seam unless something actually varies across it.
- **A finding is a candidate, not a mandate.** A recorded project convention or decision — an ADR, a CLAUDE.md or ARCHITECTURE.md rule, or similar — can legitimately keep a split the lens would otherwise flag. Respect it; don't re-flag a settled decision.

**Deepening move by dependency** — how a shallow cluster is deepened depends on what it depends on:

| Dependency | Deepening move |
|---|---|
| In-process (pure/in-memory) | Merge the modules; test through the new interface directly. |
| Local-substitutable (PGLite, memfs) | Merge; test with the stand-in. Seam stays internal. |
| Remote but owned (your services) | Define a **port** at the seam; inject an HTTP adapter for prod, in-memory for tests. |
| True external (Stripe, Twilio) | Take the dependency as an injected port; mock it in tests. |

## Audit mode

### Step 1 — Scope and cluster

Confirm what to audit — the whole repo, a directory, or a named subsystem — and read the top-level structure to identify the main modules. Then split the scope into clusters by feature/subsystem (files that change together), not just by directory — so a shallow pattern duplicated across directories still lands in one brief. Two guards:

- **Size.** If the scope is larger than three subagents can read closely, narrow it with the user first rather than sampling a big tree and presenting it as a complete audit.
- **Prior decisions.** Apply the "a finding is a candidate, not a mandate" principle — respect recorded conventions and settled decisions. If the repo has a domain glossary, name modules in its vocabulary.

### Step 2 — Run the fan-out via multi-agent-analysis

Invoke the `multi-agent-analysis` skill via the Skill tool to dispatch the subagents, merge duplicates, and apply the confidence bands and its own-verdict pass — don't restate that machinery here. Take its judged findings back for Step 3 — the ranked table is the only presentation. Hand it:

- **Problem:** "find shallow modules in <scope>."
- **Angles:** one per cluster from Step 1 (its cap-at-3, concurrent dispatch, and `opus` model apply).
- **Per-subagent lens, relayed inline** (a parent-side load doesn't reach subagents): paste the whole **The lens** section into each brief, plus how to size impact — S/M/L by how much leverage or locality the reshape unlocks, tagged which. Instruct each subagent to ground every finding in a **named signal** (the deletion-test outcome or leaked internal that shows it, not a bare assertion), and to return the [Output Schema](#output-schema) below instead of the generic Findings shape.

### Step 3 — Present the ranked table

Sort multi-agent-analysis's judged findings by impact (L → S) then confidence, and render as a table — one row per finding, columns = the [Output Schema](#output-schema) fields (Module, What's shallow, Evidence, Deepening move, Impact, Confidence). Then stop — auditing ends here.

Close with a one-line top recommendation. To pursue a finding, point the user to `grill-me` (stress-test the reshape) or `tech-design` (design it) — this skill does not carry that loop.

## Rules

- **Audit is read-only.** It analyzes and recommends; leave edits to the user or a build skill.
- **Evidence, not vibes.** Deep-vs-shallow is a judgment call — every finding names the shallow signal it rests on, or it's dropped.
- **Depth as leverage, not line ratio.** Reject the implementation-lines-to-interface-lines metric — it rewards padding.

---

## Output Schema

What each audit subagent returns.

```
Findings {
  scope: string,                   // what was audited
  findings: [ {
    module: string,                // path:symbol
    shallow: string,               // which signal, one line
    evidence: string,              // deletion-test outcome, leaked internal, or the logic N callers re-implement
    move: string,                  // the deepening reshape, per the dependency table
    impact: string,                // "S" | "M" | "L", tagged leverage | locality
    confidence: number             // 0.00–1.00 that it's genuinely shallow and the move is right
  } ],
  dropped: string[]                // findings multi-agent-analysis dropped as low-confidence or unevidenced, listed not ranked
}
```
