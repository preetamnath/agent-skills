# Planning-stage simplification — supersession weight + loop convergence

- **Date started:** 2026-08-15
- **Status:** Decisions in progress — see Decision log at the end
- **Scope:** `product-interview`, `tech-design`, `write-plan` (and the few `execute-plan` lines they cite)
- **How to resume:** read Problem + Findings, then continue the Decision log — walk each PENDING decision with the user one at a time (simplest language, proposal + why + confidence), record the call, then apply the edit set it selects.

## Problem (user's report)

1. **Supersession is too heavy pre-build.** While a feature is still in planning (nothing implemented), decisions get amended/superseded, leaving "we decided X, then changed to Y" trails. The user wants the spec to be a clean ledger of *final* decisions until execution starts.
2. **Loops re-fire unintentionally.** Gap-finding and verification passes re-run; tech-design findings route back to product-interview and the interview "gets conducted again." Loops should be intentional and bounded.
3. Candidate fixes the user floated: (a) bounded/intentional loops; (b) phase-specific gap lenses (product lenses in product-interview, technical lenses in tech-design); (c) one joint gaps pass after product-interview + tech-design back to back.

## Input research — Reflection SDD (dataleadsfuture.com)

Article: <https://www.dataleadsfuture.com/reflection-sdd-use-a-reflection-harness-to-level-up-your-openspec-workflow/>

- **Reflection Harness:** a dedicated reviewer agent audits spec files *before* code is written; spec bugs cost minutes, code bugs cost hours.
- **Bounded review loops:** max ~5 review rounds per artifact, then escalate to a human — prevents infinite critique loops.
- **Sequential "batch & freeze":** review and freeze one artifact at a time (proposal → design → specs → tasks), each building on a frozen foundation.
- **Context preservation:** explore-brief + review-log files keep the AI aligned across rounds.

**Mapping to this repo (verified):** the pipeline already *is* batch-and-freeze — spec (product-interview) → outline (tech-design lock) → plan (write-plan), each gated by greps and frozen in sequence. The reviewer role exists too (Step-3 gate, Step-4 verify, plan review panel). The one missing piece is the article's *bounded rounds*: most loops here have no cap. Conclusion: don't import the harness; cap the loops we have. — conf 0.85

## Analysis method

Two Opus subagents (multi-agent-analysis), one per question; every load-bearing citation re-verified by the parent against the skill files. Confidence scores are post-verification.

## Findings — Part 1: supersession machinery

**F1 — Supersession fires at 7 planning-stage sites; only pre-write reversals are exempt.** [verified, 0.90]
The freeze point today is "decision written to file" (product-interview Step 5). Sites: product-interview Step 5 update-in-place ("never silently overwrite locked decisions — supersede them"), Step 6 Q1 Adjust, Resumability (`### Files touched` present); tech-design 2B "Revise the AC now" (mints a superseding block), Step 5 Adjust, Resumability reopen bullets. The meaningful line is "execution started," which is already machine-checkable: `plan.md`'s `**Base SHA:**` set (write-plan Step 5 guard uses exactly this test; execute-plan Step 1.1 sets it before Wave 1).

