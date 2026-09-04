---
name: prove-behavior
description: "Choose the smallest valuable automated test evidence and prove it can detect the defect it guards. TRIGGER when: behavior-changing work needs a test decision; adding, changing, deleting, or reviewing tests; a test may be vacuous. SKIP when: only running existing checks or completing live post-ship verification (use test-completed-plan)."
---

# Prove Behavior

Treat each test as evidence against a named defect.

## Steps

### Step 1 — Name the evidence

State:

- the behavior to protect;
- one plausible defect the evidence must detect;
- the independent source of the expected behavior: a requirement, acceptance criterion, bug report, external contract, or recorded observation whose preservation is required.

Do not derive the expected result only from the implementation under test. If no independent expectation exists, identify the gap instead of encoding the current code as correct.

### Step 2 — Decide admission

Check whether an existing test, type check, static check, contract check, or live verification already detects the named defect. Add or retain automated test evidence only when its unique protection is worth its execution, maintenance, and context cost.

Choose the smallest faithful observation point:

- use a type or static check for structural guarantees;
- use a narrow behavior test for pure logic or state transitions;
- use an integration test with real local components when the defect crosses their boundary;
- reserve live or end-to-end verification for behavior smaller tests cannot observe.

Require each new test to detect a distinct defect or observe a necessary boundary; a changed method or file alone does not justify one.

### Step 3 — Shape the test

- **Interface:** Exercise the behavior through the narrowest stable interface.
- **Observation:** Prefer outputs and resulting state over private helpers, call order, or mock interactions.
- **Collaborators:** Use real local collaborators when they are deterministic and cheap; use fakes to control failures or interleavings, or to isolate uncontrollable, remote, destructive, or expensive boundaries.
- **Scope:** Make each test describe one behavior.
- **Cases:** Combine cases when they exercise the same rule and would fail for the same reason.
- **Races:** Force the intended interleaving and prove readiness with an event, barrier, or queue rather than sleeps or scheduler timing.

### Step 4 — Prove sensitivity

Use the cheapest proof that the test detects its named defect:

- **Bug or test-first change:** observe the test fail against the bug or missing behavior before the implementation makes it pass.
- **Completed non-obvious logic:** introduce one small, plausible defect in the guarded branch, operator, state transition, fence, or ordering rule and observe the focused test fail.
- **Existing guard:** when relying on an existing test whose sensitivity is unclear, introduce the named defect and observe it fail.
- **Literal round-trip:** treat an explicit input and expected output, literal value, or rendered-string assertion as self-proving when a mutation would add no information.
- **Test deletion or merge:** introduce the defect guarded by the removed test and confirm the retained evidence fails.

Count a failure only when the intended test runs and the named defect causes the failure; syntax, collection, setup, harness, or unrelated failures do not prove sensitivity.

Treat an intermittent result as unresolved, not as proof.

For a temporary mutation:

1. Run the narrowest relevant test on the original implementation and confirm the selected test is collected and passes.
2. Change only the guarded production behavior; leave unrelated user changes untouched.
3. Confirm the mutation was applied and the mutated code still parses or compiles.
4. Rerun the same test and require the expected assertion failure.
5. Restore only the temporary mutation, confirm no unrelated diff changed, and rerun the same test to prove it passes again.

### Step 5 — Report the proof

Return:

```
**Test evidence:**
- Decision: add | change | retain | reuse existing | no automated test
- Behavior: <protected behavior>
- Defect: <plausible failure>
- Source: <requirement, acceptance criterion, bug report, contract, or recorded observation>
- Proof: natural red | targeted mutation | self-proving assertion | existing evidence | live verification
- Verification: <command and result>
- Durable note: <path and reason | none>
```

Keep ordinary proof evidence in the report. Add a durable test comment only when it preserves a non-obvious constraint, historical escape, race mechanism, or replacement relationship that future readers cannot reconstruct from the test.
