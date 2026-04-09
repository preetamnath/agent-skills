# Skill Writing Guidelines

How to write, structure, and maintain skills in this repo. All skills must follow these conventions.

> **Existing skills may not yet conform.** When writing or updating skills, follow this document over existing skill patterns.


## Principles

1. **Single file.** Each skill is one `SKILL.md`. No `references/` subdirectories, no companion files. Everything the agent needs is in the file. One exception: skills with catalogs exceeding 300 lines may reference a file in the repo-root `references/` directory — see [Large catalog exception](#large-catalog-exception).
2. **Self-contained.** An agent reads SKILL.md and can execute the skill without fetching anything else.
3. **Instructions first, reference material last.** The agent hits the protocol before the appendix. Schemas and catalogs go at the bottom.
4. **Write for the agent, not the human.** Every sentence is an instruction or a constraint. No marketing copy, no "Overview" sections, no motivation paragraphs.
5. **Shared schemas have a source of truth.** The `references/` directory at the repo root holds canonical versions. When a schema is used by multiple skills, update `references/` first, then copy into each SKILL.md.


## Directory structure

```
agent-skills/
├── skills/
│   └── {skill-name}/
│       └── SKILL.md          ← the only file
├── agents/
│   └── {agent-name}.md
├── references/                ← source of truth for shared schemas and catalogs
│   ├── finding-schema.md
│   ├── diagnosis-schema.md
│   ├── alternatives-schema.md
│   ├── sanity-check-schema.md
│   ├── polaris-app-home-catalog.md
│   └── shopify-dev-mcp-tools.md
└── guides/
    └── skill-writing-guidelines.md   ← this file
```


## Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Directory name | `kebab-case`, verb-noun or noun phrase | `code-review`, `plan-builder`, `parallel-diagnosis` |
| `name` in frontmatter | Matches directory name exactly | `code-review` |
| Schema types | `PascalCase` | `ReviewOutput`, `Finding`, `DiagnosisOutput` |
| Reference files | `kebab-case`, descriptive noun | `finding-schema.md`, `polaris-app-home-catalog.md` |


## Skill archetypes

Skills fall into three patterns. Know which one you're writing — it determines the section heading, output format, and template.

| Archetype | Section heading | Output | Examples |
|-----------|----------------|--------|----------|
| **Structured output** — execute steps, return a schema | `## Instructions` | `## Output Schema` appendix, referenced by anchor | code-review, sanity-check, propose-alternatives |
| **File artifact** — interactive or procedural, writes a file | `## Protocol` | Inline markdown template in the writing step | interview-me, grill-me, plan-builder |
| **Orchestrator** — chains other skills in stages | `## Pipeline` | Reuses schemas from chained sub-skills | diagnose-review-fix-orchestrator |


## SKILL.md template

### Structured output skill

```markdown
---
name: {skill-name}
description: "{What it does + when to activate. Trigger cues for the skill router. Under 30 words.}"
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
description: "{What it does + when to activate. Under 30 words.}"
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

No `## Output Schema` appendix — the inline template IS the output definition.

### Orchestrator skill

```markdown
---
name: {skill-name}
description: "{What it does + when to activate. Under 30 words.}"
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


## Section reference

### Frontmatter (required)

```yaml
---
name: kebab-case-name
description: "What it does + trigger cues. Under 30 words."
model: opus  # optional — omit to use default (sonnet)
---
```

**`name`** — matches the directory name. Used as the slash-command name (`/sanity-check`).

**`description`** — the skill router uses this to decide when to activate. Write it for matching, not for humans. Include:
- What the skill does ("Validate a plan or decision")
- When to use it ("Use when user says 'sanity check' or wants a plan validated")
- Key synonyms that should trigger it

Bad: `"A comprehensive tool for validating plans."`
Good: `"Validate or challenge a plan, design, or decision. Confirms what's good, flags realistic concerns, and identifies blind spots."`

**`model`** (optional) — override the default model. Values: `opus`, `sonnet`. Omit to use default (sonnet). Use `opus` only for skills requiring cross-file reasoning or architectural judgment.

### H1 — Display name

Title-case. Should be recognizable as the skill's purpose. Not necessarily the same as the `name` field.

| `name` | H1 |
|--------|-----|
| `code-review` | Code Review |
| `parallel-diagnosis` | Parallel Diagnosis |
| `grill-me` | Grill Me |

### Lead paragraph

1-2 sentences after H1. States what the skill does and the goal. Plain declarative voice.

- Yes: `Move from ambiguity to clarity before building.`
- No: `This skill helps you move from ambiguity to clarity.`
- No: `A powerful skill for conducting interviews to clarify requirements.`

### When to use

Brief. Either one sentence or a tight bullet list.

For skills with clear positive/negative boundaries, use the YES/NO format:
```markdown
## When to use

YES: Bug with uncertain root cause that needs parallel investigation.
NO: Bug with obvious cause — just fix it directly.
NO: Feature work — use `plan-builder` instead.
```

For simpler skills, a sentence or bullets work:
```markdown
## When to use

When you have a goal and need to break it into sequenced work items.
Not for requirements gathering — use `interview-me` first if the goal is vague.
```

### Instructions / Protocol / Pipeline

The main body. Choose based on archetype:

| Archetype | Heading | Step format |
|-----------|---------|-------------|
| Structured output | `## Instructions` | `### N — Verb phrase` |
| File artifact / interactive | `## Protocol` | `### N — Verb phrase` |
| Orchestrator | `## Pipeline` | `### Stage N — Name` |

Guidelines for steps:
- **Imperative voice.** "Read the file" not "The agent should read the file."
- **Be specific.** Name what to read, what to check, what to output.
- **Reference appendix by anchor.** "Return output conforming to the [Output Schema](#output-schema) below."
- **Inline small templates where used.** If a step produces a markdown artifact, show the template inside that step in a fenced block.
- **Name the `AskUserQuestion` tool explicitly.** When a step requires user input, write "use the `AskUserQuestion` tool" — not "ask the user" or "ask before proceeding." See [Human-in-the-loop conventions](#human-in-the-loop-conventions) below.

### Human-in-the-loop conventions

All user-facing questions must use the `AskUserQuestion` tool by name. This applies to all three archetypes, not just orchestrators.

**When to require it:**
- **Orchestrators:** Every stage transition (mandatory per archetype template).
- **File artifact skills:** Before writing the artifact (confirmation checkpoint) and after writing (handoff prompt).
- **Structured output skills:** When inputs are ambiguous or missing (clarification before analysis).
- **All skills:** Escalation paths (repeated failures, scope expansion, inconclusive results).

**How to write it:**
- Always write "the `AskUserQuestion` tool" (not just "`AskUserQuestion`").
- Include structured options and a recommended choice.
- Example: `Use the \`AskUserQuestion\` tool with options: "Proceed", "Adjust", "Stop". Recommended: "Proceed".`

**Don't use it for:** Genuinely open-ended questions with no enumerable answers — use plain text for those.

### Rules / Constraints

Always the last section before the appendix separator. Bullet list. Each rule:

```markdown
- **Bold label.** Rule text. One concern per bullet.
```

Use `## Rules` for behavioral constraints (what the agent must/must not do).
Use `## Constraints` for output constraints (severity ranges, field limits).
Both can coexist if needed — Rules first, then Constraints.

### Appendix (after `---` separator)

Everything below the `---` horizontal rule is reference material — schemas, catalogs, lookup tables. The agent reads the protocol first, then reads the appendix sections referenced by anchor links in the protocol.

**Source comment.** If the appendix content comes from a shared schema in `references/`, add an HTML comment:
```markdown
<!-- source: references/finding-schema.md -->
```
This makes it easy to find and update all copies when the source changes.

**Section naming.** Use `## Output Schema` for output struct definitions. Use `## {Catalog Name}` for lookup references (component catalogs, tool indexes).

**Anchor links.** The protocol references the appendix via markdown anchors:
```markdown
Return output conforming to the [Output Schema](#output-schema) below.
```

### Large catalog exception

If a skill's catalog or reference material exceeds 300 lines (e.g., polaris-web-components component catalog), it lives in `references/` at the repo root. The SKILL.md instructions tell the agent to Read the file by its repo-root-relative path:

```markdown
### 1 — Load the component catalog

Read `references/polaris-app-home-catalog.md` for the full component catalog, App Bridge APIs, and layout compositions.
```

This is the only case where SKILL.md references an external file. Keep the SKILL.md protocol, rules, and any small schemas self-contained.


## Anti-patterns

| Don't | Do instead |
|-------|-----------|
| `references/` subdirectory inside the skill folder | Inline into SKILL.md appendix, or use repo-root `references/` for large catalogs |
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


## Shared schema workflow

Some schemas are used by multiple skills (e.g., `finding-schema.md` is used by code-review, fix-loop, and two-pass-review).

**Source of truth:** `references/` at the repo root.

**Update process:**
1. Edit the file in `references/`
2. Find all skills that use it: search for `<!-- source: references/{filename} -->`
3. Copy the updated content into each skill's appendix section
4. Commit all changes together

**Versioning:** Git handles version history. No version suffixes in filenames. If a schema change is breaking, update all consuming skills in the same commit.


## Checklist for new skills

### All skills

- [ ] Directory name is `kebab-case`
- [ ] `SKILL.md` is the only file in the directory
- [ ] Frontmatter has `name` and `description` (required), optionally `model`
- [ ] `description` includes trigger cues, under 30 words
- [ ] H1 is the display name, title-case
- [ ] Lead paragraph is 1-2 sentences, declarative
- [ ] `## When to use` present, includes NOT conditions if relevant
- [ ] Steps use the correct heading format for the archetype
- [ ] Protocol uses imperative voice throughout
- [ ] `## Rules` section covers edge cases and tool-use requirements
- [ ] User-facing questions reference the `AskUserQuestion` tool by name (not "ask the user")
- [ ] Escalation paths (repeated failures, ambiguous inputs) use the `AskUserQuestion` tool
- [ ] No companion files in the skill directory
- [ ] Total file length is under 300 lines (hard limit: 500)
- [ ] Skill added to repo README.md table

### Structured output skills (additional)

- [ ] Output schema is in an appendix below `---`, not mid-protocol
- [ ] Appendix schemas have a `<!-- source: references/... -->` comment if shared
- [ ] Protocol references schema via anchor link, not file path

### File artifact skills (additional)

- [ ] Artifact template shown inline in the writing step (fenced markdown block)
- [ ] File path convention documented (directory, NNN numbering)
- [ ] Skill tells user the written file path
- [ ] End condition is explicitly defined
- [ ] Confirmation checkpoint before writing artifact (via the `AskUserQuestion` tool)
- [ ] Handoff prompt after writing artifact (via the `AskUserQuestion` tool)

### Orchestrator skills (additional)

- [ ] Every stage transition has an explicit checkpoint via the `AskUserQuestion` tool
- [ ] Shortcutting rules require the `AskUserQuestion` tool before skipping stages
- [ ] Sub-skills referenced by name, with pass/receive documented
- [ ] `## Shortcutting` table present if stages can be skipped
- [ ] No custom output schema — reuses schemas from chained sub-skills

### Line limits

Line limits keep skills within a single context-window read. If a skill exceeds 300 lines, look for: redundant examples, over-specified field notes, content that belongs in repo-root `references/`. The 500-line hard limit is never exceeded.


## Concrete example: sanity-check (before → after)

### Before (broken — references external file)

```markdown
## Instructions

### Step 1 — Read the output schema
Read `references/sanity-check-schema.md` to understand the required output format.

### Step 2 — Understand what's being checked
...

### Step 4 — Return structured output
Return the `SanityCheckOutput` conforming to the schema in `references/sanity-check-schema.md`.
```

### After (self-contained — appendix pattern)

```markdown
## Instructions

### 1 — Gather context
...

### 2 — Evaluate
...

### 3 — Return output
Return a `SanityCheckOutput` conforming to the [Output Schema](#output-schema) below.

## Constraints
...

---

## Output Schema

<!-- source: references/sanity-check-schema.md -->

### SanityCheckOutput

​```
SanityCheckOutput {
  verdict: "sound" | "concerns" | "rethink",
  confirmation: what's good about this approach,
  concerns: Concern[],
  blind_spots: string[],
  reframe: string | null
}
​```

### Concern

​```
Concern {
  id: sequential number starting from 1,
  severity: "P0" | "P1" | "P2",
  ...
}
​```

### Field notes
- `verdict` — "sound" means proceed...
```

Key changes:
1. Removed the "Read external file" step entirely
2. Schema is in the appendix, referenced by anchor
3. `<!-- source: -->` comment ties it back to the canonical copy
4. Protocol reads top-to-bottom without external dependencies
