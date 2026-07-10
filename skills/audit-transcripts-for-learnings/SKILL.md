---
name: audit-transcripts-for-learnings
description: "Audit past Claude Code transcripts in a chosen scope and date window to extract reusable patterns, then walk each one to promote it into a slash command, CLAUDE.md rule, memory entry, or new skill. TRIGGER when: user wants to mine past sessions for reusable workflow patterns, recurring corrections, or validated approaches worth capturing; user asks how often a skill ran across sessions."
---

# Audit Transcripts for Learnings

Audit past Claude Code sessions to extract reusable patterns from transcripts in a chosen scope and date window, then walk the user through each one inline — promote to active config, reject, refine, or skip — all in one conversation.

## When to use

- After a sprint, project phase, or month of work — to surface what changed about *how* you work that should be encoded.
- When the user says "audit my transcripts", "what should I be capturing", "review my last N weeks", or similar.
- When repeated corrections or workflows feel familiar and worth formalising.
- When the user asks how often a skill ran, or which skills go unused — see Skill-usage mode.

NOT for deep code review or planning.

## Protocol

### 1 — Always ask scope

Use `AskUserQuestion` to ask **which transcripts to scan**. No defaults — always ask.

Question: *"Which transcripts should I audit?"*
Options:
- **This repo only** — only transcripts from the current working directory's project (resolve via `pwd` and match against `~/.claude/projects/<slug>/`).
- **All projects (global)** — every project directory under `~/.claude/projects/`.
- **Specific project** — list the top 10 project dirs by recent activity, let user pick. Rank with:
  ```
  d=$(date -v-30d +%F 2>/dev/null || date -d '30 days ago' +%F)
  for p in ~/.claude/projects/*/; do printf '%s %s\n' "$(find "$p" -maxdepth 1 -name '*.jsonl' -newermt "$d" 2>/dev/null | wc -l)" "$p"; done | sort -rn | head -10
  ```

Resolve the chosen scope to a concrete list of project directories before continuing.

**Project slug**: when a project root is needed for path resolution, derive the slug by replacing `/` with `-` in the absolute path (e.g. `/Users/x/code/Foo` → `-Users-x-code-Foo`). Verify it exists under `~/.claude/projects/<slug>/` before writing. Slugs start with `-`, so a bare slug path reads as a command flag (`stat: illegal option`) — prefix with `./` (e.g. `stat -f %m ./<slug>`) or pass `--` first.

### 2 — Always ask window

Use `AskUserQuestion` to ask **the date window**. No defaults.

Question: *"What date range?"*
Options:
- **Last 7 days**
- **Last 30 days**
- **Last 90 days**
- **Custom dates** — if chosen, ask a follow-up plain-text question for `YYYY-MM-DD` to `YYYY-MM-DD`.

Convert the window to an absolute `YYYY-MM-DD` start date — `START_DATE=$(date -v-Nd +%F 2>/dev/null || date -d 'N days ago' +%F)` (swap `N` for the window; BSD/macOS form first, GNU fallback). Pass `$START_DATE` to `find -newermt` — a relative string like "30 days ago" fails on BSD/macOS, and `2>/dev/null` hides it as zero matches.

### 3 — Discover transcripts

For each project dir in scope, run:

```
find <project-dir> -maxdepth 1 -name "*.jsonl" -newermt "$START_DATE"
```

Count total files and per-dir. Some `.claude/projects/` subdirs contain only bash safety-classifier sidechains — short non-interactive transcripts. The scan will pick these up but they yield zero findings; that's fine.

### 4 — Dispatch parallel scan

Split the file list across **2–4 parallel `general-purpose` subagents** (cap at 4 — more adds coordination overhead without speed benefit) with `model: "sonnet"`, chunked roughly evenly. Each subagent's prompt:

- Scope: the chunk of files assigned.
- Schema (verified against real transcripts): each line is a JSON envelope. For findings, only two `type` values matter:
  - `user`: `.message.content` is a **string** when the user typed something; an **array** of `tool_result` blocks otherwise (skip those for prompt analysis).
  - `assistant`: `.message.content` is always an **array** of blocks (`text`, `thinking`, `tool_use`). For tool calls: `.name` and `.input` are top-level on the block.
  - Use `jq` to scan. If uncertain on a particular project's transcripts, sample with `head -3 <file> | jq .`.