**F2 — No consumer needs pre-build supersession history.** [verified, 0.90]
- Gate greps: none grep `superseded`, `Supersedes:`, or `Superseded-by:`.
- Counters: "highest existing XX + 1" — density-independent.
- Resumability: keys on file-state (headings, header Status), never on supersession links.
- `*(revised per D-NNN-XX)*` marker: execute-plan Rules say outright "a human-readable convention, not a gate anchor — nothing greps it."
- Seat C drift review: receives superseded blocks "to catch reversion," but reversion only matters when code was written against the old decision — pre-build there is none; the rejected direction survives in the single block's `Rejected` field.
- Git: spec.md is committed at each phase gate, so in-place edits stay recoverable via diff.
- **One carve-out:** cross-spec supersession (a later spec flipping a *prior shipped* spec's block) must stay supersede-only — that spec's decisions are implemented in code.

**F3 — The rules self-contradict today.** [verified, 0.90]
tech-design writes its blocks `Status: locked` at Step 5.1, and its own Step-5 "Adjust" says *edit the Draft in place* — while product-interview's Decisions template rule says *supersede, never edit the body*. A literal agent supersedes a decision it wrote minutes earlier in the same Draft. Same shape at product-interview Step 6 Q1 Adjust. Likely the direct source of the reported noise.

**F4 — What actually protects downstream is the header-flip chain, not supersession.** [verified, 0.85]
product-interview Step 5: any decision/AC edit on a spec with populated outline → header back to `Draft` → write-plan's stale-outline gate blocks → tech-design re-runs. This chain must survive any edit-in-place change verbatim.

**Minimal edit set for edit-in-place-until-Base-SHA** (from the analysis; final shape depends on Decision 1):
1. Canonical rule at product-interview's Decisions template "Revising" comment: until this spec's plan.md has `Base SHA:` set, edit decisions of *this* spec in place to final shape, folding the overturned `Chosen` into `Rejected` with what killed it; from Base SHA on, supersede-never-edit. Never edit another spec's block in place at any phase.
2. product-interview Step 5: drop "supersede them," keep the header-flip clause.
3. product-interview Step 6 Q1: drop the supersede half of the flip/supersede rule.
4. product-interview Resumability last bullet: supersede → edit-in-place per rule 1.
5. tech-design 2B "Revise the AC now": pre-execution revise in place, no marker, no superseding pair.
6. tech-design Resumability reopen bullets (×2): supersede → edit-in-place per rule 1.
7. tech-design Rules cross-spec line: add carve-out — a prior spec's block always supersedes.
8. Add a `Base SHA` grep form to write-plan's Plan anchors (the boundary test needs one canonical form).
- `execute-plan` and `write-plan` bodies need no changes; execute-plan Step 2.5 stays the supersession home mid-build.

**Risks + mitigations:**
- Losing "why we rejected X" → covered iff rule 1 mandates the fold into `Rejected` (product-interview's pre-write-reversal rule already blesses this mechanism). 0.88
- Decision edited in place after plan.md exists (Base SHA unset) → task bodies may encode the old choice; mitigation: on such an edit, re-run write-plan Step 5's existing-plan guard. 0.80
- Seat C reversion signal → low risk; optionally name the `Rejected` fields in Seat C's charter. 0.70

## Findings — Part 2: loops and passes

**F5 — 17 backward edges, only 3 bounded.** [verified, 0.85]
Bounded: product-interview Step-3 gate ("one follow-up round"), write-plan mechanical auto-fix (1 retry), write-plan semantic PROCEED loop (1 retry). Unbounded and expensive: tech-design Step-4 verify↔amend; tech-design Step-5 Adjust→re-verify; both find-gaps passes (each re-ask re-offers "Find gaps first" forever); tech-design 2B route-back to product-interview; the any-edit header-flip → wholesale tech-design re-run.

**F6 — User's fix (b) is already implemented.** [verified, 0.90]
product-interview fences find-gaps to "Product/UX gaps only"; tech-design fences to "design-level absences only." Pushback: the leakage felt is the *route-back edge*, not the lens taxonomy.

**F7 — User's fix (c) would be worse.** [verified, 0.85]
product-interview's gaps pass runs before the spec is written — a finding there is a free edit. One joint pass after tech-design would land every product finding on a spec that already has a design, firing the header-flip → full outline re-run each time.

**F8 — "Interview conducted again" is largely a section-placement bug.** [verified, 0.80]
product-interview *has* scoped resume logic ("resume Step 2 at the open branches") but it sits after Step 6 where a re-entry never reads it; tech-design's route-back says "resolve these in product-interview, then re-run tech-design" — full re-run, no delta, no marker named. Matches the repo's own CLAUDE.md rule: when a rule under-fires, fix its section placement.

**F9 — 2B gate's default is mis-set.** [verified, 0.80]
"Route back to product-interview (rec.)" is the most expensive of the four options; "Revise the AC now" is proportionate for the common case (a hard limit bounding a number an AC states) and continues the session. The `[NEEDS CLARIFICATION]` marker mechanism itself is the right weight — keep it; move the `(rec.)`.

**F10 — Header-flip trigger is loose, its consequence wholesale.** [verified, 0.80]
Fires on *any* decision/AC edit; consequence is a full tech-design re-run with fresh 2B fan-out. A reworded AC and a scope reversal cost the same. (Precedent for scoping exists: the AC tag-flip is already "exempt from the supersession protocol.")

**F11 — Redundant pass clusters.** [verified, 0.80]
(i) Lock greps run 3× — deterministic, near-free, keep. (ii) Consumer tracing runs 3× (tech-design outline rule, write-plan Step 3 rule, write-plan S3 review) — author-check + reviewer-check, arguably fine. (iii) product-interview find-gaps re-contests the Step-3 gate's state verdicts minutes after the gate ran, on a draft not yet written — the clearest cut candidate.

**F12 — Deferred idea: move 2B's AC-scoped capacity recon into product-interview Step 3.** [0.60 — needs empirics]
Would delete the route-back class entirely (facts arrive before the WHAT locks), but reverses a deliberate fence ("possibility, not capacity"). Only worth it if 2B-after-clearance blocks are *frequent* — Decision 2 asks the user.

## Observations (outside scope, material)

- **Silent-staleness window:** a WHAT edit during tech-design's Step-5 review window flips nothing (the flip keys on `### Files touched`, withheld until lock); resumability then reads the state as "resume Step 5," skipping Step 2 — a design verified against a superseded WHAT can lock cleanly. [verified, 0.75]
- **trim-spec over-claim:** trim-spec Step 3 item 1 justifies a convention note with "or the lock gate has nothing to grep" — false for `Supersedes:`/`Superseded-by:`; no gate greps those fields. [verified]
- **Trivial-skip staleness gap:** the write-plan trivial path has no outline, so the header-flip and stale-outline gate can never fire there; plan.md can silently stale. [inferred, 0.75]
- **find-gaps nesting:** every gaps pass can go three fan-out levels deep (lenses → triage → second-opinion on pushback), uncapped. [verified, 0.80]
- **Collision check:** `meta/TASKS.md` has six queued edits to execute-plan/execute-chat/write-plan (detail in `~/Desktop/code/agentchatdeck/meta/research/skill-improvements/notes.md`) — check before editing write-plan.
- Prior design record already names the constraints this work serves: `meta/investigations/2026-05-18-workflow-redesign.md` — "the route back must be cheap," "skill proliferation has a cost."

## Proposed fix package (pending decisions below)

1. **Edit-in-place until Base SHA** — the 8-item edit set under F4. [long-term, 0.85]
2. **Bound the four unbounded loops** with the existing 1-retry idiom; find-gaps once per artifact (drop the option from the re-ask after it runs). [long-term, 0.85]
3. **Fix the route-back's two ends** — move product-interview's resume branch to the top of its Protocol; tech-design's route-back names the marker and scopes the re-entry ("resume at this marker only; re-run 2B only for surfaces the changed AC rides on"); move the 2B `(rec.)` to "Revise the AC now." [long-term, 0.80]
4. **Delta re-run on reopen** — keep the loose flip trigger, scope the tech-design re-run to the surfaces/outline sections the changed AC or decision touches. [long-term, 0.75]
5. **Side fixes** — silent-staleness window, trim-spec over-claim, trivial-skip gap (each small, independent).

## Decision log

Walk each PENDING item with the user one at a time; record the call and date; apply edits only after its decision.

| # | Decision | Options (rec. first) | Status | Call |
|---|---|---|---|---|
| 1 | Edit-in-place boundary | Base SHA set (rec.) · tech-design lock · keep supersession, fix only F3 | DECIDED 2026-08-15 | **Base SHA set** — edit in place through interview/design/plan; supersession from Base SHA on; cross-spec always supersedes |
| 2 | Route-back depth | bound only, keep fence (rec. if blocks are rare) · merge 2B recon into product-interview (if frequent) · bound now, watch | DECIDED 2026-08-15 | **Small fix now, watch** — fix-on-the-spot default, scoped resume at the broken point, delta re-check; revisit the recon merge only if late blockers stay frequent |
| 3 | Gaps passes | cap once-per-artifact + drop the state re-contest (rec.) · cap only · make mandatory-once (harness style) | DECIDED 2026-08-15 | **Once + absence-only** — keep in both skills, opt-in, max once each; governing principle recorded: *checkers verify what's written, find-gaps hunts what's not written* — drop PI's state re-contest clause |
| 4 | Reopen cost | delta re-run (rec.) · keep wholesale · scope the trigger instead | DECIDED 2026-08-15 | **Delta re-run** — any-edit tripwire stays; tech-design redoes only the surfaces/outline parts the edit touches |
| 5 | `*(revised per D-NNN-XX)*` marker pre-build | forbid pre-build so marker ⇒ mid-build amendment (rec.) · optional | DECIDED 2026-08-15 | **Forbid pre-build** — pre-build there is no revision concept at all: text is updated to final shape as if always written that way; the tag's presence now always means "changed mid-build" |
| 6 | Global round budget in spec header | skip (rec. — per-loop bounds first) · add counter, escalate at N | DECIDED 2026-08-15 | **Skip** — per-loop bounds cover the pain; revisit only if churn persists after they land |
| 7 | Side fixes (staleness window, trim-spec line, trivial-skip gap) | apply all three (rec.) · pick | DECIDED 2026-08-15 | **Applied all three** — tech-design Resumability mid-design bullet now re-checks the WHAT first; trim-spec scaffolding note corrected (Status line is the grepped form); execute-plan Step 1 checks trivial-skip plans for spec drift since plan.md's last commit |

## Implementation status

- **Applied 2026-08-15 (all decisions):** the full edit package landed across `product-interview`, `tech-design`, `write-plan`, `execute-plan`, `trim-spec` — edit-in-place until Base SHA (boundary: plan.md absent OR `Base SHA:` unset; anchor form in write-plan's Plan anchors), revise-tag forbidden pre-build, find-gaps once + absence-only, verify-loop lap cap, route-back scoped resume + rec. moved to "Revise the AC / decision now", delta re-runs on reopen (with a git-diff method to establish the change), Resumability moved to the top of product-interview's Protocol, plus the three side fixes.
- **Review pass:** three reviewer subagents (one per file) returned 20 findings; all verified and fixed — notably the Base SHA test inverting when plan.md doesn't exist, the execute-plan staleness check failing open (empty `git log` substitution, commit-only range), and the staleness check now covering ALL plans, not just trivial-skip.
- **Stale pointer found:** `meta/TASKS.md` cites `~/Desktop/code/agentchatdeck/meta/research/skill-improvements/notes.md`, which no longer exists — the queued-edits entry needs re-verifying or removal.
- **Watch items:** route-back frequency after the small fix (Decision 2 — revisit the 2B recon merge if still frequent); global round budget (Decision 6 — add only if churn persists).
