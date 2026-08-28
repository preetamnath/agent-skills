# Root `CLAUDE.md` Writing Guide

Use the root `CLAUDE.md` for always-loaded, repository-wide instructions and routes to task-specific sources.

## Admission test

Keep a line only when all five answers are yes:

1. **Repository-wide:** Could an agent need it on any task, regardless of subtree?
2. **Non-derivable:** Would reading the code, configuration, or test failure not reveal it reliably?
3. **Actionable:** Does it change what the agent reads, does, verifies, or avoids?
4. **Current:** Does it describe the repository now rather than its history or a future intention?
5. **Best owner:** Is the root the narrowest reliable place that can deliver it?

Move a line when only the best-owner test fails. Cut it when any other test fails, unless another durable document needs the fact.

## What belongs in the root

- **Current identity:** one or two lines describing the product and its durable architectural shape.
- **Universal vocabulary:** terminology every task must use consistently.
- **Intent-to-source routes:** `task or question → authoritative file`, loaded only when relevant.
- **Verification entry points:** exact repository commands and host-wide constraints needed before completion.
- **Repository-wide invariants:** rare safeguards whose omission can cause a material mistake anywhere in the repository.

## What belongs elsewhere

| Content | Owner |
|---|---|
| Subtree-local convention or file map | Nearest nested `CLAUDE.md` |
| One coupling across files without a useful common subtree | Exact path-scoped rule or executable guard |
| Multi-step procedure | Skill or named workflow document |
| Task-specific product, design, operations, or decision context | Maintained document reached by an intent route |
| Mechanism local to code | Comment or docstring beside the mechanism |
| Personal preference used across repositories | User-level instructions |
| Historical evidence or provisional findings | Dated research or investigation record |

Give every supported agent an equivalent delivery path before moving a rule into a provider-specific mechanism; `.claude/rules/` alone misses agents that discover only `AGENTS.md`.

A cross-module topic does not justify a separate document. Create or keep one only when a named task must read it before work, an intent pointer delivers it, and a workflow keeps it current; otherwise decompose its facts into local comments, ancestor instructions, or exact path rules.

## Recommended shape

```markdown
# Agent instructions

<Current repository identity in one or two lines.>

<Optional universal terminology rule.>

## Read when relevant

- <Intent> → `<authoritative path>`.

## Verify

| What | Command | Where |
|---|---|---|
| <Check> | `<command>` | `<working directory>` |

- <Verification constraints the command table cannot express.>

## <Repository-wide invariant>

- <Instruction needed across the whole repository.>
```

Include only non-empty sections whose lines pass the admission test.

## Write or reorganize the file

1. Read the current root file and every source that may own its facts: user instructions, nested `CLAUDE.md` files, path-scoped rules, skills, workflows, and living documents.
2. Classify every line as **keep**, **move**, or **cut** before rewriting.
3. Verify identity, commands, paths, and current behavior against authoritative sources.
4. Build the recommended shape from the admission test and ownership table; organize routes by reader intent, not document inventory.
5. Move each fact to its governing owner in the same change so the guidance remains available.
6. Run `compress-file`, `tighten-file`, and `structure-prose`; keep only high-confidence changes that preserve meaning.
7. Re-read the complete file without the old version visible, use the cold-read checklist, and verify every supported agent can discover equivalent guidance.

## Maintenance rules

- Replace stale guidance in place or move it to its owner.
- Point to a nested `CLAUDE.md` only when it is the deliberate task-entry index for work that starts outside its subtree; otherwise rely on automatic loading.
- Keep historical rationale in the root only when it prevents a likely wrong change; otherwise move it to the decision or investigation record.
- Split or move content when different audiences or delivery triggers need it; treat length as a signal, not a quota.

## Cold-read checklist

- Does the opening describe the repository as it exists now?
- Can an agent find each maintained task context, active work, operations, and close-out truth from a relevant intent?
- Are all commands exact, runnable, and paired with the correct working directory?
- Does every rule apply repository-wide?
- Is any procedure better owned by a skill or workflow?
- Is any fact duplicated in another instruction layer?
- Did every moved instruction reach its new owner in the same change?
- Can Claude, Codex, and other supported agents discover equivalent guidance?
- Does each line read clearly without surrounding history?
