import assert from "node:assert/strict";
import { test } from "node:test";

import {
  applyShellEnv,
  compareNodeVersions,
  createShellEnv,
  DEFAULT_PATH,
  pickNewestNodeVersion,
} from "../core.js";

test("applyShellEnv fills the variables the tool shell drops", () => {
  const env = {};
  applyShellEnv(env, { home: "/root", lang: "C.UTF-8", nodeBin: "/node/bin" });
  assert.equal(env.HOME, "/root");
  assert.equal(env.LANG, "C.UTF-8");
  assert.equal(env.LC_ALL, "C.UTF-8");
  assert.equal(env.PATH, `/node/bin:${DEFAULT_PATH}`);
});

test("applyShellEnv never overwrites an injected value", () => {
  const env = { HOME: "/custom", LANG: "en_US.UTF-8", PATH: "/opt/bin" };
  applyShellEnv(env, { home: "/root", lang: "C.UTF-8", nodeBin: "/node/bin" });
  assert.equal(env.HOME, "/custom");
  assert.equal(env.LANG, "en_US.UTF-8");
  assert.equal(env.LC_ALL, "C.UTF-8");
  assert.equal(env.PATH, "/node/bin:/opt/bin");
});

test("applyShellEnv does not duplicate an existing Node bin", () => {
  const env = { PATH: "/node/bin:/usr/bin" };
  applyShellEnv(env, { home: "/root", lang: "C.UTF-8", nodeBin: "/node/bin" });
  assert.equal(env.PATH, "/node/bin:/usr/bin");
});

test("compareNodeVersions orders numerically, not lexically", () => {
  assert.ok(compareNodeVersions("v24.18.0", "v9.11.0") > 0);
  assert.ok(compareNodeVersions("v22.1.0", "v22.10.0") < 0);
  assert.equal(compareNodeVersions("v24.18.0", "v24.18.0"), 0);
});

test("pickNewestNodeVersion ignores non-version entries", () => {
  assert.equal(
    pickNewestNodeVersion(["v22.1.0", "v24.18.0", "v9.11.0", "lts"]),
    "v24.18.0",
  );
  assert.equal(pickNewestNodeVersion(["lts"]), undefined);
});

test("createShellEnv registers a create.before hook that fills the env", async () => {
  let registered;
  const ctx = {
    shell: {
      hook: async (name, callback) => {
        registered = { name, callback };
        return { dispose() {} };
      },
    },
  };

  await createShellEnv(ctx, {
    home: "/root",
    lang: "C.UTF-8",
    nodeBin: "/node/bin",
  }).install();

  assert.equal(registered.name, "create.before");
  const event = { env: {} };
  registered.callback(event);
  assert.equal(event.env.HOME, "/root");
  assert.equal(event.env.PATH, `/node/bin:${DEFAULT_PATH}`);
});
