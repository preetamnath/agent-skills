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

Codex versions are checked in under [`agents-codex/`](agents-codex/). Copy them to a project's `.codex/agents/` or your `~/.codex/agents/` directory, and use the [sync-codex-agents](commands/sync-codex-agents/) command after changing a source agent.

## Provider integrations

- **[opencode-plugins/](opencode-plugins/)** — Reusable OpenCode 2 plugins that bridge provider-native lifecycle events to canonical hooks.

## Shared scripts

- **[validate-agent-delivery.mjs](scripts/validate-agent-delivery.mjs)** — Check any repository's canonical instruction and project-skill delivery; usage is in the [canonical delivery guide](guides/canonical-agent-delivery.md#check-delivery).

## Skills

- **[agent-soul](skills/agent-soul/)** — Load a personality archetype that shapes the agent's voice (greetings, status, closings, pushback tone).
- **[audit-transcripts-for-learnings](skills/audit-transcripts-for-learnings/)** — Mine past transcripts in a chosen scope and date window for reusable patterns, then walk each one for promotion; also counts how often a skill ran.
- **[best-answer](skills/best-answer/)** — Build the single strongest answer to one open question: a diverse panel of subagents attacks it, a clean-room `judge` maps their agreement and disagreement, then you synthesize one grounded answer. Convergent sibling of `find-gaps`.
- **[compress-file](skills/compress-file/)** — Compress one instruction file to the leanest structure that still delivers its purpose: dissolve sections that restate others, fold unique survivors into the section that governs them, prove no instruction lost. Structural sibling of `tighten-file`.
- **[deep-modules](skills/deep-modules/)** — The deep-module primitive (small interface, lots of behaviour): apply the lens to judge or shape one interface, or audit a codebase for shallow modules (delegates the fan-out to `multi-agent-analysis`, returns a ranked table). Loaded by `tech-design`.
- **[design-critique](skills/design-critique/)** — Critique already-built UI from screenshots, agree on the most useful review directions, and return ranked fixes supported by evidence without silently redesigning it.
- **[durable-docs-update](skills/durable-docs-update/)** — After coding work, sweep comments in changed files and sync only related durable guidance through WORTH → PLACE → SHAPE.
- **[execute-chat](skills/execute-chat/)** — Execute chat-agreed work through readiness, dependency-ordered build waves, review, automated and live verification, durable docs, an automatic scoped commit, and repository-defined close-out; track every stage in a task ledger.
- **[execute-plan](skills/execute-plan/)** — Execute a wave-grouped `plan.md` via parallel subagents: per-wave review with a decision-drift check, fix-verify cycles, a final review with a conditional project-test run, user-gated promotion of AC-affecting discoveries to the spec, a durable-docs pass, then the ship gate that freezes it. Resumable.
- **[explain-deeply](skills/explain-deeply/)** — Explain a feature, flow, or concept: read the source of truth, lead with the answer, and diagram each idea the answer depends on — concise, no walls of text. Not for diagnoses or actions.
- **[explain-simply](skills/explain-simply/)** — Re-explain your last response in the simplest language.
- **[find-gaps](skills/find-gaps/)** — Surface what an in-progress artifact is missing: parallel subagents each apply a different lens, scoring findings by impact and confidence; the uncertain ones pass through `triage` before you walk them one at a time. Divergent sibling of `validate-answer`.
- **[fix-verify-loop](skills/fix-verify-loop/)** — Bounded resolver for confirmed P0/P1 findings: fix → verify → up to 2 attempts → escalate.
- **[generate-mockups](skills/generate-mockups/)** — Generate UI mockups as one-file HTML, no build, grounded in the project's real design language: PREVIEW a feature's screens or states, or COMPARE 2+ visual directions to pick one. Fidelity follows the toolkit — high when it loads, approximate when it can't.
- **[grill-me](skills/grill-me/)** — Stress-test a plan, design, or decision by challenging assumptions and forcing specificity.
- **[handoff](skills/handoff/)** — Compress the live conversation into minimal, copy-paste-ready handoff prompt(s), referencing context by path instead of pasting it, so a fresh chat picks up cleanly.
- **[interview-me](skills/interview-me/)** — Socratically interview the user to clarity on any open question (decision, strategy, trade-off, refactor, research) — general scope, not a buildable feature — then write a summary to `meta/interviews/`.
- **[jtbd](skills/jtbd/)** — Frame a vague goal as the job to be done — when [situation], I want to [motivation], so I can [outcome], without [constraint] — then judge every option by job-fit. A lens you pull into any chat.
- **[map-design-language](skills/map-design-language/)** — Research a project's design language with parallel agents and write or refresh a lean `meta/DESIGN.md` of facts — surfaces, toolkits, tokens, styling models, docs pointers — that grounds mockups and new UI.
- **[memory-prune](skills/memory-prune/)** — Keep memory-native records, route guidance, state, and evidence from project memory to canonical owners, then trim or delete absorbed sources.
- **[multi-agent-analysis](skills/multi-agent-analysis/)** — Dispatch 1–3 subagents to analyze or verify something, then judge their findings yourself and present a confidence-scored answer to decide on. Read-only.
- **[place-fact](skills/place-fact/)** — Route guidance, state, or evidence already worth keeping to one canonical owner and the narrowest reliable delivery boundary.
- **[post-purchase-ui-extension](skills/post-purchase-ui-extension/)** — SDK reference for the legacy `@shopify/post-purchase-ui-extensions-react` surface — 29 components, lifecycle, sandbox rules.
- **[product-interview](skills/product-interview/)** — Move from ambiguity to clarity on WHAT to build (product + UX) via a Socratic interview, then write the decision-locked `spec.md` — the feature's build contract.
- **[refine-file](skills/refine-file/)** — Audit one current-guidance instruction file for worth, placement, and clarity; apply high-confidence edits, hold weaker proposals, then prove the result cold.
- **[second-opinion](skills/second-opinion/)** — Anchored critique of a concrete proposal: route to a stress test, ranked alternatives, or both, then synthesize back.
- **[sentry-analysis](skills/sentry-analysis/)** — Diagnose Sentry errors using logs, breadcrumbs, and codebase context.
- **[shopify-dev-mcp](skills/shopify-dev-mcp/)** — Routes Shopify Dev MCP tools for API lookups, GraphQL doc search, and code validation. Requires Shopify Dev MCP.
- **[structure-prose](skills/structure-prose/)** — Reshape one prose block into a labeled list or table when it fuses several independent rules — content verbatim, apply at confidence 0.75 or above when called directly; a connected chain of reasoning stays prose.
- **[tech-design](skills/tech-design/)** — Turn a locked product/UX spec into the HOW: gather load-bearing constraints, then append technical decisions and a verified Structure Outline to the spec.
- **[test-completed-plan](skills/test-completed-plan/)** — Drive a shipped spec's Post-ship verification checklist — the human-gated ACs the diff can't prove — to live pass/fail across three tiers (unit/frontend, real authenticated app, server-log/DB); rules out env before routing bugs to `fix-verify-loop`. The testing phase after `execute-plan`.
- **[tighten-file](skills/tighten-file/)** — Tighten an instruction file at whole-file, section, and instruction levels; apply independent edits at confidence 0.75 or above, hold weaker proposals, then prove the result cold.
- **[tighten-instruction](skills/tighten-instruction/)** — Make an instruction line read cold: clarify it into plain words, tighten each distinct instruction or fact to one positive line, and apply at confidence 0.75 or above when called directly.
- **[tldr](skills/tldr/)** — Respond in one sentence, or up to the number you specify — works mid-message or to compress a wall of text. Length sibling of `explain-simply`.
- **[triage](skills/triage/)** — Verify a panel's contested findings: fan out one independent checker per finding, each returning a consider / skip verdict and a confidence.
- **[trim-spec](skills/trim-spec/)** — Trim a bloated spec, ADR set, or design doc to what a builder needs without losing a fact: a mechanical `restated_at` inventory by parallel agents, a cheapest-first cut, then an adversarial loss pass by a fresh agent. The sibling of `compress-file` for multi-section docs that carry a decision record; in the spec pipeline it sits between a locked spec and `write-plan`.
- **[two-pass-review](skills/two-pass-review/)** — Orchestrates a reviewer + verifier agent pair for high-confidence findings.
- **[validate-answer](skills/validate-answer/)** — Trust-check an answer or a few focused decisions with multiple identical independent reads; agreement signals confidence, splits flag what's contested. Convergent sibling of `find-gaps`.
- **[vet-fact](skills/vet-fact/)** — Judge whether a current-guidance fact earns a durable instruction line: keep only what prevents a likely wrong answer; cut derivable, historical, setup, or default restatements.
- **[write-plan](skills/write-plan/)** — Sequence a locked spec and its Structure Outline into dependency-ordered, wave-grouped tasks — creates `plan.md` for execute-plan; every task cites the AC-NNN-XX it satisfies and D-NNN-XX it honors.

