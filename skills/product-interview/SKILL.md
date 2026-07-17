---
name: product-interview
description: "Move from ambiguity to clarity on WHAT to build — product scope and UX — before any technical design. TRIGGER when: user says 'product interview' or 'design a new feature'; user wants product requirements, scope, or UX clarified before building; a feature's product/UX scope is vague."
---

# Product Interview

Read the codebase, then Socratically interview the user — surfacing hidden assumptions and testing their framing — until product scope and UX are locked. Establish the WHAT; leave the HOW to `tech-design`.

## When to use

YES: non-trivial feature where the goal is vague, has multiple valid interpretations, or the UX is undecided; user says "product interview" or "design a new feature"; user has an external PRD/spec that needs transcribing into a decision-locked spec (the interview compresses to confirming, not discovering).

NO: user has a specific request with exact behavior and no product/UX ambiguity (skip to `tech-design` or `write-plan`); quick fix or single obvious change; the question is *how to implement* an already-clear feature (use `tech-design`); user says "just do it".

## Protocol

### Input

- **Feature**: a feature name/description (or an existing `meta/specs/NNN-slug/` path). Before writing anything, match it against existing folder slugs in `meta/specs/`: exactly one match → that is the spec Step 5 updates in place; more than one plausible match → list the candidates via `AskUserQuestion` — never glob-and-pick; no match → Step 5 mints a new folder. Never mint a new NNN without this check. Resolve the `NNN-slug` identity here — the matched existing folder, or (no match) the next number + a slug from the feature name — so a mid-interview `generate-mockups` call has a stable home; the folder itself is created lazily by whichever step writes first (mockups at Step 2, or spec.md at Step 5).

### Step 0 — Load the job lens

Invoke the `jtbd` skill via the Skill tool. Use its lens — the job-story format and job-fit judgment — to frame every product/scope question; skip its Steps and Job-frame output.

### Step 1 — Read context first

Before asking anything, silently explore:
- Product/architecture docs (CLAUDE.md and whatever convention docs it references — ARCHITECTURE.md, features.md — plus existing specs in `meta/specs/`)
- Existing UX in the affected area (screens, flows, components)
- Related features and any prior spec this builds on
- A light possibility scan: what the target surface/platform allows *at all*, and what data the codebase already carries — possibility only, never how-to-build, never current code as a ceiling (see the *Codebase is context* rule)

Don't ask what the codebase or an existing spec already answers. Note project conventions you find — they are constraints to honor, not decisions to re-litigate (those live in CLAUDE.md / durable docs, not in this spec).

### Step 2 — Interview: product, then UX

Resolve the **product** layer before the **UX** layer *as the default*, but treat them as one decision tree: when a UX branch blocks or would overturn a product choice, resolve that branch first (the dependency rule below governs). A UX answer that overturns an already-locked product choice follows the reversal rule below. Surface what the user is assuming, not just what they request. When the Step-1 read surfaces a load-bearing question the user didn't ask — an existing feature this overlaps, a UX pattern to reuse or deliberately diverge from — raise it, saying it came from the codebase; route technical finds to Open Questions tagged `(for tech-design)`. Draft the job-story as the product layer resolves — it anchors UX option scoring and the spec's Background. A slot you can't fill is a question to ask, not a blank to guess.

Sketch the decision space as a compact nested list once you can name two or more branches ("Here's what I think we need to figure out — does this match?"). Every node carries a trailing status — `- [branch] — [resolved: choice] | [open] | [deferred: why] | [blocked by branch]` — plus its wall tag (`[hard|ask|ours]`) where one applies; list blocking branches first. Resolve one branch at a time, blocking branches first. Update the tree inline as branches split, collapse, or resolve. Continue until every branch is resolved or explicitly deferred. If the task has only one or two flat questions, skip the tree and ask directly; if you can't yet name two branches, ask open-ended until you can — aim to sketch within 2–3 rounds. If the interview runs long, check in: summarize current clarity and offer to continue or proceed.

