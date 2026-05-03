# Agent Writing Guidelines

How to write, structure, and maintain agents in this repo. All agents must follow these conventions.

> **Existing agents may not yet conform.** When writing or updating agents, follow this document over existing agent patterns.

> **Skills are the default.** Read `guides/skill-writing-guidelines.md` first. An agent only earns its place when isolation, parallel execution, or external delegation creates real value over a skill firing inline. Most "I want focused behavior on X surface" needs are skills, not agents.


## Principles

1. **Skill-first.** If the work runs in the main thread (writing code, in-context lookup), it's a skill. Agents are for work that benefits from a fresh subagent context.
2. **Thin over fat.** When wrapping a skill, keep the agent body small. The skill is the source of truth; the agent adds isolation, an input contract, and output discipline — nothing more.
3. **Explicit input contract.** Every agent declares what the caller must pass in. Subagents start cold — they have no conversation history, no implicit context.
4. **Structured output, not narrative.** Agents return what callers can parse: a schema, a verdict, a fix list. No summaries, no preamble, no "here's what I found" framing.
5. **Match the skill's archetype.** A runner agent inherits its output shape from the skill it wraps — never invent a new schema for a runner. (Standalone agents define their own.)


## When to add an agent

| Need | Build a... |
|------|-----------|
| Inline code authoring on a specific surface | **Skill** (auto-trigger via description) |
| Inline lookup / reference loading | **Skill** |
| Structured analysis with parallelizable runs | **Runner agent** wrapping a structured-output skill |
| Adversarial second-pass over another agent's output | **Standalone agent** (own logic, may or may not load a skill) |
| Delegating to an external tool/service (Codex MCP, etc.) | **External-delegation agent** |
| Background research that would pollute main context | **Standalone agent** with read-only tools |

**When NOT to add an agent:**

- The work is "write code that follows pattern X." That's a skill.
- The skill auto-fires on description match and runs in-thread anyway. An agent wrapper adds nothing.
- The output is conversational. Agents return structured payloads; if the natural answer is prose, keep it inline.
- You'd be duplicating skill content into the agent body. Agents reference skills, not copy them.


## Directory structure

```
agent-skills/
├── agents/
│   └── {agent-name}.md               ← single file per agent
├── skills/                            ← skills the agents may reference
└── guides/
    └── agent-writing-guidelines.md   ← this file
```

Agents are flat `.md` files in `agents/`. No subdirectories, no companion files.


## Naming

| Element | Convention | Example |
|---------|-----------|---------|
| File name | `kebab-case.md`, role noun | `code-reviewer.md`, `verifier.md`, `sanity-checker.md` |
| `name` in frontmatter | Matches file name (without `.md`) | `code-reviewer` |
| Runner agents wrapping a skill | Often the skill name + role suffix | skill `sanity-check` → agent `sanity-checker` |


## Disambiguation: skill+agent pairs

When a thin runner agent wraps a skill, both have descriptions that the harness scores against the user's intent. The harness routes by description match alone — there is no built-in preference for skills over agents. If the descriptions are nearly identical, the model defaults to the cheaper route (loading the skill inline in the main thread) because nothing in the agent's description tells it isolation is wanted.

The fix: the agent's description must claim a unique trigger that the skill does not. The cleanest signal is the isolation itself.

**Pattern:**

- **Skill description** — focuses on the work itself. Does not mention isolation. The inline path is the default.
- **Agent description** — leads with "in an isolated subagent" or "for parallel execution." Reserves isolation/parallelism as the unique trigger. Adds a Do NOT clause naming the wrong intent ("Do NOT use for inline validation").

**Worked example:**

```yaml
# skills/sanity-check/SKILL.md
description: "Validate or challenge a plan, design, or decision. Confirms what's good, flags realistic concerns, and identifies blind spots."

# agents/sanity-checker.md
description: "Validate or challenge a plan, design, or decision in an isolated subagent. Confirms strengths, flags realistic concerns, surfaces blind spots. Use when isolation or parallel execution is wanted. Do NOT use for inline validation, code review, or exploratory analysis."
```

With this pattern: "sanity check this plan" routes to the skill (correct — inline is the default). "Spawn an agent to sanity check this independently" or "review this in parallel with X" routes to the agent.

**Do NOT name the paired skill in the agent's description (or vice versa).** Describe the wrong *intent* ("inline validation") instead of naming the alternative. Cross-references are brittle and clutter routing signal.

**Naming alone does not solve this.** Renaming the skill (e.g., `sanity-check-protocol`) and giving the agent the bare name (`sanity-check`) was considered. Rejected: slash commands use the skill name (`/sanity-check-protocol` is worse UX), the role-suffix convention is established, and routing keys off description text not the name. The disambiguation has to live in the descriptions.


