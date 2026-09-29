# Global instruction sharing across Claude, Codex, and OpenCode

| Field | Value |
|---|---|
| Question | Should shared global instructions move to `~/.agents/AGENTS.md`, with each tool's own global file keeping only its additions and loading the shared file? |
| Evidence scope | Global files `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, `~/.config/opencode/AGENTS.md`, `~/.config/opencode/opencode.json`, `~/.codex/config.toml`; Claude Code 2.1.283, Codex CLI 0.157.0, OpenCode 2.0.3; Codex and OpenCode docs; binary string inspection; live Codex runs. 2026-09-26 to 2026-09-29. |
| Status | Open — recommendation made; not implemented. |
| Current owners | None yet. |
| Open decisions | Codex option B or C (see Options). |
| Closure outcome | Pending. |

## Answer

Yes — move shared rules to `~/.agents/AGENTS.md` (confidence 0.80). Each tool needs a different loading mechanism, because only Claude expands `@path` imports. A path pointer inside Codex's or OpenCode's AGENTS.md is read by the model as text; it is not a load.

## Setup at investigation time

```
~/.codex/AGENTS.md            canonical shared rules + "Codex only" section
   ^                     ^
   | @import             | prose: "Read and follow ~/.codex/AGENTS.md"
~/.claude/CLAUDE.md    ~/.config/opencode/AGENTS.md
(+ "ignore Codex only")  (+ "ignore Codex only" + OpenCode-only rules)
```

`~/.agents/` already exists and holds `npx skills` skills (`skills/`, `.skill-lock.json`); it has no `AGENTS.md`.

## Findings

| # | Finding | Evidence |
|---|---|---|
| 1 | Claude expands `@~/path` imports into context. | Current `@~/.codex/AGENTS.md` content was present in a Claude session's context. |
| 2 | Codex does not expand `@path` in AGENTS.md. | `codex debug prompt-input` in a test project whose AGENTS.md held `@canary.md` and `@./canary.md`: prompt contained the literal `@canary.md` lines and not the canary file's token. Docs (learn.chatgpt.com/docs/agent-configuration/agents-md) describe only directory layering and `AGENTS.override.md`. |
| 3 | Codex reads a symlinked global AGENTS.md. | `CODEX_HOME=<tmp>` with `AGENTS.md` symlinked to another file: `prompt-input` contained the target's token. |
| 4 | Codex `developer_instructions` in `config.toml` carries multi-line Markdown verbatim. | `'''…'''` TOML string with a table, backticks, and quotes appeared unchanged in `prompt-input`, as its own **developer**-role message placed before AGENTS.md content. |
| 5 | Codex has no "developer instructions from file" key; `model_instructions_file` replaces the built-in system prompt, so it is not a substitute. | Config keys in the 0.157.0 binary; confidence 0.80. |
| 6 | Project AGENTS.md and global AGENTS.md land in the same Codex instructions block. | `prompt-input` showed global content, then `--- project-doc ---`, then project content. Pointer tests below therefore apply to the global file. |
| 7 | OpenCode loads global rules only from `~/.config/opencode/AGENTS.md` (falls back to `~/.claude/CLAUDE.md` when that file is missing). It does not parse file references in AGENTS.md. `opencode.json` `"instructions"` accepts paths, globs, `~` paths, and URLs — not inline text. | OpenCode loader code in the 2.0.3 binary; opencode.ai/docs/rules. Not tested live. |
| 8 | OpenCode lists `~/.agents` as a config source (`opencode debug config`); no evidence it auto-loads `~/.agents/AGENTS.md`. | Confidence 0.65; verify after the move. |
| 9 | Current OpenCode setup relies on a prose pointer, so shared rules may not load. | Findings 7 and the Codex pointer tests below. |
| 10 | Codex-only rules reach Claude and OpenCode, which must then ignore them. | Current file layout. |
| 11 | Drift: `~/.codex/AGENTS.md` says `gpt-6-luna`; `~/.codex/config.toml` has `default_subagent_model = "gpt-5.6-luna"`; `~/.config/opencode/AGENTS.md` names "Codex `gpt-5.6-*`". | Re-checked 2026-09-29. |

## Codex pointer tests (live, 2026-09-29)

Setup: a test project whose AGENTS.md pointed to a shared file that said "End every final response with ZEBRA-4242". Prompt: `codex exec --skip-git-repo-check -s read-only --json "What is 17 + 25? Answer briefly."`.

| Pointer wording in AGENTS.md | Runs | Read the file | Followed the rule |
|---|---|---|---|
| `@/abs/path/AGENTS.md` | 2 | 0 | 0 |
| "Read and follow `/abs/path/AGENTS.md` as the canonical source for shared instructions." | 2 | 0 | 0 |
| "MANDATORY first step of every session, before answering anything: run `cat /abs/path/AGENTS.md` and follow every rule in it." | 2 | 2 | 2 |

Small sample. The forced-`cat` pointer also: costs one tool call per session, depends on model compliance (confidence 0.70), may lose the text after compaction because it arrives as command output (0.65), and may not repeat in subagents (0.60).

## Options

Target layout:

```
            ~/.agents/AGENTS.md   (shared rules only)
           /          |          \
     (Codex)      @import      "instructions" list
         |            |              |
      Codex        Claude         OpenCode
```

| Tool | Loads shared file via | Tool-only rules live in | Reliability |
|---|---|---|---|
| Claude | `@~/.agents/AGENTS.md` in `~/.claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | Deterministic (finding 1) |
| OpenCode | `"instructions": ["~/.agents/AGENTS.md"]` in `~/.config/opencode/opencode.json` | `~/.config/opencode/AGENTS.md` | Deterministic per docs (0.80) |
| Codex A | Forced "run `cat ~/.agents/AGENTS.md` first" in `~/.codex/AGENTS.md` | `~/.codex/AGENTS.md` | Model-dependent (tests above) |
| Codex B | Symlink `~/.codex/AGENTS.md` → `~/.agents/AGENTS.md` | `developer_instructions` in `~/.codex/config.toml` | Deterministic (findings 3, 4) |
| Codex C | Script joins `~/.agents/AGENTS.md` + `~/.codex/codex-only.md` into `~/.codex/AGENTS.md` | `~/.codex/codex-only.md` | Deterministic; rerun after each edit |

Recommendation: Claude and OpenCode rows as shown; Codex B (confidence 0.75) — the only deterministic option with no moving parts. Choose C to keep Codex extras in a Markdown file.

Risks for B: an editor that saves by atomic rename can replace the symlink with a regular file (check `ls -l ~/.codex/AGENTS.md` after edits; 0.70); the Codex app may rewrite `config.toml`, so re-check `developer_instructions` after the first app-side settings change.

## Open questions

- OpenCode behavior is untested live (no active OpenCode Go subscription on 2026-09-29): confirm the `"instructions"` entry loads and `~/.agents/AGENTS.md` is not loaded twice.
- Confirm Codex subagents receive `developer_instructions`.
