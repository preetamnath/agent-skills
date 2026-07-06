# Writing Guide

Patterns for authoring skills and agents. Hard rules — break the loader, build, or schema sync if violated — are marked 🔒; treat everything else as a default, not law.

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
| Skill directory | `kebab-case`, verb-noun or noun phrase | `write-plan`, `sentry-analysis` |
| Agent file | `kebab-case.md`, role noun, flat in `agents/` | `code-reviewer.md`, `verifier.md` |
| `name` in frontmatter | Matches directory (skill) or filename without `.md` (agent) | `write-plan`, `code-reviewer` |
| Schema types | `PascalCase` | `ReviewOutput`, `Finding` |
| Reference files | `kebab-case`, descriptive noun | `{schema-name}-schema.md`, `{surface}-catalog.md` |
| Step headings | `### Step N — Verb phrase` | `### Step 1 — Read context`, `### Step N — Return output` |

🔒 `name` must match the directory (skill) or filename (agent) exactly, or the loader can't resolve it — every other row here is style.

### Frontmatter — shared fields

- 🔒 **`description`** — the loader hard-limits this at 1024 chars and drops the rest; keep it under 1000 for headroom. Cover: what it does, when to use, synonyms, disambiguating negatives. Skip internal schema field names.
- **`model`** (agents) — `opus` for cross-file or architectural reasoning; `sonnet` for routine I/O or delegation wrappers. Skills typically omit (defaults to sonnet).

Behavioral constraints go under `## Rules` as `- **Bold label.** Rule text.` bullets. Skills with output limits (severity ranges, field caps) add `## Constraints` after.

### Tables

Default to the minimum column set — drop any column that restates or is derivable from an adjacent one, and put short qualifiers inline. A single-value column (confidence, 🔒, severity) isn't redundancy — keep it.

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

**Description shape.** `{what it does}. TRIGGER when: {phrases the user says}; {one condition}.` Add a negative only to disambiguate a confusable sibling. Mechanics, artifacts, preconditions, and any "Use when…" restatement belong in the body — not the description.

### Typical shell

````markdown
---
name: {skill-name}
description: "..."
---

# {Display Name}

