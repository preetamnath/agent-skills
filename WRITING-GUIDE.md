# Writing Guide

Field notes from skills and agents written so far — a synthesis that grows as we learn. Hard constraints (loader limits, schema sync, anchor conventions) are flagged; treat the rest as patterns, not law.

## Decision: skill or agent?

| Need | Build a... |
|------|-----------|
| Inline code authoring or reference loading | **Skill** (auto-trigger via description) |
| Adversarial second pass over another agent's output | **Standalone agent** with read-only tools |
| Background research that would pollute main context | **Standalone agent** with read-only tools |
| Parallel structured analysis across N artifacts | **Standalone agent** (caller fans out) |
| Delegating to an external tool/service (Codex MCP, etc.) | **External-delegation agent** |

---

## Common conventions

### Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Skill directory | `kebab-case`, verb-noun or noun phrase | `plan-builder`, `sentry-analysis` |
| Agent file | `kebab-case.md`, role noun, flat in `agents/` | `code-reviewer.md`, `verifier.md` |
| `name` in frontmatter | Matches directory (skill) or filename without `.md` (agent) | `plan-builder`, `code-reviewer` |
| Schema types | `PascalCase` | `ReviewOutput`, `Finding` |
| Reference files | `kebab-case`, descriptive noun | `{schema-name}-schema.md`, `{surface}-catalog.md` |
| Step headings | `### N — Verb phrase` | `### 1 — Read context`, `### N — Return output` |

### Frontmatter — shared fields

- **`description`** — routing text **under 1000 chars** (loader hard limit 1024). Cover: what it does, when to use, synonyms, disambiguating negatives. Skip internal schema field names.
- **`model`** (agents) — `opus` for cross-file or architectural reasoning; `sonnet` for routine I/O or delegation wrappers. Skills typically omit (defaults to sonnet).

Behavioral constraints go under `## Rules` as `- **Bold label.** Rule text.` bullets. Skills with output limits (severity ranges, field caps) add `## Constraints` after.

---

## Skills

### Archetypes

| Archetype | Section heading | Output |
|-----------|----------------|--------|
| **Structured output** — execute steps, return a schema | `## Instructions` | `## Output Schema` appendix, referenced by anchor |
| **File artifact** — interactive or procedural, writes a file | `## Protocol` | Inline markdown template in the writing step |
| **Orchestrator** — chains other skills in stages | `## Pipeline` | Reuses schemas from chained sub-skills |

### Frontmatter — skill-specific

**`TRIGGER when:`** (optional, ~25 words) — semicolon-separated positive conditions in user-intent language. Use patterns over enumeration (`<s-*>` not `s-button, s-card`). Put negatives and domain terms in the base description.

Example: `"...Not for checkout extensions. TRIGGER when: code contains <s-*> tags; user asks to build/update/fix UI in a Shopify app; user mentions cards, modals, or forms."`

### Typical shell

````markdown
---
name: {skill-name}
description: "..."
---

# {Display Name}

{1-2 plain declarative sentences.}

## When to use

