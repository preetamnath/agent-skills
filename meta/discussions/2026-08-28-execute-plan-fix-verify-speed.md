# Execute-plan critical-path analysis

- **Date:** 2026-08-29
- **Status:** Walkthrough in progress — resolver changes implemented; remaining recommendations pending
- **Scope:** Completed SPEC-027 `execute-plan` run through its final `turn_done`; initial SPEC-028, SPEC-029, and SPEC-030 runs supply comparison data
- **Excluded:** SPEC-027 deployment, post-ship testing, push, and later miscellaneous UI work
- **Resume:** Discuss Recommendation 2's durable-docs scheduling next.

## Answer

The completed run confirms that the main slowdown is a workflow shape, not only feature size. `[verified, 0.99]`

The user supplied this run-level override after Wave 2:

```text
parallel read-only pre-gates
-> one fixer for related findings
-> parallel per-finding verification
-> unchanged regression and final reviews
```

The executor followed it from Wave 3 onward. It produced no staged-write collision, kept a separate verdict for every finding, and still found interaction defects in later regression passes. The source `fix-verify-loop` skill now implements this shape: related findings share batches of at most four, independent verifier and fixer groups run concurrently, overlapping findings use one fixer, every finding keeps its own outcome, and the parent stages groups sequentially. `[verified, 0.99]`

Two other measured opportunities rank above context-packet optimization:

1. Do not run the full durable-docs sweep before a known ship-debt build and then run it again after the code changes. `[recommendation, long-term, 0.98]`
2. Remove avoidable question waits by locking shared defaults before execution and proving same-round fixer-owned staging. `[recommendation, long-term, 0.95]`

## Evidence

### Boundary and method

The audit queried `/root/.local/share/agentchatdeck/app.db` read-only. SPEC-027 starts at user event `285087` and spans two parent turns because the first provider stream ended unexpectedly. The exact boundary is the recovery turn's `turn_done` at `2026-08-29T03:09:25Z`, after commit `d7cf671` froze the plan. Later work is excluded. `[verified, 1.00]`

Subagent ends were de-duplicated by `subagent_id` with last-end-wins. Child token counters show scale but are not clean marginal usage because follow-ups can reuse a provider child thread and report cumulative context. `[verified, 0.96]`

### Completed SPEC-027 shape

| Measure | Result |
|---|---:|
| Parent wall span | 14.76 h |
| Visible subagent runs | 188 started, 187 ended |
| Child active time, summed | 20.62 h |
| Reported child tokens | 24.34 M |
| Parent wait calls | 389 |
| Implementation waves | 7, including ship debt |
| Review findings recorded | 59 across wave units and final review |

The unmatched child was a Wave 7 diagnosis started 45 seconds before the disconnect. Recovery used the durable plan state and did not repeat a wave. `[verified, 0.99]`

### Cross-run resolver scale

Resolver calls include pre-gates, fixers, post-fix verifiers, and fix-regression work. Active wall is the union of child intervals, not summed overlapping time.

| Spec | Parent span | Subagents | Reported tokens | Resolver calls | Resolver active wall | Resolver tokens |
|---|---:|---:|---:|---:|---:|---:|
| 028 | 21.29 h | 121 | 15.23 M | 75 | 5.92 h | 7.85 M |
| 029 | 8.37 h | 111 | 15.00 M | 31 | 2.21 h | 3.51 M |
| 030 | 16.20 h | 135 | 17.81 M | 59 | 4.51 h | 8.10 M |
| 027 | 14.76 h | 188 | 24.34 M | 99 | 6.67 h | 11.95 M |

SPEC-027's count is broad: it includes related lower-severity verification, regression fixes, the final-review fix, and the final-suite regression fix. This proves recurrence and scale, not that all resolver time is removable. `[verified, 0.97]`

### Before and after the batching instruction

Wave 2 used the source skill's serial shape for five related P1s in `stt_service/service.py` and its tests:

```text
F1 pre-gate -> fix -> verify
F2 pre-gate -> fix -> verify
F3 pre-gate -> fix -> verify
F4 pre-gate -> fix -> verify
F5 pre-gate -> fix -> verify
```

The five pre-gates consumed 16.0 child minutes. The longest was 4.2 minutes, so parallelizing only that read-only phase had an 11.8-minute upper-bound wall saving. Five fixers also repeated the same focused service suite and mutation setup against overlapping state. `[verified, 0.99]`

After the instruction:

| Unit | Read-only checks | Mutation lane | Post-fix checks |
|---|---|---|---|
| Wave 3 | 3 parallel P1 pre-gates | 1 coupled installer fixer | 3 parallel verdicts |
| Wave 4 | 1 P1 pre-gate | 1 coupled recovery fixer | 6 parallel related verdicts |
| Wave 5 | 2 parallel P1 pre-gates | 1 coupled runtime fixer | parallel per-finding verdicts |
| Wave 6 | 6 parallel finding checks | 1 coupled composer fixer | 6 parallel verdicts; one bounded retry |
| Wave 7 | 2 review seats in parallel | 1 shared-lifecycle fixer | separate verifier plus regression review |

