# Agent Skills Repo

## Authoring

- Read `WRITING-GUIDE.md` before authoring or editing a skill or agent.
- Before reporting done, run these in order — each one stops itself when there's nothing to do:
  - On a file you created: `compress-file`, `tighten-file`, `structure-prose`.
  - On lines you edited: `tighten-instruction`, `structure-prose`.

## Sync on change

- When updating a shared schema in `references/`, sync all consumers per `WRITING-GUIDE.md`.
- When a skill/agent/command is added, removed, or renamed, sync both the `README.md` list and `.claude-plugin/plugin.json`'s `skills` array to match `skills/` — alphabetical order.
- When a skill/agent/command's purpose changes, update its `README.md` description.

## Commit & install

- Run `scripts/validate-skills.sh` once when I ask to commit.
- After a commit that adds or updates a skill/agent/command, offer to install the changed ones based on the instructions below:

| Type | Install |
|---|---|
| Skill | run `npx skills add preetamnath/agent-skills --skill <changed names>` (prefill the names) |
| Agent | copy `agents/<name>.md` → `~/.claude/agents/<name>.md` |
| Command | copy `commands/<name>/<name>.md` → `~/.claude/commands/<name>.md` (flat — no subdir) |
