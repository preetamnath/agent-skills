# Agent Skills

A collection of skills and agents for AI coding agents to help with specialized engineering tasks.

Built by [Preetam Nath](https://github.com/preetamnath).

## Available Skills

| Skill | Description |
|-------|-------------|
| [adversarial-consensus](skills/adversarial-consensus/) | Multi-agent pattern for producing airtight fixes. Parallel independent diagnosis, consensus synthesis, adversarial critique, then hardened solution. |
| [code-review](skills/code-review/) | Structured code review with P0-P3 findings, confidence scores, and criteria-based analysis. |
| [fix-loop](skills/fix-loop/) | Bounded fix-and-verify protocol for resolving findings from a review. Max 2 attempts per finding, escalates on failure. |
| [git-commit-message](skills/git-commit-message/) | Generate git commit messages in a specific bullet-point format with a conventional header. |
| [grill-me](skills/grill-me/) | Stress-test a plan, design, or decision by challenging assumptions, exposing gaps, and forcing specificity. |
| [interview-me](skills/interview-me/) | Move from ambiguity to clarity before building. Interview the user until you could confidently hand off to be built. |
| [plan-builder](skills/plan-builder/) | Create dependency-ordered executable plans from a goal + context. Produces markdown checkbox plans. |
| [plan-runner](skills/plan-runner/) | Execute markdown plan files with checkbox items sequentially. Resumable across conversations. |
| [polaris-web-components](skills/polaris-web-components/) | Polaris web component catalog and rules for the Shopify App Home surface. Requires Shopify Dev MCP. |
| [propose-alternatives](skills/propose-alternatives/) | Propose 2-3 genuinely different approaches to a problem with concrete trade-offs and confidence scores. |
| [sanity-check](skills/sanity-check/) | Validate or challenge a plan, design, or decision. Flags realistic concerns and blind spots. |
| [sentry-analysis](skills/sentry-analysis/) | Analyze Sentry error logs, breadcrumbs, and codebase context to diagnose and explain root causes. |
| [shopify-dev-mcp](skills/shopify-dev-mcp/) | Routes Shopify Dev MCP tools for API lookups, GraphQL doc search, and code validation. Requires Shopify Dev MCP. |
| [two-pass-review](skills/two-pass-review/) | Orchestrates a reviewer + verifier agent pair for high-confidence review findings. |

## Agents

Agent definitions that pair with skills above. These are **not** installable via `npx skills` — copy manually (see below).

| Agent | Model | Description |
|-------|-------|-------------|
| [reviewer](agents/reviewer.md) | opus | Reviews artifacts against explicit criteria. Produces structured P0-P3 findings. |
| [verifier](agents/verifier.md) | opus | Adversarial verification of reviewer findings. Kills false positives. |
| [codex](agents/codex.md) | sonnet | Independent second opinion from Codex (OpenAI) via MCP. Modes: code-review, propose-alternatives, sanity-check. |
| [shopify-developer](agents/shopify-developer.md) | opus | Shopify features: Polaris web components, GraphQL, checkout extensions. Loads polaris-web-components + shopify-dev-mcp skills. |

## Installation

Install skills via [skills.sh](https://skills.sh/) — a package manager for AI agent skills.

```bash
npx skills add preetamnath/agent-skills
```

During install you'll be prompted to choose which coding agents to install for (Claude Code, Gemini CLI, Cursor, etc.) and whether to install globally or per-project.

### Agents (manual)

Claude Code:
```bash
cp agents/*.md ~/.claude/agents/
```

Codex:
```bash
cp agents/*.md ~/.codex/agents/
```

### Updating

```bash
npx skills update
```

## Usage

Once installed, your agent will automatically detect and use these skills when relevant to your tasks. You can also invoke them explicitly — for example, in Claude Code, type `/interview-me` to start an interview.

## License

[MIT](LICENSE.md)
