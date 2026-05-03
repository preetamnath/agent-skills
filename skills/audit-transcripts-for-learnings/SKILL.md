---
name: audit-transcripts-for-learnings
description: Audit past Claude Code transcripts in a chosen scope and date window to extract reusable patterns, then walk through each one to promote it into a slash command, CLAUDE.md rule, memory entry, or new skill. Use when the user wants to retrospectively mine sessions for workflow improvements, recurring corrections, validated approaches, or repeated procedures worth capturing.
---

# Audit Transcripts for Learnings

Retrospective audit of past Claude Code sessions. Extracts reusable patterns from transcripts in a chosen scope and date window, then walks the user through each one inline — promote to active config, reject, refine, or skip — in a single conversation.

## When to use

- After a sprint, project phase, or month of work — to surface what changed about *how* you work that should be encoded.
- When the user says "audit my transcripts", "what should I be capturing", "review my last N weeks", or similar.
- When repeated corrections or workflows feel familiar and worth formalising.

## When NOT to use

- For analysing skill *usage* (which skills you do/don't invoke) — that is a separate audit.
- For deep code review or planning — wrong tool.

## Protocol

### 1 — Always ask scope

Use `AskUserQuestion` to ask **which transcripts to scan**. No defaults — always ask.

Question: *"Which transcripts should I audit?"*
Options:
- **This repo only** — only transcripts from the current working directory's project (resolve via `pwd` and match against `~/.claude/projects/<slug>/`).
- **All projects (global)** — every project directory under `~/.claude/projects/`.
- **Specific project** — list the top 10 project dirs by recent activity, let user pick. (Use `find ~/.claude/projects -maxdepth 1 -mindepth 1 -type d | xargs -I {} sh -c 'echo "$(find {} -name "*.jsonl" -newermt "30 days ago" 2>/dev/null | wc -l) {}"' | sort -rn | head -10` to rank.)

Resolve the chosen scope to a concrete list of project directories before continuing.

**Project slug**: when a project root is needed for path resolution, derive the slug by replacing `/` with `-` in the absolute path (e.g. `/Users/x/code/Foo` → `-Users-x-code-Foo`). Verify it exists under `~/.claude/projects/<slug>/` before writing.

### 2 — Always ask window

Use `AskUserQuestion` to ask **the date window**. No defaults.

Question: *"What date range?"*
Options:
- **Last 7 days**
- **Last 30 days**
- **Last 90 days**
- **Custom dates** — if chosen, ask a follow-up plain-text question for `YYYY-MM-DD` to `YYYY-MM-DD`.

Convert the window to an absolute start date for `find -newermt`.

### 3 — Discover transcripts

For each project dir in scope, run:

```
find <project-dir> -maxdepth 1 -name "*.jsonl" -newermt "<start-date>"
```

Count total files and per-dir. Some `.claude/projects/` subdirs contain only bash safety-classifier sidechains — short non-interactive transcripts. The scan will pick these up but they yield zero findings; that's fine.

### 4 — Dispatch parallel scan

Split the file list across **2–4 parallel `general-purpose` subagents** with `model: "sonnet"`, chunked roughly evenly. Each subagent's prompt:

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
- Return: structured findings as JSON or markdown. For each finding include: category, one-line summary, evidence (file path + 1–2 quoted lines), and a tentative recommendation.

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

For each finding, check if it's already covered. If yes, note it and demote the recommendation (skip-by-default or merge-with-existing rather than create-new).

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

## Rules

- **Always ask scope and window.** No defaults. Two `AskUserQuestion` calls before any scanning.
- **Inline only.** Do not write intermediate files to `~/.claude/skills/learned/` — findings live in the conversation. The user explicitly chose this design.
- **One question per round during the walkthrough.** Don't shotgun multiple findings in one prompt.
- **Recommendation-first.** Every `AskUserQuestion` lists your recommended option first, marked `(Recommended)`, with one-sentence reasoning embedded in the option's `description`.
- **Overlap detection is mandatory.** Always read existing CLAUDE.md / commands/ / skills/ in Step 6 before showing findings. Naming the existing rule that overlaps is more useful than a generic "this might overlap".
- **Frequency matters.** A correction repeated 5 times across 5 sessions is more important than a one-off insight, even if the one-off is technically clever.
- **No content fabrication.** Every finding must cite at least one transcript file path. If you can't, drop it.
- **Cap subagent count at 4.** More than that adds coordination overhead without speed benefit for typical scan sizes.
- **Confidentiality is not in scope for v1.** Internal use; no PII scrubbing layer. If this skill is ever shared externally, that becomes a Future Work item.
