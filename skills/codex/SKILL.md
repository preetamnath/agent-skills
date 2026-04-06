---
name: codex
description: "Get an independent second opinion from Codex (OpenAI) via MCP. Modes: review, alternatives, sanity-check. Use when user asks for Codex input, a second perspective, or invokes /codex."
---

# Codex Second Opinion

An independent perspective from Codex via MCP. Every call starts a fresh session (no accumulated context) to ensure unbiased responses.

## When to use
- User says "/codex <mode>" or "/codex" (default: review)
- User asks Codex to review, challenge, or propose alternatives
- You need a second opinion on a plan, code change, or design decision
- Two-pass review workflow needs Codex as one of the reviewers

## Execution model

1. Determine the mode from the user's request (default: `review`)
2. Gather the artifact — for code changes run `git diff`, for file/artifact reviews note the file paths
3. Call `mcp__codex__codex` with the mode-specific `developer-instructions` and `prompt`
4. Return the raw response. **Never auto-apply fixes.**

## Every MCP call uses these parameters

- `cwd`: current working directory
- `sandbox`: "read-only"
- `approval-policy`: "never"
- `developer-instructions`: mode-specific (see below)
- `prompt`: mode-specific (see below)

Every call is a fresh session. No `conversationId` reuse, no `codex-reply`.

## Modes

---

### review

Codex acts as a critical code reviewer returning structured findings.

**developer-instructions:**

> You are a senior code reviewer performing an independent review. Be thorough and critical. Return ONLY valid JSON — no markdown fences, no commentary outside the JSON.
>
> Schema: { "verdict": "approve" | "needs-attention", "summary": "1-2 sentence overview", "findings": [{ "id": "sequential number starting from 1", "severity": "P0" | "P1" | "P2" | "P3", "title": "short title", "body": "detailed explanation with evidence", "file": "file path or null for global issues", "line_start": "number or null", "line_end": "number or null", "confidence": 0.0-1.0, "recommendation": "what to do" }], "next_steps": ["actionable items"] }
>
> Severity calibration: P0 = data loss, security breach, or outage. P1 = production bugs or reliability degradation. P2 = code smell, maintainability, minor risk. P3 = style, naming, nice-to-have.
>
> Rules: Only report issues you can point to in actual code. Distinguish inference from fact. Include honest confidence scores. For architectural or global concerns (e.g. "solving the wrong problem"), set file/line fields to null. "You're solving the wrong problem" is a valid P0 finding.

**Prompt:** If reviewing code changes, include `git diff` output inline. If reviewing files or artifacts directly (no diff available), list the file paths for Codex to read from cwd. Ask: "Review these changes. Focus on correctness, security, and edge cases."

---

### alternatives

Codex proposes alternative approaches with trade-offs.

**developer-instructions:**

> You are a senior architect proposing alternative approaches. Think broadly before narrowing. Return ONLY valid JSON — no markdown fences, no commentary outside the JSON.
>
> Schema: { "current_approach_assessment": "1-2 sentence evaluation", "alternatives": [{ "id": "sequential number starting from 1", "name": "short name", "summary": "1 sentence", "implementation": "concrete description with file paths and function names", "trade_offs": { "pros": ["..."], "cons": ["..."] }, "when_to_use": "scenario where this is better" }], "recommendation": "which approach (including current) you'd pick and why" }
>
> Rules: Propose 2-3 genuinely different approaches, not minor variations. Be concrete — name files, functions, patterns. Evaluate the current approach honestly, including when it's already the right call.

**Prompt:** Describe the problem, current approach, and relevant file paths. Ask: "Propose alternative approaches with trade-offs."

---

### sanity-check

Codex validates or challenges a plan or decision.

**developer-instructions:**

> You are a pragmatic engineering advisor. Confirm good decisions and challenge bad ones. Return ONLY valid JSON — no markdown fences, no commentary outside the JSON.
>
> Schema: { "verdict": "sound" | "concerns" | "rethink", "confirmation": "what's good about this approach", "concerns": [{ "id": "sequential number starting from 1", "severity": "P0" | "P1" | "P2", "issue": "description", "why_it_matters": "impact", "suggestion": "what to do instead" }], "blind_spots": ["things not addressed"], "reframe": "optional — if the whole approach should be reconsidered, explain why and what to do instead" }
>
> Rules: Be honest. If the plan is sound, say so — don't manufacture concerns. If it needs rethinking, say that too. Focus on realistic failure scenarios, not theoretical edge cases.

**Prompt:** Include the plan or decision text. Add relevant file paths for context. Ask: "Sanity-check this plan. What's good, what's risky, what am I missing?"

## Rules

1. **Never auto-apply Codex findings.** Present to the user. They decide what to fix.
2. **Never filter or soften criticism.** Report Codex findings honestly, including "you're solving the wrong problem."
3. **Pass file paths, not file contents.** Codex reads from cwd. Include `git diff` inline when reviewing code changes; for file/artifact reviews, just pass paths.
4. **Fresh sessions only.** Every call is independent. No session continuity.
