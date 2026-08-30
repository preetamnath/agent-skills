# Root `AGENTS.md` Writing Guide

Use root `AGENTS.md` for current, non-derivable guidance whose delivery trigger is any repository task. Root `AGENTS.md` is canonical; other providers load a derived or automatically guarded view.

## Load the lenses

Invoke the Skill tool to load `vet-fact`, `place-fact`, `compress-file`, `tighten-instruction`, and `structure-prose`. Use WORTH → PLACE → SHAPE for every candidate line; do not restate their criteria here.

## What the root owns

- **Current identity.** One or two lines that orient every task to the product and its durable architectural shape.
- **Universal vocabulary.** Terms every task must use consistently.
- **Read-when-relevant routes.** A task or question mapped to one authoritative, non-auto-loaded source.
- **Verification entry points.** Exact repository commands and host constraints needed before completion.
- **Repository-wide invariants.** Rare safeguards whose omission can cause a material mistake anywhere in the repository.

Route each kept fact that fails root PLACE through `place-fact`. Create provider views through the same placement contract; keep one root authoring path.

## Recommended shape

```markdown
# Agent instructions

<Current repository identity in one or two lines.>

<Optional universal terminology rule.>

## Read when relevant

- <Task or question> → `<authoritative path>`.

## Verify

| What | Command | Where |
|---|---|---|
| <Check> | `<command>` | `<working directory>` |

- <Verification constraint the command table cannot express.>

## Repository-wide invariants

- <Instruction needed across the whole repository.>
```

Include only non-empty sections whose lines pass WORTH and PLACE.

## Write or reorganize the file

1. Read the current root instructions, their provider delivery views, and every trigger-reachable source that may already own a candidate fact.
2. Pin the file's purpose and exact invariants, then classify each candidate as KEEP, MOVE, or CUT through `vet-fact` and `place-fact`.
3. For every MOVE or new artifact, record `place-fact`'s full placement contract in the analysis; keep one canonical owner and derive or guard every delivery view.
4. Verify identity, commands, paths, and behavior against authoritative sources.
5. Build the recommended shape by task trigger, move each fact to its canonical owner in the same change, and retire any view the new delivery makes unnecessary.
6. Apply `compress-file`, then `tighten-instruction` to every changed instruction block, then `structure-prose` to fused blocks.
7. Re-read every changed source and destination in full against the checklist below.

## Cold-read checklist

- Does the opening describe the repository as it exists now?
- Does every kept root line apply to any repository task and prevent a likely wrong answer?
- Does each route point only to a required source that will not already auto-load?
- Are commands exact, runnable, and paired with the correct working directory?
- Did every moved fact reach its canonical owner in the same change?
- Is the result free of duplicate ownership, mixed scopes, broken routes, and unnecessary eager loading?
- Does current guidance exclude active state and dated evidence except for justified routes?
- Does every provider view derive from the canonical file or have an automatic equality guard?
- Can every supported agent discover equivalent guidance at the trigger and after compaction when required?
- Does each line read clearly without surrounding history?
- Does each added always-loaded line earn eager delivery? Treat growth as a review signal, never a quota.
