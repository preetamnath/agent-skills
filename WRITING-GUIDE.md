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

### Notation

- `<angle>` — a fill-in the agent replaces.
- `[square]` — a literal tag emitted as-is (`[verified]`, `[done]`).
- Migrate an existing file only when you touch it.

### Frontmatter — shared fields

- 🔒 **`description`** — the loader drops content after 1024 chars; stay under 1000. Include what it does, when to use it, synonyms, and disambiguating negatives; omit internal schema fields.
- **`model`** (agents) — `opus` for cross-file or architectural reasoning; `sonnet` for routine I/O or delegation wrappers. Skills typically omit (defaults to sonnet).

Place constraints by scope:

- Put a cross-cutting invariant no single Step owns under `## Rules` as `- **Bold label.** Rule text.`
- Put a step-specific constraint in that Step; never echo it under Rules.
- Add `## Constraints` for output limits such as severity ranges or field caps.

### Tables

Use the minimum column set. Drop columns derivable from adjacent ones, put short qualifiers inline, and keep meaningful single-value columns such as confidence, 🔒, or severity.

### Artifact admission and ownership

- Create a skill, agent, or reference only for a distinct trigger, scope, upkeep, or retirement boundary. File count alone is not bloat; duplicated ownership, mixed scopes, broken routes, and eagerly loaded payload are.
- Give each instruction one canonical owner and write path. Deliver it elsewhere through a relative symlink, native import, or generated view. Keep a copy only when derivation cannot work, and guard exact equality automatically.
- Put the rule at the point of use only when that file owns the behavior. Otherwise, link or load the owner instead of paraphrasing it.

---

## Skills

### Archetypes

| Archetype | Section heading | Canonical example |
|-----------|----------------|--------|
| **Lens** — one primitive judgment, no subagents | `## Steps` (bare numbered list) | `tighten-instruction`, `vet-fact`, `place-fact` |
| **Composite (fan-out panel)** — loads lenses, fans reviewers, triages, walks findings | `## Steps` (`### Step N`) | `find-gaps` |
| **Score-gated file editor** — scores reversible edits, applies high-confidence ones, proves the result cold | `## Steps` (`### Step N`) | `compress-file`, `tighten-file`, `refine-file` |
| **Structured output** — execute steps, return a schema | `## Instructions` | `sentry-analysis` |
| **File artifact** — interactive or procedural, writes a file | `## Protocol` | `product-interview`, `write-plan` |

