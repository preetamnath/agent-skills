import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

import {
  createBridge,
  createHookRunner,
  extractToolText,
  makePayload,
  namespaceSessionId,
  toolCommand,
} from "../core.js";

test("maps native and structured tools into canonical hook commands", () => {
  assert.equal(toolCommand("bash", { command: "cat backend/app.py" }), "cat backend/app.py");
  assert.equal(toolCommand("apply_patch", { patch: "*** Update File: backend/app.py" }), "*** Update File: backend/app.py");
  assert.equal(toolCommand("read", { filePath: "backend/it's.py" }), "cat -- 'backend/it'\\''s.py'");
  assert.equal(toolCommand("grep", { pattern: "needle", path: "backend" }), "rg -- 'needle' 'backend'");
  assert.equal(toolCommand("glob", { pattern: "**/*.py", path: "backend" }), "rg --files -g '**/*.py' 'backend'");
  assert.equal(toolCommand("edit", { path: "backend/app.py" }), "touch -- 'backend/app.py'");
  assert.equal(toolCommand("provider.wrapper", { command: "sed -n '1p' backend/app.py" }), "sed -n '1p' backend/app.py");
});

test("payloads namespace session state by provider and location", () => {
  assert.equal(namespaceSessionId("session-1", "/repo"), "opencode2:/repo:session-1");
  assert.deepEqual(
    makePayload({ cwd: "/repo", sessionID: "session-1", tool: "read", input: { path: "a.md" } }),
    {
      cwd: "/repo",
      session_id: "opencode2:/repo:session-1",
      tool_name: "read",
      tool_input: { command: "cat -- 'a.md'" },
    },
  );
});

test("extracts every supported text result shape", () => {
  assert.equal(extractToolText("plain"), "plain");
  assert.equal(extractToolText({ output: "output" }), "output");
  assert.equal(extractToolText({ content: "content" }), "content");
  assert.equal(extractToolText({ content: [{ type: "text", text: "one" }, { type: "image", url: "x" }, { text: "two" }] }), "one\ntwo");
});

function makeMockContext(directory, hookResults = []) {
  const storageValues = new Map();
  const hooks = new Map();
  const calls = [];
  const ctx = {
    storage: {
      async get(key) {
        return storageValues.get(key);
      },
      async set(key, value) {
        storageValues.set(key, value);
      },
      async remove(key) {
        storageValues.delete(key);
      },
    },
    session: {
      async get({ sessionID }) {
        assert.equal(sessionID, "s1");
        return { location: { directory } };
      },
      async hook(name, callback) {
        hooks.set(`session:${name}`, callback);
        return { dispose() {} };
      },
    },
    tool: {
      async hook(name, callback) {
        hooks.set(`tool:${name}`, callback);
        return { dispose() {} };
      },
    },
    event: {
      async subscribe() {
        return {
          async *[Symbol.asyncIterator]() {},
        };
      },
    },
  };
  let resultIndex = 0;
  const runHook = async (event, payload) => {
    calls.push({ event, payload });
    const result = hookResults[resultIndex++];
    return result || { ok: true };
  };
  return { ctx, hooks, calls, storageValues, runHook };
}

