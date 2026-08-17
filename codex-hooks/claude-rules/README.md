# Global Claude-rule matching hook

This package is the source of truth for the global Codex hook that injects only
the repository-local `.claude/rules/*.md` instructions matching a tool's
explicit target files.

## Contract

Before a tool runs, the hook maps explicit repository paths to rule `paths`
frontmatter:

```text
Codex hook payload
  -> tool-specific path normalizer
  -> exact reads, writes, directories, and safe glob prefixes
  -> nearest Git repository
  -> .claude/rules/**/*.md with supported `paths` frontmatter
  -> exact path / directory / glob intersection
  -> matching rule instructions only
```

Matching follows these rules:

- **Rule discovery:** Walk the nearest repository's `.claude/rules/` without
  following directory symlinks. Accept only Markdown files with supported,
  non-empty `paths` frontmatter.
- **Path boundary:** Normalize tool input before matching. Never treat regexes,
  SQL, bare wildcards, shell variables, or patch-body text as paths.
- **No target:** Emit no context when no explicit supported path exists.
- **Compound operations:** Union every explicit supported path, even when
  another part of the operation is dynamic.

## Hook contracts

The current global configuration is represented by
[`hooks.example.json`](hooks.example.json).

| Hook | Trigger | Input | Output | Exit behavior |
|---|---|---|---|---|
| `pre-tool-use` | `PreToolUse` events matched to `Bash|apply_patch` | JSON containing `cwd`, `tool_name`, and `tool_input.command` | One JSON `hookSpecificOutput.additionalContext` containing only new matching rule paths; no output on no match | Always `0`; failures are reported to stderr and fail open |
| `post-tool-use` | `PostToolUse` events matched to `Bash` | The command/cwd plus `tool_response` | No stdout; updates per-session rule-read state | Always `0`; state or parse failures do not block the tool |
| `post-compact` | Every `PostCompact` event | Session/transcript identity | No stdout; removes that session's hash state | Always `0`; cleanup failures do not block the session |

All three hooks key state by `transcript_path`, then `session_id`. PostToolUse
records a rule hash only when a recognized read returns every substantive rule
line in order. Injecting a rule path does not prove Codex opened that rule.

## Coverage

| Covered | Behavior |
|---|---|
| Known Bash readers | Explicit operands for commands such as `cat`, `sed`, `rg`, `grep`, `find`, `file`, SQLite clients, and Git pathspec operations |
| Known Bash writers | Explicit sources and destinations for commands such as `cp`, `mv`, `install`, `ln`, `mkdir`, `rm`, `tee`, `touch`, redirections, and `sed -i` |
| `apply_patch` | Paths declared by `Add File`, `Update File`, `Delete File`, and `Move to` headers; supports multi-file patches |
| Matching | Exact files, directories, safe path-prefixed globs, and the union of multi-file or compound operations |
| No match or failure | No context for unsupported, outside-repository, malformed, or target-free input; internal failures report a bounded diagnostic and exit `0` |

| Deliberately not covered | Reason |
|---|---|
| Other structured tools | Add an adapter only after capturing the tool's live `tool_name` and `tool_input` shape |
| Unknown commands' positional operands | Their path semantics are not safely guessable; shell redirection targets remain supported |
| Runtime-generated paths | Variables, command substitution, loops, scripts, and `xargs` can hide the final path until execution |
| Activity outside Codex tools | The hook sees only registered Codex hook events |

## Install on another Codex computer

After pulling this repository, point Codex to this file:

```text
Read codex-hooks/claude-rules/README.md and install this global hook on this
computer. Preserve unrelated hooks, use this computer's absolute paths, run
the documented tests, verify the installed copy, and tell me when to restart
Codex and trust the hooks.
```

The installing agent must:

1. Run the unit tests from this directory.
2. Create `~/.codex/hooks/` if needed, then copy `claude_rules.py` there.
3. Merge exactly one of each registration from `hooks.example.json` into
   `~/.codex/hooks.json`. Preserve unrelated hooks and resolve `~` to this
   computer's absolute home path in each command.
4. Validate `hooks.json` as JSON and verify the installed script byte-for-byte:

```sh
python3 -m json.tool ~/.codex/hooks.json >/dev/null
cmp -s claude_rules.py ~/.codex/hooks/claude_rules.py
```

5. Restart Codex and trust the hooks. In a repository with scoped
   `.claude/rules`, run one matching and one no-match live probe, then remove
   both files. If none is available, report that live verification was skipped.

Keep the installed script byte-identical to this checked-in source. After the
registration exists, source-only updates require only the copy, comparison,
and restart steps.

## Verify

Run the portable suite from this directory:

```sh
python3 -m unittest discover -s tests -p 'test*.py'
```

The external transcript test skips when its local archive is absent. Replay
the original CartKing regression without executing its commands:

```sh
python3 replay_transcript.py \
  --repo-root /Users/preetamnath/Desktop/code/OakPostPurchase \
  /Users/preetamnath/.codex/sessions/2026/08/17/rollout-2026-08-17T10-02-08-01a00dfd-bd81-7c02-8b97-518fe8297ea5.jsonl \
  --expect-no-matches
```

The replay parses JSONL without executing transcript commands. The archived
session contains 126 completed Bash events and must match no Oak application
rule. Use `--json` for machine-readable output and `--verbose` for every event.
See [`AUDIT.md`](AUDIT.md) for the trace reconstruction, root cause, and live
verification results.
