---
name: supervise-plan
description: "Keep a long execute-plan run alive across context windows: from a separate chat, watch the shared mailbox and respawn a fresh orchestrator whenever the run pauses at a wave boundary. TRIGGER when: user says 'supervise the plan run' or 'babysit the plan'."
---

# Supervise Plan

Continuity daemon for a multi-session `execute-plan` run. The orchestrator does the work and decides when to pause — it logs `PAUSED` at a wave boundary when its context runs high (its Step 1.10). This skill owns only continuity — respawn and notify — and stays deliberately ignorant of the plan's content. Fresh orchestrator sessions start with zero conversational state because `execute-plan` resumes from disk (checkboxes + Base SHA).

## Protocol

### Input

- **Spec folder**: `meta/specs/NNN-slug/` containing `plan.md`. Run this skill from the project repo containing the spec folder — the self-gauge and launcher assume that working directory.
- **Optional override**: Ghostty font size (default 17).

### Step 0 — Bootstrap

1. Verify `plan.md` exists and its Status is not FROZEN — otherwise tell the user and stop.
2. If the mailbox doesn't exist: create it (format in [Mailbox format](#mailbox-format)) and append `supervisor | initialize execute-plan | total N waves | HH:MM` — N = the count of `### Wave` headings in `plan.md`, the one look at plan structure this skill takes. The mailbox's existence is what switches on `execute-plan`'s wave-boundary checkpoint.
3. If the mailbox has no `orchestrator |` line, spawn the orchestrator via the [Launcher](#launcher) with command `claude "/execute-plan meta/specs/NNN-slug"`.
4. Invoke the `loop` skill via the Skill tool with the watch cycle (Step 1) as the recurring prompt, every 10 minutes.

### Step 1 — Watch cycle (each wake)

Read the mailbox and `plan.md`'s `Status:` line only. Act on the FIRST matching row:

| Condition | Action |
|---|---|
| plan Status is FROZEN | Final report (Step 3). End the loop — do not reschedule. |
| Newest `orchestrator \|` line is `PAUSED after wave N` with no later `supervisor \| RESUME` line | Spawn the next session (Step 2). |
| Otherwise | Nothing — next wake in 10 min. |

**Self-gauge — run last on every wake that continues the loop.** Every wake adds tokens to this session; hand off before the watcher itself runs out of context. Compute your own context per the [Context gauge](#context-gauge); if ≥ 180k: append `supervisor | supervisor handoff | ctx NNNk | HH:MM`, spawn a fresh supervisor via the [Launcher](#launcher) with command `claude "/supervise-plan meta/specs/NNN-slug"`, tell the user, and end your loop — the fresh supervisor rebuilds its state from the mailbox alone.

### Step 2 — Spawn the next session

1. Launch `claude "/execute-plan meta/specs/NNN-slug"` via the [Launcher](#launcher).
2. Append `supervisor | RESUME execute-plan | wave N+1 | HH:MM` (N from the `PAUSED` line; write `final review` instead of `wave N+1` when the `PAUSED` line is marked `(final wave)` — the fresh session enters Step 4, not a wave) and notify the user: "handoff done - fresh orchestrator running".
3. The new session reports next at its first wave boundary — or, for a `(final wave)` resume, writes no further `orchestrator |` lines and ends at Status FROZEN.

### Step 3 — Final report

When `plan.md`'s `Status:` is FROZEN (Step 1's first row): notify the user the plan has shipped, then post in chat in this shape:

```
**Plan shipped — supervision complete:**
- Sessions spawned: [N]
- Pauses taken: [N]
- Mailbox: [path]
```

(Write `Pauses taken: 0 — completed in one session` when the run never paused.) Leave the file in the spec folder — it is the run's history. End the loop.

## Rules

- **Continuity only, never content.** Read only the mailbox, `plan.md`'s `Status:` line and `### Wave` headings, and your own transcript for the [Context gauge](#context-gauge); write only mailbox appends; act only by spawning tabs and notifying.
- **Spawn only from `PAUSED`** — it marks a clean disk checkpoint; anything else (silence, a stuck tab) is the user's to inspect.
- **Append-only mailbox, ASCII-only lines** — they are grep anchors; line ownership in [Mailbox format](#mailbox-format).
- **Notify via macOS notification**: `osascript -e 'display notification "<msg>" with title "supervise-plan: NNN-slug"'` — plus a one-line entry in your own chat.
- **Spawned sessions run in the user's default permission mode** — walk-away continuity assumes that mode doesn't prompt.
- **Spawned tabs steal focus** — upstream Ghostty bug #11457, not a fault.
- **Ghostty AppleScript is a preview API** (since 1.3.0; may change in 1.4). If the launcher errors, first re-check the inner-quote escaping (the usual cause); only on a genuine API failure fall back to `open -na Ghostty.app --args --working-directory=<dir> --input='raw:<command>\n'` and warn the user it spawns a separate app instance (a second Dock icon; AppleScript can then target the wrong instance). Never drive a live session via tmux/keystroke injection.

---

## Mailbox format

Location: `meta/specs/NNN-slug/mailbox.md`. Append-only, one event per line, `HH:MM` local time, pure ASCII. Exact line forms:

```
supervisor | initialize execute-plan | total 7 waves | 10:45
orchestrator | wave 2 complete | ctx 143k | 11:02
orchestrator | wave 3 complete | ctx 186k | 12:26
orchestrator | PAUSED after wave 3 | ctx 186k | 12:26
supervisor | RESUME execute-plan | wave 4 | 12:31
supervisor | supervisor handoff | ctx 185k | 14:40
```

A `PAUSED` line is answered by a later `supervisor | RESUME` line; unanswered → Step 2. A `PAUSED after wave N (final wave)` variant — written at loop exit, before Step 4 — spawns identically, but is the LAST handoff: the fresh session runs finalization (Steps 4-7) writing no more `orchestrator |` lines, and ends at Status FROZEN (caught by Step 1's first row). `execute-plan` writes the `orchestrator |` lines at its wave-boundary and pre-finalization checkpoints; everything else is the supervisor's.

## Context gauge

<!-- source: references/context-gauge.md -->

How a Claude Code session measures its own context fill in absolute tokens (works because `CLAUDE_CODE_SESSION_ID` is exported to Bash subprocesses):

```bash
python3 -c "
import json, os
sid = os.environ['CLAUDE_CODE_SESSION_ID']
proj = os.path.expanduser('~/.claude/projects/<encoded-project-dir>')
last = None
for line in open(f'{proj}/{sid}.jsonl'):
    try: d = json.loads(line)
    except: continue
    u = (d.get('message') or {}).get('usage')
    if d.get('type') == 'assistant' and u and u.get('input_tokens') is not None: last = u
ctx = last['input_tokens'] + last.get('cache_read_input_tokens',0) + last.get('cache_creation_input_tokens',0)
print(f'{round(ctx/1000)}k')
"
```

`<encoded-project-dir>` is the project path with `/` replaced by `-` (e.g. `-Users-you-code-myrepo`). The transcript JSONL format is internal to Claude Code and can change between releases — if the fields vanish, fall back to the statusline's `context_window` fields and update `references/context-gauge.md` plus its consumers.

## Launcher

Verified on Ghostty 1.3.1, macOS. Opens a visible tab in the user's existing window — same app instance — or a new window when none exist. Three constraints on the `<command>` string:

- ASCII only — bytes go to the pty raw; multi-byte characters get mangled.
- End with the linefeed — that is what executes the command.
- Escape inner double quotes as `\"` inside the AppleScript string — an unescaped `claude "..."` is a syntax error. The block below shows a real escaped command:

```bash
osascript \
  -e 'tell application "Ghostty"' \
  -e 'set cfg to new surface configuration' \
  -e 'set initial working directory of cfg to "<project-dir>"' \
  -e 'set font size of cfg to 17' \
  -e 'set initial input of cfg to "claude \"/execute-plan meta/specs/NNN-slug\"" & linefeed' \
  -e 'if (count of windows) = 0 then' \
  -e 'new window with configuration cfg' \
  -e 'else' \
  -e 'new tab in front window with configuration cfg' \
  -e 'end if' \
  -e 'end tell'
```