## Agent archetypes

Agents fall into four patterns. Know which one you're writing — it determines the body size, the `skills:` frontmatter, and the rules.

| Archetype | Wraps a skill? | Body size | Output | Examples |
|-----------|---------------|-----------|--------|----------|
| **Thin runner** — wraps a structured-output skill, adds isolation | Yes (single skill) | ~25-30 lines | Skill's `Output Schema` | code-reviewer, propose-alternatives, sanity-checker |
| **Fat runner** — routes between skill-delegation and self-execution | Sometimes | ~100-150 lines | Skill's schema or own | (none currently — see note below) |
| **Standalone** — own logic, optional skill load | Optional | ~100-150 lines | Own schema | reviewer, verifier |
| **External delegation** — wraps an external tool/service | Often (for self-review) | ~150-300 lines | Own schema or delegated | codex-execute, codex-review |

**Prefer splitting over fat runners.** When the routing decision is a simple type-check (e.g., "code vs. non-code"), build two single-purpose agents and let the harness route by `description`. The fat-runner archetype remains documented for cases where the branches share substantial input contract or post-processing — but in practice, splitting is almost always cleaner. The `reviewer` agent originally fit this archetype; it was split into `code-reviewer` (thin runner over `code-review`) and `reviewer` (standalone for non-code artifacts) so each agent fits a textbook archetype.


## Agent template

### Thin runner (most common)

```markdown
---
name: {agent-name}
description: "{What the agent does, in an isolated subagent. Claim isolation/parallelism as the unique trigger. Include explicit Do NOT clauses. See `Disambiguation: skill+agent pairs` below.}"
model: opus  # or sonnet — match the skill's model field
tools: Read, Grep, Glob, Bash  # minimum read tools; add only what the skill needs
skills:
  - {skill-name}
---

You are a {role}. {One sentence stating what the agent does — written in second person.}

Execute the preloaded `{skill-name}` skill end-to-end.

## Input contract

The caller provides:
1. **{Field}** — {what it is, format, where to find it}
2. **{Field}** — {...}
3. **{Field}** (optional) — {...}

If {required field} is missing or vague, ask before proceeding.

## Rules

- Don't produce a summary or narrative. The structured output IS the response.
- {Other agent-specific behavioral rules}
```

