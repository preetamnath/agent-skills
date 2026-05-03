# Codex MCP Conventions

Shared boilerplate for agents that route requests to Codex (OpenAI) via the `mcp__codex__codex` tool. Inlined by `codex-code-review`, `codex-sanity-checker`, and `codex-propose-alternatives`.

Each agent inlines two blocks below: the **MCP call parameters** (used inside the "Construct the MCP call" execution step) and the **Rules** section (appended at the end, before the per-mode Output Schema appendix). The `prompt` and `developer-instructions` templates and the Output Schema are mode-specific and stay inline in each agent.

Each inlined block carries a suffixed marker so the propagation grep can disambiguate them: `<!-- source: references/codex-mcp-conventions.md (params) -->` precedes the parameters block; `<!-- source: references/codex-mcp-conventions.md (rules) -->` precedes the Rules block. Update both locations when this SoT changes.

Note: rule 5 is intentionally per-mode customized in each agent — the canonical wording below is a superset listing all three payload types, but each agent narrows it to its own ("Only inline git diff output." / "Only inline plan text." / "Only inline problem/approach text."). Drift is by design.

## MCP call parameters

Use these exact parameters (do not add, remove, or rename — and never pass `conversationId` or `threadId`; every call is a fresh session):

```
cwd: <working directory from your environment context — never guess or hardcode>
sandbox: "read-only"
approval-policy: "never"
developer-instructions: <see template below; insert the full Output Schema where {SCHEMA} appears>
prompt: <see template below; substitute placeholders>
```

## Rules

1. **Never auto-apply Codex findings.** Return to parent. User decides what to fix.
2. **Never filter or soften.** Report Codex response exactly, including harsh findings.
3. **Safety parameters are invariant.** `sandbox` is always `"read-only"`, `approval-policy` is always `"never"`. No exceptions.
4. **Fresh sessions only.** No `conversationId`, no `threadId`, no `codex-reply`.
5. **Pass file paths, not contents.** Codex reads from cwd. Only inline the small per-mode payload (e.g., git diff output, plan text, or problem/approach text) that Codex needs verbatim.
6. **On MCP failure, return the error verbatim.** Do not retry.
