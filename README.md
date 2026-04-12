# Agent Skills

A collection of skills and agents for AI coding agents to help with specialized engineering tasks.

Built by [Preetam Nath](https://github.com/preetamnath).

## Available Skills

| Skill | Description |
|-------|-------------|
| [code-review](skills/code-review/) | Structured code review with P0-P3 findings, confidence scores, and criteria-based analysis. |
| [diagnose-review-fix-orchestrator](skills/diagnose-review-fix-orchestrator/) | End-to-end pipeline for uncertain bugs: diagnose root cause, review the fix, then verify and harden. Chains parallel-diagnosis → two-pass-review → fix-loop. |
| [fix-loop](skills/fix-loop/) | Bounded fix-and-verify protocol for resolving findings from a review. Max 2 attempts per finding, adaptive verification, escalates to user on failure. |
| [git-commit-message](skills/git-commit-message/) | Generate git commit messages in a specific bullet-point format with a conventional header. |
| [grill-me](skills/grill-me/) | Stress-test a plan, design, or decision by challenging assumptions, exposing gaps, and forcing specificity. |
| [interview-me](skills/interview-me/) | Move from ambiguity to clarity before building. |
| [parallel-diagnosis](skills/parallel-diagnosis/) | Parallel independent root-cause diagnosis for uncertain bugs. Two agents investigate independently, then converge on a unified diagnosis. |
| [plan-builder](skills/plan-builder/) | Creates dependency-ordered, wave-grouped executable plans from a goal + context. Produces markdown plans with parallel execution waves compatible with plan-runner. |
| [plan-runner](skills/plan-runner/) | Executes wave-grouped markdown plans via parallel subagents. Orchestrates implementation, per-wave review, fix cycles, and final two-pass-review. Resumable across conversations. |
| [polaris-web-components](skills/polaris-web-components/) | Polaris web component catalog and rules for the polaris-app-home surface. |
| [propose-alternatives](skills/propose-alternatives/) | Propose 2-3 genuinely different approaches to a problem with concrete trade-offs. |
| [sanity-check](skills/sanity-check/) | Validate or challenge a plan, design, or decision. Confirms what's good, flags concerns and blind spots. |
| [sentry-analysis](skills/sentry-analysis/) | Analyze Sentry error logs, breadcrumbs, and codebase context to diagnose and explain the root cause of issues. |
| [shopify-dev-mcp](skills/shopify-dev-mcp/) | Routes Shopify Dev MCP tools for API lookups, GraphQL doc search, and code validation. Requires Shopify Dev MCP. |
| [two-pass-review](skills/two-pass-review/) | Orchestrates a reviewer + verifier agent pair for high-confidence review findings. |

## Agents

Agent definitions that pair with skills above. These are **not** installable via `npx skills` — copy manually (see below).

| Agent | Model | Description |
|-------|-------|-------------|
| [reviewer](agents/reviewer.md) | opus | Reviews artifacts against explicit criteria. Produces structured P0-P3 findings. |
| [verifier](agents/verifier.md) | opus | Adversarial verification of reviewer findings. Kills false positives. |
| [codex-review](agents/codex-review.md) | sonnet | Independent second opinion from Codex (OpenAI) via MCP. Modes: code-review, propose-alternatives, sanity-check. Read-only. |
| [codex-execute](agents/codex-execute.md) | sonnet | Delegate implementation to Codex (OpenAI) via MCP. Codex writes code, self-reviews via a separate read-only call, and fixes P0/P1 findings — up to 2 cycles. |
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

Codex uses `.toml` agent definitions, not raw markdown. Ask Codex to convert the agent `.md` file to its `.toml` format:

```
Convert agents/reviewer.md to a Codex .toml agent definition
```

### Updating

```bash
npx skills update
```

## Usage

Once installed, your agent will automatically detect and use these skills when relevant to your tasks. You can also invoke them explicitly — for example, in Claude Code, type `/interview-me` to start an interview.

## License

[MIT](LICENSE.md)
