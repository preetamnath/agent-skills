# TASKS

Active work on this repo's skills/agents/commands, and on the global agent setup they run in.

## Schema

Every task gets a row in `## Summary` and an entry under `## Open` — update
both together:

```
**<short title>**
  <optional one-line description when the title can't carry it>
  Status: <value>
  Detail: <where the full detail lives>
  Blocked: ⚠️ <reason>
  Notes: <gotcha, next action, or pending decision>
```

- **`Status:`** — 💡 Discovery → 🔨 Building → ⚙️ Testing → ✅ Shipped.
- **`Detail:`** — link to the investigation, plan, or spec when one exists.
  Omit when this entry is the only record.
- **`Blocked:`** — add while stuck; remove on unblock.
- **`Notes:`** — ≤2 sentences, carrying only what Status / Blocked / Detail /
  git history don't. Omit when empty.
- Prune an entry (and its Summary row) once Status is ✅ Shipped AND the work
  is committed — git history is the record.

---

## Summary

| Status | Task |
|--------|------|
| 💡 Discovery | Share global instructions across Claude, Codex, and OpenCode |

---

## Open

**Share global instructions across Claude, Codex, and OpenCode**
  Move shared rules to `~/.agents/AGENTS.md`; each tool's own file keeps its extras and loads the shared file.
  Status: 💡 Discovery
  Detail: [012-global-instruction-sharing](investigations/012-global-instruction-sharing/notes.md)
  Notes: Pending decision: Codex option B (symlink + `developer_instructions`) or C (generated file). Fix the `gpt-5.6-luna` drift in `~/.codex/config.toml` and `~/.config/opencode/AGENTS.md` during the move.