{1-2 plain sentences — optional; add only when the step headings don't already orient the reader.}

## When to use

{Brief entry conditions. Include explicit NOT conditions if commonly confused with another skill. Skip if the description's TRIGGER/SKIP already covers it.}

## {Archetype-specific section — see deltas below}

### Step 1 — {Verb phrase}

{Step body.}

### Step N — {Verb phrase}

{Step body.}

## Rules

- **{Bold label}.** {One concern per bullet.}
````

Per-archetype deltas from the base template above:

#### Structured output

- Main section `## Instructions`; final step returns the schema by anchor: `### Step N — Return output conforming to the [Output Schema](#output-schema) below.`
- Append `---` then `## Output Schema` with `<!-- source: references/{schema-name}.md -->` and inlined schema content. 🔒 The `#output-schema` anchor and `## Output Schema` heading are grep/link contracts — keep the exact text and lowercase-hyphenated casing, or `[Output Schema](#output-schema)` references break.
- Canonical example: `skills/sentry-analysis/SKILL.md`.

#### File artifact

- Main section `## Protocol`. Typical penultimate step confirms before writing (`AskUserQuestion` with "Looks good — write it" / "Adjust before writing"); final step writes the artifact, reports the path, and offers next steps via `AskUserQuestion`.
- Inline the markdown template inside the write step as a fenced block.
- Canonical examples: `skills/write-plan/SKILL.md`, `skills/product-interview/SKILL.md`.

#### Orchestrator

- Main section `## Pipeline`. Stages: `### Stage N — {Name}` with an explicit Skill-tool call to load the dependency (see [Loading a dependency skill](#loading-a-dependency-skill)) + input/output + a checkpoint via `AskUserQuestion`.
- Orchestrators reuse their chained sub-skills' schemas instead of defining their own.
- `## When to use` often uses `YES: {conditions} / NO: {conditions}` format. An optional `## Shortcutting` table can map conditions to skip-to-stages (require `AskUserQuestion` before applying any shortcut).
- Canonical example: none in-repo — the fan-out panel skills (`tighten-file`, `validate-answer`, `find-gaps`) chain sub-skills but use the `## Steps` panel shape, not `## Pipeline`.

#### Loading a dependency skill

A dependency skill loads only via an explicit Skill-tool call. A bare name in prose leaves loading to model discretion; an inline paraphrase of its logic suppresses the load. Assume referenced skills are installed. Canonical wording: **invoke the `{X}` skill via the Skill tool**; for an eager multi-lens load, **invoke the Skill tool to load `{X}`, `{Y}`, `{Z}`**.

Two independent axes set the call — **when it fires** and **where it runs**.

**When it fires:**

- **Eager** — the dependency applies on every run (it is the skill's core lens): load it in a preflight `### Step 0`.
- **Lazy** — the dependency fires only conditionally (`triage` when its band is non-empty, `second-opinion` on pushback): call it at its own guarded step, so an unused dependency never loads.

**Where it runs:**

- **Relayed-lens** — subagents apply the dependency as a per-item lens: relay the Step 0 loaded criteria into each subagent's brief, since a parent-side load doesn't reach subagents.
- **Parent-run** — the parent runs the dependency itself.

A relayed lens loads eager (`refine-file`, `durable-docs-update` Step 0); a parent-run dependency loads lazy at its guarded step. Document only what you pass to and receive from it.

### References

Put reference material below `---`; link to it from the protocol by anchor (e.g., `[Output Schema](#output-schema)`). For shared schemas, add `<!-- source: references/{filename}.md -->` and follow the [Shared schema workflow](#shared-schema-workflow).

| Material | Location | Use when |
|----------|----------|----------|
| Schema or small reference (< 300 lines) | Inline in SKILL.md appendix | Default |
| Shared across skills, or single catalog > 300 lines | Repo-root `references/` | See [Shared schema workflow](#shared-schema-workflow) |
| Multi-file catalog owned by one skill, loaded one entry per session | `skills/{name}/references/` | Catalog would exceed 300 lines if inlined |

Skill-owned references: SKILL.md contains a catalog table; the agent reads only the selected entry (`references/{entry}.md`, or `${CLAUDE_SKILL_DIR}/references/{entry}.md` for a CWD-agnostic absolute path).

### Pinned chat output

When a step tells the agent to report, summarize, or surface something to the user in chat, pin the exact shape — left unpinned, every run improvises its own format. A pin is three parts: a bolded heading naming the moment, a fenced fill-in template, and an empty-case line:

````markdown
```
**[Heading naming the moment]:**
- [field]: [fill-in | alternative]
```

(Write `None — [what empty means]` when the list is empty.)
````

Pin the load-bearing surfaces — output the user acts on (gate results, pre-write summaries, review context). Skip one-liners whose content the step already dictates (a file path, a single sentence) — a template there is ceremony, not clarity. Canonical examples: `product-interview` Step 4, `tech-design` Steps 1 and 5.

### Skill anti-patterns

| Don't | Do instead |
|-------|-----------|
| "Read `references/schema.md` to understand the format" | "Return output conforming to the [Output Schema](#output-schema) below" |
| "Summarize / surface / report X" with the shape left to the reading agent | Pin the shape — heading + fill-in template + empty-case line (see [Pinned chat output](#pinned-chat-output)) |
| `## Overview`, `## Purpose`, `## Background`, or "Introduction" section | Cut. Lead paragraph + When to use is enough |
| "This skill will help you..." | "Validate a plan or decision." (imperative/declarative) |
| Schema mid-protocol or repeated across steps | Define once in appendix, reference by anchor |
| Naming a dependency skill in prose, or inlining a paraphrase of its logic | Load it via an explicit Skill-tool call; document only what you pass and receive |

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

### Step 1 — {Verb phrase}

{Step body.}

### Step N — Return output

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
| Vague input contract: "the caller provides context" | Numbered fields with formats: "1. **Artifact** — file path or diff range" |

---

## Shared schema workflow

🔒 `references/` is the source of truth but is not installed — inline its content into every consumer, or the copies silently drift.

Update process:
1. Edit the file in `references/`.
2. Find all consumers: `grep -r "source: references/{filename}" skills/ agents/`.
3. Copy the updated content into each consumer's appendix.
4. Commit all changes together.
