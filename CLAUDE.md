# Agent Skills Repo

A collection of skills and agents for AI coding agents. Skills are single-file `SKILL.md` definitions; agents are standalone `.md` files.


## Repo structure

```
agent-skills/
├── skills/           ← each skill is a directory with one SKILL.md
├── agents/           ← agent definitions (.md files)
├── references/       ← source of truth for shared schemas and catalogs
├── guides/           ← authoring guidelines and conventions
└── README.md         ← public-facing: skill list, installation, usage
```


## Key files

- **Skill writing guidelines** — `guides/skill-writing-guidelines.md`. Read before writing or modifying any skill. Covers naming, templates (3 archetypes), anti-patterns, and checklists.
- **Shared schemas** — `references/`. Canonical versions of schemas used across multiple consumers (skills and agents). When updating a schema, edit here first, then propagate to each consumer's appendix (search for `<!-- source: references/{filename} -->` comments). `references/` itself is repo-authoring source-of-truth and is NOT installed alongside skills/agents — every consumer must inline the content.


## Conventions

- **Single file per skill, usually.** Each skill directory contains `SKILL.md`. No companion files. Exception: a skill that owns a multi-file catalog (selectively loaded per session, not shared across skills) may keep it in `skills/{name}/references/`. See `guides/skill-writing-guidelines.md` for criteria.
- **Self-contained.** SKILL.md includes everything the agent needs — schemas inlined in an appendix below a `---` separator, referenced by anchor links from the protocol.
- **Three archetypes.** Structured output (`## Instructions`), file artifact (`## Protocol`), orchestrator (`## Pipeline`). See the guidelines for templates.
- **Shared schema workflow.** Edit repo-root `references/` → find consumers via `<!-- source: -->` comments (in both `skills/` and `agents/`) → copy updated content into each consumer's appendix → commit together. Repo-root `references/` is for *shared* material only; skill-owned references live with the skill.


## Working in this repo

- Before writing a new skill: read `guides/skill-writing-guidelines.md`.
- Before modifying a shared schema: check which consumers use it with `grep -r "<!-- source: references/{filename}" skills/ agents/`.
- Skills are installed to `~/.claude/skills/` (Claude Code) or `~/.agents/skills/` via `npx skills add`. Do not auto-install or copy after modifying — the user requests installation explicitly when ready.
- Agent `.md` files in `agents/` are copied manually to `~/.claude/agents/` (Claude Code) or converted to `.toml` for Codex. Same rule: wait for an explicit request before copying.
