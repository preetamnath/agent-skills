# Agent Skills Repo

## Repo structure

```
agent-skills/
├── skills/           ← each skill is a directory with one SKILL.md
├── agents/           ← agent definitions (.md files)
├── references/       ← source of truth for shared schemas and catalogs
├── guides/           ← authoring guidelines
└── README.md
```


## Key files

- `guides/skill-writing-guidelines.md` — read before writing or modifying any skill.
- `guides/agent-writing-guidelines.md` — read before writing or modifying any agent.
- `references/` — repo-authoring SoT for shared schemas and catalogs. Not installed alongside skills/agents; consumers must inline content. When updating a shared schema: edit here first, then propagate to every consumer's appendix (find them with `grep -r "<!-- source: references/{filename}" skills/ agents/`). Commit together.


## Working in this repo

- Skills install to `~/.claude/skills/` (Claude Code) or `~/.agents/skills/` via `npx skills add`. Don't auto-install — wait for an explicit user request.
- Agents in `agents/*.md` are copied manually to `~/.claude/agents/` (Claude Code) or converted to `.toml` for Codex. Same rule: wait for the user.


## Working style

- **One decision at a time.** When walking through design decisions on a skill, agent, or feature, present ONE decision at a time with discussion before asking. Don't bundle independent fixes into a single multi-select `AskUserQuestion` call. For each decision: explain the mechanism (what's happening today), the problem (why it matters), the proposed fix, then ask one focused question. Wait for the answer before moving on. Use multi-select only for genuinely co-decided sub-options *within* a single fix.

- **Multi-reviewer findings: filter by ANY, not ALL.** When dispatching N reviewers in parallel with a confidence threshold (e.g., "≥ 0.80"), filter to findings where *at least one* reviewer crossed the threshold — not findings where all reviewers agreed. Different reviewers calibrate confidence differently and surface different real concerns; consensus-only loses real findings. Take the max confidence across reviewers, show which reviewers crossed the bar (e.g., "0.85 / 0.30 — A1 only") so disagreement is transparent, and walk findings sequentially per the rule above.
