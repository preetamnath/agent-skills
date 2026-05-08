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

- **[agent-soul](skills/agent-soul/)** — Load a personality archetype that shapes the agent's voice (greetings, status, closings, pushback tone).
- **[audit-transcripts-for-learnings](skills/audit-transcripts-for-learnings/)** — Mine past transcripts in a chosen scope and date window for reusable patterns, then walk each one for promotion.
- **[fix-verify-loop](skills/fix-verify-loop/)** — Bounded resolver for confirmed P0/P1 findings: fix → verify → up to 2 attempts → escalate.
- **[grill-me](skills/grill-me/)** — Stress-test a plan, design, or decision by challenging assumptions and forcing specificity.
- **[interview-me](skills/interview-me/)** — Move from ambiguity to clarity before building.
- **[plan-builder](skills/plan-builder/)** — Produce dependency-ordered, wave-grouped markdown plans from a goal + context. Compatible with plan-runner.
- **[plan-runner](skills/plan-runner/)** — Execute wave-grouped markdown plans via parallel subagents, with per-wave review and final two-pass review. Resumable.
- **[post-purchase-ui-extension](skills/post-purchase-ui-extension/)** — SDK reference for the legacy `@shopify/post-purchase-ui-extensions-react` surface — 29 components, lifecycle, sandbox rules.
- **[sentry-analysis](skills/sentry-analysis/)** — Diagnose Sentry errors using logs, breadcrumbs, and codebase context.
- **[shopify-dev-mcp](skills/shopify-dev-mcp/)** — Routes Shopify Dev MCP tools for API lookups, GraphQL doc search, and code validation. Requires Shopify Dev MCP.
- **[sync-codex-agents](skills/sync-codex-agents/)** — Convert `agents/*.md` to Codex `.toml` and stage for install to `~/.codex/agents/`. Skips Claude-only MCP wrappers.
- **[two-pass-review](skills/two-pass-review/)** — Orchestrates a reviewer + verifier agent pair for high-confidence findings.

## Agents

- **[code-reviewer](agents/code-reviewer.md)** *(opus)* — Structured code review with P0–P3 findings and confidence scores.
- **[codex-code-review](agents/codex-code-review.md)** *(sonnet)* — Independent code review via Codex (OpenAI) MCP. Read-only.
- **[codex-propose-alternatives](agents/codex-propose-alternatives.md)** *(sonnet)* — Independent 2–3 alternative approaches via Codex MCP. Read-only.
- **[codex-sanity-checker](agents/codex-sanity-checker.md)** *(sonnet)* — Independent sanity-check of a plan or decision via Codex MCP. Read-only.
- **[propose-alternatives](agents/propose-alternatives.md)** *(opus)* — Propose 2–3 genuinely different approaches with trade-offs and a recommendation.
- **[reviewer](agents/reviewer.md)** *(opus)* — Reviews non-code artifacts (PRDs, plans, ACs, prose) against explicit criteria. P0–P3 findings.
- **[sanity-checker](agents/sanity-checker.md)** *(opus)* — Validate or challenge a plan, design, or decision. Surfaces blind spots.
- **[verifier](agents/verifier.md)** *(opus)* — Adversarial verification of `code-reviewer` / `reviewer` findings. Kills false positives.

## Sync agents to Codex

Codex uses `.toml`, not `.md` with frontmatter. The [sync-codex-agents](skills/sync-codex-agents/) skill converts the standalone agents and stages them for install at `~/.codex/agents/`.

Trigger: `sync codex agents`. The skill converts → diffs against existing → asks before installing. `codex-*` MCP wrappers are skipped (Claude-only). Requires Python 3.11+.

## Authoring

New skills go in `skills/`, new agents in `agents/`. Read [WRITING-GUIDE.md](WRITING-GUIDE.md) first — it covers naming, frontmatter, archetypes, templates, anti-patterns, and shared-schema propagation.

## License

[MIT](LICENSE.md)
