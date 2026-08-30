# Execute-plan critical-path analysis

- **Date:** 2026-08-29
- **Status:** Walkthrough complete — structural changes implemented; further resolver-context expansion deferred pending post-change data
- **Scope:** Completed SPEC-027 `execute-plan` run through its final `turn_done`; initial SPEC-028, SPEC-029, and SPEC-030 runs supply comparison data
- **Excluded:** SPEC-027 deployment, post-ship testing, push, and later miscellaneous UI work
- **Resume:** Measure the next three substantial execute-plan runs against the resolver-context baseline below.

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

Two other measured opportunities rank above resolver-context optimization:

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

**Walkthrough status:** Implemented in `skills/execute-plan/SKILL.md` by `8b8c702`. Runs with untriaged ship debt now mark durable docs pending, close the final code phase, then run one Mode-B sweep over `$PLAN_BASE_SHA..HEAD` before writing the Completion record. The ship-debt-only second sweep was removed. `[verified, 0.99]`

### 3. Remove the two proven question traps

**Shared defaults:** Add a technical-design or write-plan completeness check: every literal/default consumed by two or more tasks must have one named owner and value, or be an explicit user decision before execution. `[long-term, 0.94]`

**Same-round staging:** In `fix-verify-loop`, record the path-scoped staged diff before fixer dispatch. If it was clean, no other mutator ran, and the returned staged change is confined to approved returned files, proceed and record fixer ownership. Any pre-existing hunk, out-of-scope path, mismatch, concurrent mutator, or external index change keeps the current question. Also tell fixers not to run `git add`. `[long-term, 0.97]`

**Walkthrough status:** The accepted implementation prevents the same-round staged state: fixers never run `git add`; the parent snapshots the path-scoped index before dispatch, validates the returned paths, and stages one group at a time. Any unexpected index or path change remains user-gated. `execute-plan` also matches accepted Step-4 paths to the staged path set and commits them before downstream review, documentation, or ship gates. `[verified, 0.99]`

**Shared-default status:** Implemented in `8b8c702`. `tech-design` owns this check because the exact value and canonical source are implementation design, while `write-plan` only sequences the locked design. The Structure Outline must now name every literal/default shared by two or more files or components, and design verification checks it before lock. `[verified, 0.98]`

### 4. Pass each resolver the required context up front

**Recommendation:** Give each resolver agent one immutable packet: finding set, criteria, approved paths, governing path rules, review range, staged diff, and prior-attempt evidence. Use task-only child history when supported. Agents still read current source and required repository instructions. `[long-term, 0.87]`

**Walkthrough status:** `execute-plan` and `execute-chat` now pass the resolver's required findings, approved artifact paths, and governing criteria explicitly at every call site. Paths named only by a finding still require the resolver's scope-expansion gate. The resolver remains responsible for adding path rules, the exact staged diff, and prior-attempt evidence to each child dispatch. Its output now returns every validated path with remaining staged fix-loop changes, and `execute-chat` adds those paths to its collected scope. `[verified, 0.99]`

The read-only AgentChatDeck baseline sampled resolver-labeled subagents in the same SPEC-027–030 turns. Names are heuristic, so the table measures setup shape rather than every resolver invocation.

| Spec | Sampled resolver runs | Avg tool calls | Rule-read calls | Spec/plan calls | Git-context calls | Avg rule + spec/plan reads |
|---|---:|---:|---:|---:|---:|---:|
| 027 | 33 | 17.0 | 76 | 26 | 94 | 3.09 |
| 028 | 69 | 23.6 | 208 | 17 | 229 | 3.26 |
| 029 | 31 | 24.9 | 83 | 4 | 111 | 2.81 |
| 030 | 15 | 18.9 | 42 | 10 | 44 | 3.47 |

**Measurement verdict:** Do not add more context yet. Repository-rule reads dominate the candidate setup calls and must remain current; Git-context reads are also live state, not reusable inputs. The explicit findings, criteria, and approved paths landed after these runs, so there is no post-change comparison yet. Measure the next three substantial runs; investigate task-only child history in AgentChatDeck only if repeated setup remains material. `[recommendation, 0.94]`

### 5. Scale final review after a fix

**Recommendation:** Keep the initial Integration or Full final review, but classify each committed final-review or verification fix before reviewing it again. `[long-term, 0.97]`

- **Small:** At most 2 files and 100 changed lines, one code path, no high-risk surface, and clear affected criteria and consumers. Run one focused `two-pass-review`.
- **Medium:** Small does not fit, at most three affected review seats can be named, and no Full condition holds. Run only those seats in parallel.
- **Full:** More than 5 files or 400 changed lines, a high-risk surface, a contract/decision/outline change, four or more affected seats, or unclear evidence or blast radius. Re-run the Full panel.

Small and Medium reuse unaffected evidence from the initial review. The audited final fix changed 434 lines, so it would still select Full; the new gate removes repeated whole-build review only for bounded fixes. `[verified, 0.98]`

**Walkthrough status:** Implemented in `skills/execute-plan/SKILL.md`. Step-4 fixes now land in their own commit, select Small/Medium/Full from that commit's diff, and merge or replace review evidence according to the selected gate. `[verified, 0.99]`

**Execute-chat applicability:** Use a simpler two-scope form instead of copying the seat-based table. A bounded fix reviews only the returned fix files plus affected callers and consumers; a broad, high-risk, or unclear fix keeps the current whole-run `two-pass-review`. Apply the same choice after a working-gate fix, which currently has no explicit regression-review step. Execute-chat has no multi-seat final panel and keeps all work uncommitted until its final gate, so a separate Medium seat mode or fix-commit classifier would add machinery without a distinct review action. `[recommendation, 0.98]`

**Execute-chat status:** Implemented in `8b8c702` as one Bounded/Whole-run post-fix gate. Review fixes and working-gate fixes use the same bounded rule and one automatic regression pass. `[verified, 0.99]`

## Keep these gates

- **Regression review:** It found real interactions after individually verified fixes. `[verified, 1.00]`
- **Initial final review and one automatic post-fix gate:** Keep the plan-wide Integration/Full review, then use the Small/Medium/Full gate above for a committed fix. `[verified, 0.99]`
- **Final full checks:** They caught the Slash-menu regression. Keep backend and frontend full suites sequential on this VPS. `[verified, 1.00]`
- **Per-finding verdicts:** Group mutation work, not result accounting. `[verified, 0.99]`
- **Fail-closed writes:** Parallelize only disjoint files and checks. `[verified, 1.00]`

## Decision order

| Order | Change | Expected impact | Confidence |
|---|---|---|---:|
| 1 | Parallel pre-gates, then conflict-group fixers | Largest repeated resolver-path reduction | 0.99 |
| 2 | Defer the first docs sweep when debt is pending | Up to 14.9 measured duplicate wall minutes; remeasure the combined sweep | 0.98 |
| 3 | Prove same-round staging; lock shared defaults upstream | Addresses 38.7 measured question-wait minutes | 0.95 |
| 4 | Bounded resolver context | Lower setup repetition; measure after structural changes | 0.87 |
| 5 | Scale the post-fix review to the committed fix | Avoid repeated whole-build panels after bounded fixes | 0.97 |

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
- Shared-default completeness: `agent-skills/skills/tech-design/SKILL.md`
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
