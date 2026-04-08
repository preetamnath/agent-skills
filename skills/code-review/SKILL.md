---
name: code-review
description: "Structured code review with P0-P3 findings, confidence scores, and criteria-based analysis. Use for reviewing code changes, PRs, or specific files."
---

# Code Review

Analyze code changes for correctness, security, edge cases, and quality. Return structured findings in the Finding schema v1.

## When to use

- Reviewing code changes (staged, unstaged, or specific commits)
- Reviewing specific files or file sets
- Quick structured review of a PR or branch

For full two-pass review with adversarial verification, use `/two-pass-review` instead.

## Instructions

### Step 1 — Read the output schema

Read `references/finding-schema-v1.md` to understand the required output format.

### Step 2 — Gather the artifact

Determine what to review:
- If the user specified files: read those files
- If the user specified a diff range: run `git diff <range>`
- Otherwise: run `git status` and `git diff` to see current changes

For modified files, review the diff. For untracked files, read the full content. For deleted files, check for broken references.

If related files are needed for context (types, interfaces, callers), read them too.

### Step 3 — Automated checks

If the project supports it:
- Read `package.json` to check available scripts
- If a `lint` script exists, run it
- If `tsconfig.json` exists, run `npx tsc --noEmit`
- Note any failures as P0/P1 findings

### Step 4 — Analyze

Review the code for:
- **Correctness** — does the code do what it's supposed to?
- **Security** — injection, unauthorized access, data exposure?
- **Edge cases** — unhandled scenarios, boundary conditions?
- **Bugs** — obvious errors, off-by-one, null references?
- **Performance** — inefficient patterns (only flag with evidence)?

Do NOT flag: style preferences, naming opinions, theoretical risks without evidence, or things you'd do differently but aren't wrong.

### Step 5 — Return findings

Return a `ReviewOutput` envelope conforming to the Finding schema v1 (see `references/finding-schema-v1.md`).

- Set `verdict` and `evidence` to `null` on all findings
- Include honest `confidence` scores — 1.0 means certain, below 0.5 means you're guessing
- Populate `checks_run` with what you evaluated (files, criteria, lint/typecheck results)
- If no issues are found, return an empty findings array — don't manufacture problems

## Constraints

- Do NOT implement fixes unless explicitly asked
- Report only — present findings for the user to review