test("bridge persists a match, acknowledges it quietly, and re-arms after compaction", async () => {
  const mock = makeMockContext("/repo", [
    { ok: true, additionalContext: "Read and follow `/repo/.claude/rules/backend.md`." }, // pre-tool-use
    { ok: true, additionalContext: "Read and follow `/repo/.claude/rules/backend.md`." }, // context injects
    { ok: true }, // post-tool-use
    { ok: true }, // context stays quiet
    { ok: true }, // post-compact
    { ok: true, additionalContext: "Read and follow `/repo/.claude/rules/backend.md`." }, // context re-arms
  ]);
  const bridge = createBridge(mock.ctx, { runHook: mock.runHook });
  const cleanup = await bridge.install();
  await mock.hooks.get("tool:execute.before")({
    tool: "read",
    sessionID: "s1",
    input: { filePath: "backend/app.py" },
  });
  assert.equal(mock.storageValues.size, 1);

  const firstContext = { sessionID: "s1", system: [] };
  await mock.hooks.get("session:context")(firstContext);
  assert.deepEqual(firstContext.system, [
    { type: "text", text: "Read and follow `/repo/.claude/rules/backend.md`." },
  ]);

  await mock.hooks.get("tool:execute.after")({
    tool: "read",
    sessionID: "s1",
    input: { filePath: ".claude/rules/backend.md" },
    status: "completed",
    result: { content: [{ type: "text", text: "rule body" }] },
  });

  const quietContext = { sessionID: "s1", system: [] };
  await mock.hooks.get("session:context")(quietContext);
  assert.deepEqual(quietContext.system, []);

  await bridge.compacted({ type: "session.compaction.ended", sessionID: "s1" });

  const thirdContext = { sessionID: "s1", system: [] };
  await mock.hooks.get("session:context")(thirdContext);
  assert.deepEqual(thirdContext.system, [
    { type: "text", text: "Read and follow `/repo/.claude/rules/backend.md`." },
  ]);
  assert.deepEqual(mock.calls.map((call) => call.event), [
    "pre-tool-use",
    "pre-tool-use",
    "post-tool-use",
    "pre-tool-use",
    "post-compact",
    "pre-tool-use",
  ]);
  await cleanup();
});

test("bridge subscribes to the public compaction event and can stop it", async () => {
  let nextResolve;
  let returned = false;
  const source = {
    [Symbol.asyncIterator]() {
      return {
        next: () => new Promise((resolve) => (nextResolve = resolve)),
        return: async () => {
          returned = true;
          nextResolve?.({ done: true });
          return { done: true };
        },
      };
    },
  };
  const mock = makeMockContext("/repo", [{ ok: true }]);
  mock.ctx.event.subscribe = async () => source;
  const bridge = createBridge(mock.ctx, { runHook: mock.runHook });
  const cleanup = await bridge.install();
  nextResolve({ value: { type: "session.compaction.ended", sessionID: "s1" }, done: false });
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(mock.calls[0]?.event, "post-compact");
  await cleanup();
  assert.equal(returned, true);
});

test("real canonical Python hook matches and then acknowledges a temporary rule", async () => {
  const repo = await mkdtemp(join(tmpdir(), "opencode-rules-integration-"));
  try {
    // Use a repository marker so this dependency-free test avoids spawning git.
    await mkdir(join(repo, ".git"));
    await mkdir(join(repo, ".claude", "rules"), { recursive: true });
    await mkdir(join(repo, "backend"));
    await writeFile(join(repo, "backend", "app.py"), "print('ok')\n");
    const rule = "---\npaths:\n  - backend/**\n---\nKeep backend changes type-safe.\n";
    await writeFile(join(repo, ".claude", "rules", "backend.md"), rule);
    const runHook = createHookRunner({ timeoutMs: 5_000 });
    const payload = {
      cwd: repo,
      session_id: `integration-${Date.now()}-${Math.random()}`,
      tool_name: "read",
      tool_input: { command: "cat -- 'backend/app.py'" },
    };
    const matched = await runHook("pre-tool-use", payload);
    assert.equal(matched.ok, true);
    assert.match(matched.additionalContext, /Read and follow/);
    assert.match(matched.additionalContext, /backend\.md/);
    await runHook("post-tool-use", {
      ...payload,
      tool_input: { command: "cat -- '.claude/rules/backend.md'" },
      tool_response: "Keep backend changes type-safe.",
    });
    const quiet = await runHook("pre-tool-use", payload);
    assert.equal(quiet.ok, true);
    assert.equal(quiet.additionalContext, undefined);
    await runHook("post-compact", payload);
  } finally {
    await rm(repo, { recursive: true, force: true });
  }
});
