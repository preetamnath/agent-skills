---
name: prove-behavior
description: "Decide whether automated test evidence should change, choose the lowest test level that can detect the named material defect, and prove sensitivity. TRIGGER when: code changes observable behavior; adding, changing, deleting, or reviewing automated tests; checking that a test detects its claimed defect. SKIP when: only running existing checks or performing live post-ship verification (test-completed-plan)."
---

# Prove Behavior

A valid test distinguishes required behavior from a plausible, material defect. It continues to pass after an internal refactor that preserves the behavior.

## Steps

### Step 1 — Name the evidence

State:

- the required behavior;
- its accepted source: a requirement, acceptance criterion, contract, known bug, or recorded observation whose preservation is required;
- one plausible defect the evidence must detect;
- the meaningful harm that defect would cause.

Meaningful harm includes a broken user task, violated contract, corrupt data, weakened security or accessibility, or a repeated costly failure.

If no accepted source, named defect, or meaningful harm exists, choose `no automated test`.

A **speculative test** protects no current requirement, contract, known bug, or plausible material risk. Do not add it. A reachable edge case with meaningful harm is not speculative.

A **tautological test** derives its expected result from the same implementation logic that produces the actual result. Derive the expectation from the accepted source instead.

### Step 2 — Decide the evidence

1. Check whether a reliable existing test, type check, static check, or contract check detects the named defect in the normal verification command or CI. If it does, reuse it.
2. For a bug fix, find why reliable evidence did not fail. Add or change evidence only for a real behavior gap. If a guard existed but was skipped or absent from CI, repair its execution instead of duplicating it.
3. Do not add a separate UI text or presentation test when another test already proves the same behavior.
4. Add or retain automated evidence only when it gives unique protection worth its execution, maintenance, and context cost.

Choose the lowest test level that can detect the defect:

| Level | Use when |
|---|---|
| Unit test | One rule or module can prove the behavior. |
| Integration test | Application parts must work together to prove the behavior. |
| End-to-end test | The full application is necessary, and unit or integration tests cannot prove the critical behavior. |

Live verification proves the current result. It does not provide future automated protection. Route required post-ship verification to `test-completed-plan`.

### Step 3 — Shape the test

- **Interface:** Use an existing stable production interface that a real caller uses at the selected level. Do not expose private code or add a production interface only for testing.
- **Observation:** Prefer observable outputs and resulting state. Assert a call, order, or interaction only when that interaction is required behavior.
- **Collaborators:** Use real application collaborators when they are fast and predictable. Use test doubles only for external, uncontrollable, destructive, or expensive boundaries, or to force a failure.
- **Scope:** Group assertions and cases that protect the same behavior and fail for the same reason. Separate tests that detect different defects.
- **Races:** Force the intended interleaving and prove readiness with an event, barrier, or queue. Do not rely on sleeps or scheduler timing.

A **change-detector test** fails after an internal refactor even though behavior remains correct. Do not add one.

### Step 4 — Prove sensitivity

Writing a test before or after production code does not determine its value. Every admitted test must fail for its named defect and pass for the correct behavior.

Use the cheapest valid proof:

- **Natural red:** Run the test against the bug or missing behavior and require the expected assertion failure. Then run it after the correct implementation and require it to pass.
- **Targeted mutation:** When the behavior already works or an existing guard is unclear, introduce one small instance of the named defect and require the focused test to fail.
- **Removal or merge:** Introduce the defect guarded by the removed test and require the retained evidence to fail.

Count a failure only when the intended test runs and the named defect causes its assertion to fail. A syntax, collection, setup, harness, unrelated, or intermittent failure does not prove sensitivity.

For a temporary mutation:

1. Run the narrowest relevant test on the original implementation. Confirm that the selected test runs and passes.
2. Change only the guarded production behavior. Leave unrelated user changes untouched.
3. Confirm that the mutation exists and that the changed code still parses or compiles.
4. Rerun the same test. Require the expected assertion failure.
5. Restore only the temporary mutation. Confirm that no unrelated diff changed, then rerun the test and require it to pass.

### Step 5 — Report the decision

Return:

```
**Test evidence:**
- Decision: add | change | retain | reuse existing | remove | no automated test
- Behavior: <required behavior>
- Source: <accepted source>
- Defect: <plausible, material defect>
- Harm: <meaningful consequence>
- Existing evidence: <what already detects the defect | none>
- Level: unit | integration | end-to-end | none
- Proof: natural red | targeted mutation | removal or merge | not applicable
- Verification: <command and result>
- Live follow-up: test-completed-plan | none
- Durable note: <path and reason | none>
```

Keep ordinary proof evidence in the report. Add a durable test comment only when it preserves a non-obvious constraint, historical escape, race mechanism, or replacement relationship that future readers cannot reconstruct from the test.
