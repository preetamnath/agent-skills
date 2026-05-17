# Writing Guide

Skills are the default; build an agent only for isolation, parallel execution, or external delegation.

## Decision: skill or agent?

| Need | Build a... |
|------|-----------|
| Inline code authoring or reference loading | **Skill** (auto-trigger via description) |
| Adversarial second pass over another agent's output | **Standalone agent** with read-only tools |
| Background research that would pollute main context | **Standalone agent** with read-only tools |
| Parallel structured analysis across N artifacts | **Standalone agent** (caller fans out) |
| Delegating to an external tool/service (Codex MCP, etc.) | **External-delegation agent** |

Throughout this guide: **spawn** an `<agent>` (new isolated context); **load** or **invoke** a `<skill>` (in-thread).

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

**`description`** — routing text. Include: what it does, when to use, synonyms, negatives for disambiguation. **Under 1000 characters** (loader hard limit 1024). Omit internal schema field names — they don't route.

**`model`** (optional) — `opus` for cross-file reasoning, analysis, or architectural judgment; `sonnet` for routine I/O or external delegation wrappers. Skills omit (defaults to sonnet); agents set it explicitly.

### Rules and Constraints

Use `## Rules` for behavioral constraints, with bullets `- **Bold label.** Rule text. One concern per bullet.` Skills add `## Constraints` after Rules for output limits (severity ranges, field caps).

### Voice

- **Imperative.** "Read the file" not "The agent should read the file."
- **Prefer firm verbs.** Default to "Check for X", "Flag if Y", "Demote when Z" over "consider", "you might want to", or "evaluate as needed".

---

## Skills

### Archetypes

| Archetype | Section heading | Output |
|-----------|----------------|--------|
| **Structured output** — execute steps, return a schema | `## Instructions` | `## Output Schema` appendix, referenced by anchor |
| **File artifact** — interactive or procedural, writes a file | `## Protocol` | Inline markdown template in the writing step |
| **Orchestrator** — chains other skills in stages | `## Pipeline` | Reuses schemas from chained sub-skills |

### Frontmatter — skill-specific

**`TRIGGER when:` clause** (optional) — append to the description for skills with domain-specific vocabulary users may not say verbatim. Format: `TRIGGER when: {semicolon-separated conditions}`. Positive triggers only, in user-intent language; put negatives and domain terms in the base description. Use patterns over enumeration (`<s-*>` not `s-button, s-card`). Aim for ~25 words.

Example: `"...Not for checkout extensions. TRIGGER when: code contains <s-*> tags; user asks to build/update/fix UI in a Shopify app; user mentions cards, modals, or forms."`

### Templates

Include `## When to use` only when entry conditions don't fit in the description's TRIGGER/SKIP.

All skill templates share this shell:

````markdown
---
name: {skill-name}
description: "..."   # see Frontmatter
---

# {Display Name}

{1-2 sentences. Plain declarative — no "this skill will..."}

## When to use

{Brief entry conditions. Include explicit NOT conditions if commonly confused with another skill.}

## {Archetype-specific section — see deltas below}

### 1 — {Verb phrase}

{Step body.}

### N — {Verb phrase}

{Step body.}

## Rules

- **{Bold label}.** {Rule text. One concern per bullet.}
````

Archetype deltas:

#### Structured output

- Main section: `## Instructions`. Final step: `### N — Return output conforming to the [Output Schema](#output-schema) below.`
- Append `---` then `## Output Schema` with `<!-- source: references/{schema-name}.md -->` and inlined schema content.
- Canonical example: `skills/sentry-analysis/SKILL.md`.

#### File artifact

- Main section: `## Protocol`. Include `### N-1 — Confirm before writing` (use `AskUserQuestion` with "Looks good — write it" / "Adjust before writing") and `### N — Write artifact`.
- Write to `meta/workflows/{type}/{type}-NNN-<topic-slug>.md` (increment NNN from highest existing; start at 001). Tell the user the file path. After writing, use `AskUserQuestion` to offer next steps.
- Inline the markdown template inside the write step as a fenced block; no `## Output Schema` appendix.
- Optional `### End condition` ("Stop when: {condition}") before `## Rules`.
- Canonical examples: `skills/plan-builder/SKILL.md`, `skills/interview-me/SKILL.md`.

