---
description: Seed or migrate canonical, boundary-scoped agent guidance across a repository. Map the code and current delivery system, preserve correct artifacts, plan one canonical owner with derived views, shape every change, and verify facts and delivery. Use for a new guidance setup, a sprawling root file, or a mature repository adopting current patterns.
---

# Seed or Migrate Agent Context

Infer seed or migrate mode from repository evidence, then apply WORTH → PLACE → SHAPE to preserve correct artifacts and change only the gaps.

## When to use

- The repository has no structured agent guidance, one sprawling root instruction file, or an established setup that needs current ownership, scoping, symlink, rule, or guard patterns.
- At least one non-obvious subsystem, coupling, convention, or gotcha earns durable guidance.

For a small single-purpose repository, write one root `AGENTS.md` plus any required provider delivery view directly.

Use [Root `AGENTS.md` Writing Guide][root-agents-guide] for root content and [Canonical Agent Delivery][canonical-delivery-guide] for `AGENTS.md`, `CLAUDE.md`, project-skill, symlink, and delivery-guard mechanics. Do not duplicate either guide here.

## Inputs

1. **Target repository** — defaults to the current working directory.
2. **Reference repository** (optional) — a trusted example whose delivery-boundary choices may inform, never dictate, this repository.
3. **Decision records** (optional) — ADRs, locked spec decisions, design records, or known invariants to verify against current code.
4. **Transient sources** (optional) — active-state files such as `CONTEXT.md` or `plan.md`; mine them but never reconcile, rewrite, or delete them.

## Workflow

### Phase 0 — Load and relay the lenses

Invoke the Skill tool to load `vet-fact`, `place-fact`, `compress-file`, `tighten-instruction`, and `structure-prose`. Relay only the criteria each subagent applies; subagents do not inherit parent-loaded skills.

### Phase 1 — Infer mode and map the repository in parallel

Classify the run from repository evidence:

- **Seed** — no repository-owned instruction artifacts exist.
- **Migrate** — any repository-owned instruction artifact exists and needs reconciliation, tighter placement, canonical delivery, or current guards.

Do not ask the user to choose when the evidence is clear. Record the inferred mode and why.

Dispatch read-only agents across independent subtrees and sources. Scale the pool to the repository; each agent returns a self-contained report and proposes no homes.

- **Code and flows.** Map entry points, subsystem boundaries, data/control flow, cross-cutting couplings, conventions, gotchas, and non-obvious verification obligations.
- **Current delivery.** Inventory comments, root and nested `AGENTS.md`, provider views such as `CLAUDE.md`, project skills, path-scoped rules, delivery guards, maintained current documents, workflows, active state, and dated evidence.
- **Delivery mechanics.** Evaluate mechanics against [Canonical Agent Delivery][canonical-delivery-guide].
- **Reference repository.** When supplied, extract useful boundary decisions; never copy an artifact merely because the reference has one.
- **Decision records.** When supplied, extract locked current conclusions and their rationale; verify each against code and leave raw evidence in its evidence lane.

Return each candidate fact with its source, constrained paths, and delivery trigger. Mark transient sources so later phases leave them untouched.

### Phase 2 — Build the placement-contract plan

Run current-guidance candidates through `vet-fact`, then route keeps through `place-fact`. Skip WORTH for active state and dated evidence; use `place-fact` only when those records themselves need placement.

Record one row per proposed or existing artifact:

```text
| # | Action + artifact | Delivery trigger + scope | Canonical owner | Delivery views | Upkeep / guard | Retirement | Why this boundary | Confidence |
|---|---|---|---|---|---|---|---|---:|
```

Use `KEEP`, `CREATE`, `REWRITE`, `MOVE`, `SPLIT`, or `RETIRE` as the action. Record `place-fact`'s complete contract in the table; choose the delivery boundary before considering reuse.

- Create only when no current artifact has the same trigger, scope, audience, upkeep, and retirement path.
- Reconcile existing instruction artifacts in the same table; a correct artifact is KEEP and remains untouched.
- **Root content.** Write or decompose root guidance through [Root `AGENTS.md` Writing Guide][root-agents-guide].
- **Canonical delivery.** Make `AGENTS.md` canonical and derive any required provider view through [Canonical Agent Delivery][canonical-delivery-guide].
- List every transient source as a non-proposal and leave it untouched.
- Flag an unrelated catch-all document for a later `refine-file` audit instead of rewriting or deleting it here.
- List considered but rejected artifacts below the table with a one-line reason.