## Agents

- **[code-reviewer](agents/code-reviewer.md)** — Reviews code changes, PRs, or files for correctness, security, edge cases, and bugs. P0–P3 findings.
- **[propose-alternatives](agents/propose-alternatives.md)** — Proposes 2–4 genuinely different approaches with trade-offs and a recommendation.
- **[reviewer](agents/reviewer.md)** — Reviews non-code artifacts (PRDs, plans, ACs, prose) against explicit criteria. P0–P3 findings.
- **[sanity-checker](agents/sanity-checker.md)** — Validates or challenges a plan, design, or decision. Surfaces blind spots.
- **[verifier](agents/verifier.md)** — Verifies `code-reviewer` / `reviewer` findings adversarially. Kills false positives.

## Commands

User-invoked slash commands. Install by copying the `.md` file into `~/.claude/commands/<name>.md` (or `.claude/commands/` for project-scoped).

- **[seed-claude-context](commands/seed-claude-context/)** — Seed or migrate canonical, boundary-scoped repository guidance while preserving correct artifacts and deriving each delivery view from one owner.
- **[sync-codex-agents](commands/sync-codex-agents/)** — Sync `agents/*.md` to checked-in `agents-codex/*.toml`. Requires Python 3.11+.

## Guides

- **[Canonical agent delivery](guides/canonical-agent-delivery.md)** — Keep repository instructions and project skills on one canonical write path with relative provider symlinks and shared delivery validation.
- **[Root `AGENTS.md` writing guide](guides/root-AGENTSmd-writing-guide.md)** — Write and maintain a lean canonical repository briefing and task router with derived provider delivery.

## Authoring

New skills go in `skills/`, new agents in `agents/`, new commands in `commands/`. Read [WRITING-GUIDE.md](WRITING-GUIDE.md) first — it covers naming, frontmatter, archetypes, templates, anti-patterns, and shared-schema propagation.

## License

[MIT](LICENSE.md)
