# Backend test audit — pass 1 brief

You audit one shard of the backend tests in `/Users/preetamnath/Desktop/code/agentchatdeck`. You are a subagent: do not spawn subagents.

## Purpose

We just updated our test rules. We want to learn what they do when applied to a real suite: which tests stay, which need repair, which would be removed. We also want to learn where the rules are unclear or give a doubtful verdict. Your report feeds both.

## Rules to apply (read these first, in full)

1. Global rule, `/Users/preetamnath/.codex/AGENTS.md`, section `## Testing` (lines 53-55).
2. Skill, `/Users/preetamnath/Desktop/code/agent-skills/skills/prove-behavior/SKILL.md` — the whole file. Pay special attention to Step 1 (accepted source, defect, harm), Step 2 (reuse existing evidence, unique protection, level table, and the "Before you remove or merge a test" block), Step 3 (interface, observation, change-detector), and Step 4.
3. Repo conventions: `/Users/preetamnath/Desktop/code/agentchatdeck/backend/tests/AGENTS.md`, `backend/tests/CLAUDE.md`, `backend/AGENTS.md`, `backend/CLAUDE.md`, and the root `AGENTS.md`/`CLAUDE.md` if present. Also `backend/tests/conftest.py` and `backend/tests/sessions_harness.py` as needed.

Apply only these rules. Do not bring in outside testing doctrine.

## Constraints

- Report only. Do not edit, create, or delete any file in the repo. Do not run mutations.
- You may run focused, read-only test commands (for example one test file with pytest) if you need to know whether a test currently passes. Find the right command in the repo docs. Do not run the whole suite.
- Ground every non-keep verdict in the test's actual assertion and the production code it exercises (file:line). Read the production code; do not judge from test names.
- Where a removal or merge would need a Step 4 "removal or merge" proof you did not run, mark `proof needed`.

## Verdicts (one per test function, or per group of tests with the same verdict and reason)

| Verdict | Meaning |
|---|---|
| Keep | Valid under the rules; unique protection. |
| Repair | Protects a real requirement but the assertion is weak, over-specified, unscoped, flaky-by-design, or a change-detector in part. Say the smallest fix. |
| Merge | Duplicates another test's protection for the same defect; say which test keeps it (the lowest level that detects it). |
| Remove | Speculative, tautological, change-detector, or no unique protection. Name what evidence still covers the defect, or say none is needed and why. |
| Investigate | Cannot decide from source; say exactly what is unresolved. |

## Output

Write your full report to `/private/tmp/claude-501/-Users-preetamnath-Desktop-code-agent-skills/064f5753-127c-4033-ab84-329a86322a7b/scratchpad/audit/pass1-<SHARD>.md` (this scratchpad file is the one file you may write). Use this shape:

```
# Pass 1 — <SHARD>

## Summary
| File | Tests | Keep | Repair | Merge | Remove | Investigate |
(one row per file, plus a total row; count test functions, parametrized cases count once)

## Non-keep verdicts
| Test (file:line) | Verdict | Required behavior / source | Named defect | Evidence (test + prod file:line) | Smallest fix or remaining guard | Confidence 0.00-1.00 |

## Notable keeps
Up to 10 keeps that a naive reader might wrongly remove (static/cross-file/contract checks, interaction assertions that are the requirement, race tests). One line each with why it stays.

## Rule feedback
Each place the global rule or prove-behavior was unclear, silent, conflicting, or pushed you toward a verdict you doubt. Quote the rule line, give the test example, and propose the smallest wording change if you have one. Confidence 0.00-1.00 each.
```

Then return to the caller: the summary table's total row, the count of non-keep verdicts by type, your top 5 most confident non-keep verdicts (one line each), and your top 3 rule-feedback items (one line each). Do not return the full report text.
