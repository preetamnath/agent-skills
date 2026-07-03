---
name: test-completed-plan
description: "Run the live testing phase after execute-plan ships a build — drive the spec's '### Post-ship verification' checklist (the human-gated ACs the diff can't prove) to pass/fail across three tiers: unit/frontend, real authenticated app, and server-log/DB. TRIGGER when: a shipped spec's Post-ship verification list needs behavioral testing; user says 'test the completed plan', 'run the testing phase', or 'verify the shipped spec'. SKIP for code review (use two-pass-review) or re-verifying code-gated ACs settled at the ship gate."
---

# test-completed-plan

The **testing phase** of the build pipeline. It runs primarily *after* `execute-plan` has frozen the plan and written the spec's Post-ship verification checklist, and its single job is to drive those **human-gated AC lines** to a real pass/fail by exercising the running app — then tick the boxes it can honestly tick.

---

## When to use

**Use** when `execute-plan` has shipped a spec and its `### Post-ship verification` block has unchecked `- [ ] **AC-N:** steps → expected` lines that need live behavioral proof.

This skill verifies **behavior**, not code — it does *not* fix bugs (hand confirmed P0/P1 findings to `fix-verify-loop`) or recompute code-gated ACs (settled at the ship gate).

**Standalone entry** (no `execute-plan` hand-off — testing one item from a `plan.md` checklist, or an ad-hoc list of behavior checks): treat that checklist as the input in place of the spec's `### Post-ship verification` block, and record PASS/FAIL inline in whatever checklist you're driving. Everything else — tier routing, the auth ladder, the env rule-out gate, the verifier gate, cleanup, and the companion-sweep — applies unchanged; only the spec-tick mechanics and the `### Testing findings` block (Step 4) fall away.

---

## Inputs

1. **The spec's checklist** — `meta/specs/NNN-*/spec.md` → `## Completion record → ### Post-ship verification`. Each line is the unit of work: `- [ ] **AC-N:** <steps> → expected: <result>`.
2. **The repo config** — `meta/workflows/automated-testing/automated-testing-instructions.md`. The skill carries the *procedure*; the config supplies the *values* (how to start the app, auth, logs, DB, etc.). See the contract below.

---

## Repo config contract

