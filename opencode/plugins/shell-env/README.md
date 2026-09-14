# shell-env

OpenCode 2 plugin that restores `HOME`, `LANG`/`LC_ALL`, and the newest Node
bin directory for every tool shell.

OpenCode's tool shell runs with a curated environment that omits `HOME`,
`PATH`, and the locale. Commands that read them then fail in ways that look
unrelated to OpenCode: `git`/`gh` cannot find the user's config, `npm`/`node`
are "not found", and Ruby tooling aborts on non-ASCII input under a US-ASCII
locale. The `create.before` shell hook is the one seam that can put them back.

Only missing values are filled, so an explicitly injected value wins.

## Install

Copy this directory to `~/.config/opencode/plugins/shell-env/`. OpenCode loads
every plugin under that directory automatically; reload the server or start a
new session to activate it.

## Test

```sh
node --test
```
