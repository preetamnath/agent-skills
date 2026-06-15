# Agent Skills Repo

- Read `WRITING-GUIDE.md` before authoring or editing a skill or agent.
- If you create a new file, run `tighten-file` before reporting done.
- If you are editing file, run `tighten-instruction` on the changed lines before reporting done.
- When updating a shared schema in `references/`, sync all consumers per `WRITING-GUIDE.md`.
- When a skill/agent/command is added, removed, or renamed, sync both the `README.md` list and `.claude-plugin/plugin.json`'s `skills` array to match `skills/` — alphabetical order.
- When a skill/agent/command's purpose changes, update its `README.md` description.
- When I ask for a commit, run `scripts/validate-skills.sh` first and block the commit if it fails.
