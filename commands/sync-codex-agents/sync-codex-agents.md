---
description: Convert agents/*.md to Codex .toml and stage for install at ~/.codex/agents/
allowed-tools: Bash, Read, AskUserQuestion
---

# Sync Codex Agents

Convert `agents/*.md` (Claude format) to `.toml` (Codex format), stage in `.tmp/codex-agents/`, then offer to install into `~/.codex/agents/` and clean up.

## When to use

When the user wants to refresh Codex agents from the repo's Claude agents — typically after editing one or more files in `agents/`. Not for the `codex-*` MCP-wrapper agents (those are Claude-only and the script skips them).

## Protocol

### 1 — Run the conversion script

Run `bash` with `commands/sync-codex-agents/scripts/convert.py` (or `python3.12 commands/sync-codex-agents/scripts/convert.py` if the shebang fails to resolve).

The script requires **Python 3.11+** (uses `tomllib` for post-check validation).

The script:
- Reads `agents/*.md`.
- Skips files whose `tools:` line contains `mcp__codex__codex` (the Claude-only MCP wrappers).
- Writes `.tmp/codex-agents/<name>.toml` for each remaining agent.
- Wipes any pre-existing `.toml` files in that directory before writing (keeps the staging area in sync with current source).
- Runs deterministic post-checks: parses each output with `tomllib`, verifies required fields, exact body round-trip, filename/name match, and absence of MCP wrapper leakage. Exits non-zero on any failure.

If the script exits non-zero, **stop**. Show the user the script's stderr output and ask how they want to proceed via the `AskUserQuestion` tool with options: "Investigate and retry (Recommended)", "Abort". Do not proceed to step 2 until the script exits zero.

### 2 — Diff against the existing destination

For each generated `.tmp/codex-agents/<name>.toml`, compare against `~/.codex/agents/<name>.toml` if it exists:

```
diff -u ~/.codex/agents/<name>.toml .tmp/codex-agents/<name>.toml
```

Summarize for the user as a short table: agent name, status (`new`, `unchanged`, `modified`), and lines changed when modified. If any destination file would be overwritten with substantive changes the user did not initiate (e.g., they hand-edited the Codex copy), call this out explicitly.

### 3 — Confirm install destination and cleanup

Use the `AskUserQuestion` tool with these options:

- **Install to `~/.codex/agents/` and remove `.tmp/` (Recommended)** — `cp .tmp/codex-agents/*.toml ~/.codex/agents/ && rm -rf .tmp/codex-agents`
- **Install to `~/.codex/agents/` and keep `.tmp/`** — copy only
- **Install elsewhere** — ask the user for the destination path, then copy and ask again about cleanup
- **Skip install — leave files in `.tmp/`** — user will copy manually

### 4 — Execute the chosen action

Run the corresponding shell commands. After install, list what was installed (paths) so the user can verify.

## Rules

- **Never auto-install.** Always confirm via the `AskUserQuestion` tool in step 3 before writing to `~/.codex/agents/` or any destination outside the repo. Auto mode does not override this — installing modifies a directory outside the repo.
- **Never convert `codex-*` wrappers.** These agents use `mcp__codex__codex` and exist only to call Codex from Claude. They make no sense inside Codex itself. The script filters them; if a user asks to include one, refuse and explain why.
- **Stop on script failure.** If `convert.py` exits non-zero, do not proceed. The post-checks catch real bugs (truncated bodies, malformed TOML, MCP leakage) — bypassing them defeats the point of the skill.
- **Frontmatter fields `model` and `tools` are dropped.** Codex's agent format has no equivalent. If a user asks where these went, explain.
- **The TOML format is inferred from one example** (`~/.codex/agents/codex.toml`). If Codex rejects a generated file, the script is wrong, not the source `.md`. Update the script.
- **Diff before overwriting.** Step 2 is not optional — silent overwrites of hand-edited Codex agents are the most likely way this skill loses user data.
- **Re-run end-to-end on every invocation.** Don't try to detect "nothing changed" and skip. The script is fast and idempotent; running it always is safer than partial runs.

## Gotchas

- **Apostrophes in descriptions** (e.g., `verifier`'s `another agent's findings`) require TOML basic-string escaping, not literal-string. The script uses basic strings (`"..."`) for `name` and `description` and handles escaping. If you ever switch to literal strings (`'...'`), apostrophes will break the parse.
- **Triple-single-quote in body** would terminate the TOML literal multi-line string early. The script detects this and falls back to multi-line basic (`"""..."""`) with escaping. None of the current agents trip this, but a future agent containing a `'''` Python heredoc could.
- **Trailing newline trim.** TOML strips one newline immediately after the opening `'''` (or `"""`). The renderer relies on this and does NOT add an extra `\n` before the closing delimiter — adding one would inject a phantom newline into the parsed body and break exact round-trip. The post-check enforces exact round-trip via `tomllib`, so this kind of regression is caught immediately.
- **Filename stem must match `name` field.** Codex looks up agents by filename. The post-check enforces this; do not rename outputs.
- **`.tmp/` is gitignored** at repo root via `/.tmp/`. Outputs never appear in `git status`.