The safe split held: read-only checks fanned out; overlapping writes stayed in one fixer; disjoint implementation groups fanned out; staging remained sequential. Regression review still found cross-fix interactions in Waves 3–6, so that gate remains necessary. `[verified, 0.99]`

### Blocking questions

Only two question cards blocked execution, both before the user's standing autonomy instruction:

| Question | Wait | Better prevention |
|---|---:|---|
| Choose shared STT port | 29.0 min | Lock the service/client default in technical design or the plan packet |
| Accept same-round fixer-staged hunks | 9.7 min | Snapshot the index before dispatch and prove fixer ownership |

After the user authorized high-confidence reversible recommendations, no further question card blocked execution. Contract changes, deployment, external state, and unresolved risk remained outside that authority. `[verified, 0.99]`

The port wait is mainly an upstream specification gap. Two parallel tasks needed one literal, but the locked design specified loopback reachability without selecting the port. Relaxing all contract gates is not the right fix. `[verified, 0.96]`

The staging wait is narrower. The fixer staged its own two files before returning. The current skill can reuse hunks from an earlier resolved finding, but cannot prove same-round fixer ownership because it records staged state after fixer dispatch. `[verified, 0.98]`

### Duplicate durable-docs work

SPEC-027 had 11 untriaged debt entries after final review, so another code wave was predictable. The workflow still ran a plan-wide docs/comment sweep before debt triage, then a second debt-scoped sweep after Wave 7.

| Sweep | Runs | Child time | Wall time | Reported tokens |
|---|---:|---:|---:|---:|
| Before ship debt | 8 | 31.5 min | 14.9 min | 1.50 M |
| After ship debt | 6 | 33.9 min | 16.6 min | 0.71 M |

When untriaged debt exists, defer the first sweep and run one final sweep over `$PLAN_BASE_SHA..HEAD` after debt closes. This preserves coverage and removes predictable duplication. `[recommendation, long-term, 0.98]`

### Other hiccups

- The first parent turn ended after 13.9 hours. Automated `Continue` began recovery about 20 seconds later. Existing resume markers worked; this run does not justify new resumability logic. `[verified, 0.98]`
- The first full backend suite ran in the restricted Codex sandbox and hung on Starlette cross-thread wakeup. Diagnosis cost about 10 minutes. The run added the root `CLAUDE.md` instruction, so this recurrence is already addressed locally. `[verified, 0.99]`
- The final frontend suite found a real Slash-menu disabled-state regression missed by focused checks and reviewers. Keep the full final suite. `[verified, 1.00]`
- Wait cards mostly overlap child execution. Optimizing their display or polling does not shorten the mutation/review path. `[verified, 0.99]`

## Recommendations

### 1. Make the field-tested resolver shape durable

**Recommendation:** Change `skills/fix-verify-loop/SKILL.md` in two small commits. `[long-term, 0.99]`

1. **Parallel pre-gate phase.** Verify all unverified P0/P1 findings before mutation. Use one merged verifier for up to four related findings; otherwise split by shared files, symbols, or call chains and run those read-only batches in parallel. Return one verdict per finding.
2. **Conflict-group mutation phase.** Put findings that share files, tests, symbols, mutable artifacts, call chains, or a root cause into one fixer. Run fixers concurrently only for proven-disjoint paths and checks. Stage groups sequentially. Verify every finding separately, with the two-attempt bound retained per finding.

Fail closed when overlap is uncertain. Cap ordinary groups at four unless one root cause cannot split safely. Preserve every finding's verdict, retry, and escalation state. `[recommendation, 0.97]`

The first commit is the smallest safe gain. The second has a successful four-unit multi-finding field test, but changes the mutation contract and should land separately. `[recommendation, 0.98]`

**Walkthrough status:** The parallel pre-gate phase is implemented in `208f387`. Conflict-group mutation, parallel grouped verification, and parent-only sequential staging are implemented in `79f56d3`. The current full-file refinement preserves that behavior and adds parent-side validation of every returned path before staging. `[verified, 0.99]`

### 2. Run durable-docs once after the last code phase

**Recommendation:** In `skills/execute-plan/SKILL.md`, if Step 5 sees any untriaged `[Future]` or `[deferred]` entry, defer the sweep until Step 6.2 closes. Run it over `$PLAN_BASE_SHA..HEAD`, then write the completion record and freeze. With no untriaged debt, keep the existing path. `[long-term, 0.98]`

This changes scheduling, not documentation coverage or freeze ordering. `[verified, 0.99]`

### 3. Remove the two proven question traps

**Shared defaults:** Add a technical-design or write-plan completeness check: every literal/default consumed by two or more tasks must have one named owner and value, or be an explicit user decision before execution. `[long-term, 0.94]`