The skill reads these sections from `automated-testing-instructions.md` (a missing section = that capability isn't available for this repo; degrade gracefully):

| Section | What the skill learns |
|---|---|
| **App shape** | SPA vs embedded-iframe vs SSR; whether the cross-origin-iframe wall applies |
| **Start the app** | dev command, port discovery, readiness signal, tunnel/proxy facts |
| **URLs & surfaces** | named surfaces (path, auth-required y/n, which tier reaches them), incl. the no-auth "create mode" entry |
| **Auth rungs** | which rungs of the auth ladder exist here + how (cheapest first) |
| **Unit-test setup** | the project's test commands (e.g. `pytest`, `vitest`) + how to run them (Tier 1) |
| **Backend logs** | path, how to tail, what they capture, what they DON'T, + the sanctioned temp-payload-log recipe and its removal |
| **DB introspection** | read-only query command (ORM shell / dbshell), connection/port, key models for persistence checks |
| **Frontend observability** | console/network access + known limits (the iframe request-body wall) |
| **Optional add-ons** | e.g. a parked Chrome DevTools MCP config for perf/Lighthouse/heap — only if a plan needs it |
| **Cleanup** | repo-specific teardown items |
| **Gotchas** | repo-specific traps |
| **Env health & recovery** | recovery values the Step-5 env rule-out draws on |

**Rule:** nothing repo-specific is hardcoded here — the skill knows the *kinds* of facts, the config supplies the *values*.

---

## Protocol

### Step 0 — Resolve the repo config
- Read `meta/workflows/automated-testing/automated-testing-instructions.md`.
- **If present:** use the rungs/values it declares.
- **If missing:** ask the user upfront (app shape, how to start it, auth available, log/DB access), then **offer to scaffold the file** from the answers so the next run is config-driven (Step 8 fills its real values after the run). Don't hard-fail.

### Step 1 — Scope to the minimum modalities
Read the plan/spec and the checklist. **Only spin up the tiers the ACs actually need** — a backend-only plan needs no browser; a pure-UI plan needs no DB. Classify up front:
- Pure render / validation / formatting → **Tier 1** (frontend-only / unit).
- Real flows, navigation, persistence, visual → **Tier 2** (authenticated app).
- Payloads, "what actually persisted", server-side effects → **Tier 3** (logs / DB).

### Step 1.5 — Bring up the app (only for tiers that need it)
Skip for a backend-only run. Otherwise, before Tier-2/3 work:
- **Probe** the config's readiness command. **Up → proceed silently.**
- **Down → AskUserQuestion: "Dev server isn't up — will you start it, or should I?"**
  - *You start it* → wait for "ready," then re-probe.
  - *I start it* → run the config's start command in the background; if it's interactive and stalls, degrade to asking you.
- After attach, if the iframe snapshot shows a tunnel/DNS error instead of app content → treat as **env-down** (see Step 5), re-prompt; never record a FAIL against the AC.

### Step 2 — Auth
Resolve the rung via [Auth resolution](#the-auth-ladder) (first match wins), then stay on the cheapest rung that covers each AC; escalate (and prompt in the moment — "AC-N needs your logged-in account, enable remote debugging and say ready") only when an AC needs the user's real account.

### Step 3 — Verify each checklist line
For each `- [ ]` line, route to a tier and run it (see [the three tiers](#the-three-tiers)). Capture first-hand evidence. Never assert a payload's contents from the browser network panel if the app is in a cross-origin iframe — see [the wall](#the-iframe-request-body-wall).

### Step 4 — Record results (tick boxes safely)
- **PASS** → tick the box by an **exact-string single-line Edit** of that one line, and append a dated note (`*(confirmed YYYY-MM-DD)*`) + evidence path. Keep it minimal.
- **Judgment-gate ACs — where PASS turns on something a second reader could dispute** (does the layout / spacing / hierarchy read right) → **don't tick on your own read alone: spawn the `verifier` agent** — artifact = the screenshot(s) + evidence path, finding = the proposed PASS, criterion = "is this AC met by this evidence?". Tick only on a `confirmed` verdict; otherwise record FAIL / PARTIAL with the verifier's reason. **Discrete-state ACs** — a readable attribute, DOM presence/absence, a count, or which-of-two renders — tick on your own first-hand evidence even when a screenshot corroborates; a screenshot doesn't make a discrete state a judgment call (don't burn a verifier spawn on a state a machine already read).
- **FAIL / PARTIAL / DEFERRED** → leave unticked. **Rule out env first (Step 5)** so a harness failure isn't logged as a miss. For a plain miss, record severity + evidence. For a **judgment / visual gate**, write the verdict *into the line* in a fixed shape: date · mode/tier · verdict-with-nuance · one-line recommended action · the why. For PARTIAL/DEFERRED, note what's covered vs owed / what blocks it.
- **After a fix re-verifies a line** → the new PASS note supersedes the FAIL verdict; keep a one-line trace of what was wrong, don't stack full verdicts.
- Tick **only** on evidence captured *this run* — never infer PASS from execute-plan's earlier code-gated result, and never regex-replace across the block.
- **Findings index** → maintain a `### Testing findings` block under the spec's `## Completion record` (the durable analog to `### Review filter stats`); never re-list the ticks:
  ```
  ### Testing findings
  Run: <date> · tiers: <1/2/3> · artifacts: <absolute scratchpad dir> · counts: PASS n · FAIL n · PARTIAL n · DEFERRED n

  In-scope (blocks a tick — acted on this run):
  - <id> · <contract-break | bug Pn> · <AC-ref> · <evidence path> · <routed: escalated / fix-verify-loop → re-verified>

  Out-of-scope (surfaced only — not fixed, not auto-filed):
  - <id> · <bug Pn | idea> · <evidence path> · <one-line what & why>
  ```
- **Standalone (no spec):** tick/record each line inline in the checklist you were handed (a plan's checklist box, or your chat report for an ad-hoc list); skip the `### Testing findings` block above, and carry bugs / out-of-scope findings into your Step-7 report instead.

### Step 5 — Route bugs
- **First, rule out the environment before routing a FAIL to `fix-verify-loop`** — a misclassified env failure burns a fix on a non-bug:
  1. **Retry once** — re-snapshot and re-wait; a stale ref or flaky wait fails the *action*, not the AC.
  2. **Check the app is up** — run the config's readiness probe (**Env health & recovery** / **Start the app**); down → treat as env-down, never a FAIL.
  3. **Still failing or unclear → pause and ask the user** — never log a FAIL against an unresolved env failure.
  A symptom that survives this is a real bug → route it below.
- Confirmed P0/P1 (with evidence) → **invoke the `fix-verify-loop` skill**, then re-verify the line.
- A failure that **contradicts an AC or a locked D-NN** → it's a contract break, not a code fix (the plan is frozen; the spec is the live contract): **escalate to the user** to reconcile the spec (revise the AC or supersede the `D-NN`), and index it under *In-scope* in the Testing findings block. Never silently fix it.
- **Out-of-scope finding** (a latent bug unrelated to any AC, or a "simpler/better design" idea beyond the spec) → **surface it under *Out-of-scope*** in the Testing findings block; never fix it and never auto-file it to any tracker.

### Step 6 — Cleanup (mandatory)
- Remove every temp instrument added (e.g. the payload logger) and **confirm a clean tree with `git diff`** before reporting done.
- Close/detach any browser session the skill opened; never leave a debugging port exposed unattended.
- **Never commit or copy auth-state / cookies / tokens.** Treat saved-state files as credentials.
- All artifacts go to the session scratchpad with **absolute paths** (cwd can reset and leak files into the repo).

### Step 7 — Report
Summarize to the chat: AC pass/fail/partial/deferred counts, which tier proved each, deferred items + blockers, any temp instrumentation added **and confirmed removed**, the artifact dir, and bugs found + routing. The durable record is the spec's ticked checklist + Testing findings block — don't duplicate it here. Standalone (no spec): your chat report plus the inline checklist edits ARE the durable record, so make them complete.

### Step 8 — Sweep learnings into the companion
This run learned repo-specific values the config lacked — persist them so the next run doesn't rediscover them. Sweep the **clean final state** (post Step-6 cleanup), never mid-run scratch.
- **Keep** a learning only if a future run would repeat the discovery without it; route each to its section:

  | Learned this run | → Section |
  |---|---|
  | The attach form that connected, or a rung confirmed | Auth rungs |
  | A new repo trap | Gotchas |
  | The real readiness signal / a corrected "is it up?" check | Start the app |
  | A surface exercised (path · auth? · tier) | URLs & surfaces |
  | A working temp-payload-log recipe, or the log path/format | Backend logs |
  | A working DB query form, a new key model, or a port fix | DB introspection |
  | A recurring env failure + its recovery | Env health & recovery |
  | An observability limit or version threshold confirmed | Frontend observability |
- **Drop** session-only noise: AC results (they live in the spec), one-off flakes a retry cleared, feature bugs and ideas (they live in the spec's Testing findings), and run-command facts (they belong in the nested `CLAUDE.md` the companion points to).
- **Bootstrap:** if Step 0 scaffolded an empty companion, this is where its sections get their first real values.
- **Confirm before writing** — the companion is committed: show the per-section additions, let the user approve, append in each section's existing shape, and skip values already present.

---

## The three tiers

```
┌───────────────────────────────────────────────────────────────────────────┐
│ TIER 1  Frontend-only / unit   no auth; dev server + project unit tests     │ ~most UI/logic ACs
│ TIER 2  Real authenticated app  agent-browser via auth ladder               │ real save/load, flows, visual
│ TIER 3  Ground truth            backend logs + read-only DB queries          │ payloads + what persisted
└───────────────────────────────────────────────────────────────────────────┘
Rule: use the LOWEST tier that can decide the AC. Tier 2 is BLIND to payloads → pair with Tier 3.
```

| Modality | Tier | Verifies | Limit |
|---|---|---|---|
| Dev-server / unit tests | 1 | render, validation, state logic | no real auth/persistence; can't pierce Shadow DOM in jsdom/happy-dom |
| Browser (real, in-iframe) | 2 | real UX flows, save→reload, visual | can't read the iframe request **body** |
| Console | 2 | client errors/exceptions | doesn't prove server outcome |
| Network (list/status) | 2 | request fired + status code | **not the request body** across a cross-origin iframe |
| Screenshots | 1–2 | layout, visual judgment | no assertion semantics |
| Backend logs | 3 | request reached server, status, code path | not request bodies (until instrumented) |
| Temp payload log | 3 | the **exact payload** sent | must be removed after (cleanup) |
| DB introspection | 3 | what **truly persisted** | read-only; build-ahead fields may be legitimately absent |

---

## The auth ladder

The skill walks rungs **cheapest-first**, using only the rungs the repo config says exist.

```
                                         mode      needs the user?
Rung 0  No auth        dev server, create/new mode       LAUNCH    no
Rung 1  Saved state    replay saved cookies → own browser LAUNCH    no (one-time capture)
Rung 2  Credentials    own browser drives the login form  LAUNCH    no (creds from env/secret)
Rung 3  Attach         connect to the user's logged-in    ATTACH    YES (prompts in the moment)
                       Chrome via CDP remote debugging
   ▲ cheapest / no human                       costliest / interrupts the user ▲
```

- **Launch mode (Rungs 0–2):** the tool spins up its *own* debugging browser and authenticates itself. Rung 1 = saved-state reuse: capture once after a manual login (`agent-browser … state save <states-dir>/<service>-<account>.json`), replay with `state load` (use a **headed** browser if the auth provider/proxy rejects headless replays). The state file is a credential — gitignore the states dir, scope capture to the app's origins, never print/commit/paste cookie values. Rung 2 = drive an email/password login with creds from env/secret.
- **Attach mode (Rung 3):** for the user's real session. The "Allow remote debugging" toggle is a **human action** (a security wall — a tool can't flip it on an already-running browser), so attach always prompts just-in-time.
- **Auth resolution — first match wins:**
  1. **Explicit instruction** — the user named a rung for this run → use it.
  2. **Config** — `automated-testing-instructions.md` declares the rung(s) → walk them cheapest-first.
  3. **Neither** — infer the cheapest rung the task/spec actually needs, then confirm via an `AskUserQuestion` gate **before launching**; offer to record the choice in the config so the next run hits branch 2.

**Connection & recovery notes (from CDP/auth-reuse practice):**
- **If a rung fails, fall back to the next viable one** (e.g. saved state expired / redirects to login → re-attach live or recapture state).
- **Diagnose CDP attach failures:** connection refused = no debug server (toggle off / wrong port); HTTP 403 or WebSocket rejected = needs the right remote-allow-origins or a dedicated debug port; loads but redirected to login = stale/expired state → recapture.

---

## The iframe request-body wall

**Symptom:** in an embedded app inside a cross-origin iframe, the browser cannot read an XHR's **request body** (HAR + network-detail return empty postData; `eval` into the iframe is same-origin-blocked).

**Truth:** this is a **client-implementation gap, not a hard limit.** CDP *can* read it via `Target.setAutoAttach({flatten:true})` + `Network.getRequestPostData` / `Fetch` on the iframe's own target — but **no tool wires this up today** (open issues on both agent-browser and chrome-devtools-mcp). So treat it as a wall *for now*.

**How to beat it — pre-test instrumentation (a paired lifecycle):**
1. **SETUP (before the AC):** add the repo-config-declared temp log — typically one line at the write endpoint (`logger.info(request.body)`) or a dev fetch-wrapper that logs the payload — making the otherwise-unobservable payload visible to the agent.
2. **VERIFY:** run the AC; read the captured payload from the log (or read the persisted result from the DB).
3. **TEARDOWN (mandatory):** remove the instrument; confirm a clean `git diff`. A left-behind logger is the top risk.

**Never** assert payload contents from the browser network panel across the iframe — an empty body means "unobservable here," not "no payload" and not "correct payload."

---

## Browser tooling

- **Default to `agent-browser`** (CDP CLI) — it drives the cross-origin iframe DOM today (snapshot/click/fill/check + screenshots), proven end-to-end. Attach to the user's Chrome (`agent-browser connect <port>`) or launch its own browser + replay saved state.
- **Chrome DevTools MCP** is an optional, config-declared add-on — reach for it *only* when a plan needs its unique strengths: performance traces / Core Web Vitals, Lighthouse audits, network/CPU throttling, or heap-snapshot leak analysis. It does *not* solve the iframe request-body wall.
- Both are CDP clients; "remote debugging" is the transport, the tools sit on top.

---

## Rules

- **Temp instrumentation left behind.** Record every temp edit's file:line; mandatory `git diff`-clean gate before "done"; report "removed".
- **No destructive DB writes during "introspection".** Read-only only (SELECT / `.filter()`). Never `.save()/.delete()/UPDATE`. Stop for approval before any state change.
- **No false PASS from the iframe wall.** Never assert payload from the browser network panel; route body claims to Tier 3 (log or DB).
- **No false FAIL on build-ahead fields.** DB-absent ≠ fail when the spec marks a field deferred/stubbed; verify the frontend concern at Tier 1 instead.
- **Beat flaky waits.** `wait --load networkidle` / re-snapshot after navigation; screenshot on failure for triage.
- **Don't over-collect auth secrets.** Prefer attaching to an existing session; never persist tokens; redact any token in logs/screenshots.
- **No ticking without first-hand evidence.** Tick only on evidence captured this run, with an artifact path; exact-string single-line edit.
- **Degrade for non-web repos.** Capabilities are config-probed; skip absent tiers; fall back to "run the project's verification command + the checklist steps".

---

## Pipeline fit

```
product-interview → tech-design → write-plan → execute-plan ──(ship gate)──┐
                                                                            │ writes spec's
                                                                            ▼ ### Post-ship verification (- [ ] human-gated ACs)
                                                  ┌──────────────────────────────────────┐
                                                  │  test-completed-plan  (this skill)    │
                                                  │  drives those - [ ] lines to [x]      │
                                                  └─────────────────┬────────────────────┘
                                                     bug found ─────┘──► fix-verify-loop ──► re-verify line
```
