---
name: handoff
description: Compress the live conversation into minimal, copy-paste-ready handoff prompt(s) — context referenced by file path, not pasted — so a fresh chat picks up cleanly. TRIGGER when: user says handoff, handover, new-chat / fresh-chat prompt, prompt to continue or resume elsewhere; user asks for separate prompts to explore N different things in their own chats.
---

# Handoff

Each prompt is self-contained, scoped to one thread, and points at the files holding the context instead of restating them.

## When to use

- Context window is filling and the work should continue in a new chat.
- The chat has spawned several distinct threads the user wants to explore in separate chats — emit one prompt per thread.
- Wrapping a session and the user wants a clean resume later.

Skip when "resume the work in `<doc>`" already suffices — just hand them that path.

## Protocol

### Step 1 — Scope the handoffs

Read the user's request plus the conversation, then decide how many prompts and their boundaries:

- **User named the items** ("give 2 separate prompts — 1… 2…", "one for X, one for Y") → one prompt per item, in the order given. Note run-order if they're sequenced.
- **One thread** → one prompt.
- **Ambiguous** (chat sprawled across topics, user just said "handoff") → `AskUserQuestion`: one combined prompt, or separate per thread — list the threads you'd split into so the choice is concrete.

### Step 2 — Locate context to reference, don't restate

For each thread, point `Read first:` at the durable doc that holds the work's state — `CONTEXT.md`, `plan.md`, `interview.md`, a spec or discussion doc, else the specific source files, a commit, or a PR. In the prompt, carry only what that doc misses: current status, the last decision, the next action.

If no doc holds the state and the context won't fit a lean prompt, recommend creating one — default `CONTEXT.md`.

### Step 3 — Draft each prompt

Fill the skeleton. Put each field's label on its own line, value(s) beneath; bullet the values when there's more than one. Omit empty fields — `Status:` only when resuming mid-work, not for a fresh-start handoff.

```
Repo:
<abs path>[ · Working dir: <dir> — never touch <x>]

Read first:
- <path>
- <path>

Status:
<one line — where things stand>

Goal:
<the one outcome this chat should reach>

Constraints:
- <read-only vs act intent — "analysis only, present for me to decide" vs "kick off the work">
- <don'ts; guardrails not guaranteed by the target's config>

Output:
<what to produce / the format expected>
```

- **Don't restate the user's standing global preferences** — the target session loads its own `CLAUDE.md`. Carry only task-specific guardrails and the output contract.

### Step 4 — Emit

Print each prompt as its own independently copy-pasteable block. If sequenced, add one run-order line after them ("Run 1 first; fire 2 once it lands").

## Rules

- **Minimal by default, context by reference.** Point at bulk context by path; never paste it.
- **Never merge distinct threads** — one self-contained prompt each.
- **Inline, not a file.** The output is the pasted prompt; don't write it to disk unless asked.
- **Reflect current state.** Re-read the conversation's end state; drop any next-step that already happened.
- **Externalize transient state.** In-session task lists don't survive into a new chat — point the prompt at the durable doc as source of truth and tell it to rebuild its task list from there.
- **Pin the intent.** Every prompt says whether the new chat should act or only analyze.
