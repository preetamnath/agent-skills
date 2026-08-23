# OpenCode 2 Claude-rules bridge

This dependency-free OpenCode 2 plugin loads from
`~/.config/opencode/plugins/claude-rules/` and invokes the canonical matcher at
`/root/.codex/hooks/claude_rules.py`. It does not reimplement Claude-rule
discovery or matching.

## Install or update

Copy the plugin files into the global plugin directory:

```sh
mkdir -p ~/.config/opencode/plugins/claude-rules/test
cp .gitignore README.md core.js index.js package.json \
  ~/.config/opencode/plugins/claude-rules/
cp test/core.test.js ~/.config/opencode/plugins/claude-rules/test/
```

- **Canonical matcher.** Install the matcher before this bridge.
- **Dependencies.** No `npm install` or SDK package is needed.
- **Updates.** Update this bridge when the matcher contract changes.

- **Reloading.** OpenCode watches the plugin directory, so an existing OpenCode
  2 terminal can discover the plugin without a restart.

The hook path can be overridden for tests with
`OPENCODE_CLAUDE_RULES_HOOK`. Hook failures are fail-open and diagnostics go to
stderr only.

Run the tests with:

```sh
node --test
```
