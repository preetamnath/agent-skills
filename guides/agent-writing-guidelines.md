# Agent Writing Guidelines

> **Skills are the default.** Read `guides/skill-writing-guidelines.md` first. An agent only earns its place when isolation, parallel execution, or external delegation creates real value over a skill firing inline.

## When to add an agent

| Need | Build a... |
|------|-----------|
| Inline code authoring or reference loading | **Skill** (auto-trigger via description) |
| Adversarial second pass over another agent's output | **Standalone agent** with read-only tools |
| Background research that would pollute main context | **Standalone agent** with read-only tools |
| Parallel structured analysis across N artifacts | **Standalone agent** (caller fans out) |
| Delegating to an external tool/service (Codex MCP, etc.) | **External-delegation agent** |

## Naming

Agents are flat `.md` files in `agents/`. No subdirectories, no companion files.

| Element | Convention | Example |
|---------|-----------|---------|
| File name | `kebab-case.md`, role noun | `code-reviewer.md`, `verifier.md`, `sanity-checker.md` |
| `name` in frontmatter | Matches file name (without `.md`) | `code-reviewer` |

## Agent archetypes

| Archetype | Output | Example |
|-----------|--------|---------|
| **Standalone** — own logic and schema, runs in isolation | Own schema (often a shared one inlined from `references/`) | `code-reviewer`, `sanity-checker`, `propose-alternatives`, `reviewer`, `verifier` |
| **External delegation** — wraps an external tool/service | Delegated tool's response, returned verbatim | `codex-code-review`, `codex-sanity-checker`, `codex-propose-alternatives` |

## Standalone agent template

```markdown
---
name: {agent-name}
description: "..."   # see Frontmatter section
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
```

Canonical examples: `agents/code-reviewer.md`, `agents/sanity-checker.md`, `agents/reviewer.md`, `agents/verifier.md`. A separate `## Output format` heading before `## Rules` is also acceptable when output discipline needs more than one line — see `agents/reviewer.md`.

## External delegation agent template

Same structure as standalone, plus:
- The wrapped tool's transport in `tools:` (e.g., `mcp__codex__codex`).
- An `## Execution steps` section that constructs the MCP call from the input contract and inlined Output Schema, then returns the response verbatim.
- Invariants for the wrapped tool (sandbox mode, approval policy, session handling) listed in `## Rules`.

Canonical example: `agents/codex-code-review.md`. MCP conventions live in `references/codex-mcp-conventions.md`.

## Frontmatter

| Field | Notes |
|-------|-------|
| `name` | Matches the file name. |
| `description` | Used by the harness to route. What the agent does, when to spawn it, what it does NOT do. **Under 1000 characters** (hard limit is 1024 — the loader rejects any agent file with a longer description; budget the remaining 24 chars for safety). Don't list internal schema field names in parens — those don't route. |
| `model` | `opus` for analysis or architectural judgment; `sonnet` for routine I/O or external delegation wrappers. |
| `tools` | Minimum read tools. Never grant `Edit` or `Write` to review/analysis agents. Add MCP transports for external-delegation agents. |

## Conventions

- **`## Input contract`** — required. Numbered fields with formats. If a required field is missing, ask before proceeding.
- **`## Rules`** — must include "structured output IS the response." No closing summary, no narrative.
- **Shared schemas.** When inlining a schema from `references/`, mark it with `<!-- source: references/{filename}.md -->` so the propagation grep in `CLAUDE.md` finds it.
- **"spawn" vs "load".** "Spawn the `<agent>` agent" creates a new isolated context. "Load the `<skill>` skill" runs in-thread. Mismatching the verb causes in-thread execution of work meant for a subagent.

## Anti-patterns

| Don't | Do instead |
|-------|-----------|
| Add an agent that auto-fires on a description trigger to write code inline | Make it a skill — skills auto-load into the main thread; agents are for isolation |
| Grant `Edit` or `Write` to a review or analysis agent | Read-only tools (`Read, Grep, Glob, Bash`) — review agents never write |
| Body that summarizes what the agent did at the end | Structured output IS the response — no closing summary |
| Soft language: "consider", "you might want to", "evaluate as needed" | Direct: "Check for X", "Flag if Y", "Demote when Z" |
| Delegate to a subagent without using "spawn" | "Spawn the `<agent>` agent" — explicit verb prevents in-thread execution |
| Vague input contract: "the caller provides context" | Numbered fields with formats: "1. **Artifact** — file path or diff range" |
| Re-define a shared schema instead of inlining from `references/` | Inline with `<!-- source: references/{filename}.md -->` and propagate per `CLAUDE.md` |