The skill's full SKILL.md content (protocol + Output Schema appendix) is auto-injected into the subagent's context at spawn — see [Claude Code agents docs](https://code.claude.com/docs/en/agents.md) ("The full skill content is injected, not just made available for invocation"). The "Execute the preloaded skill end-to-end" line points the model at it. The agent body adds only what the skill doesn't have: an input contract and output discipline. No `## How you work` heading, no `## Output Schema` appendix on a thin runner.

### Fat runner

When the agent needs routing logic before delegating:

```markdown
---
name: {agent-name}
description: "..."
model: opus
tools: Read, Grep, Glob, Bash
skills:
  - {skill-name}
---

You are a {role}. ...

## Input contract
...

## How you {verb}

0. **Route by {dimension}.**
   - **{Type A}**: follow the loaded `{skill-name}` skill's protocol — {what it does} — and return its `{SchemaName}`. Stop here.
   - **{Type B}**: continue with steps 1–N below.

1. {Self-execution step 1}
2. ...

## Output format

Return a `{SchemaName}` envelope conforming to the [Output Schema](#output-schema) below.

## Rules
...

---

## Output Schema

<!-- source: references/{schema-name}.md -->

{Schema inlined for the self-execution path. Same shape as the skill's schema if the runner returns the skill's output.}
```

### Standalone agent

No skill load — the agent does its own work end-to-end:

```markdown
---
name: {agent-name}
description: "..."
model: opus
tools: Read, Grep, Glob, Bash
---

You are a {role}. ...

## Input contract
...

## How you {verb}
...

## Output format

Return a `{SchemaName}` ...

## Rules
...

---

## Output Schema

<!-- source: references/{schema-name}.md -->

{Full schema}
```

### External delegation agent

Wraps a third-party tool (e.g., Codex MCP). Same structure as standalone, plus:
- The wrapped tool's transport in `tools:` (e.g., `mcp__codex__codex`).
- A self-review or fix-cycle protocol if the external tool's output needs validation.
- See `agents/codex-execute.md` and `agents/codex-review.md` for full examples.


## Section reference

### Frontmatter

```yaml
---
name: kebab-case-name
description: "What it does + when to use. Includes Do NOT clauses for disambiguation. Under 40 words."
model: opus           # required for runner agents (match skill); sonnet OK for execution agents
tools: Read, Grep, Glob, Bash   # minimum read tools; add the skill's needs + nothing extra
skills:
  - skill-name        # only when the agent invokes the skill's behavior
---
```

**`name`** — matches the file name (without `.md`). Used as the `subagent_type` parameter when spawning.

**`description`** — the harness uses this to decide when this agent is the right delegate. Include:
- What the agent does
- When to spawn it ("Use for code review, spec review, plan audit")
- Negative conditions ("Do NOT use for exploratory analysis")

**`model`** — runner agents should match the wrapped skill's `model` field. Standalone agents pick based on task complexity (analysis → `opus`; routine I/O → `sonnet`).

**`tools`** — start with the read minimum (`Read, Grep, Glob, Bash`). Add only what the agent or skill actually uses. Common additions: `WebFetch` for canonical doc lookup, `mcp__*` for external services. Never grant write tools (`Edit`, `Write`) to runner or review agents.

**`skills:`** — list skills the agent loads. Use ONLY when the agent actually invokes the skill's behavior (executes its protocol or returns its schema). Do not add `skills: [name]` purely to inherit a schema embedded in the skill's appendix — inline the schema in the agent body with a `<!-- source: references/... -->` comment instead.

### Role line

One sentence after frontmatter, second person, declarative.

- Yes: `You are a reviewer. You find real problems — not style nits, not theoretical risks.`
- Yes: `You are a sanity checker. You validate plans, designs, and decisions — confirming strengths, flagging real concerns, and surfacing blind spots.`
- No: `This agent is a code reviewer that helps users find bugs.`
- No: `A specialized agent for review tasks.`

### Input contract

Required for every agent. Subagents start cold — no conversation history. The contract makes the cold start predictable.

```markdown
## Input contract

The caller provides:
1. **{Field name}** — {what it is, format, where to find it}
2. **{Field name}** — {...}
3. **{Field name}** (optional) — {...}

If {required field} is missing or vague, ask before proceeding.
```

Number every field. Mark optional ones explicitly. Specify format (file paths, diff range, structured object). End with the escalation rule for missing required input.

### How you work

The body. Choose based on archetype:

| Archetype | Heading | Body |
|-----------|---------|------|
| Thin runner | _none — single body line_ | "Execute the preloaded `{skill-name}` skill end-to-end." (placed right after the role line, no heading) |
| Fat runner | `## How you {verb}` | Routing step `0` first, then numbered steps for the self-execution path |
| Standalone | `## How you {verb}` | Numbered steps describing the agent's own protocol |
| External delegation | `## Instructions` (matches orchestrator skill style) | Validate input → call external tool → self-review → fix cycle |

**Why no heading on a thin runner.** The skill's full SKILL.md (protocol + Output Schema appendix) is auto-injected into the subagent at spawn — the model already has the instructions. The single "Execute the preloaded skill end-to-end" line is the entire pointer the model needs; a `## How you work` section that just paraphrases the skill is dead weight. See [Claude Code agents docs](https://code.claude.com/docs/en/agents.md): *"The full skill content is injected, not just made available for invocation."*

**Use "spawn" vs "load" vs "preloaded" precisely.** When this agent itself spawns a subagent, write "spawn the `<agent>` agent." When it loads a skill in-context (skill invoked via description-match inside the agent's turn), write "load the `<skill>` skill." When pointing the model at a skill listed in the agent's own `skills:` frontmatter (already in the system prompt at spawn), write "execute the preloaded `<skill>` skill." Mismatching causes orchestrators to execute in-thread work they intended to delegate, or causes thin runners to look for a skill that's already loaded.

### Output format

Required. Tells the agent exactly what to return.

For thin runner agents:
- No `## Output format` heading. The preloaded skill defines the schema in its own appendix and tells the model to return it. The runner's body just adds the input contract + rules.

For fat runners and standalone agents:
```markdown
## Output format

Return a `{SchemaName}` envelope conforming to the [Output Schema](#output-schema) below.

- {Field-specific instructions, e.g., "Set `verdict` to null on all findings — the verifier populates it"}
```
With the schema inlined in an appendix below `---`.

### Rules

Always present. Bullet list. The most important rule for every runner agent:

```markdown
- Don't produce a summary or narrative. The structured output IS the response.
```

Other rules cover: evidence requirements (cite file:line, no citation = not a finding), what NOT to flag, escalation paths, scope boundaries.

### Appendix (for fat runner / standalone / external delegation)

Same convention as skills: schemas below a `---` separator, with `<!-- source: references/{filename} -->` comments when the schema is shared. Thin runners do NOT have an appendix — they inherit the skill's schema by reference.


## Anti-patterns

| Don't | Do instead |
|-------|-----------|
| Add an agent that auto-fires on a description trigger to write code inline | Make it a skill — skills auto-load into the main thread, agents are for isolation |
| Duplicate the skill's protocol prose into the agent body | Trust the preload: "Execute the preloaded `{skill-name}` skill end-to-end." (skill content is already in the system prompt) |
| Add a `## How you work` section to a thin runner that paraphrases the skill | Drop the heading — single body line after the role is enough, the skill's instructions are already loaded |
| Define a new output schema for a thin runner | Inherit from the skill's `## Output Schema` appendix |
| `skills: [name]` purely to inherit a schema (no behavior invocation) | Inline the schema in the agent body with a `<!-- source: -->` comment |
| Grant `Edit` or `Write` to a review/runner agent | Read-only tools (`Read, Grep, Glob, Bash`) — review agents never write |
| Agent description that mirrors the paired skill's description | Claim isolation/parallelism as the unique trigger — see `Disambiguation: skill+agent pairs` |
| Naming the paired skill in the agent description (or vice versa) | Describe the wrong intent ("Do NOT use for inline validation") instead of naming the alternative |
| Body that summarizes what the agent will do at the end | Structured output IS the response — no closing summary |
| Soft language: "consider", "you might want to", "evaluate as needed" | Direct: "Check for X", "Flag if Y", "Demote when Z" |
| Agent that delegates to a subagent without using "spawn" | "Spawn the `<agent>` agent" — explicit verb prevents in-thread execution |
| Vague input contract: "the caller provides context" | Numbered fields with formats: "1. **Artifact** — file path or diff range" |


## Checklist for new agents

### All agents

- [ ] File name is `kebab-case.md` in `agents/`
- [ ] Frontmatter has `name`, `description`, `tools` (required); `model` and `skills` as appropriate
- [ ] `name` matches the file name (without `.md`)
- [ ] `description` includes both positive triggers and Do NOT clauses
- [ ] Role line is second-person declarative, one sentence
- [ ] `## Input contract` is present, numbered, with format hints
- [ ] Required fields have an explicit "ask before proceeding" escalation
- [ ] `## Rules` includes "structured output IS the response" for runners
- [ ] No write tools (`Edit`, `Write`) for review/runner agents
- [ ] No duplicated skill content in the agent body

### Thin runner agents

- [ ] Body is under 30 lines
- [ ] `skills: [skill-name]` present in frontmatter
- [ ] Single line after the role: "Execute the preloaded `{skill-name}` skill end-to-end." (no `## How you work` heading)
- [ ] No `## Output format` heading (inherited from skill)
- [ ] No `---` separator / appendix (inherited from skill)
- [ ] Agent's `description` claims a unique trigger (e.g., "in an isolated subagent") that the skill's description does not
- [ ] Agent's `description` does not name the paired skill (describe wrong intent instead)

### Fat runner / standalone agents

- [ ] `## How you {verb}` numbered protocol present
- [ ] Routing step (if fat runner) is numbered `0` and lists each artifact type
- [ ] `## Output format` specifies the schema name and any field-specific rules
- [ ] Schema appendix below `---` separator
- [ ] Shared schemas have `<!-- source: references/{filename} -->` comment

### External delegation agents

- [ ] External tool's transport listed in `tools` (e.g., `mcp__codex__codex`)
- [ ] Self-review or fix-cycle protocol if the external tool's output needs validation
- [ ] Bounded retry count (e.g., "up to 2 cycles") — never unbounded


## Concrete example: thin runner (full file)

```markdown
---
name: sanity-checker
description: "Validate or challenge a plan, design, or decision in an isolated subagent. Confirms strengths, flags realistic concerns, surfaces blind spots. Use when isolation or parallel execution is wanted. Do NOT use for inline validation, code review, or exploratory analysis."
model: opus
tools: Read, Grep, Glob, Bash
skills:
  - sanity-check
---

You are a sanity checker. You validate plans, designs, and decisions — confirming strengths, flagging real concerns, and surfacing blind spots.

Execute the preloaded `sanity-check` skill end-to-end.

## Input contract

The caller provides:
1. **Subject** — the plan, design, or decision to validate (inline text or file paths)
2. **Context** — relevant code files, constraints, or requirements that bound the decision
3. **Concern** (optional) — specific aspect the caller wants scrutinized

If the subject is missing or too vague to evaluate, ask before proceeding.

## Rules

- Don't produce a summary or narrative. The structured output IS the response.
```

That's the full file. 24 lines. The skill (`sanity-check`) is 91 lines and gets auto-injected into the subagent's context at spawn — the agent body adds only an input contract, an output-discipline rule, and a description that reserves "isolated subagent" as its unique trigger so the harness doesn't default to firing the skill inline.
