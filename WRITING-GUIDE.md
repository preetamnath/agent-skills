# Writing Guide

Authoring guidelines for skills (in `skills/`) and agents (in `agents/`).

**Skills are the default.** Skills auto-load into the main thread via their description. An agent only earns its place when isolation, parallel execution, or external delegation creates real value over a skill firing inline.

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

These apply equally to skills and agents. Archetype-specific overrides are noted in the Skills and Agents sections.

### Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Skill directory | `kebab-case`, verb-noun or noun phrase | `plan-builder`, `sentry-analysis` |
| Agent file | `kebab-case.md`, role noun, flat in `agents/` (no subdirectories, no companion files) | `code-reviewer.md`, `verifier.md` |
| `name` in frontmatter | Matches directory (skill) or filename without `.md` (agent) | `plan-builder`, `code-reviewer` |
| Schema types | `PascalCase` | `ReviewOutput`, `Finding` |
| Reference files | `kebab-case`, descriptive noun | `{schema-name}-schema.md`, `{surface}-catalog.md` |

### Frontmatter — shared fields

**`description`** — the harness uses this to route. Write it for matching, not for humans. Include what it does, when to use it, key synonyms, and negative conditions if needed for disambiguation. **Under 1000 characters** (hard limit is 1024 — the loader rejects any file with a longer description; budget the remaining 24 chars for safety). Don't list internal schema field names in parens — those don't route.

**`model`** (optional) — `opus` for cross-file reasoning, analysis, or architectural judgment; `sonnet` for routine I/O or external delegation wrappers. Skills omit for default (sonnet). Agents typically set it explicitly.

Archetype-specific fields (`tools`, `TRIGGER when:`) are documented in their respective sections below.

### Step heading pattern

Numbered steps with verb phrases: `### 1 — Read context`, `### 2 — Analyze`, `### N — Return output`. Never bare `### Step 1`.

### Rules formatting

Use `## Rules` for behavioral constraints (what the agent must/must not do). Each bullet:

```
- **Bold label.** Rule text. One concern per bullet.
```

Skills additionally use `## Constraints` for output constraints (severity ranges, field limits). When both exist: Rules first, then Constraints.

### Voice

- **Imperative.** "Read the file" not "The agent should read the file."
- **No soft language.** Cut "consider", "you might want to", "evaluate as needed". Use "Check for X", "Flag if Y", "Demote when Z".

### Spawn / invoke / load glossary

This vocabulary is load-bearing — mismatching the verb causes in-thread execution of work meant for a subagent.

| Verb | Means | Example |
|------|-------|---------|
| **spawn** the `<agent>` agent | Creates a new isolated subagent context | "Spawn the `code-reviewer` agent" |
| **load** / **invoke** the `<skill>` skill | Runs in-thread, in the current context | "Load the `plan-builder` skill" |

When delegating from a skill or agent body, choose the verb intentionally.

---

## Skills

### Archetypes

| Archetype | Section heading | Output |
|-----------|----------------|--------|
| **Structured output** — execute steps, return a schema | `## Instructions` | `## Output Schema` appendix, referenced by anchor |
| **File artifact** — interactive or procedural, writes a file | `## Protocol` | Inline markdown template in the writing step |
| **Orchestrator** — chains other skills in stages | `## Pipeline` | Reuses schemas from chained sub-skills |

### Frontmatter — skill-specific

**`TRIGGER when:` clause** (optional) — append to the description for skills with domain-specific vocabulary users may not say verbatim. Format: `TRIGGER when: {semicolon-separated conditions}`. Positive triggers only (negatives go in the base description). Focus on user-intent language, not domain terms already in the base description. Use patterns over enumeration (`<s-*>` not `s-button, s-card`). Under 25 words.

Example: `"...Not for checkout extensions. TRIGGER when: code contains <s-*> tags; user asks to build/update/fix UI in a Shopify app; user mentions cards, modals, or forms."`

