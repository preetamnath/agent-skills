# Agent Skills

A collection of skills and agents for AI coding agents to help with specialized engineering tasks.

Built by [Preetam Nath](https://github.com/preetamnath).

## Quick Start

Install via [skills.sh](https://skills.sh/) — a package manager for AI agent skills:

```bash
npx skills add preetamnath/agent-skills
```

During install you'll be prompted to choose which coding agents to install for (Claude Code, Gemini CLI, Cursor, etc.) and whether to install globally or per-project.

## Available Skills

| Skill | Description |
|-------|-------------|
| [agent-soul](skills/agent-soul/) | Load a personality archetype that shapes the agent's voice — greetings, status, closings, pushback tone — while keeping plans, diffs, and recommendations neutral. |
| [code-review](skills/code-review/) | Structured code review with P0-P3 findings, confidence scores, and criteria-based analysis. |
| [fix-verify-loop](skills/fix-verify-loop/) | Bounded resolver for confirmed P0/P1 findings. For each finding: fix → verify resolution via the verifier agent → up to 2 attempts → escalate. Scoped to per-finding resolution; regressions are the caller's job. |
| [git-commit-message](skills/git-commit-message/) | Generate git commit messages in a specific bullet-point format with a conventional header. |
| [grill-me](skills/grill-me/) | Stress-test a plan, design, or decision by challenging assumptions, exposing gaps, and forcing specificity. |
| [interview-me](skills/interview-me/) | Move from ambiguity to clarity before building. |
| [plan-builder](skills/plan-builder/) | Creates dependency-ordered, wave-grouped executable plans from a goal + context. Produces markdown plans with parallel execution waves compatible with plan-runner. |
| [plan-runner](skills/plan-runner/) | Executes wave-grouped markdown plans via parallel subagents. Orchestrates implementation, per-wave review, fix cycles, and final two-pass-review. Resumable across conversations. |
| [polaris-app-home-app-bridge](skills/polaris-app-home-app-bridge/) | Shopify App Bridge surface for Polaris App Home — `useAppBridge` hook, all `shopify.*` APIs, and App Bridge web components (`<s-app-nav>`, `<s-app-window>`, `<form data-save-bar>`). |
| [polaris-app-home-page-patterns](skills/polaris-app-home-page-patterns/) | Polaris App Home page templates (Homepage, Index, Details, Settings) and compositions (Empty state, Setup guide, Callout card, etc.) — index of named patterns. |
| [polaris-app-home-web-components](skills/polaris-app-home-web-components/) | Polaris `<s-*>` web component catalog for the Admin App Home surface — pages, sections, buttons, modals, tables, forms, layout. |
| [post-purchase-extension](skills/post-purchase-extension/) | Post-purchase UI extension SDK reference — 29 React components, lifecycle, and sandbox rules for the legacy `@shopify/post-purchase-ui-extensions-react` SDK (distinct from the modern `polaris-checkout-extensions` surface). |
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
| [sanity-check](agents/sanity-check.md) | opus | Validate or challenge a plan, design, or decision. Confirms what's good, flags concerns and blind spots. |
| [propose-alternatives](agents/propose-alternatives.md) | opus | Propose 2-3 genuinely different approaches to a problem with concrete trade-offs. |
| [shopify-polaris-app-home-developer](agents/shopify-polaris-app-home-developer.md) | opus | Shopify Admin App Home: Polaris `<s-*>` web components, App Bridge APIs (`useAppBridge`, `shopify.*`), and GraphQL (Admin / Storefront / Customer). Loads polaris-app-home-* skills + shopify-dev-mcp. |
| [shopify-post-purchase-extension-developer](agents/shopify-post-purchase-extension-developer.md) | opus | Shopify legacy post-purchase upsell extensions (`@shopify/post-purchase-ui-extensions-react`, package in maintenance). Validates with `tsc` + WebFetch — MCP validator rejects this surface. Loads post-purchase-extension + shopify-dev-mcp. |

## Installation

### Install a specific skill

Pass `--skill` (or `-s`) with one or more skill names from the table above:

```bash
npx skills add preetamnath/agent-skills --skill agent-soul
npx skills add preetamnath/agent-skills --skill agent-soul code-review
```

List available skills in this repo without installing:

```bash
npx skills add preetamnath/agent-skills --list
```

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
