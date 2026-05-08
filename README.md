# Agent Skills

A collection of skills and agents for AI coding agents to help with specialized engineering tasks. Built by [Preetam Nath](https://github.com/preetamnath).

## Quickstart

Install all skills:

```bash
npx skills add preetamnath/agent-skills
```

Install specific skills (multiple OK):

```bash
npx skills add preetamnath/agent-skills --skill <name>
```

List available skills without installing:

```bash
npx skills add preetamnath/agent-skills --list
```

Powered by [skills.sh](https://skills.sh/).

Agents are not installable via `npx skills`. Copy manually:

```bash
cp agents/*.md ~/.claude/agents/
```

Or paste this prompt into your AI coding agent to install them:

```
Install the agent definitions from https://github.com/preetamnath/agent-skills/tree/main/agents into ~/.claude/agents/ (create the directory if it doesn't exist). Fetch every .md file from that directory and write it to ~/.claude/agents/<same-filename>.md verbatim. After installing, list the agents you installed.
```

For Codex (`~/.codex/agents/`), use the [sync-codex-agents](skills/sync-codex-agents/) skill — it converts the standalone agents to `.toml` and stages them for install.

## Skills

- **[agent-soul](skills/agent-soul/)** — Load a personality archetype that shapes the agent's voice — greetings, status, closings, pushback tone — while keeping plans, diffs, and recommendations neutral.
- **[audit-transcripts-for-learnings](skills/audit-transcripts-for-learnings/)** — Audit past transcripts in a chosen scope and date window to extract reusable patterns, then walk through each one for promotion.
- **[fix-verify-loop](skills/fix-verify-loop/)** — Bounded resolver for confirmed P0/P1 findings. For each finding: fix → verify resolution via the verifier agent → up to 2 attempts → escalate. Scoped to per-finding resolution; regressions are the caller's job.
- **[grill-me](skills/grill-me/)** — Stress-test a plan, design, or decision by challenging assumptions, exposing gaps, and forcing specificity.
- **[interview-me](skills/interview-me/)** — Move from ambiguity to clarity before building.
- **[plan-builder](skills/plan-builder/)** — Creates dependency-ordered, wave-grouped executable plans from a goal + context. Produces markdown plans with parallel execution waves compatible with plan-runner.
- **[plan-runner](skills/plan-runner/)** — Executes wave-grouped markdown plans via parallel subagents. Orchestrates implementation, per-wave review, fix cycles, and final two-pass-review. Resumable across conversations.
- **[post-purchase-ui-extension](skills/post-purchase-ui-extension/)** — Post-purchase UI extension SDK reference — 29 React components, lifecycle, and sandbox rules for the legacy `@shopify/post-purchase-ui-extensions-react` SDK (distinct from the modern `polaris-checkout-extensions` surface).
- **[sentry-analysis](skills/sentry-analysis/)** — Analyze Sentry error logs, breadcrumbs, and codebase context to diagnose and explain the root cause of issues.
- **[shopify-dev-mcp](skills/shopify-dev-mcp/)** — Routes Shopify Dev MCP tools for API lookups, GraphQL doc search, and code validation. Requires Shopify Dev MCP.
- **[sync-codex-agents](skills/sync-codex-agents/)** — Convert this repo's Claude agents (`agents/*.md`) to Codex `.toml` format, stage in `.tmp/codex-agents/`, then offer to install into `~/.codex/agents/`. Skips Claude-only MCP wrappers. Requires Python 3.11+.
- **[two-pass-review](skills/two-pass-review/)** — Orchestrates a reviewer + verifier agent pair for high-confidence review findings.

## Agents

- **[code-reviewer](agents/code-reviewer.md)** *(opus)* — Structured code review with P0-P3 findings and confidence scores. Reviews code changes, PRs, or specific files.
- **[reviewer](agents/reviewer.md)** *(opus)* — Reviews non-code artifacts (PRDs, plans, test results, ACs, prose) against explicit criteria. Produces P0-P3 findings.
- **[verifier](agents/verifier.md)** *(opus)* — Adversarial verification of `code-reviewer` / `reviewer` findings. Kills false positives.
- **[sanity-checker](agents/sanity-checker.md)** *(opus)* — Validate or challenge a plan, design, or decision. Confirms strengths, flags realistic concerns, surfaces blind spots.
- **[propose-alternatives](agents/propose-alternatives.md)** *(opus)* — Propose 2-3 genuinely different approaches with concrete trade-offs and a recommendation.
- **[codex-code-review](agents/codex-code-review.md)** *(sonnet)* — Independent code review from Codex (OpenAI) via MCP. Returns structured P0–P3 findings. Read-only.
- **[codex-sanity-checker](agents/codex-sanity-checker.md)** *(sonnet)* — Independent sanity-check from Codex (OpenAI) via MCP. Validates a plan, design, or decision. Returns P0–P2 findings. Read-only.
- **[codex-propose-alternatives](agents/codex-propose-alternatives.md)** *(sonnet)* — Independent proposal of 2–3 different approaches from Codex (OpenAI) via MCP. Read-only.

## License

[MIT](LICENSE.md)