**Run each branch explore → stretch → verify (in order)** — name the ideal before checking what's real, so a constraint never caps a choice the user hasn't reached for yet.
- **Explore / stretch:** for a non-trivial or ambiguous UX branch, name and score 2+ options by job-fit before locking; an obvious single-UX branch skips this. Escalate to parallel subagents (and any available design skills) only for high-stakes or high-ambiguity UX.
- **Sketch, then decide fidelity:** sketch every resolved UX branch in ASCII — one sketch for a single design, one per option when comparing. When a visual branch is worth *seeing* at higher fidelity, ask via `AskUserQuestion` ("ASCII is enough" / "see it in high fidelity"); on high fidelity, **invoke the `generate-mockups` skill via the Skill tool** (PREVIEW a screen, or COMPARE directions), passing the resolved spec-mockups path (`meta/specs/NNN-slug/mockups/`) and the design context you know. It renders there and returns the pick + rejected directions; you record them into the UX section at Step 5 — it does not write the spec. Skip the ask on trivial sketches.
- **Verify (just-in-time):** when a load-bearing claim is unchecked — a decision rests on it — fire a subagent at the source of truth (code / docs / SDK), but only when a wrong answer would *invalidate agreed scope*, not merely redirect a branch. Check product-surface **possibility** only (can the surface do it at all?), never how-to-build or capacity — those go to Open Questions tagged `(for tech-design)`.
- **Hit a wall? Tag it.** `[hard]` = outside our control (external SDK / platform) → law; stamp its assumption (e.g. "given the SDK has no programmatic redirect") so it reopens if the dependency changes. `[ask]` = cross-team, movable by request. `[ours]` = our code, we change freely. `[hard]` is a real constraint; `[ask]`/`[ours]` are guidance — if either forces a worse UX, challenge it (or flag the ask) first, then record the user's final call and move on.
- **Don't lock a UI pattern whose surface feasibility is unverified** — verify possibility first, or lock it "pending feasibility."

Completeness lens (verify nothing is missing — these are a lens, not a required structure):
- **Product / scope** — the job to be done, in the jtbd job-story format (loaded at Step 0); who it's for; what's in, what's out; success criteria.
- **UX and behavior** — happy path, error states, empty states, user flows, the surfaces/screens touched.
- **Acceptance criteria** — observable, testable conditions for "done."
- **Constraints** — compatibility, platform limits, dependencies, boundaries.
- **Clarity** — resolve remaining ambiguity or contradictions.

When a load-bearing assumption surfaces, test it once ("Does this constraint actually exist?" / "What's the simplest version still worth shipping?"). Challenge the framing, not the person. If a stated requirement seems materially wrong (product value, UX harm), say so with reasoning; record the user's final call, not yours.

If a later answer or feasibility finding overturns a choice the user already locked this session, re-confirm via `AskUserQuestion` and record the overturned choice in the replacing decision's Rejected field, citing what killed it — pre-write reversals need no supersession pair, but the why must reach the record.

Record each resolved choice as a **`D-NNN-XX` decision block** (see the Spec.md template — it defines the id format) with Status, Chosen, Rejected, Rationale. Classify anything unresolved by exactly one rule:
- A framed-but-unresolved **decision** → a `D-NNN-XX` block with `Status: open`.
- A blocking unknown inside any section → an inline `[NEEDS CLARIFICATION: ...]` marker.
- Non-blocking notes → Open Questions (these do NOT block the gate).

Deferring a decision is itself a decision: propose it, the user confirms, and it lands as a **locked** `D-NNN-XX` whose Chosen is the deferral (alternatives marked *deferred* in Rejected) — a confirmed deferral never blocks the gate.

The lock gate greps exactly two forms — see **Gate anchors** below. Anything blocking must carry one of them, or it will not block.

### Step 3 — Pre-confirm verification gate

Once Step 2's branches are resolved or deferred, and before the Step-4 summary, run this required gate over the resolved UX elements that are **load-bearing** (an AC, another decision, or user-facing behavior rests on them) — two passes, two grains. The gate always runs; on a trivial feature it may be near-empty (nothing load-bearing beyond the Existing-patterns check) — record that and move on.

**Pass 1 — per element.** For each load-bearing element:
- **States** — error / empty / edge: what happens when data is missing, the call fails, or a value hits a boundary?
- **Expectation-Fidelity** — does what the element implies (its label, control, default, or placement) match what actually happens? Flag every mismatch.
- **Surface-Obligations** — any obligation the surface itself imposes (e.g. accessibility/compliance on a regulated surface), where it demands it.

**Pass 2 — the assembled whole.** Do the cleared elements coexist and work together on the real surface(s)? Check combination-possibility + cross-element interference, and re-verify the load-bearing facts the interview leaned on. Surface/platform possibility is validated here — launch subagents in parallel, one per applicable area below (Existing-patterns always runs), each carrying the flows it must validate:

