# Global Claude-rule hook audit

This file preserves the CartKing trace, original defect, and verification of
the replacement hook. Injected context proves only what the hook emitted, not
that Codex opened the referenced rule.

## Baseline wiring and matching logic

- **[verified | 1.00]** The original `/Users/preetamnath/.codex/hooks.json`
  registered `PreToolUse` and `PostToolUse` for Bash, plus `PostCompact`; all
  called `/Users/preetamnath/.codex/hooks/claude_rules.py`.
- **[verified | 1.00]** The baseline runtime was the 474-line installed file
  at `/Users/preetamnath/.codex/hooks/claude_rules.py`. The checked-in source
  now lives in this directory; installation is a separate copy-and-compare
  step.
- **[verified | 0.99]** The baseline discovered the nearest repository's
  `.claude/rules/*.md`, parsed `paths`, and matched resolved command tokens.
- **[verified | 0.99]** `extract_scopes` treated every shell token as a path.
  Bare wildcards became the current directory, whose root scope matched every
  rule. This caused the false injections.

## Three hook contracts

| Hook | Input and trigger | Output and exit behavior | Intended scope |
|---|---|---|---|
| `pre-tool-use` | `PreToolUse` event matched to `Bash`; JSON `cwd` plus `tool_input.command` | JSON `hookSpecificOutput.additionalContext` when a rule matches; otherwise no stdout. Baseline exceptions could escape and return `1`; the corrected source fails open with bounded stderr diagnostics and `0`. | Select scoped repository rules before a shell command. |
| `post-tool-use` | `PostToolUse` event matched to `Bash`; command/cwd plus `tool_response` | No stdout. Records a rule-content hash only after a recognizable rule read returns rule text. Baseline and corrected cleanup paths are non-blocking. | Prevent duplicate injections after a rule was actually read. |
| `post-compact` | Every `PostCompact` event; session/transcript identity | No stdout. Removes that session's hash state and exits `0` unless the process itself crashes. | Reset the per-session read ledger. |

**[verified | 0.99]** The baseline configuration was Bash-only. A structured
file-edit tool was not registered. The follow-up probe below establishes the
`apply_patch` event shape.

## Transcript reconstruction

The archived JSONL is
`/Users/preetamnath/.codex/sessions/2026/08/17/rollout-2026-08-17T10-02-08-01a00dfd-bd81-7c02-8b97-518fe8297ea5.jsonl`.
Each of its 15 emitted contexts contained all 22 discovered rule files.

| Context ordinals | Next Bash operation | Expected | Actual |
|---|---|---|---|
| 23 | Rule discovery | None: not an application target | All 22 rules |
| 218, 286, 330, 554 | SQLite research reads | None: targets only `meta/cartking-research/**` | All 22 rules |
| 346, 473, 573 | `git diff --check` | None: no target file | All 22 rules |
| 737, 744 | Research Markdown, SQLite, and screenshot checks | None: research paths only | All 22 rules |
| 828, 835, 896 | Screenshot copy and inventory | None: research paths only | All 22 rules |
| 1044 | Repository/global rule search | None: no application target | All 22 rules |
| 1051 | Rule-file read loop | None: no application target | All 22 rules |

**[verified | 1.00]** `app-shell-parity.md` and
`control-label-fallback.md` exclude `meta/cartking-research/**`; neither should
have fired. Bad target extraction created an over-broad root scope. The matcher
did not ignore valid rule globs.

## The observed exit-code-1 failure

- **[verified | 1.00]** The transcript reports `PreToolUse hook (failed): hook
  exited with code 1` at ordinal 959 without identifying the invocation.
- **[verified | 0.99]** Baseline replay produced 11 non-zero results from long
  SQLite commands; ordinal 280 is a minimal reproduction.
- **[verified | 1.00]** Ordinal 280 raised uncaught `OSError: [Errno 63] File
  name too long` at `resolved.is_file()`: the hook treated SQL as a path and
  lacked a top-level exception boundary.
- **[inferred | 0.86]** This is the likely cause of the transcript's reported
  failure because it reproduces the same event type and appears in the same
  research sequence. The exact failed command remains unproven from the
  transcript alone.

## Corrected design and verification

The replacement normalizes each supported tool into a `FileOperation` before
matching. It has no root fallback, checks glob intersection, and fails open
with bounded stderr diagnostics and exit code `0`. See [`README.md`](README.md)
for the current contract and coverage boundaries.

| Verification | Result |
|---|---|
| Package suite | **[verified | 1.00]** 28 tests passed, including match, no-match, multi-file, dynamic input, malformed input, and fail-open cases |
| Archived transcript replay | **[verified | 1.00]** All 126 Bash events replayed; zero rules matched |
| Live `apply_patch` event shape | **[verified | 1.00]** `tool_name` is `apply_patch`; `tool_input.command` contains the patch envelope |
| Scoped live patch | **[verified | 1.00]** A `.d.ts` add injected only `typescript-augmentations.md` |
| Research live patch | **[verified | 1.00]** A `meta/cartking-research/**` add injected no rules |
| Multi-file live cleanup | **[verified | 1.00]** Deleting both probe files injected only the `.d.ts` rule; both files were removed |
| Installed state | **[verified | 1.00]** Global PreToolUse matches `Bash|apply_patch`; installed source is byte-identical to the checked-in source |

The first fresh-session test also exposed an unknown-command false-positive:
`codex exec -C <repo>` treated its working directory as a target and selected
all rules. The final normalizer does not guess unknown commands' positional
semantics; known adapters and shell redirections remain supported.
