# Agent Skills Repo

## Pending work

- Check `meta/TASKS.md` before reworking a skill — it lists queued edits.

## Authoring

- Read `WRITING-GUIDE.md` before authoring or editing a skill or agent.
- When a rule under-fires, fix its section placement and name its output form — keep the trigger broad, since a stray firing costs less than a miss.
- Before reporting done, run these in order; each stops when it finds no improvement:
  - On a file you created: `compress-file`, `tighten-file`, `structure-prose`.
  - After each instruction-text edit, invoke the `tighten-instruction` skill, then the `structure-prose` skill, via the Skill tool.
- Apply a lens change only at `c ≥ 0.75` and when it preserves every instruction's meaning; otherwise hold it without editing.

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
