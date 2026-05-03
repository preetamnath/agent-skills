# Skill Writing Guidelines


## Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Directory name | `kebab-case`, verb-noun or noun phrase | `plan-builder`, `sentry-analysis`, `interview-me` |
| `name` in frontmatter | Matches directory name exactly | `plan-builder` |
| Schema types | `PascalCase` | `ReviewOutput`, `Finding`, `DiagnosisOutput` |
| Reference files | `kebab-case`, descriptive noun | `{schema-name}-schema.md`, `{surface}-catalog.md` |


## Skill archetypes

| Archetype | Section heading | Output |
|-----------|----------------|--------|
| **Structured output** — execute steps, return a schema | `## Instructions` | `## Output Schema` appendix, referenced by anchor |
| **File artifact** — interactive or procedural, writes a file | `## Protocol` | Inline markdown template in the writing step |
| **Orchestrator** — chains other skills in stages | `## Pipeline` | Reuses schemas from chained sub-skills |


## SKILL.md template

### Structured output skill

```markdown
---
name: {skill-name}
description: "..."   # see Frontmatter section
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
```

### File artifact skill

```markdown
---
name: {skill-name}
description: "..."   # see Frontmatter section
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
```

### Orchestrator skill

```markdown
---
name: {skill-name}
description: "..."   # see Frontmatter section
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
```


## Frontmatter

**`description`** — the skill router uses this to match user intent. Write it for matching, not for humans. Include what the skill does, when to use it, key synonyms, and negative conditions if needed for disambiguation. Under 60 words. Don't list internal schema field names in parens — those don't route.

**`TRIGGER when:` clause** (optional) — append to the description for skills with domain-specific vocabulary users may not say verbatim. Format: `TRIGGER when: {semicolon-separated conditions}`. Positive triggers only (negatives go in the base description). Focus on user-intent language, not domain terms already in the base description. Use patterns over enumeration (`<s-*>` not `s-button, s-card`). Under 25 words.

Example: `"...Not for checkout extensions. TRIGGER when: code contains <s-*> tags; user asks to build/update/fix UI in a Shopify app; user mentions cards, modals, or forms."`

**`model`** (optional) — `opus` or `sonnet`. Omit for default (sonnet). Use `opus` only for cross-file reasoning or architectural judgment.


## Writing steps (Instructions / Protocol / Pipeline)

- **Imperative voice.** "Read the file" not "The agent should read the file."
- **Name the `AskUserQuestion` tool explicitly.** Write "use the `AskUserQuestion` tool" — not "ask the user" or "ask before proceeding." Required for: orchestrator stage transitions; file-artifact pre/post-write checkpoints; structured-output ambiguity or missing inputs; all escalation paths. Always include structured options and a recommended choice. Not for genuinely open-ended questions with no enumerable answers.
- **Distinguish "spawn" from "invoke" when delegating.** Use **"spawn the `<agent>` agent"** when work must run in an isolated subagent context. Use **"invoke" / "load the `<skill>` skill"** when work runs in-thread. Mismatching the verb causes orchestrators to execute in-thread work they intended to delegate.
- **Inline small templates where used.** If a step produces a markdown artifact, show the template inside that step in a fenced block.

## Rules / Constraints

Use `## Rules` for behavioral constraints (what the agent must/must not do). Use `## Constraints` for output constraints (severity ranges, field limits). Both can coexist — Rules first, then Constraints. Each bullet: `- **Bold label.** Rule text. One concern per bullet.`

## Appendix

Everything below `---` is reference material. The agent reads the protocol first, then the appendix sections referenced by anchor links. Add `<!-- source: references/{filename}.md -->` for shared schemas. Protocol references the appendix via anchor link, e.g., `[Output Schema](#output-schema)`.


## Large catalog exception

If a skill's catalog or reference material exceeds 300 lines, it lives in `references/` at the repo root. The SKILL.md instructions tell the agent to Read the file by its repo-root-relative path:

```markdown
### 1 — Load the catalog

Read `references/{filename}.md` for the full reference material.
```

Use repo-root `references/` when the material is **shared across multiple skills** or is a single large catalog file. Keep the SKILL.md protocol, rules, and any small schemas self-contained.

## Skill-owned references exception

A skill may keep `skills/{name}/references/` when **all** apply: material is owned by one skill (not shared); it's a multi-file catalog with standalone entries; the skill loads only one (or few) entries per session; the catalog would exceed the 300-line soft limit if inlined. Example: `skills/agent-soul/references/<archetype>.md` (38 archetypes, one per session).

When using this pattern: SKILL.md contains a catalog table (one line per entry); SKILL.md instructs the agent to read only the selected entry by path `references/{entry}.md` (or `${CLAUDE_SKILL_DIR}/references/{entry}.md` for a CWD-agnostic absolute path); entry files share a common schema documented in SKILL.md.

Do not use this pattern for schemas, small reference tables, content loaded every session (all inline in appendix), or material shared across skills (use repo-root `references/`).


## Anti-patterns

| Don't | Do instead |
|-------|-----------|
| `references/` subdirectory inside the skill folder for small material | Inline into SKILL.md appendix. The subdirectory pattern is only for skill-owned multi-file catalogs — see [Skill-owned references exception](#skill-owned-references-exception) |
| "Read `references/schema.md` to understand the format" | "Return output conforming to the [Output Schema](#output-schema) below" |
| Separate "Overview" or "Introduction" section | Lead paragraph after H1 covers this |
| "This skill will help you..." | "Validate a plan or decision." (imperative/declarative) |
| Numbered steps without verb phrases: `### Step 1` | `### 1 — Read context` |
| Schema definitions mid-protocol | Schema in appendix, referenced by anchor |
| Soft language ("consider", "you might want to", "as needed") | Direct instructions ("Check for X", "Flag if Y") |
| Repeating the schema in multiple protocol steps | Define once in appendix, reference by anchor |
| Adding `## Overview`, `## Purpose`, `## Background` | Cut it. The lead paragraph + When to use is enough |
| Generic description: "A tool for reviewing code" | Trigger-rich: "Structured code review with P0-P3 findings, confidence scores, and criteria-based analysis" |
| Auto-proceeding between orchestrator pipeline stages | Every stage transition requires human approval via the `AskUserQuestion` tool |
| Defining a new output schema for an orchestrator | Reuse schemas from chained sub-skills |
| Describing sub-skill behavior inline in an orchestrator | Reference by name, document only what you pass and receive |
| "Stop and ask the user" or "ask before proceeding" (unnamed tool) | "Use the `AskUserQuestion` tool with options: ..." (structured, named) |
| "invoke the `<skill>` skill" when the intent is subagent isolation | "spawn the `<agent>` agent" — skills load in-thread; only spawning an agent creates a new context |


## Shared schema workflow

Source of truth is `references/` at the repo root. This directory is repo-authoring SoT only — it is NOT installed alongside skills or agents, so every consumer must inline the content.

Update process: (1) edit the file in `references/`; (2) find all consumers: `grep -r "<!-- source: references/{filename} -->" skills/ agents/`; (3) copy the updated content into each consumer's appendix; (4) commit all changes together. Git handles version history — no version suffixes in filenames.
