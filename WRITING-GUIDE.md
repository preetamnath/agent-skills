# Writing Guide

🔒 marks requirements that protect loading, links, or shared-schema sync. Other guidance is a default; choose the clearest structure for the task.

## Choose a skill or agent

- **Skill:** Own a user-triggered workflow, including workflows that dispatch subagents.
- **Agent:** Do one delegated task in isolation, such as review, research, or tool-specific work.

## Common conventions

| Element | Convention |
|---|---|
| Skill directory and agent file | `kebab-case`; agents are flat in `agents/` |
| Frontmatter `name` | 🔒 Match the skill directory or agent filename without `.md` exactly |
| Schema type | `PascalCase` |
| Reference file | Descriptive `kebab-case`, such as `{schema-name}-schema.md` |
| Step heading | `### Step N — Verb phrase` when numbered headings help |

Use `<angle>` for a value the agent fills in and `[square]` for a literal tag it emits. Update an existing file's notation only when you touch that file.

- 🔒 **Frontmatter:** Start each skill or agent with YAML frontmatter containing a nonempty `name` and `description`.
- 🔒 **Description:** Keep `description` under 1000 characters; the loader drops content after 1024. State what the artifact does and when to use it. Omit internal schema fields.
- **Claude agent model:** In `agents/*.md`, use `opus` for cross-file or architectural reasoning and `sonnet` for routine I/O or delegation wrappers. Skills usually omit `model`.
- **Instruction placement:** Put a step-specific rule in its step. Put a rule that governs several steps in `## Rules`; put output limits in `## Constraints`. Do not repeat a rule in several places.
- **Tables:** Use only columns that help compare rows. Keep meaningful confidence, severity, or requirement columns.
- **Artifact scope:** Create a skill, agent, or reference when it has a distinct trigger, scope, upkeep, or retirement boundary. File count alone does not decide this.
- **Ownership:** Give each instruction one canonical owner. Deliver it elsewhere through a relative symlink, native import, or generated view. Keep a copy only when derivation cannot work, and guard its equality automatically.

## Skills

### Description and structure

- Use `TRIGGER when:` for clear user intents.
- Add `SKIP when:` only when it improves routing; name the destination skill when one exists.
- Put mechanics, preconditions, and output contracts in the body.

| Shape | Use | Example |
|---|---|---|
| Lens | One judgment in a short numbered `## Steps` list | `vet-fact` |
| Workflow | Several steps, possibly with subagents, under `## Steps` | `find-gaps` |
| Structured output | `## Instructions` ending in an output contract | `triage` |
| File artifact | `## Protocol` with a clear write step and artifact template | `write-plan` |

- Use a short lead only when headings do not orient the reader.
- Add `## When to use` only when the description does not settle entry and exclusion conditions.
- Keep an artifact template near the step that writes it. Define the write or approval gate for that workflow.

For instruction-file edits:

- Pin the file's purpose and required tokens, then score each independent edit.
- If a caller owns the file-level gate, return the proposal and score without editing. Otherwise, apply at `c ≥ 0.75` and hold lower-confidence edits.
- Re-read changed files cold and fix any loss of meaning or broken reference.

For a workflow with subagents, derive distinct tasks from the artifact, pass each worker the relevant source and return contract, define how findings are checked, and specify how the user decides on them. Size and timing of the dispatch belong to that workflow.

### Dependency skills

- Load a dependency through an explicit call, such as **invoke the `{X}` skill via the Skill tool**, before first use. Load one used on every run early; load a conditional dependency in its guarded step.
- If subagents apply a lens, pass its criteria in their briefs; a parent-side load does not reach them.
- Naming a skill as a destination is fine; naming it as a dependency does not load it.
- Do not copy a dependency's procedure into its caller.

### References and chat output

- Put small reference material after a `---` separator and link to it by anchor.
- Put material shared across artifacts, or a catalog over 300 lines, in repo-root `references/`.
- For a skill-owned multi-file catalog, keep an index in `SKILL.md` and read only the selected `references/{entry}.md`; use `${CLAUDE_SKILL_DIR}/references/{entry}.md` when the path must ignore the current directory.

Pin the shape of a chat result the user must act on: give it a heading, named fields, and an empty-case line. Skip a template for a one-line result such as a file path.

When a skill uses a schema, end its procedure with a link to `## Output Schema` and define the schema once after `---`. 🔒 Keep that heading and its `#output-schema` anchor when links target it. Use bounded source markers only when the schema comes from a shared file in `references/`.

## Agents

- Give review and analysis agents only the read tools they need.
- State required inputs as numbered, formatted fields, including paths and formats. Say what to do when an input is missing.
- Give each agent a clear return contract. When it returns a shared schema, follow the workflow below. Avoid a second narrative summary when the structured result is the response.

The existing `agents/code-reviewer.md`, `agents/reviewer.md`, and `agents/verifier.md` show input contracts and shared output schemas.

## Shared schema workflow

🔒 `references/` is the canonical source but is not installed. Inline each shared fragment into its consumers and guard source-to-consumer equality automatically.

Bound the canonical fragment with `<!-- fragment: {id} -->` and `<!-- /fragment: {id} -->`. Bound each copy with `<!-- source: references/{file}.md#{id} -->` and `<!-- /source: references/{file}.md#{id} -->`. Indent the full block when it is nested.

1. Edit the file in `references/`.
2. Find every consumer: `rg -l 'source: references/{filename}#' skills agents`.
3. Copy the new content into each bounded consumer span.
4. Run `scripts/validate-skills.sh` to check manifests and exact copy equality.
5. Commit the source and consumers together.
