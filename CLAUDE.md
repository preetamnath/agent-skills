# Agent Skills Repo

- **Read `WRITING-GUIDE.md` before authoring or editing a skill or agent.**
- **After you create a file, run `tighten-file` before reporting done.**
- **After you edit a file, run `tighten-instruction` on the changed lines before reporting done.**
- **"File" means any file — docs and config (README, CLAUDE.md, JSON) included, not just skill/agent content.**
- **When updating a shared schema in `references/`, sync all consumers per `WRITING-GUIDE.md`.**
- **When a skill/agent/command is added, removed, or renamed, sync both the README list and `.claude-plugin/plugin.json`'s `skills` array to match `skills/` — alphabetical, before committing.**
- **When a skill/agent/command's purpose changes, update its README description.**