- What to extract per file (with file path + approximate line for evidence):
  - **Corrections** — user message says "no", "don't", "stop doing X", or rewords a previous instruction.
  - **Validations** — user accepts a non-obvious choice ("yes exactly", "perfect", "keep doing that") without pushback.
  - **Repeated workflows** — same multi-step sequence (3+ tool calls in same order) appearing across 2+ different sessions.
  - **Friction moments** — user expresses frustration, retries the same thing, or mentions a tool limitation.
  - **Surprises that worked** — assistant tried something unconventional and it succeeded.
- Filter out:
  - Trivia — anything that wouldn't save meaningful time if encoded as config (typos, syntax fixes, transient infra hiccups).
  - **Obvious** patterns — fixes any agent would arrive at unprompted.
  - **Non-reusable** — only applies to that one transcript or task, not to future sessions.
  - Anything already documented in CLAUDE.md or active skills/commands (Step 6 dedupes further).
- Return: structured findings as JSON or markdown. For each finding: category, one-line summary, evidence (file:line + 1–2 quoted lines), tentative recommendation, and two scores — `impact` (Minimal 0.25 · Low 0.5 · Medium 1 · High 2 · Massive 3 — how much encoding helps) and `confidence` (0.00–1.00 — how sure it's real, not an extraction artifact).

Cap each subagent's response at ~600 words. The orchestrator (this skill) aggregates.

### 5 — Aggregate and dedupe

Merge all subagent outputs. Collapse near-duplicates (same correction expressed in different sessions = one finding with multiple evidence pointers). Frequency raises priority but doesn't gate inclusion — a single high-value insight is still a finding.

### 6 — Read existing config for overlap detection

Before presenting findings, read these so you can flag overlaps:

Read based on **where the skill is invoked from** (not on audit scope):

**Always:**
- `~/.claude/CLAUDE.md`
- List filenames in `~/.claude/commands/`
- List filenames in `~/.claude/skills/` (top level only)
- List skill dirs in `~/Desktop/code/agent-skills/skills/`

**If `pwd` is inside a project** (resolve project root by walking up for the nearest `.git/` or `CLAUDE.md`):
- `<project-root>/CLAUDE.md`
- List filenames in `<project-root>/.claude/commands/` and `<project-root>/.claude/skills/`
- The project's `~/.claude/projects/<slug>/memory/MEMORY.md` index

Do **not** iterate every project's CLAUDE.md when audit scope is global — only the project you're currently inside (if any).

For each finding, check if it's already covered. If yes, note it — naming the specific overlapping rule, not a generic "this might overlap" — and demote the recommendation (skip-by-default or merge-with-existing rather than create-new).

### 7 — Present summary

Show one block:

```
Audit complete: <scope> · <window>
Files scanned: N · Findings: M

By suggested action:
  • Promote: X
  • Refine first: Y
  • Skip (already covered): Z
  • Reject candidates: W

By category:
  • Corrections: ...
  • Repeated workflows: ...
  • etc.
```

### 8 — Walk through findings one by one

For each finding (in this priority order: highest-frequency corrections first, then repeated workflows, then the rest):

#### a. Show the finding

- Category + one-line summary.
- Evidence (compressed — file:line + quoted excerpt).
- Overlap flag if any (e.g. "*Already partially in CLAUDE.md global rule about X*").
- Your recommendation: **Promote**, **Refine first**, **Skip**, or **Reject** — with one-sentence reason.
- Scores: `Impact: High (2) · Conf: 0.xx`.

#### b. Ask the user

Use `AskUserQuestion`:

Question: *"What would you like to do with this finding?"*
Options (Recommended option first):
- **Promote** — accept and create active configuration
- **Refine first** — discuss modifications before deciding
- **Skip** — leave it; do nothing
- **Reject** — explicitly discard (won't surface again)

Do **not** ask follow-ups unless an ambiguity in the finding genuinely requires it. Keep moving.

### 9 — Handle each decision

#### If Skip or Reject

- One-sentence acknowledgment. Move on. (Re-running an audit may re-surface a rejected finding — that's expected; reject again.)

#### If Refine first

- Discuss modifications inline with the user.
- For non-trivial reshaping (different artifact type, different scope, different framing), consider spawning the `propose-alternatives` agent before re-asking.
- Re-show the refined finding and re-ask the question.

#### If Promote

Two `AskUserQuestion` prompts in sequence (do not combine into multiSelect — they're sequential decisions with different option sets):

**Prompt 1: "What should this become?"**

Use the artifact-type matrix below. Pre-select your recommendation as option 1.

| Type | When to use | Loaded |
|---|---|---|
| **Slash command** (`commands/*.md`) | Actionable procedures invoked on-demand — debugging workflows, setup steps, code generation templates | Only when user types `/command-name` |
| **CLAUDE.md rule** | Behavioral rules Claude should always follow — coding style, response format, "always do X / never do Y" | Every session (always-on context) |
| **Memory entry** (`memory/*.md`) | Project/user context that informs decisions — who the user is, what's being worked on, external references | Every session (auto-loaded, lighter than CLAUDE.md) |
| **Skill** (`skills/<name>/SKILL.md`) | Complex multi-step capabilities with phases — rare, most patterns are better as commands or rules | When matched by skill system |

**Prompt 2: "Global or project-scoped?"**

If artifact type = **Memory entry**, skip this prompt — memory is always project-scoped.

| Scope | When |
|---|---|
| **Global** (`~/.claude/`) | Pattern applies across projects — general technique, language-level pattern, workflow preference |
| **Project-scoped** (`<project>/.claude/` or `~/.claude/projects/<slug>/`) | Pattern is specific to one tech stack, codebase, or workflow |

For findings tagged with project-specific domains (e.g. `shopify, django`), recommend project-scoped. For language-level or workflow patterns, recommend global.

#### Execute promotion

Write the artifact at the correct path:

| Type | Global path | Project-scoped path |
|---|---|---|
| **Slash command** | `~/.claude/commands/<name>.md` | `<project-root>/.claude/commands/<name>.md` |
| **CLAUDE.md rule** | Append to `~/.claude/CLAUDE.md` | Append to `<project-root>/CLAUDE.md` |
| **Memory entry** | `~/.claude/projects/<project-slug>/memory/<name>.md` + update `MEMORY.md` index | _N/A_ |
| **Skill** | `~/Desktop/code/agent-skills/skills/<name>/SKILL.md` (then update repo README) | `<project-root>/.claude/skills/<name>/SKILL.md` |

Steps:
1. Draft the artifact content from the finding.
2. Write the file. Tell the user the path and a one-line summary of what was written.
3. If a skill was created in `agent-skills/skills/`, also append a row to its README table.
4. Ask the user to review the file and flag any changes. If they say no changes, move to the next finding. If they request changes, apply them, re-write, and re-ask.

### 10 — Final summary

After all findings are processed:

```
Audit complete.
  • Promoted: N (list with paths)
  • Refined: N
  • Skipped: N
  • Rejected: N
```

If anything was promoted to `~/.claude/CLAUDE.md` or to a skill, briefly remind the user that those take effect on the next session.

## Skill-usage mode

Use this flow when the user wants how often a skill ran, not patterns to promote.

### Usage step 1 — Ask which skill, scope, and window

`AskUserQuestion` for the skill name(s); reuse Steps 1–2 for scope and window.

### Usage step 2 — Count real activations, not catalog mentions

Every transcript embeds the full skill catalog, so `grep -l "<skill-name>"` over-counts massively. Count a file as an activation only when it contains:
- A verbatim line from the skill's **body** (present only when the skill fires) — pick a distinctive phrase from its SKILL.md.
- A `Skill` tool_use naming it (`"name":"Skill"` … `"<skill-name>"`).

Exclude the `agent-skills` repo's own project dir — editing a SKILL.md embeds its body and self-matches. Get per-file dates with `stat -f %m ./<file>` (leading-dash slugs — see Step 1).

### Usage step 3 — Present the usage table

Report in this shape — one row per skill:

```
**Skill usage — [scope] · [window]:**
| Skill | Activations | Sessions | Projects | First use | Last use |
|---|---|---|---|---|---|
| [name] | [N] | [N] | [N] | [date] | [date] |
```

Flag any skill with zero real activations — a candidate to retire or fix its triggering.

## Rules

- **Inline only.** Do not write intermediate files to `~/.claude/skills/learned/` — findings live in the conversation. The user explicitly chose this design.
- **One question per round during the walkthrough.** Don't shotgun multiple findings in one prompt.
- **No content fabrication.** Every finding must cite at least one transcript file path. If you can't, drop it.
- **No PII scrubbing (v1).** Internal use only; add scrubbing before sharing externally.
