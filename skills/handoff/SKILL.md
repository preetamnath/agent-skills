---
name: handoff
description: "Compress the live conversation into minimal, copy-paste-ready handoff prompt(s) — context referenced by file path, not pasted — so a fresh chat picks up cleanly. TRIGGER when: user says handoff, handover, new-chat / fresh-chat prompt, prompt to continue or resume elsewhere; user asks for separate prompts to explore N threads in their own chats."
---

# Handoff

Skip when "resume the work in `<doc>`" already suffices — just hand them that path.

## Protocol

### Step 1 — Scope the handoffs

Use the request and conversation to choose the prompt count and boundaries:

- **Named items.** Write one prompt per item, in order; note any sequencing.
- **One thread.** Write one prompt.
- **Ambiguous threads.** Use `AskUserQuestion` to ask whether to combine or separate them, and list the proposed split.

### Step 2 — Locate context to reference, don't restate

- **Source.** Point `Read first:` at the state artifact the workflow already maintains (`plan.md`, `interview.md`, spec, or investigation); otherwise reference the source files, commit, or PR.
- **Delta.** Add only missing current status, the last decision, and the next action. Drop completed next actions and tell the new chat to rebuild its task list from the sources.
- **Missing owner.** If the remaining state cannot fit a lean prompt, use `AskUserQuestion` to ask whether and where to create an active-state artifact. Use a location maintained by an existing workflow or chosen by the user; never default to `CONTEXT.md`.

### Step 3 — Draft each prompt

- **Skeleton.** Use only the headings below; fold needed details into an existing field.
- **Fields.** Put each label on its own line, place values beneath it, and bullet multiple values. Omit empty fields; include `Status:` only for work in progress.
- **Preferences.** Let the target load its own repository instructions. Carry only task-specific guardrails.

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

Return each prompt in a separate copy-pasteable block; write files only when asked. Add one paste instruction and one run-order line when sequenced.
