# Codex global storage cleanup

Use this runbook to remove inactive standalone releases, clear diagnostic logs, and disable memories and analytics without deleting session transcripts.

## Preflight

1. Read `~/.codex/config.toml` before any mutation.
2. Resolve `~/.codex/packages/standalone/current`, then confirm its target with `~/.codex/packages/standalone/current/codex --version`.
3. List and measure every directory under `standalone/releases/`. Mark only siblings of the active target for deletion.
4. Inspect `logs_2.sqlite` with `.schema`, `PRAGMA quick_check`, page counts, file sizes, and `lsof`.
5. Record the count and size of `~/.codex/sessions/**/*.jsonl`; also check `~/.codex/archived_sessions` when present.

## Apply

1. Change only these settings and preserve all unrelated TOML:

   ```toml
   [features]
   memories = false

   [analytics]
   enabled = false
   ```

2. Delete each inactive release by its verified absolute path. Keep the `current` symlink and its target.
3. Clear and compact only the diagnostic `logs` table:

   ```sh
   sqlite3 ~/.codex/logs_2.sqlite \
     '.timeout 60000' \
     'BEGIN IMMEDIATE; DELETE FROM logs; DELETE FROM sqlite_sequence WHERE name="logs"; COMMIT;' \
     'VACUUM;' \
     'PRAGMA optimize;' \
     'PRAGMA wal_checkpoint(TRUNCATE);'
   ```

   Active Codex chats can add fresh rows immediately. A nonzero final row count is normal.
   If the file stays large after `VACUUM`, rerun the WAL checkpoint when active chats are idle.

## Verify and report

- Recheck the active symlink, binary version, and remaining release directories.
- Confirm Codex reports the `memories` feature as `false`; inspect the two config settings directly.
- Run `PRAGMA quick_check`, confirm `freelist_count = 0`, and compare database disk use before and after.
- Confirm no transcript file disappeared; active transcript files can grow during cleanup.
- Report reclaimed space as deleted-release space plus reduced database space.

## Never do this

- Never delete `standalone/current`, its target, the whole `releases/` directory, or releases selected by an unresolved glob or variable.
- Never delete or externally truncate `logs_2.sqlite`, its WAL/SHM files, `sessions/`, `archived_sessions/`, or transcript JSONL files.
- Never replace the live database file while Codex processes hold it open; use SQLite transactions, `VACUUM`, and a final WAL checkpoint.
- Never rewrite the full config when two targeted edits are sufficient.
