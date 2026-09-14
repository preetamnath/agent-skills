import { readdirSync } from "node:fs";
import { join } from "node:path";

/** Bash's own fallback PATH when the tool shell inherits none. */
export const DEFAULT_PATH =
  "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin";

/**
 * Restore the variables OpenCode's tool shell drops from its curated env.
 *
 * Only MISSING keys are filled: an explicitly injected value (for example a
 * per-session `ACD_*` var or a caller-set PATH) must win.
 */
export function applyShellEnv(env, { home, lang, nodeBin }) {
  if (env.HOME === undefined) env.HOME = home;
  if (env.LANG === undefined) env.LANG = lang;
  if (env.LC_ALL === undefined) env.LC_ALL = lang;
  if (nodeBin !== undefined) {
    const parts = (env.PATH ?? DEFAULT_PATH)
      .split(":")
      .filter((part) => part !== "");
    if (!parts.includes(nodeBin)) env.PATH = [nodeBin, ...parts].join(":");
  }
  return env;
}

/** Numeric-aware compare so v24.18.0 sorts above v9. */
export function compareNodeVersions(a, b) {
  const left = a.split(/\D+/).filter(Boolean).map(Number);
  const right = b.split(/\D+/).filter(Boolean).map(Number);
  const length = Math.max(left.length, right.length);
  for (let index = 0; index < length; index += 1) {
    const diff = (left[index] ?? 0) - (right[index] ?? 0);
    if (diff !== 0) return diff;
  }
  return 0;
}

/** The newest `v*` entry among a versions directory's names, or undefined. */
export function pickNewestNodeVersion(entries) {
  const versions = entries.filter((name) => /^v?\d/.test(name));
  if (versions.length === 0) return undefined;
  return versions.sort(compareNodeVersions).at(-1);
}

function nodeBinUnder(versionsRoot) {
  try {
    const newest = pickNewestNodeVersion(readdirSync(versionsRoot));
    return newest === undefined ? undefined : join(versionsRoot, newest, "bin");
  } catch {
    return undefined;
  }
}

/**
 * Register the shell hook that restores HOME, the locale, and the Node bin
 * directory for every tool shell OpenCode creates.
 */
export function createShellEnv(ctx, options = {}) {
  const home = options.home ?? process.env.HOME ?? "/root";
  const lang = options.lang ?? "C.UTF-8";
  const nodeBin =
    options.nodeBin ??
    nodeBinUnder(
      options.nodeVersionsRoot ?? join(home, ".nvm", "versions", "node"),
    );
  return {
    async install() {
      return ctx.shell.hook("create.before", (event) => {
        applyShellEnv(event.env, { home, lang, nodeBin });
      });
    },
  };
}