| Area | When relevant | Verify |
|---|---|---|
| UI components | Feature uses specific components/libraries | Component exists, supports the interaction, composition constraints |
| External data/APIs | UX depends on external data | Data is available, fields exist |
| Platform constraints | Feature rides a platform (Shopify, extension, etc.) | The UX is permitted by the platform |
| Existing patterns | Always | The affected area's existing UX patterns and conventions |

Scope: possibility, not capacity. Constraint depth — rate limits, quotas, throughput, batch caps — is `tech-design`'s constraint recon (its Step 2B); don't duplicate it here.

Each subagent returns: exists (yes/no), capabilities, gotchas, and **`blocks: <the decision or flow it invalidates> | none`** — `none` is a valid result. Deposit load-bearing possibility verdicts in the relevant `D-NNN-XX` Rationale or the Constraints section, not conversation. Any gate finding — a Pass-1 miss (broken state, fidelity or obligation gap) or a Pass-2 `blocks` hit — feeds back into the tree (one follow-up round); resolve it with the user (re-explore, don't silently narrow), then proceed; if still unresolved after that round, classify it by Step 2's rule (open decision / clarification marker / Open Question) and move on.

### Step 4 — Pre-write summary

Before writing, summarize the contract in chat in this exact shape — enough to spot a wrong turn without reproducing every AC:

```
**Contract summary (pre-write):**
- Scope: [one line]
- Decisions: D-NNN-XX [title] → [Chosen]        (one line per decision)
- Constraints: [one line each]
- ACs: [n] ([x] code-gated, [y] human-gated)
- Step-3 gate: [clean | each finding and how it resolved]

**Assumptions I'm carrying (never discussed):**
- [assumption] — [what rests on it]
```

(Write `None — everything load-bearing was discussed` when the assumptions list is empty.) Then use `AskUserQuestion` to collect the choice: "Write the draft" / "Adjust first" / "Find gaps first". Recommended: write the draft. The full verbatim contract — the numbered AC list with gating tags and every `D-NNN-XX` block — belongs in the file, not chat: Step 5 writes it as `Status: Draft` for the user to review. Reviewers verify diffs against that AC text, so it must be exact in the file.

On **Find gaps first** — opt-in, for a complex feature or when you lack the domain depth to spot missing cases — invoke the `find-gaps` skill over the assembled contract. Its primary lens is **what's missing**: missing scope, AC-coverage holes. It also contests the Step-3 gate's state verdicts: pass it a manifest of the elements Pass 1 cleared, and have its fresh-eyes subagents re-raise a state only where they disagree (an independent examiner catches what the gate rationalized away, without re-litigating settled ground). Product/UX gaps only — not a technical-gap hunt (`tech-design`'s job); fence every lens to the WHAT layer and send technical gaps to Open Questions tagged `(for tech-design)`. Applied gaps re-enter Step 2; a new flow on an external surface re-runs the Step-3 gate on the delta. Then re-summarize and re-ask the write-the-draft choice.

### Step 5 — Write / update the spec

Write to `meta/specs/NNN-<topic-slug>/spec.md` using the `NNN-slug` resolved at Input (create the folder if a mid-interview mockup hasn't already). If a spec for this feature already exists (resolved at **Input**), **update it in place** (append/modify sections; never silently overwrite locked decisions — supersede them; continue both counters: the next `D-NNN-XX` takes the highest existing `XX` in this spec (technical ones included) + 1, new ACs likewise). On any edit to a decision or AC of a spec whose Structure Outline is populated (its `### Files touched` heading is present), set the header `Status:` back to `Draft` — the frozen outline was verified against the old WHAT, and the `Draft` header is what routes `tech-design` back through a re-design instead of past it. Tell the user the path: the spec is written as `Status: Draft`, not yet committed — ask them to open and review the file (the verbatim contract is read here, not in chat). Revisions and commit are Step 6's job.

This skill writes the WHAT sections; `tech-design` later appends technical Decisions + the Structure Outline (and appends to Constraints / Accepted risks what its recon proves); `execute-plan` appends the Completion record at ship. For the full file shape, see the **Spec.md template** at the end of this file.

### Step 6 — Review, commit, route

Stop here once every product/UX branch is resolved or deferred and the spec is written. Step 5 sent the user to read the file — this step turns that review into approval, then handles commit and routing as two tightly-coupled `AskUserQuestion` rounds.

**Q1 — Draft look right? If so, commit?** Frame it as the approval, then offer: "Commit now" (recommended) / "Skip commit for now" / "Adjust the draft first". Either of the first two *is* the approval — proceed to Q2. "Adjust" loops back: edit the Draft in place and re-ask Q1; if the edit overturns a locked decision or touches an AC on a spec with a populated outline, the Step-5 header-flip/supersede rule fires. On commit, stage only spec.md — the durable trace that the confirmation happened:

```
git add meta/specs/NNN-slug/spec.md && git commit -m "spec(NNN-slug): discovery — product/UX decisions + ACs"
```

(Use the slug resolved at Input. If `git status --porcelain meta/specs/NNN-slug/` shows anything else in the folder, leave it unstaged and tell the user.) On skip, leave it uncommitted and say so — `tech-design` Step 6 stages the whole spec.md and sweeps it up, but until then it lives uncommitted, so re-offer the commit at any session boundary.

**Q2 — Where next?**
- **`tech-design`** — default: the WHAT is locked and the feature needs implementation decisions before sequencing.
- **`grill-me`** — if `Status: open` decisions or clarification markers remain, or a load-bearing assumption wasn't pressure-tested.
- **`write-plan`** directly — only for a trivial change with one obvious implementation.

The WHAT must be locked (both Gate anchor greps clean) before `tech-design` will proceed.

### Resumability

On re-entry, run Step 0 first — the lens loads per session — then read what exists on disk; the spec encodes where a prior session stopped:

- **No folder / no `spec.md`** (per the Input check) → nothing written; start at Step 1.
- **`spec.md` exists but core sections are missing or placeholder** → an interrupted prior session; re-read what's there and rejoin the interview (Step 2) at the gaps — resume from the file, don't reconstruct from memory.
- **Spec complete but the Gate anchor greps hit** (`Status: open` decisions / clarification markers) → a parked investigation, not damage; resume Step 2 at the open branches.
- **`### Files touched` present** → `tech-design` already designed on this WHAT; reopening it invalidates a frozen outline — confirm with the user first, and supersede (never edit) any locked decision being revisited; the Step-5 header-flip rule fires on the rewrite.

## Rules

- **One question per round.** Tightly coupled follow-ups are fine; shotgunning unrelated questions is not. Presenting/updating the tree counts as part of the round.
- **Always use `AskUserQuestion` for questions with distinct choices** — with your recommendation and why. Plain text only for genuinely open-ended questions.
- **Product + UX only.** Technical approach, data shapes, and file layout are `tech-design`'s job — route them to Open Questions tagged `(for tech-design)` and move on — tech-design reads them at its discovery step.
- **Codebase is context, not constraint.** Existing code shows what IS, not what MUST BE; the user may intentionally diverge. A wall is **law** only when it's outside our control (external SDK / platform) — tag `[hard]`, stamp its assumption; anything we or a teammate can change (`[ours]` our code, `[ask]` cross-team) is **guidance** — challenge it before it narrows the vision.
- **Proportional effort — load-bearing only.** Spend a subagent, verification, or UX-exploration round only where a decision rests on the answer; skip passing mentions and obvious single-UX branches. Match effort to stakes.
- **Anchor questions in what you read.** Reference specific code or docs when asking — "I see X in ARCHITECTURE.md — does that apply here?"
- **Play back concrete scenarios, not abstract questions.** Confirm behavior by walking one specific case in the shape `[trigger]: [what happens] — right?` ("Save fails offline: the draft stays and a retry shows — right?") — a wrong detail draws the correction an abstract question won't.
- **Conventions belong in durable docs, not the spec.** "Utils go in `utils/`" is a project rule (CLAUDE.md), not a feature decision. Only record a `D-NNN-XX` when it's a real, feature-specific, reversible-at-cost choice.
- **The spec is the feature's build contract + record** — it settles at ship; post-ship product/UX evolution belongs to future specs and durable docs, not retroactive edits here.
- **Only spec.md and plan.md mint ids.** spec.md mints `D-NNN-XX`/`AC-NNN-XX`; plan.md mints `F-NNN-XX` (execute-plan's job; format in write-plan's Plan anchors). All other artifacts — interview notes, triage/backlog files, research — cite existing ids and never mint their own.

---

## Spec.md template

Other skills inline only their own sections and point here:

```markdown
# SPEC-NNN: [Feature name]

- **Status:** Draft        <!-- Draft → Locked → Shipped. Set Draft: product-interview; → Locked: tech-design Step 6 (iff lock greps clean); → Shipped: execute-plan ship gate. The trivial route (product-interview → write-plan directly) skips tech-design and legitimately ships from Draft. Locked = zero open decisions and zero clarification markers. The lock gates grep per-decision markers, not this line; write-plan's stale-outline gate is the one gate that reads it (see Gate anchors). -->
- **Created:** [YYYY-MM-DD]
- **Source:** [origin — roadmap item, request, prior spec it builds on]

## Background
[Who needs this and why. The one-line job, in the jtbd job-story format (loaded at Step 0). The layer/scope boundary in a sentence. One short paragraph.]

## Requirements
[The WHAT, as observable rules — the densest, most load-bearing content. Enumerate edge cases per rule. No IDs: nothing downstream cites requirements — ACs are the citable contract.]
- [the rule] — edge cases: [list]
- [the rule] — edge cases: [list]

## UX
[Flows and states: happy path, error, empty. Surfaces/screens touched. Low fidelity is fine — ASCII mocks or bullet flows. Record the visual/structural options explored, not just the chosen one — keep each rejected layout/flow (mock or one line) with why it lost. When `generate-mockups` produced a page, link it (`mockups/…`) with any notes and stamp it *directional, not final*; the design system / `meta/DESIGN.md` wins if they disagree. Backend-only features: the externally observable contract — which fields/behavior a consumer sees; field types, nullability, and shapes belong to tech-design's outline, which takes precedence.]

## Out of scope
[Only Out-of-scope — don't restate In-scope (that duplicates Requirements). Annotate coupling.]
- [excluded item] — [coupling note]

## Acceptance Criteria
[Observable, testable "done" conditions — the contract an independent reviewer checks the diff against; the implementer never self-certifies.
**Numbering & rigor:** ids are `AC-NNN-XX` — `NNN` = this spec's folder number, `XX` = a zero-padded two-digit counter starting 01; plan tasks and tests cite the ids; scale rigor to scope.
**Gating tag (MANDATORY):** every AC carries exactly one — code-gated (machine-checkable against the diff) or human-gated with the concrete how (routed to Post-ship verification at ship). Tags are provisional at discovery; tech-design confirms or flips each once the approach is chosen — a tag-only edit, exempt from the supersession protocol.
**Revising:** ACs are the live contract — revise in place with a trailing *(revised per D-NNN-XX)* marker; the why lives in the superseding decision.
**One physical line per AC:** ID, behavior, gating tag, and any *(revised per D-NNN-XX)* marker all on that line; the gates select by line.]
- **AC-NNN-01:** [observable behavior] — [code-gated]
- **AC-NNN-02:** [observable behavior] — [human-gated: how to verify, concretely]

## Decisions
[Inline, atomic `D-NNN-XX` blocks — the durable why.
**Id format:** `NNN` = this spec's folder number; `XX` = a zero-padded two-digit counter starting 01 — ONE counter per spec, shared by product (this skill) and tech (tech-design) decisions. Ids are unique across the repo (the folder number guarantees it) and never renumbered.
**Type marker:** each heading carries `[product]` or `[tech]` after the colon — advisory for readers and routing, no gate greps it.
**Citing:** cite the full id (`per D-NNN-07`), never a line number.
**Revising:** supersede, never edit the body (ACs are the one revise-in-place exception, marked as above).]

### D-NNN-01: [product] [decision title]
- **Status:** locked       <!-- open | locked | superseded — lowercase, load-bearing (see Gate anchors). Unresolved decision = open; any open blocks downstream. -->
- **Chosen:** [the choice]
- **Rejected:** [alt — why it lost]; [alt — *deferred*, not rejected forever — why]
- **Rationale:** [the constraint that drove it; cite a verified fact if load-bearing]
- **Supersedes:** —
- **Superseded-by:** —     <!-- set when Status flips to superseded; the ONLY edits ever made to a superseded block are Status + this line -->

## Structure Outline
<!-- WRITTEN BY tech-design — leave empty at discovery. Design snapshot: written `Status: Draft` for review, FROZEN once `Status: Locked`; never edited in place — replaced only by a tech-design re-run. Deviations during build live as [Implementation] entries in plan.md's Execution Log; after ship, code is the source of truth for structure. -->
<!-- Section format lives in skills/tech-design/SKILL.md (Step 3); it ends with a "### Files touched" heading — load-bearing: write-plan's outline-present gate greps it (see Gate anchors below). -->

## Constraints
[Fixed boundaries: compatibility, performance, platform limits, dependencies. Append-by-both: discovery seeds it; tech-design appends the load-bearing numbers its recon proves. Tag each wall `[hard]` (outside our control — stamp the assumption) · `[ask]` (cross-team, movable) · `[ours]` (our code) — advisory annotations, no gate greps them.]
- [constraint] — `[hard|ask|ours]`

## Accepted risks (knowingly carried)
[Append-by-both: discovery seeds it; tech-design appends the risks the user accepts.]
- [risk we choose to live with] — [why acceptable]

## Open Questions
[NON-BLOCKING notes only — this section does not block the lock gate; blockers must be open-status decisions or inline clarification markers (see Gate anchors). Implementation questions for tech-design land here, tagged `(for tech-design)`. Omit this section entirely when empty.]
- [non-blocking question] — [why it can wait]

---

## Completion record
<!-- WRITTEN BY execute-plan at the ship gate — leave absent until then. Settles the spec: outcome stamped onto the contract. -->

**Shipped:** [date] · **Status:** Complete | Partial

### Criteria results
| AC | Result |
|---|---|
| AC-NNN-01 | PASS / PARTIAL / FAIL — [1-line evidence] |

### Post-ship verification
<!-- WRITTEN BY execute-plan at ship: manual test cases for the whole feature; each `- [ ]` as steps → expected result, human-gated ACs led by `AC-NNN-XX:`. "None — nothing manually observable" if none. -->
- [ ] [steps] → [expected result]
- [ ] AC-NNN-XX: [steps] → [expected result]

### Deferred / what this does NOT close
- [deferred debt or known limitation, with severity] — or "None"

### Review filter stats
<!-- one line aggregating the Wave Reviews tallies: review findings the fix-verify-loop pre-gate dropped + findings demoted, across all waves — so what the filter rejected stays visible -->
- [N dropped by pre-gate, M demoted, across all waves] — or "None"
```

### Gate anchors (load-bearing — exact forms matter)

These live OUTSIDE the template so they are never copied into a spec instance. Downstream gates (tech-design Step 1, write-plan Step 1) block on:

```
grep -nE '^[[:space:]]*-[[:space:]]*\*\*Status:\*\*[[:space:]]*open' spec.md   # any hit ⇒ blocked
grep -n '\[NEEDS CLARIFICATION:' spec.md                                       # any hit ⇒ blocked
grep -n '^### Files touched' spec.md                                           # write-plan Step 1 only: no hit ⇒ outline missing
grep -nE '^[[:space:]]*-[[:space:]]*\*\*Status:\*\*[[:space:]]*Draft' spec.md  # write-plan Step 1 only: + outline present ⇒ stale outline (reopened)
```

Rules that keep these greps sound — breaking any of them silently breaks the pipeline:
1. **POSIX ERE only** (`[[:space:]]`, never `\s`) — gates run through varying grep builds.
2. **Case split is load-bearing**: header Status values are Capitalized (`Draft/Locked/Shipped`); decision Status values are lowercase (`open/locked/superseded`). That asymmetry is what keeps the header line out of the decision-gate regex. Never normalize one to the other.
3. **Clarification markers are always written with the colon** (`[NEEDS CLARIFICATION: ...]`). The ban is by location, not intent: the colon form must NEVER appear in the canonical template body, or any text destined for a spec instance, where the gate would catch it; an illustrative `: ...` placeholder in this rules block or interview prose, as here, is fine — the gate reads spec.md, never SKILL.md.
4. **Each AC is ONE physical line** — `- **AC-NNN-XX:** behavior — [tag]`, keeping any `*(revised per D-NNN-XX)*` marker on that same line (a long AC stays on one line; the gates care about line *count*, not length). Both AC selections (execute-plan Step 4 / Seat A code-gated, Step 5.3 human-gated) grep the AC line, then filter for the tag — a tag wrapped onto a continuation line silently drops the AC from review or post-ship verification.
5. plan.md-side anchors (typed log tags, promotion marker, deferred tags) are defined beside the canonical plan template in `skills/write-plan/SKILL.md`.