### Templates

#### Structured output skill

````markdown
---
name: {skill-name}
description: "..."   # see Frontmatter
---

# {Display Name}

{1-2 sentences. What the skill does and the goal. Plain declarative — no "this skill will..."}

## When to use

{Brief entry conditions. Single sentence or tight bullet list.}
{Include explicit NOT conditions if commonly confused with another skill.}

## Instructions

### 1 — {Verb phrase}

{Instructions for step 1.}

### 2 — {Verb phrase}

{Instructions for step 2.}

### N — Return output

Return output conforming to the [Output Schema](#output-schema) below.

## Rules

- **{Bold label}.** {Rule text. One concern per bullet.}

---

## Output Schema

<!-- source: references/{schema-name}.md -->

{Full schema content inlined. Struct definitions, field notes, calibration tables.}
````

#### File artifact skill

````markdown
---
name: {skill-name}
description: "..."
---

# {Display Name}

{1-2 sentences. Plain declarative.}

## When to use

{Entry conditions.}

## Protocol

### 1 — {Verb phrase}

{Instructions.}

### N-1 — Confirm before writing

Present a brief summary to the user via the `AskUserQuestion` tool with options: "Looks good — write it", "Adjust before writing". Recommended: "Looks good — write it".

### N — Write artifact

Write to `meta/workflows/{type}/{type}-NNN-<topic-slug>.md`. Find the highest existing NNN in the directory, increment by 1 (start at 001 if empty). Tell the user the file path.

```markdown
## {Artifact Title}: [topic]

### Section
| Column | Column |
|---|---|
| ... | ... |
```

After writing, use the `AskUserQuestion` tool to offer next steps (e.g., "Proceed to plan-builder", "Done for now").

### End condition

Stop when: {explicit condition — e.g., "every load-bearing decision has a specific answer"}.

## Rules

- **{Bold label}.** {Rule text.}
````

#### Orchestrator skill

````markdown
---
name: {skill-name}
description: "..."
---

# {Display Name}

{1-2 sentences. Plain declarative.}

## When to use

YES: {conditions where this skill applies}
NO: {conditions where a simpler skill suffices}

## Pipeline

### Stage 1 — {Name}

Load the `{sub-skill-name}` skill.
Pass: {what input to provide}.
Receive: {what output to expect}.

**Checkpoint:** Present findings to user via the `AskUserQuestion` tool. Proceed only on approval.

### Stage 2 — {Name}

{Same pattern.}

## Shortcutting

Before applying any shortcut, confirm with the user via the `AskUserQuestion` tool.

| If... | Then skip to... |
|---|---|
| {condition} | Stage N |

## Constraints

- Orchestrators do NOT define their own output schema. Use the schemas from chained sub-skills.
- Every stage transition requires human approval via the `AskUserQuestion` tool.
````

### Writing skill steps

- **Name the `AskUserQuestion` tool explicitly.** Write "use the `AskUserQuestion` tool" — not "ask the user" or "ask before proceeding." Required for: orchestrator stage transitions; file-artifact pre/post-write checkpoints; structured-output ambiguity or missing inputs; all escalation paths. Always include structured options and a recommended choice. Not for genuinely open-ended questions with no enumerable answers.
- **Inline small templates where used.** If a step produces a markdown artifact, show the template inside that step in a fenced block.

### Appendix conventions

Everything below `---` is reference material. The agent reads the protocol first, then the appendix sections referenced by anchor links. The protocol references the appendix via anchor link, e.g., `[Output Schema](#output-schema)`. Add `<!-- source: references/{filename}.md -->` for shared schemas (see [Shared schema workflow](#shared-schema-workflow)).

### Large catalog exception

If a skill's catalog or reference material exceeds 300 lines, it lives in `references/` at the repo root. The SKILL.md instructions tell the agent to Read the file by its repo-root-relative path:

```markdown
### 1 — Load the catalog

Read `references/{filename}.md` for the full reference material.
```

Use repo-root `references/` when the material is **shared across multiple skills** or is a single large catalog file. Keep the SKILL.md protocol, rules, and any small schemas self-contained.

### Skill-owned references exception

A skill may keep `skills/{name}/references/` when **all** apply: material is owned by one skill (not shared); it's a multi-file catalog with standalone entries; the skill loads only one (or few) entries per session; the catalog would exceed the 300-line soft limit if inlined. Example: `skills/agent-soul/references/<archetype>.md` (38 archetypes, one per session).

When using this pattern: SKILL.md contains a catalog table (one line per entry); SKILL.md instructs the agent to read only the selected entry by path `references/{entry}.md` (or `${CLAUDE_SKILL_DIR}/references/{entry}.md` for a CWD-agnostic absolute path); entry files share a common schema documented in SKILL.md.

Do not use this pattern for schemas, small reference tables, content loaded every session (all inline in appendix), or material shared across skills (use repo-root `references/`).

### Skill anti-patterns

| Don't | Do instead |
|-------|-----------|
| `references/` subdirectory inside the skill folder for small material | Inline into SKILL.md appendix. The subdirectory pattern is only for skill-owned multi-file catalogs — see [Skill-owned references exception](#skill-owned-references-exception) |
| "Read `references/schema.md` to understand the format" | "Return output conforming to the [Output Schema](#output-schema) below" |
| Separate "Overview" or "Introduction" section | Lead paragraph after H1 covers this |
| "This skill will help you..." | "Validate a plan or decision." (imperative/declarative) |
| Schema definitions mid-protocol | Schema in appendix, referenced by anchor |
| Repeating the schema in multiple protocol steps | Define once in appendix, reference by anchor |
| Adding `## Overview`, `## Purpose`, `## Background` | Cut it. The lead paragraph + When to use is enough |
| Generic description: "A tool for reviewing code" | Trigger-rich: "Structured code review with P0-P3 findings, confidence scores, and criteria-based analysis" |
| Auto-proceeding between orchestrator pipeline stages | Every stage transition requires human approval via the `AskUserQuestion` tool |
| Defining a new output schema for an orchestrator | Reuse schemas from chained sub-skills |
| Describing sub-skill behavior inline in an orchestrator | Reference by name, document only what you pass and receive |
| "Stop and ask the user" or "ask before proceeding" (unnamed tool) | "Use the `AskUserQuestion` tool with options: ..." (structured, named) |

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

### Conventions

- **`## Input contract`** — required. Numbered fields with formats. If a required field is missing, ask before proceeding.
- **`## Rules`** — must include "structured output IS the response." No closing summary, no narrative.

### Agent anti-patterns

| Don't | Do instead |
|-------|-----------|
| Add an agent that auto-fires on a description trigger to write code inline | Make it a skill — skills auto-load into the main thread; agents are for isolation |
| Grant `Edit` or `Write` to a review or analysis agent | Read-only tools (`Read, Grep, Glob, Bash`) — review agents never write |
| Body that summarizes what the agent did at the end | Structured output IS the response — no closing summary |
| Vague input contract: "the caller provides context" | Numbered fields with formats: "1. **Artifact** — file path or diff range" |
| Re-define a shared schema instead of inlining from `references/` | Inline with `<!-- source: references/{filename}.md -->` and propagate per [Shared schema workflow](#shared-schema-workflow) |

---

## Shared schema workflow

Source of truth is `references/` at the repo root. This directory is repo-authoring SoT only — it is NOT installed alongside skills or agents, so every consumer must inline the content.

Update process:
1. Edit the file in `references/`.
2. Find all consumers: `grep -r "<!-- source: references/{filename} -->" skills/ agents/`.
3. Copy the updated content into each consumer's appendix.
4. Commit all changes together.

Git handles version history — no version suffixes in filenames.