#### Orchestrator

- Main section: `## Pipeline`. Stages: `### Stage N — {Name}` with `Load the {sub-skill} skill. / Pass: {input}. / Receive: {output}. / **Checkpoint:** Present findings via AskUserQuestion. Proceed only on approval.`
- `## When to use` uses `YES: {conditions} / NO: {conditions}` format.
- Optional `## Shortcutting` table mapping conditions to skip-to-stages; require `AskUserQuestion` before applying any shortcut.
- Replace `## Rules` with `## Constraints`. Standard constraints: "Orchestrators do NOT define their own output schema — use the schemas from chained sub-skills." and "Every stage transition requires human approval via `AskUserQuestion`."
- Canonical example: `skills/tighten-file/SKILL.md`.

### Writing skill steps

- **Naming and options for `AskUserQuestion`.** Write "use the `AskUserQuestion` tool" (not "ask the user") with enumerated options and a recommended choice. Skip only for open-ended questions with no enumerable answers.
- **Inline small templates where used.** If a step produces a markdown artifact, show the template inside that step in a fenced block.

### References

Place inline reference material below `---` and link from the protocol via anchor (e.g., `[Output Schema](#output-schema)`). Add `<!-- source: references/{filename}.md -->` for shared schemas (see [Shared schema workflow](#shared-schema-workflow)).

| Material | Location | Use when |
|----------|----------|----------|
| Schema or small reference (< 300 lines) | Inline in SKILL.md appendix | Default |
| Shared across multiple skills, or single catalog > 300 lines | Repo-root `references/` | Update via [Shared schema workflow](#shared-schema-workflow) |
| Multi-file catalog owned by one skill, loaded one entry per session | `skills/{name}/references/` | Catalog would exceed 300 lines if inlined; entries share a common schema documented in SKILL.md. Example: `skills/agent-soul/references/<archetype>.md` |

For repo-root `references/`, SKILL.md tells the agent to Read by repo-root-relative path:

```markdown
### 1 — Load the catalog

Read `references/{filename}.md` for the full reference material.
```

For skill-owned `references/`, SKILL.md contains a catalog table (one line per entry) and tells the agent to read only the selected entry by `references/{entry}.md` (or `${CLAUDE_SKILL_DIR}/references/{entry}.md` for a CWD-agnostic absolute path).

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

**`tools`** — minimum read tools. Never grant `Edit` or `Write` to review/analysis agents. Add MCP transports for external-delegation agents (e.g., `mcp__codex__codex`).

### Templates

#### Standalone agent

````markdown
---
name: {agent-name}
description: "..."   # see Frontmatter
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

### 2 — {Verb phrase}

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

Canonical examples: `agents/code-reviewer.md`, `agents/sanity-checker.md`, `agents/reviewer.md`, `agents/verifier.md`. A separate `## Output format` heading before `## Rules` is also acceptable when output discipline needs more than one line — see `agents/reviewer.md`.

#### External delegation agent

Same structure as standalone, plus:
- The wrapped tool's transport in `tools:` (e.g., `mcp__codex__codex`).
- An `## Execution steps` section that constructs the MCP call from the input contract and inlined Output Schema, then returns the response verbatim.
- Invariants for the wrapped tool (sandbox mode, approval policy, session handling) listed in `## Rules`.

Canonical example: `agents/codex-code-review.md`. MCP conventions live in `references/codex-mcp-conventions.md`.

### Agent anti-patterns

| Don't | Do instead |
|-------|-----------|
| Body that summarizes what the agent did at the end | Structured output IS the response — no closing summary |
| Vague input contract: "the caller provides context" | Numbered fields with formats: "1. **Artifact** — file path or diff range" |

---

## Shared schema workflow

`references/` at the repo root is the source of truth, but is not installed with skills/agents — every consumer must inline the content.

Update process:
1. Edit the file in `references/`.
2. Find all consumers: `grep -r "<!-- source: references/{filename} -->" skills/ agents/`.
3. Copy the updated content into each consumer's appendix.
4. Commit all changes together.
