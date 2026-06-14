# Agent Skills

A collection of skills, agents, and commands for AI coding agents. Built by [Preetam Nath](https://github.com/preetamnath).

## Quickstart

Install all skills:

```bash
npx skills add preetamnath/agent-skills
```

Install specific skills:

```bash
npx skills add preetamnath/agent-skills --skill <skillname1> <skillname2>
```

List available skills without installing:

```bash
npx skills add preetamnath/agent-skills --list
```

Powered by [skills.sh](https://skills.sh/).

Agents are not installable via `npx skills`. Paste this prompt into your AI coding agent to install them:

```
Install the agent definitions from https://github.com/preetamnath/agent-skills/tree/main/agents into ~/.claude/agents/ (create the directory if it doesn't exist). Fetch every .md file from that directory and write it to ~/.claude/agents/<same-filename>.md verbatim. After installing, list the agents you installed.
```

For Codex (`~/.codex/agents/`), use the [sync-codex-agents](commands/sync-codex-agents/) command.

## Skills

- **[agent-soul](skills/agent-soul/)** — Load a personality archetype that shapes the agent's voice (greetings, status, closings, pushback tone).
- **[audit-transcripts-for-learnings](skills/audit-transcripts-for-learnings/)** — Mine past transcripts in a chosen scope and date window for reusable patterns, then walk each one for promotion.
- **[durable-docs-update](skills/durable-docs-update/)** — After a coding task or plan, audit code comments and durable docs (CLAUDE.md, ARCHITECTURE.md, .claude/rules) for the changed files; propose scoped adds/updates the user approves.
- **[execute-plan](skills/execute-plan/)** — Execute a wave-grouped `plan.md` via parallel subagents: per-wave review with a decision-drift check, fix-verify cycles, a final review, user-gated promotion of AC-affecting discoveries to the spec, and a ship gate. Resumable.
- **[explain-deeply](skills/explain-deeply/)** — Build the user's mental model: ground in source-of-truth, walk top-down with diagrams as the spine. Not for diagnoses or actions.
- **[fix-verify-loop](skills/fix-verify-loop/)** — Bounded resolver for confirmed P0/P1 findings: fix → verify → up to 2 attempts → escalate.
- **[grill-me](skills/grill-me/)** — Stress-test a plan, design, or decision by challenging assumptions and forcing specificity.
- **[handoff](skills/handoff/)** — Compress the live conversation into minimal, copy-paste-ready handoff prompt(s) — one self-contained prompt per thread, context referenced by file path rather than pasted — so a fresh chat picks up cleanly.
- **[interview-me](skills/interview-me/)** — Socratically interview the user to clarity on any open question (decision, strategy, trade-off, refactor, research) — general scope, not a buildable feature — then write a summary to `meta/interviews/`.
- **[multi-agent-analysis](skills/multi-agent-analysis/)** — Divergent analysis: parallel subagents each apply a distinct lens to an in-progress artifact, scoring findings by impact and confidence; synthesize into a table and walk one at a time. The exploratory sibling of `panel-review`.
- **[panel-review](skills/panel-review/)** — Multi-reviewer panel (R0 + two parallel subagents) on N focused questions about a near-final artifact; walks decisions one at a time.
- **[place-fact](skills/place-fact/)** — The PLACE lens: route a kept fact to its durable home by delivery trigger and most-local-wins (in-file comment, nested CLAUDE.md, path-scoped rule, root CLAUDE.md, ARCHITECTURE.md, or a skill).
- **[post-purchase-ui-extension](skills/post-purchase-ui-extension/)** — SDK reference for the legacy `@shopify/post-purchase-ui-extensions-react` surface — 29 components, lifecycle, sandbox rules.
- **[product-interview](skills/product-interview/)** — Move from ambiguity to clarity on WHAT to build (product + UX) via a Socratic interview, then write the decision-locked `spec.md` — the feature's build contract.
- **[refine-file](skills/refine-file/)** — Audit one instruction file by composing the durable-instruction lenses (vet-fact / place-fact / tighten-instruction); cut, move, or tighten each fact on approval. Single-file sibling of durable-docs-update.
- **[second-opinion](skills/second-opinion/)** — Anchored critique of a concrete proposal: rate the fix, generate ranked alternatives, flag blind spots, synthesize back.
- **[sentry-analysis](skills/sentry-analysis/)** — Diagnose Sentry errors using logs, breadcrumbs, and codebase context.
- **[shopify-dev-mcp](skills/shopify-dev-mcp/)** — Routes Shopify Dev MCP tools for API lookups, GraphQL doc search, and code validation. Requires Shopify Dev MCP.
- **[tech-design](skills/tech-design/)** — Turn a locked product/UX spec into the HOW: gather load-bearing constraints, then append technical decisions and a verified Structure Outline to the spec.
- **[tighten-file](skills/tighten-file/)** — File-level tightening pass on an instruction file (CLAUDE.md, skill, agent prompt) using `tighten-instruction` as the lens at whole-file, section, and instruction levels.
- **[tighten-instruction](skills/tighten-instruction/)** — Collapse a multi-clause line (command or fact) in a skill, CLAUDE.md, agent prompt, or rule into one positive line that reads cold.
- **[two-pass-review](skills/two-pass-review/)** — Orchestrates a reviewer + verifier agent pair for high-confidence findings.
- **[vet-fact](skills/vet-fact/)** — The WORTH lens: judge whether a candidate fact earns a durable-doc line — keep only what a future agent would get wrong without; cut anything derivable, setup, breadcrumb, or restated default.
- **[write-plan](skills/write-plan/)** — Sequence a locked spec and its Structure Outline into dependency-ordered, wave-grouped tasks — creates `plan.md` for execute-plan; every task cites the AC-N it satisfies and D-NN it honors.

## Agents

- **[code-reviewer](agents/code-reviewer.md)** — Structured code review with P0–P3 findings and confidence scores.
- **[propose-alternatives](agents/propose-alternatives.md)** — Propose 2–3 genuinely different approaches with trade-offs and a recommendation.
- **[reviewer](agents/reviewer.md)** — Reviews non-code artifacts (PRDs, plans, ACs, prose) against explicit criteria. P0–P3 findings.
- **[sanity-checker](agents/sanity-checker.md)** — Validate or challenge a plan, design, or decision. Surfaces blind spots.
- **[verifier](agents/verifier.md)** — Adversarial verification of `code-reviewer` / `reviewer` findings. Kills false positives.

### Codex MCP wrappers

Bridge from Claude to OpenAI's Codex via MCP for an independent second opinion. Read-only.

- **[codex-code-review](agents/codex-code-review.md)** — Independent code review via Codex (OpenAI) MCP.
- **[codex-propose-alternatives](agents/codex-propose-alternatives.md)** — Independent 2–3 alternative approaches via Codex MCP.
- **[codex-sanity-checker](agents/codex-sanity-checker.md)** — Independent sanity-check of a plan or decision via Codex MCP.

## Commands

User-invoked slash commands. Install by copying the `.md` file into `~/.claude/commands/<name>.md` (or `.claude/commands/` for project-scoped).

- **[memory-prune](commands/memory-prune/)** — Review project memories and recommend which to promote into a durable doc, rule, command, or skill; confirms before applying.
- **[seed-claude-context](commands/seed-claude-context/)** — Seed a layered Claude-context surface (root CLAUDE.md, nested CLAUDE.md, `.claude/rules/`, living ARCHITECTURE.md) across a repo via parallel mapping, planning, wave drafting, and review. Works with or without a reference repo.
- **[sync-codex-agents](commands/sync-codex-agents/)** — Convert `agents/*.md` to Codex `.toml` and stage for install at `~/.codex/agents/`. Skips Claude-only MCP wrappers. Requires Python 3.11+.

## Authoring

New skills go in `skills/`, new agents in `agents/`, new commands in `commands/`. Read [WRITING-GUIDE.md](WRITING-GUIDE.md) first — it covers naming, frontmatter, archetypes, templates, anti-patterns, and shared-schema propagation.

## License

[MIT](LICENSE.md)