Apply the [per-archetype deltas](#lens) below to the base shell.

### Frontmatter — skill-specific

**Description shape.** `{what it does}. TRIGGER when: {phrases the user says}.` Make TRIGGER precise enough to exclude sibling skills. Put mechanics, artifacts, preconditions, and any "Use when…" restatement in the body.

- **`TRIGGER when:`** (~25 words) — semicolon-separated positive conditions in user-intent language; patterns over enumeration (`<s-*>`, not `s-button, s-card`).
- **`SKIP when:`** — add only to route away from a *named* confusable sibling a precise TRIGGER still can't exclude (`SKIP when: trust-checking an answer you have (validate-answer)`). Never a restatement of TRIGGER.

Example: `"...TRIGGER when: code contains <s-*> tags; user asks to build/update/fix UI in a Shopify app."`

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

#### Lens

- Main section `## Steps` as a **bare numbered list** (`1.`, `2.` …), not `### Step N` headings — the steps read straight through.
- Optional lead: `Primitive: **NAME** — {one-line gloss}` naming the single judgment (see `vet-fact`, `place-fact`).
- An editing lens puts its confidence gate in the final numbered step: score the independent edit; return it without editing when a caller owns a file-level gate; otherwise apply at `c ≥ 0.75` and hold it below that threshold.
- No `## Rules` — the steps carry the whole procedure.

#### Composite (fan-out panel)

- Use `## Steps` with `### Step N — {Verb}` headings.
- In **Step 0**, load lens skills via the Skill tool; see [Loading a dependency skill](#loading-a-dependency-skill).
- **Dispatch** R0 (you) and R1/R2 (`general-purpose` subagents, parallel), relaying the loaded criteria into each brief.
- **Triage** the contested middle, **walk** findings one at a time via `AskUserQuestion`, then summarize applied / skipped / dropped plus net compression.
- When the skill uses shared bands, inline the matching `references/confidence-bands.md` mode per the [Shared schema workflow](#shared-schema-workflow).

#### Score-gated file editor

- Resolve scope, load any lens skills, and pin the file's purpose and invariants.
- Score each independent edit `0.00–1.00`; apply at `c ≥ 0.75` and hold lower-confidence proposals without asking.
- Re-read every changed file cold. Revert or fix any edit that changes meaning, placement, or another pinned invariant.
- Report applied and held edits plus the net change. Ask only when the requested scope is materially ambiguous, not for an in-scope reversible edit.

#### Structured output

- Main section `## Instructions`; final step returns the schema by anchor: `### Step N — Return output conforming to the [Output Schema](#output-schema) below.`
- Append `---` then `## Output Schema` with `<!-- source: references/{schema-name}.md -->` and inlined schema content. 🔒 The `#output-schema` anchor and `## Output Schema` heading are grep/link contracts — keep the exact text and lowercase-hyphenated casing, or `[Output Schema](#output-schema)` references break.

#### File artifact

- Main section `## Protocol`. Penultimate step confirms before writing (`AskUserQuestion` with "Looks good — write it" / "Adjust before writing"); final step writes the artifact, reports the path, and offers next steps via `AskUserQuestion`.
- Inline the markdown template inside the write step as a fenced block.

#### Loading a dependency skill

A dependency loads only through an explicit Skill-tool call. A bare name leaves loading to model discretion; an inline paraphrase suppresses it. Assume referenced skills are installed.

Use these exact calls: **invoke the `{X}` skill via the Skill tool**; for an eager multi-lens load, **invoke the Skill tool to load `{X}`, `{Y}`, `{Z}`**.

| Axis | Mode | Rule |
|------|------|------|
| When | **Eager** | Load a dependency used on every run in preflight `### Step 0`. |
| When | **Lazy** | Call a conditional dependency in its guarded step so it stays unloaded when unused. |
| Where | **Relayed-lens** | Relay Step 0 criteria into every subagent brief; a parent-side load does not reach subagents. |
| Where | **Parent-run** | The parent invokes and applies the dependency. |

A relayed lens loads eager (`durable-docs-update` Step 0); a parent-run dependency loads lazy at its guarded step. A score-gated file editor may eagerly load a parent-run lens it applies throughout (`tighten-file`, `refine-file`).

### References

Put reference material below `---` and link to it from the protocol by anchor. For shared schemas, add `<!-- source: references/{filename}.md -->` and follow the [Shared schema workflow](#shared-schema-workflow).

| Material | Location | Use when |
|----------|----------|----------|
| Schema or small reference (< 300 lines) | Inline in SKILL.md appendix | Default |
| Shared across skills, or single catalog > 300 lines | Repo-root `references/` | See [Shared schema workflow](#shared-schema-workflow) |
| Multi-file catalog owned by one skill, loaded one entry per session | `skills/{name}/references/` | Catalog would exceed 300 lines if inlined |

For skill-owned references, keep the catalog in SKILL.md and read only the selected entry: `references/{entry}.md`, or `${CLAUDE_SKILL_DIR}/references/{entry}.md` when the path must ignore CWD.

### Pinned chat output

Pin the exact shape of chat output the user acts on. Use a bolded heading, a fenced fill-in template, and an empty-case line:

````markdown
```
**<Heading naming the moment>:**
- <field>: <fill-in | alternative>
```

(Write `None — <what empty means>` when the list is empty.)
````

Skip a template when the step already dictates a one-line result such as a file path. Canonical examples: `product-interview` Step 4 and `tech-design` Steps 1 and 5.

### Skill anti-patterns

| Don't | Do instead |
|-------|-----------|
| "Read `references/schema.md` to understand the format" | "Return output conforming to the [Output Schema](#output-schema) below" |
| "Summarize / surface / report X" with the shape left to the reading agent | Pin the shape — heading + fill-in template + empty-case line (see [Pinned chat output](#pinned-chat-output)) |
| `## Overview`, `## Purpose`, `## Background`, or "Introduction" section | Cut. Lead paragraph + When to use is enough |
| A `## Rules` / `## Notes` section that restates the Steps | Dissolve it; fold each unique invariant into the Step it governs |
| "This skill will help you..." | "Validate a plan or decision." (imperative/declarative) |
| Schema mid-protocol or repeated across steps | Define once in appendix, reference by anchor |
| Naming a dependency skill in prose, or inlining a paraphrase of its logic | Load it via an explicit Skill-tool call; document only what you pass and receive |

---

## Agents

Standalone agents run in isolation and own their logic and output schema, often inlined from `references/`.

### Frontmatter — agent-specific

**`tools`** — grant only the required read tools. Omit `Edit` and `Write` from review and analysis agents.

### Typical shape

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

Canonical examples: `agents/code-reviewer.md`, `agents/sanity-checker.md`, `agents/reviewer.md`, and `agents/verifier.md`. The last uses `## Output format` when the envelope needs population rules absent from the shared schema. Always give numbered, formatted input fields; never only "the caller provides context."

---

## Shared schema workflow

🔒 `references/` is the canonical source but is not installed. Inline its content into every consumer, bound each copied span, and guard source-to-consumer equality automatically.

🔒 Give every source marker a visible span: place it immediately before a heading so the section is the span, or indent it inside a block so the indent is the span. Never put a flush-left marker mid-prose.

Update process:
1. Edit the file in `references/`.
2. Find all consumers: `grep -r "source: references/{filename}" skills/ agents/`.
3. Copy the updated content into each consumer's bounded span.
4. Run the equality guard.
5. Commit the source and consumers together.
