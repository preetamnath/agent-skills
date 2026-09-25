# Test value and audit calibration — 2026-09-25

| Field | Value |
|---|---|
| Question | Which rules should govern new tests and future removal of weak tests? |
| Evidence scope | Prior Codex task `01a0c852-f1c7-7160-bba5-e4c9af297154`; six supplied screenshots; OpenClaw `test-audit` skill at `main` on 2026-09-25; current global `AGENTS.md` and `prove-behavior`; read-only samples from `agentchatdeck` and `OakPostPurchase` on 2026-09-25. `agentchatdeck` was pulled first and was current. |
| Status | Decided (instruction edits); audit prompt pending |
| Current owners | Global `/Users/preetamnath/.codex/AGENTS.md` for the test-value rule and skill trigger; `skills/prove-behavior/SKILL.md` for test decisions. |
| Open decisions | One standard for text-matching assertions in the later audit prompt (see calibration note below). |
| Closure outcome | Pending. Applied 2026-09-26: see Decisions below. |

## Decisions (2026-09-26)

1. **Global validity:** applied. `AGENTS.md` Testing rule and `prove-behavior` lead line now say "a required behavior or contract"; "distinguishes" and "internal refactors" kept, because "detects" drops the pass half and "changes" conflicts with the skill's change-detector definition.
2. **Boundary selection:** no separate edit. The skill already requires a stable caller interface (Step 3 Interface) and unique protection (Step 2 item 4). The missing piece, which duplicate to keep, moved into item 3.
3. **Removal safety:** applied as a "Before you remove or merge a test" block after the level table in `prove-behavior` Step 2.
4. **Production seams:** applied as one bullet in the same block.

Calibration note for the audit prompt: `HomeSkeleton.test.tsx:63` is judged "Repair evidence" for a CSS text match, but `shellParity.test.ts:60,100,114` and `cssBudget.test.ts:38` use the same exact-text pattern and are judged "Keep". The audit prompt needs one standard. Candidate, not yet decided: text matching is valid when textual equality is itself the contract.

## Source judgments

- The strongest shared rule is defect sensitivity: a test must fail for a plausible, material violation of an accepted requirement or contract, then pass for correct behavior. It should survive changes that preserve that requirement. The global file and skill already state most of this. Google Testing Blog's [behavior guidance](https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html) supports refactor stability, with a stated exception for implementation constraints such as caching.
- The screenshots' bans on unit tests written after code and preference for E2E as the sole mechanism are opinions, not established admission rules. Their useful point is to avoid tautologies and implementation coupling. [Google's E2E analysis](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html) and [Fowler's test pyramid](https://martinfowler.com/bliki/TestPyramid.html) describe speed, reliability, and diagnosis costs of broad tests, while noting context-specific exceptions.
- The [OpenClaw test-audit skill](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md) adds two useful controls: one primary owner for each contract with another layer only for distinct risk, and a retention check before deletion. Its category list is a discovery aid, not a deletion rule. Its Vitest, PR, and campaign steps are specific to OpenClaw.
- The current `prove-behavior` skill already rejects speculative, tautological, duplicate, and change-detector tests; requires stable caller interfaces; permits unit, integration, and E2E tests; and requires natural-red or targeted-mutation proof. Preserve these rules. A pre-fix run is valuable when possible, but a targeted mutation also proves sensitivity when the old code cannot run.

## Read-only calibration cases

These are source-review judgments, not completed mutation or removal proofs.

| Case | Judgment | Actual signal and limit |
|---|---|---|
| `agentchatdeck/backend/tests/test_gen_types.py:107` | Keep | Compares all generated schema fields with Pydantic fields. Detects dropped fields in the Python-to-TypeScript contract; the generator-freshness check does not. |
| `agentchatdeck/frontend/src/lib/ephemeralId.test.ts:32` | Keep, review exact format assertions | Forces absence of `crypto.randomUUID` and checks usable distinct IDs. Exact `m-`/`w-` formats may exceed the caller contract. |
| `agentchatdeck/frontend/src/api/writeOwnership.test.ts:60` | Keep with stated limit | Scans for prohibited writers across production source. It protects an architecture boundary that types cannot fully express, but lexical matches can flag harmless text and cannot prove all writes absent. |
| `OakPostPurchase/frontend/src/shell/__tests__/shellParity.test.ts:44` | Keep | Compares separate dev and production shells after allowed differences. A one-sided tag change can be silent in a build. |
| `OakPostPurchase/frontend/src/shell/__tests__/cssBudget.test.ts:34` | Keep | Compares independent TypeScript and Django limits and refusal markers. The Vite build also enforces the CSS budget on actual build output. |
| `OakPostPurchase/frontend/src/analytics/__tests__/eventScrub.test.ts:43` | Keep | Tests the configured PostHog hook and sibling `$set`/`$set_once` bags. A wrong nesting previously let credentials pass through. |
| `OakPostPurchase/apps/discount_rail/tests/test_node_lifecycle.py:530` | Keep | Asserts no external write after a failed read. Here absence of a collaborator call is required behavior. |
| `agentchatdeck/frontend/src/lib/providerAccent.test.ts:117` | Removal candidate | A static import of the same module already occurs before collection. A later dynamic import appears to add no independent import-time signal. Prove with the named defect before deleting. |
| `agentchatdeck/backend/tests/test_gen_types.py:199` | Repair assertion | The `title: string` search scans all emitted interfaces; another interface can satisfy it if `ApprovalRequest.title` disappears. Scope the assertion to the claimed interface. |
| `OakPostPurchase/frontend/src/components/home/__tests__/HomeSkeleton.test.tsx:63` | Repair evidence | A CSS regex checks only the skeleton's `180px` literal. It cannot detect a change to the loaded grid and can fail after equivalent CSS syntax changes. |
| `agentchatdeck/backend/tests/test_sessions_queue.py:477` | Investigate, do not delete yet | The barrier pauses provider send after the first prompt is persisted. It tests an overlap during handoff, but does not reach the claimed pre-persist atomic conflict. Its incremental value over the sequential duplicate test remains unproved. |

## Candidate instruction delta for discussion

1. **Global validity:** Decide whether `required behavior` should explicitly include accepted operational, architecture, and cross-file contracts. The present skill accepts contracts; the short global rule can be read more narrowly.
2. **Boundary selection:** Clarify `choose the lowest test level` so it means the smallest reliable test through an existing stable caller boundary, with one primary owner for a contract and additional layers only for distinct risks. Do not make E2E the default.
3. **Removal safety:** Before deleting or merging, identify the exact assertion, real contract, production owner, normal verification path, relevant callers, and remaining evidence. Keep unique static or lower-level checks when they detect material drift between independent artifacts. A failing baseline can be a product bug. Use the existing removal-or-merge defect proof.
4. **Production seams:** Consider a short check for production exports, flags, or wrappers left solely for removed tests. Verify non-test callers before cleanup. This may belong in the later one-time audit prompt if it makes the general skill too long.

Do not add a fixed test-level ratio, a ban on post-code unit tests, a static-test blacklist, or a requirement for screenshots after every E2E run.
