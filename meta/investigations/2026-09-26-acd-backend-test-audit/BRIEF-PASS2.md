# Backend test audit — pass 2 brief (verify)

You verify pass-1 findings for the backend tests in `/Users/preetamnath/Desktop/code/agentchatdeck`. You are a subagent: do not spawn subagents.

## Context

Pass 1 applied our test rules to every backend test and flagged some as Repair, Merge, Remove, or Investigate. Pass-1 reviewers can misread code. Your job is to confirm or demote each flagged verdict against the source, adversarially. Do not trust the pass-1 reasoning; re-derive it.

Rules (read first, in full):
1. `/Users/preetamnath/.codex/AGENTS.md`, section `## Testing` (lines 53-55). The file on disk is canonical; it says "a required behavior or contract".
2. `/Users/preetamnath/Desktop/code/agent-skills/skills/prove-behavior/SKILL.md`.
3. Repo conventions: `backend/tests/AGENTS.md` and `backend/tests/CLAUDE.md` in the repo.

The pass-1 brief is at `/private/tmp/claude-501/-Users-preetamnath-Desktop-code-agent-skills/064f5753-127c-4033-ab84-329a86322a7b/scratchpad/audit/BRIEF.md` (verdict definitions).

## Constraints

- Report only. Do not edit, create, or delete any repo file. Do not run mutations. Tests cannot run on this machine (no `.venv`); judge from source.
- For every finding, read the test body and the production code it exercises. For Merge/Remove, open the named retained guard and confirm it detects the same defect.
- Depth order: Remove, Merge, Investigate first (these delete protection); then Repair.

## Per-finding judgment

For each row in the "Non-keep verdicts" tables of your assigned reports, return one of:

| Result | Meaning |
|---|---|
| Confirmed | The verdict and its reason hold. |
| Changed | A different verdict is right (say which: Keep / Repair / Merge / Remove / Investigate) and why. |
| Rejected | Pass 1 misread the code; the test is fine as is (Keep). |

Also judge the proposed fix or retained guard: correct, or what is wrong with it.

## Output

Write the full result to `/private/tmp/claude-501/-Users-preetamnath-Desktop-code-agent-skills/064f5753-127c-4033-ab84-329a86322a7b/scratchpad/audit/pass2-<GROUP>.md`:

```
# Pass 2 — <GROUP>

## Tally
| Pass-1 verdict | Flagged | Confirmed | Changed | Rejected |

## Per finding
| Test (file:line) | Pass-1 verdict | Result | Final verdict | Reason (file:line evidence) | Confidence 0.00-1.00 |

## Rule-caused errors
Pass-1 errors that the rules caused or allowed (not plain misreads). Quote the rule line and say what wording would have prevented the error.
```

Then return to the caller: the tally table, the list of Changed/Rejected findings (one line each), and the top rule-caused errors (one line each). Do not return the full report text.
