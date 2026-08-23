import { createHash } from "node:crypto";
import { spawn } from "node:child_process";

export const DEFAULT_HOOK_PATH = "/root/.codex/hooks/claude_rules.py";
export const DEFAULT_PYTHON = process.env.OPENCODE_CLAUDE_RULES_PYTHON || "python3";
const STORAGE_PREFIX = "opencode-claude-rules/v1/";
const HOOK_TIMEOUT_MS = 5_000;
const MAX_PENDING_OPERATIONS = 64;
const MAX_INSTRUCTION_LENGTH = 8_000;

function compact(value, limit = 400) {
  return String(value ?? "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, limit);
}

function diagnostic(event, error) {
  const detail = compact(error instanceof Error ? `${error.name}: ${error.message}` : error);
  if (detail) process.stderr.write(`opencode-claude-rules: ${event} failed open (${detail})\n`);
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function quoteShell(value) {
  return `'${String(value).replaceAll("'", "'\\''")}'`;
}

function firstString(input, keys) {
  for (const key of keys) {
    if (typeof input?.[key] === "string" && input[key].trim()) return input[key];
  }
  return undefined;
}

function stringList(input, keys) {
  for (const key of keys) {
    const value = input?.[key];
    if (typeof value === "string" && value.trim()) return [value];
    if (Array.isArray(value)) {
      const items = value.filter((item) => typeof item === "string" && item.trim());
      if (items.length) return items;
    }
  }
  return [];
}

/** Map an OpenCode tool call to the canonical Codex-hook command envelope. */
export function toolCommand(tool, input) {
  const value = isObject(input) ? input : {};
  const name = String(tool || "").toLowerCase();

  if (name === "apply_patch" || name.endsWith("apply_patch")) {
    return firstString(value, ["patch", "diff", "command", "cmd"]);
  }

  if (["bash", "shell", "command", "terminal", "exec", "run"].includes(name)) {
    return firstString(value, ["command", "cmd", "script"]);
  }

  // Pass through a wrapper's shell command before structured-tool fallbacks.
  const nativeCommand = firstString(value, ["command", "cmd"]);
  if (nativeCommand) return nativeCommand;

  const paths = stringList(value, [
    "filePath",
    "file_path",
    "filepath",
    "path",
    "directory",
    "dir",
    "file",
    "files",
  ]);
  const pathArgs = paths.map(quoteShell).join(" ");

  if (name === "read" || name.endsWith(".read") || name.includes("read")) {
    return pathArgs ? `cat -- ${pathArgs}` : undefined;
  }
  if (name === "list" || name === "ls" || name.endsWith(".list") || name.includes("list")) {
    return pathArgs ? `ls -- ${pathArgs}` : "ls -- .";
  }
  if (name === "grep" || name === "search" || name.includes("grep") || name.includes("search")) {
    const pattern = firstString(value, ["pattern", "query", "regex", "search"]) || "*";
    return `rg -- ${quoteShell(pattern)}${pathArgs ? ` ${pathArgs}` : " ."}`;
  }
  if (name === "glob" || name.includes("glob")) {
    const pattern = firstString(value, ["pattern", "glob", "query"]) || "*";
    const base = firstString(value, ["path", "directory", "dir"]);
    return `rg --files -g ${quoteShell(pattern)}${base ? ` ${quoteShell(base)}` : " ."}`;
  }
  if (
    name === "write" ||
    name === "edit" ||
    name === "replace" ||
    name.includes("write") ||
    name.includes("edit")
  ) {
    return pathArgs ? `touch -- ${pathArgs}` : undefined;
  }

  return undefined;
}

export function namespaceSessionId(sessionID, location) {
  const session = String(sessionID || "unknown");
  const cwd = String(location || "unknown");
  return `opencode2:${cwd}:${session}`;
}

export function makePayload({ cwd, sessionID, tool, input }) {
  const command = toolCommand(tool, input);
  if (!command || typeof cwd !== "string" || !cwd) return undefined;
  return {
    cwd,
    session_id: namespaceSessionId(sessionID, cwd),
    tool_name: String(tool || ""),
    tool_input: { command },
  };
}

function hookPath() {
  return process.env.OPENCODE_CLAUDE_RULES_HOOK || DEFAULT_HOOK_PATH;
}

function parseHookOutput(stdout) {
  const text = String(stdout || "").trim();
  if (!text) return undefined;
  try {
    const parsed = JSON.parse(text);
    const context = parsed?.hookSpecificOutput?.additionalContext;
    return typeof context === "string" && context.trim() ? context.trim() : undefined;
  } catch (error) {
    diagnostic("hook output parsing", error);
    return undefined;
  }
}

function runPython(executable, args, input, timeoutMs = HOOK_TIMEOUT_MS) {
  return new Promise((resolve, reject) => {
    const child = spawn(executable, args, { stdio: ["pipe", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    let settled = false;
    const timer = setTimeout(() => {
      child.kill("SIGTERM");
      if (!settled) {
        settled = true;
        reject(new Error(`timeout after ${timeoutMs}ms`));
      }
    }, timeoutMs);
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => (stdout += chunk));
    child.stderr.on("data", (chunk) => (stderr += chunk));
    child.once("error", (error) => {
      clearTimeout(timer);
      if (!settled) {
        settled = true;
        reject(error);
      }
    });
    child.once("close", (code, signal) => {
      clearTimeout(timer);
      if (settled) return;
      settled = true;
      resolve({ code, signal, stdout, stderr });
    });
    child.stdin.end(input);
  });
}

export function createHookRunner({
  executable = DEFAULT_PYTHON,
  script = hookPath(),
  timeoutMs = HOOK_TIMEOUT_MS,
  run = runPython,
} = {}) {
  return async function runHook(event, payload) {
    try {
      const result = await run(executable, [script, event], `${JSON.stringify(payload)}\n`, timeoutMs);
      if (result?.stderr) diagnostic(`${event} hook`, compact(result.stderr));
      if (result?.code !== 0) {
        diagnostic(`${event} hook`, `exit ${result?.code ?? "unknown"}`);
        return { ok: false };
      }
      return { ok: true, additionalContext: parseHookOutput(result.stdout) };
    } catch (error) {
      diagnostic(`${event} hook`, error);
      return { ok: false };
    }
  };
}

function keyFor(sessionID, location) {
  const source = `${namespaceSessionId(sessionID, location)}\n${location}`;
  return `${STORAGE_PREFIX}${createHash("sha256").update(source).digest("hex")}`;
}

function payloadKey(payload) {
  return `${payload.tool_name}\n${payload.tool_input?.command || ""}`;
}

async function getState(storage, key) {
  try {
    const state = await storage.get(key);
    if (!isObject(state)) return { version: 1, pending: [] };
    const pending = Array.isArray(state.pending)
      ? state.pending
          .filter((item) => isObject(item) && isObject(item.payload))
          .slice(-MAX_PENDING_OPERATIONS)
      : [];
    return { version: 1, pending };
  } catch (error) {
    diagnostic("storage read", error);
    return { version: 1, pending: [], failed: true };
  }
}

async function putState(storage, key, state) {
  try {
    const pending = (Array.isArray(state.pending) ? state.pending : [])
      .filter((item) => isObject(item) && isObject(item.payload))
      .slice(-MAX_PENDING_OPERATIONS)
      .map((item) => ({
        ...item,
        instructions: compact(item.instructions, MAX_INSTRUCTION_LENGTH),
      }));
    await storage.set(key, { version: 1, pending });
    return true;
  } catch (error) {
    diagnostic("storage write", error);
    return false;
  }
}

export function extractToolText(result) {
  if (typeof result === "string") return result;
  if (isObject(result)) {
    if (typeof result.output === "string") return result.output;
    if (typeof result.content === "string") return result.content;
    if (Array.isArray(result.content)) {
      return result.content
        .map((part) => {
          if (typeof part === "string") return part;
          if (isObject(part) && typeof part.text === "string") return part.text;
          return "";
        })
        .filter(Boolean)
        .join("\n");
    }
  }
  return "";
}

async function sessionLocation(ctx, sessionID, cache) {
  if (cache.has(sessionID)) return cache.get(sessionID);
  try {
    const session = await ctx.session.get({ sessionID });
    const directory = session?.location?.directory;
    if (typeof directory === "string" && directory) {
      cache.set(sessionID, directory);
      return directory;
    }
  } catch (error) {
    diagnostic("session lookup", error);
  }
  return undefined;
}

function uniqueInstructions(items) {
  return [...new Set(items.flatMap((item) => String(item || "").split("\n").map((line) => line.trim()).filter(Boolean)))];
}

function appendSystemPart(context, instructions) {
  const unique = uniqueInstructions(instructions);
  if (!unique.length) return;
  const text = unique.join("\n");
  if (!Array.isArray(context.system)) context.system = [];
  if (!context.system.some((part) => part?.type === "text" && part?.text === text)) {
    context.system.push({ type: "text", text });
  }
}

/** Keep mapping, persistence, and hook calls testable without the OpenCode SDK. */
export function createBridge(ctx, { runHook = createHookRunner(), locationCache = new Map() } = {}) {
  const registrations = [];
  let stopped = false;

  async function locate(sessionID) {
    return sessionLocation(ctx, sessionID, locationCache);
  }

  async function before(input) {
    const cwd = await locate(input.sessionID);
    const payload = makePayload({ cwd, sessionID: input.sessionID, tool: input.tool, input: input.input });
    if (!payload) return;
    const result = await runHook("pre-tool-use", payload);
    if (!result.ok || !result.additionalContext) return;
    const key = keyFor(input.sessionID, cwd);
    const state = await getState(ctx.storage, key);
    const operationKey = payloadKey(payload);
    const existing = state.pending.find((item) => item.key === operationKey);
    const item = { key: operationKey, payload, instructions: result.additionalContext };
    if (existing) Object.assign(existing, item);
    else state.pending.push(item);
    await putState(ctx.storage, key, state);
  }

  async function after(input) {
    if (input.status !== "completed") return;
    const cwd = await locate(input.sessionID);
    const payload = makePayload({ cwd, sessionID: input.sessionID, tool: input.tool, input: input.input });
    if (!payload) return;
    await runHook("post-tool-use", { ...payload, tool_response: extractToolText(input.result) });
  }

  async function context(input) {
    const cwd = await locate(input.sessionID);
    if (!cwd) return;
    const key = keyFor(input.sessionID, cwd);
    const state = await getState(ctx.storage, key);
    const next = [];
    const instructions = [];
    for (const item of state.pending) {
      const result = await runHook("pre-tool-use", item.payload);
      if (!result.ok) {
        next.push(item);
        instructions.push(item.instructions);
      } else if (result.additionalContext) {
        item.instructions = result.additionalContext;
        next.push(item);
        instructions.push(result.additionalContext);
      } else next.push({ ...item, acknowledged: true });
    }
    await putState(ctx.storage, key, { pending: next });
    appendSystemPart(input, instructions);
  }

  async function compacted(event) {
    const sessionID = event?.sessionID || event?.properties?.sessionID || event?.data?.sessionID;
    if (typeof sessionID !== "string") return;
    const cwd = await locate(sessionID);
    if (!cwd) return;
    const payload = { cwd, session_id: namespaceSessionId(sessionID, cwd) };
    await runHook("post-compact", payload);
    // Keep pending operations: post-compact clears acknowledgements, so context re-arms them.
  }

  async function subscribe() {
    try {
      const source = await ctx.event.subscribe();
      const iterator = source?.[Symbol.asyncIterator]?.();
      if (!iterator) return undefined;
      const consume = (async () => {
        try {
          while (!stopped) {
            const step = await iterator.next();
            if (step.done) break;
            const event = step.value;
            if (event?.type === "session.compaction.ended") await compacted(event);
          }
        } catch (error) {
          if (!stopped) diagnostic("event subscription", error);
        }
      })();
      return { iterator, consume };
    } catch (error) {
      diagnostic("event subscription", error);
      return undefined;
    }
  }

  return {
    async install() {
      registrations.push(await ctx.tool.hook("execute.before", before));
      registrations.push(await ctx.tool.hook("execute.after", after));
      registrations.push(await ctx.session.hook("context", context));
      const subscription = await subscribe();
      return async () => {
        stopped = true;
        if (subscription?.iterator?.return) {
          try {
            await subscription.iterator.return();
          } catch (error) {
            diagnostic("event cleanup", error);
          }
        }
        await Promise.all(
          registrations
            .filter(Boolean)
            .map(async (registration) => {
              try {
                await registration.dispose?.();
              } catch (error) {
                diagnostic("hook cleanup", error);
              }
            }),
        );
      };
    },
    before,
    after,
    context,
    compacted,
    get stopped() {
      return stopped;
    },
  };
}

export { diagnostic, keyFor, quoteShell };
