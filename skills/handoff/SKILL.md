---
name: handoff
description: "Compress the live conversation into minimal, copy-paste-ready handoff prompt(s) — context referenced by file path, not pasted — so a fresh chat picks up cleanly. TRIGGER when: user says handoff, handover, new-chat / fresh-chat prompt, prompt to continue or resume elsewhere; user asks for separate prompts to explore N threads in their own chats."
---

# Handoff

Skip when "resume the work in `<doc>`" already suffices — just hand them that path.

## Protocol

### Step 1 — Scope the handoffs

Read the user's request plus the conversation, then decide how many prompts and their boundaries:

- **User named the items** ("give 2 separate prompts — 1… 2…", "one for X, one for Y") → one prompt per item, in the given order; note run-order if sequenced.
- **One thread** → one prompt.
- **Ambiguous** (chat sprawled across topics, user just said "handoff") → `AskUserQuestion`: one combined prompt, or separate per thread — list the threads you'd split into.

### Step 2 — Locate context to reference, don't restate

For each thread, point `Read first:` at the durable doc that holds the work's state — `CONTEXT.md`, `plan.md`, `interview.md`, a spec or discussion doc, else the specific source files, a commit, or a PR. Carry only what that doc misses — current status, last decision, next action — re-reading the conversation's end to drop any next-step already done, and tell the prompt to rebuild its task list from that doc. If no doc holds the state and the context won't fit a lean prompt, recommend creating one — default `CONTEXT.md`.

### Step 3 — Draft each prompt

Fill the skeleton — no invented headers (`Method:`/`Background:`/`How to work:`); fold genuinely needed extras into an existing field, cut the rest. Put each field's label on its own line, value(s) beneath; bullet multiple values. Omit empty fields — `Status:` only when resuming mid-work. Don't restate the user's global preferences — the target loads its own `CLAUDE.md`; carry only task-specific guardrails.

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

### Step 4 — Emit

Print each prompt as its own copy-pasteable block; write it to disk only if asked. Add only a one-line paste-instruction and — when sequenced — one run-order line ("Run 1 first; fire 2 once it lands"), never a note recapping the block's own choices.
