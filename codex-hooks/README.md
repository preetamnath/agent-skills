# Codex hooks

Reusable global Codex hook implementations live here. The current package is
[`claude-rules/`](claude-rules/), which matches repository files against
`.claude/rules` path scopes, injects only applicable rule context, and replays
archived Codex transcripts for regression checks.

- [`claude-rules/README.md`](claude-rules/README.md) — implementation contract, hook registration, install, and tests.
- [`claude-rules/AUDIT.md`](claude-rules/AUDIT.md) — evidence from the original CartKing transcript and the corrected design.
