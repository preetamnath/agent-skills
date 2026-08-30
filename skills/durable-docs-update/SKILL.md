---
name: durable-docs-update
description: "After a coding task or plan, sweep comments in changed files, then sync high-confidence current guidance through WORTH → PLACE → SHAPE. Change-scoped, not repository-wide. TRIGGER when: user asks to update/sync durable docs, code comments, or AGENTS.md after work; an executor skill reaches close-out."
---

# Durable Docs Update

Make two judgments in order:

| Judgment | Question | A "no" means |
|---|---|---|
| **Sweep** | Should this comment exist? | Delete the comment. |
| **Docs pass** | Does this fact belong in current guidance? | Drop the fact. |

Run the sweep first; otherwise a worthless comment can disappear from the proposals but remain in code.

Callers invoke this skill inline, never as a leaf subagent; it fans out its own subagents.

## Input

Resolve scope through one mode:

| Mode | Use when | Scope and change content |
|---|---|---|
| **A — session** | Run directly in the working session. | Files this agent created or edited, from its Edit/Write history; current state plus session knowledge. |
| **B — range** | A commit range `A..B` is available. | Names from `git diff --name-only A..B`; content from `git diff A..B`. |
| **C — caller-supplied** | An orchestrator delegated uncommitted edits. | Explicit file list plus `git diff -- <those files>`. |

Never derive scope from `git status`; the working tree is process-global. Mode C uses only the caller's named files.

Optional inputs:

- **discoveries** — the caller's `Discovery:` bullets, already reduced to gotchas or couplings.
- **context** — the work's goal and criteria.
- **spec** — the work's `spec.md`; Step 1 mines its locked `D-NNN-XX` decisions.

## Protocol

### Step 0 — Load the lenses

Load `vet-fact` for WORTH, `place-fact` for PLACE, and `tighten-instruction` plus `structure-prose` for SHAPE. Relay the loaded criteria in every Step 1 and Step 4 subagent brief; subagents do not inherit parent-loaded skills.

### Step 1 — Sweep comments, then gather candidates

Resolve the mode and build the in-scope code-file list. For each file, sweep its comments before gathering doc candidates. Inspect each changed code file in full, never the whole repository.

For each comment, in order:

1. If it contradicts the code, rewrite it to the current fact.
2. If it fails `vet-fact`, score WORTH from `0.0–1.0`; delete at `≥ 0.75`, otherwise leave it and return it as `left_alone`.
3. If its fact is sound but muddy, tighten it in place.
4. If its fact also belongs in current guidance, hold it as a `doc_candidate` and leave a one-line comment behind.

Score only comment WORTH decisions. Verify contradictions against code without scoring. Apply `tighten-instruction`, then `structure-prose`, to every rewritten or tightened comment.

Keep a `D-NNN-XX` or `AC-NNN-XX` id beside the fact it labels. Cut task ids, wave numbers, and `F-NNN-XX` finding ids while keeping any fact they obscure.

Run the work by mode:

- **Mode A — main agent, serial.** Use session memory. If the file set is too large and a commit range exists, switch to Mode B. Per file: sweep, note changes and gotchas or couplings, then inspect related sources.
- **Modes B/C — fan out.** Group files by nearest parent `AGENTS.md` and dispatch up to 3 Sonnet subagents. Assign each file to exactly one subagent.
  - Give each subagent its files, scoped diff, matching discoveries, locked decisions, and the Step 0 criteria. The sweep edits; the gather only proposes.
  - Require scoped Git reads and mutations. Never let a subagent run `git stash`, `git checkout -- .`, `git reset`, or another whole-tree mutation. Read committed baselines with `git show HEAD:<path>`.
  - Require a sweep tally (`corrected`, `deleted`, `tightened`), `deleted` and `left_alone` lists as `{ file, line, text, confidence }`, every Step 2 row at `≥ 0.75`, and the count below threshold. Return no file contents.
  - Merge tallies, deduplicate proposals by target and rule, keep the highest confidence, and treat shared path rules or maintained documents as one target.

Inspect only related sources:

- The file's comments, ancestor `AGENTS.md` files, and matching path rules.
- A root-routed task document only when the change purpose matches its route.
- Any target selected by `place-fact`; crossing modules does not choose a document by itself.

