---
name: memory-prune
description: "Prune project memory files: keep memory-native records, route guidance, state, and evidence to canonical owners, then trim or delete absorbed sources. TRIGGER when: user says 'prune my memories', 'clean up memory', 'what memories should be promoted', or 'review my memory dir'. SKIP when: routing one fact (place-fact), or auditing one instruction file or AGENTS.md (refine-file)."
---

# Memory Prune

## Protocol

### Step 0 — Resolve and read the memory set

Resolve `~/.claude/projects/<slug>/memory/`, where `<slug>` replaces every non-alphanumeric character in the absolute current directory with `-`, with `ls ~/.claude/projects/ | grep -Fx -- "$(pwd | sed 's|[^a-zA-Z0-9]|-|g')"`. If it returns zero or multiple matches, show the candidates and ask the user to choose. Read every `*.md` except the `MEMORY.md` index, including frontmatter and `metadata.type`; stop if none exist.

### Step 1 — Load the lenses

Invoke the Skill tool to load `vet-fact`, `place-fact`, `tighten-instruction`, and `structure-prose`; this workflow owns memory dispositions.

### Step 2 — Classify and score each fact

Judge coherent facts or blocks; one file can span lanes. Treat `metadata.type` only as a signal: `user` or `feedback` leans memory-native; `project` or `reference` leans toward guidance, state, or evidence.

| Material | Verdict |
|---|---|
| Current guidance kept by `vet-fact` | **PROMOTE** through `place-fact`. |
| Setup or onboarding excluded by `vet-fact` | **ROUTE** to the README. |
| Stale, derivable, or duplicated guidance | **DROP**. |
| Active state or unique evidence/open decisions | Skip `vet-fact`; **ROUTE** through `place-fact`. |
| Completed state or evidence with no unique value | **DROP** when `place-fact`'s retirement condition applies. |
| User preference, feedback, or deliberately auto-loaded live context | **KEEP** only when memory is its canonical owner with upkeep and retirement paths. |

For every PROMOTE or ROUTE, including README routes, record `place-fact`'s full placement contract in the analysis; do not paste it into the repository.

Score each verdict `0.0–1.0`; name the target or why memory remains the owner. Derive each file's source disposition from all its facts:

| Disposition | Use when |
|---|---|
| **DELETE** | Every fact will be absorbed or dropped. |
| **TRIM** | Some facts remain; remove absorbed or dropped blocks, preserve the rest, and point only when the placement contract requires it. |
| **NONE** | Memory remains the canonical owner for the complete file. |

### Step 3 — Present and confirm

Present every recommendation at confidence `≥ 0.70`, sorted by confidence:

```text
| # | Confidence | Memory and block | Verdict | Target | Source disposition | Why |
|---|---:|---|---|---|---|---|
```

Report the count below `0.70`; stop if no row qualifies. KEEP rows are informational. Confirm each PROMOTE, ROUTE, or DROP before editing a target or source.

### Step 4 — Apply and prove

For each approved PROMOTE or ROUTE:

1. Shape PROMOTE material with `tighten-instruction`, then `structure-prose`; preserve ROUTE material in its owner's required form.
2. Write the canonical target and required delivery views; verify the trigger, upkeep, and retirement path.

Recompute source dispositions from approved rows. DELETE removes the source; TRIM preserves unabsorbed blocks and refreshes stale frontmatter or summaries. Leave declined and below-threshold facts unchanged.

Update `MEMORY.md`: remove deleted sources, refresh trimmed sources, and keep `- [Title](file.md) — one-line summary` for all others.

Cold-read every changed source and target in full. Fix only run-caused or exposed contradictions, duplicate ownership, mixed scopes, broken routes, lost evidence, or unnecessary eager loading.

### Step 5 — Report

```text
**Memory prune:**
- Promoted: [memory block → target, one per line | none]
- Routed: [memory block → target, one per line | none]
- Kept: [memory block, one per line | none]
- Dropped: [memory block, one per line | none]
- Sources: [N deleted, N trimmed, N unchanged]
- Below threshold: [N]
```
