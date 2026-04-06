# Agents

Agent definitions for Claude Code. These are **not** installable via `npx skills` — they must be manually copied to `~/.claude/agents/`.

## Installation

```bash
cp agents/*.md ~/.claude/agents/
```

## Available Agents

| Agent | Model | Description |
|-------|-------|-------------|
| [reviewer](reviewer.md) | opus | Reviews artifacts against explicit criteria. Produces structured P0-P3 findings. Pairs with the `two-pass-review` skill. |
| [verifier](verifier.md) | opus | Adversarial verification of reviewer findings. Kills false positives. Run after a reviewer pass. |
| [codex](codex.md) | sonnet | Thin wrapper for Codex (OpenAI) via MCP. Makes `mcp__codex__codex` calls and returns raw results. Requires the Codex MCP server to be configured. |

## Usage

Agents are spawned by skills or by you directly:

- **reviewer + verifier** are orchestrated by the `two-pass-review` skill
- **codex** is invoked when you need a second opinion — run via `Agent` tool with `subagent_type: "codex"`