Gather and filter:

- **Comment candidates** — facts held during the sweep.
- **Discoveries** — passed `Discovery:` bullets.
- **Locked decisions** — locked spec decisions that constrain an in-scope file.
- **Matching sources** — merge a discovery with the decision it restates; keep the decision's rationale wording.
- **Existing facts** — drop duplicates; use UPDATE when current guidance drifted from changed code.
- **Historical breadcrumbs** — classify as TRIM.
- **Excluded records** — active-state documents, dated investigations, session logs, handoffs, process/workflow documents, `.agents/skills/`, `.claude/skills/`, `.claude/commands/`, and material unrelated to the changed code.

### Step 2 — Classify, place, shape, and score

Classify each potential change:

- **ADD** — add a current rule, instruction, or in-file comment at the boundary selected by `place-fact`.
- **UPDATE** — align an existing fact with changed code.
- **TRIM** — keep the fact but remove bloat or breadcrumbs; preserve any valid `Discovered:` freshness stamp defined by `vet-fact`.
- **DELETE** — remove a fact that no longer applies.
- **MOVE** — move a fact to its correct owner and delivery boundary.

For every ADD or MOVE, record `place-fact`'s full placement contract in the analysis; do not paste the contract into the repository. Choose the delivery boundary before considering whether to reuse, create, or split an artifact.

Shape every proposal with `tighten-instruction`, then `structure-prose`:

- Write current guidance in present tense, without history.
- When `vet-fact` keeps rationale, preserve the reason as `behaviour — constraint`.

Score confidence from `0.0–1.0` that the fact, action, and target are correct. Score impact as `Label (value)`: Minimal (0.25), Low (0.5), Medium (1), High (2), or Massive (3).

### Step 3 — Present and gate

Apply every candidate with confidence `≥ 0.75`; drop every candidate below it, regardless of source or action. Do not add a separate proof gate for MOVE or DELETE.

Skip triage because the proposal table makes these edits easy to review and revert. Present qualifying proposals, sorted by confidence:

```text
| # | Confidence | Impact | Target | Action | Proposal | Why |
|---|---:|---:|---|---|---|---|
| 1 | 0.92 | High (2) | src/foo/views.py:142 | ADD comment | "Trailing slash required — webhook signer drops it otherwise" | Recurring gotcha found this session |
| 2 | 0.88 | Massive (3) | src/foo/AGENTS.md §Auth | ADD | "JWT verification runs before request parsing — parsing first breaks the HMAC check" | Cross-file coupling is not locally visible |
| 3 | 0.83 | Minimal (0.25) | src/foo/AGENTS.md §Style | TRIM | Keep the present rule; cut plan history and the obsolete rationale paragraph | Historical bloat |
```

Apply every qualifying row without asking. Report the count below threshold. If none qualify, continue to Step 5; the sweep still gets reported.

### Step 4 — Apply and check coherence

Group qualifying edits by file and dispatch up to 3 Sonnet subagents. Assign each file to one subagent; assign both sides of a MOVE to the same subagent. Pass proposals verbatim and include the Step 1 Git-safety rules.

Each subagent:

1. Applies the qualifying proposals to its files.
2. Applies `tighten-instruction`, then `structure-prose`, only to lines it changed.
3. Returns one line per file: `src/foo/AGENTS.md: +1 rule under §Auth, TRIM §Style`.

After all subagents return:

1. For every document this run created, apply `compress-file`, `tighten-file`, then `structure-prose`.
2. Cold-read each changed durable document in full. Fix only issues this run caused or exposed: contradiction, duplicate ownership, mixed delivery scopes, broken routes, or unnecessary eager loading.
3. Keep the normal `≥ 0.75` confidence gate; this coherence read is not a separate destructive-edit gate.

### Step 5 — Report

The caller does not repeat this report.

```text
**Docs sync:**
- Comments: [n] corrected, [m] deleted, [k] tightened
  - deleted: [file:line — "text" (0.NN), one per line | none]
  - left alone, unsure: [file:line — "text" (0.NN), one per line | none]
- Docs: [file — what changed, one per line | none needed]
- Dropped: [K] candidates below 0.75
- Instruction delta: [net lines], [artifacts added], [artifacts removed], [always-loaded lines]; review signal only, never a quota
```