{Brief entry conditions. Include explicit NOT conditions if commonly confused with another skill. Skip if the description's TRIGGER/SKIP already covers it.}

## {Archetype-specific section — see deltas below}

### 1 — {Verb phrase}

{Step body.}

### N — {Verb phrase}

{Step body.}

## Rules

- **{Bold label}.** {One concern per bullet.}
````

Archetype deltas:

#### Structured output

- Main section `## Instructions`; final step returns the schema by anchor: `### N — Return output conforming to the [Output Schema](#output-schema) below.`
- Append `---` then `## Output Schema` with `<!-- source: references/{schema-name}.md -->` and inlined schema content. The anchor `#output-schema` is load-bearing — keep it lowercased and hyphenated.
- Canonical example: `skills/sentry-analysis/SKILL.md`.

#### File artifact

- Main section `## Protocol`. Typical penultimate step confirms before writing (`AskUserQuestion` with "Looks good — write it" / "Adjust before writing"); final step writes the artifact, reports the path, and offers next steps via `AskUserQuestion`.
- Inline the markdown template inside the write step as a fenced block.
- Canonical examples: `skills/plan-builder/SKILL.md`, `skills/interview-me/SKILL.md`.

#### Orchestrator

- Main section `## Pipeline`. Stages: `### Stage N — {Name}` with sub-skill load + input/output + a checkpoint via `AskUserQuestion`.
- Orchestrators don't define their own output schema — they reuse the schemas of the sub-skills they chain.
- `## When to use` often uses `YES: {conditions} / NO: {conditions}` format. An optional `## Shortcutting` table can map conditions to skip-to-stages (require `AskUserQuestion` before applying any shortcut).
- Canonical example: `skills/tighten-file/SKILL.md`.

### References

Place inline reference material below `---` and link from the protocol via anchor (e.g., `[Output Schema](#output-schema)`). For shared schemas, add `<!-- source: references/{filename}.md -->` and follow the [Shared schema workflow](#shared-schema-workflow).

| Material | Location | Use when |
|----------|----------|----------|
| Schema or small reference (< 300 lines) | Inline in SKILL.md appendix | Default |
| Shared across multiple skills, or single catalog > 300 lines | Repo-root `references/` | See [Shared schema workflow](#shared-schema-workflow) |
| Multi-file catalog owned by one skill, loaded one entry per session | `skills/{name}/references/` | Catalog would exceed 300 lines if inlined |

Skill-owned references: SKILL.md contains a catalog table; the agent reads only the selected entry (`references/{entry}.md`, or `${CLAUDE_SKILL_DIR}/references/{entry}.md` for a CWD-agnostic absolute path).

### Skill anti-patterns

| Don't | Do instead |
|-------|-----------|
| "Read `references/schema.md` to understand the format" | "Return output conforming to the [Output Schema](#output-schema) below" |
| `## Overview`, `## Purpose`, `## Background`, or "Introduction" section | Cut. Lead paragraph + When to use is enough |
| "This skill will help you..." | "Validate a plan or decision." (imperative/declarative) |
| Schema mid-protocol or repeated across steps | Define once in appendix, reference by anchor |
| Defining a new output schema for an orchestrator | Reuse schemas from chained sub-skills |
| Describing sub-skill behavior inline in an orchestrator | Reference by name, document only what you pass and receive |

---

## Agents

### Archetypes

| Archetype | Output | Example |
|-----------|--------|---------|
| **Standalone** — own logic and schema, runs in isolation | Own schema (often a shared one inlined from `references/`) | `code-reviewer`, `sanity-checker`, `propose-alternatives`, `reviewer`, `verifier` |
| **External delegation** — wraps an external tool/service | Delegated tool's response, returned verbatim | `codex-code-review`, `codex-sanity-checker`, `codex-propose-alternatives` |

### Frontmatter — agent-specific

**`tools`** — minimum read tools. Review/analysis agents shouldn't have `Edit` or `Write`. External-delegation agents add MCP transports (e.g., `mcp__codex__codex`).

### Typical shape

#### Standalone agent

````markdown
---
name: {agent-name}
description: "..."
model: opus
tools: Read, Grep, Glob, Bash
---

You are a {role}. {One sentence stating what the agent does — second person.}

## Input contract

The caller provides:
1. **{Field}** — {what it is, format, where to find it}
2. **{Field}** — {...}
3. **{Field}** (optional) — {...}

If {required field} is missing or vague, ask before proceeding.

## How you work

### 1 — {Verb phrase}

{Step body.}

### N — Return output

Return a `{SchemaName}` envelope conforming to the [Output Schema](#output-schema) below.

## Rules

- **{Bold label}.** {One concern per bullet.}
- **Structured output.** Don't produce a summary or narrative. The structured output IS the response.

---

## Output Schema

<!-- source: references/{schema-name}.md -->

{Full schema content inlined.}
````

Canonical examples: `agents/code-reviewer.md`, `agents/sanity-checker.md`, `agents/reviewer.md`, `agents/verifier.md` (see `agents/reviewer.md` for a `## Output format` variant).

#### External delegation agent

Same structure as standalone, plus:

- The wrapped tool's transport in `tools:` (e.g., `mcp__codex__codex`).
- An `## Execution steps` section that constructs the MCP call from the input contract and inlined Output Schema, then returns the response verbatim.
- Invariants for the wrapped tool (sandbox mode, approval policy, session handling) in `## Rules`.

Canonical example: `agents/codex-code-review.md`. MCP conventions live in `references/codex-mcp-conventions.md`.

### Agent anti-patterns

| Don't | Do instead |
|-------|-----------|
| Body that summarizes what the agent did at the end | Structured output IS the response — no closing summary |
| Vague input contract: "the caller provides context" | Numbered fields with formats: "1. **Artifact** — file path or diff range" |

---

## Shared schema workflow

`references/` at the repo root is the source of truth, but is not installed with skills/agents — every consumer must inline the content. Skipping the sync causes silent schema drift.

Update process:
1. Edit the file in `references/`.
2. Find all consumers: `grep -r "source: references/{filename}" skills/ agents/`.
3. Copy the updated content into each consumer's appendix.
4. Commit all changes together.