### Phase 3 — Sanity-check the plan in parallel

Dispatch `sanity-checker` agents with separate focuses:

- **Admission and granularity.** Each artifact has a distinct delivery boundary; no thin duplicate, mixed scope, or topic-owned catch-all remains.
- **Coverage and truth.** Every high-risk fact has an owner and still matches current code; derivable facts and stale decisions are absent.
- **Delivery and lifecycle.** Every supported agent receives the fact at its trigger; views, guards, upkeep, and retirement are complete.

Merge verified P0/P1 findings into the plan and record rejected findings.

### Phase 4 — Clarify and confirm

Bundle unresolved placement choices into one `AskUserQuestion` with at most four questions. Name every proposed CREATE, SPLIT, MOVE, or RETIRE so the user can challenge it.

Present the revised contract table and non-proposals for confirmation. After approval, use `TaskCreate` for each artifact plus shaping, verification, and final reporting.

### Phase 5 — Draft in dependency order

Build the actual dependency graph: create canonical targets before pointers, imports, symlinks, generated views, or other consumers. Draft independent targets in parallel.

- Draft only confirmed CREATE, REWRITE, MOVE, or SPLIT rows; leave KEEP rows untouched.
- Apply each confirmed RETIRE after its dependents are removed or re-homed; keep the retiring source and replacement owner in one task.
- Assign every MOVE or SPLIT source, destination, and delivery view to one `general-purpose` subagent; otherwise assign each canonical artifact and its views to one subagent.
- Give every drafter the self-contained brief below, including the loaded lens criteria.
- Accept verified corrections to the brief; never soften a false fact into vague prose.
- If writing under `.claude/rules/` is blocked as self-modification, create a frontmatter-only placeholder, then re-dispatch the body edit.

### Phase 6 — Shape and cold-read every changed artifact

For each created or rewritten text artifact:

1. Apply `compress-file` to dissolve repeated or misplaced structure.
2. Apply `tighten-instruction` to every changed instruction block.
3. Apply `structure-prose` only to fused blocks whose independent rules need scan-friendly structure.
4. Read the complete artifact cold and fix only contradictions, duplication, broken referents, or mixed delivery scopes caused or exposed by this run.

Use no file or line quota. Record net instruction lines, artifacts added or removed, and always-loaded growth as review signals.

### Phase 7 — Verify facts and delivery in parallel

Run two read-only lanes, then one fix pass:

- **Fact lane.** Verify every load-bearing claim in changed current guidance against its source code, configuration, or guard. Correct false claims; drop derivable, stale, default, or duplicated claims.
- **Delivery lane.** Verify each placement contract: canonical owner, exact scope, working pointers/views, automatic equality guards for unavoidable copies, quoted and resolving rule globs, future-file coverage, supported-agent discovery, upkeep, retirement, and separation of current guidance from state/evidence.

1. Apply confirmed high-confidence P0/P1 fixes, then cold-read every affected artifact again.
2. Preserve one canonical owner and remove only delivery views made unnecessary by the fix.
3. After implementation work changes source comments or durable facts, run `durable-docs-update` for ongoing maintenance; this command owns repository-wide seeding and migration.

### Phase 8 — Report

```text
**Agent guidance seeded or migrated:**
- Mode: [seed | migrate] — [evidence]
- Artifacts: [created, rewritten, moved, split, retired, and kept paths]
- Placement contracts: [final table]
- Fact corrections: [corrected or dropped claims | none]
- Non-proposals: [artifact and reason | none]
- Open decisions: [decision | none]
- Growth: [net instruction lines, artifacts added, artifacts removed, always-loaded lines]; review signal only
```

## Drafting brief

```text
# Artifact
[Action, path, and artifact kind]

# Placement contract
[Delivery trigger; canonical owner and scope; delivery views; upkeep/guard; retirement; why this boundary]

# Inspect first
[Exact source paths]

# Facts to encode
[Verified fact candidates with source symbols]

# Exclude
[Facts owned elsewhere, derivable material, state/evidence, and unapproved scope]

# Lenses
[Loaded vet-fact, place-fact, tighten-instruction, and structure-prose criteria]

# Verification and return
Verify every fact against its source. Drop and report false candidates. Return the changed path and every factual or placement deviation.
```

[root-agents-guide]: https://github.com/preetamnath/agent-skills/blob/main/guides/root-AGENTSmd-writing-guide.md
[canonical-delivery-guide]: https://github.com/preetamnath/agent-skills/blob/main/guides/canonical-agent-delivery.md