**Same-round staging:** In `fix-verify-loop`, record the path-scoped staged diff before fixer dispatch. If it was clean, no other mutator ran, and the returned staged change is confined to approved returned files, proceed and record fixer ownership. Any pre-existing hunk, out-of-scope path, mismatch, concurrent mutator, or external index change keeps the current question. Also tell fixers not to run `git add`. `[long-term, 0.97]`

**Walkthrough status:** The accepted implementation prevents the same-round staged state: fixers never run `git add`; the parent snapshots the path-scoped index before dispatch, validates the returned paths, and stages one group at a time. Any unexpected index or path change remains user-gated. `[verified, 0.99]`

### 4. Send a bounded execution packet

**Recommendation:** Give each resolver agent one immutable packet: finding set, criteria, approved paths, governing path rules, review range, staged diff, and prior-attempt evidence. Use task-only child history when supported. Agents still read current source and required repository instructions. `[long-term, 0.87]`

**Walkthrough status:** `execute-plan` and `execute-chat` now pass the resolver's required findings, approved artifact paths, and governing criteria explicitly at every call site. Paths named only by a finding still require the resolver's scope-expansion gate. The resolver remains responsible for adding path rules, the exact staged diff, and prior-attempt evidence to each child dispatch. Its output now returns every validated path with remaining staged fix-loop changes, and `execute-chat` adds those paths to its collected scope. `[verified, 0.99]`

Measure this after Recommendations 1–3. Wall time and repeated tool reads are better measures than cumulative token counters. `[recommendation, 0.92]`

## Keep these gates

- **Regression review:** It found real interactions after individually verified fixes. `[verified, 1.00]`
- **Final review and one automatic re-review:** The second five-seat panel took about five wall minutes because seats ran in parallel. Narrowing it adds complexity for little saving. `[verified, 0.97]`
- **Final full checks:** They caught the Slash-menu regression. Keep backend and frontend full suites sequential on this VPS. `[verified, 1.00]`
- **Per-finding verdicts:** Group mutation work, not result accounting. `[verified, 0.99]`
- **Fail-closed writes:** Parallelize only disjoint files and checks. `[verified, 1.00]`

## Decision order

| Order | Change | Expected impact | Confidence |
|---|---|---|---:|
| 1 | Parallel pre-gates, then conflict-group fixers | Largest repeated resolver-path reduction | 0.99 |
| 2 | Defer the first docs sweep when debt is pending | Up to 14.9 measured duplicate wall minutes; remeasure the combined sweep | 0.98 |
| 3 | Prove same-round staging; lock shared defaults upstream | Addresses 38.7 measured question-wait minutes | 0.95 |
| 4 | Bounded context packet | Lower setup repetition; measure after structural changes | 0.87 |

## Success measures

Compare the next three substantial runs with SPEC-027 through SPEC-030:

- Pre-gate launches scale with related batches, not finding count.
- Related findings use one mutation lane; disjoint lanes never overwrite working-tree or index state.
- Resolver wall time and visible runs fall without more final/regression P1 findings.
- Runs with ship debt perform one plan-wide durable-docs sweep after the final code state.
- Same-round fixer staging asks only when ownership proof fails.
- Shared-default questions occur before Wave 1 or not at all.
- Per-finding dropped, demoted, retry, and escalation counts remain visible.

## Change ownership

- Resolver scheduling and staging proof: `agent-skills/skills/fix-verify-loop/SKILL.md`
- Docs-sweep ordering: `agent-skills/skills/execute-plan/SKILL.md`
- Shared-default completeness: `agent-skills/skills/tech-design/SKILL.md` or `agent-skills/skills/write-plan/SKILL.md`, after deciding which phase owns the missing value
- Task-only child history: AgentChatDeck orchestration only if the skill cannot supply it

Edit source skills only under `/root/Desktop/code/agent-skills/skills/`; installed copies are runtime evidence. `[verified, 1.00]`

## Sources

- AgentChatDeck SQLite: `/root/.local/share/agentchatdeck/app.db`
- Thread: `4dec9ca4-ef8b-4c20-8048-56862414f9ae`
- SPEC-027 turns: `01a04853-617d-7e22-879e-2f5b424a2f7d`, `01a04b4e-b59a-7d60-925a-4dc394e41734`
- Compared turns: SPEC-028 `01a0336b-26cd-7092-be2f-2b542a713bb2`; SPEC-029 `01a03d02-f0fd-7330-9593-f6734de64207`; SPEC-030 `01a04233-ee4d-7473-9fc9-54856622a974`
- Durable records: `agentchatdeck/meta/specs/027-vps-speech-to-text/plan.md` through `030-browser-mode/plan.md`
- Prior autonomy audit: `agentchatdeck/meta/investigations/002-execute-plan-autonomy-audit/notes.md`
- Source skills: `agent-skills/skills/execute-plan/SKILL.md`, `agent-skills/skills/execute-chat/SKILL.md`, `agent-skills/skills/fix-verify-loop/SKILL.md`
