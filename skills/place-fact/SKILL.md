---
name: place-fact
description: "Route guidance, state, or evidence already worth keeping to one canonical owner and the narrowest reliable delivery boundary. TRIGGER when: user asks 'where should this go', 'which file/rule/home does this belong in', 'is this in the right place', or 'should this be a pointer'; placing or re-homing kept material."
---

# Place Fact

Primitive: **PLACE** — which durable owner and delivery boundary should hold this material?

## Steps

1. **Name the delivery trigger — the moment a future agent must already hold the material.** A topic, folder, or existing file does not choose the home; the trigger does.
2. **Map the trigger to the narrowest reliable home:**

   | Trigger | Home | Admit only when |
   |---|---|---|
   | Any repository task | Root `AGENTS.md` | The instruction or route is repository-wide and non-derivable. |
   | Reading or editing one mechanism | Comment or docstring beside it | The mechanism needs a constraint, assumption, or tempting-wrong-path warning. |
   | Reading, editing, or creating files in one cohesive subtree | Nearest ancestor `AGENTS.md` | A real module boundary has one rule for every current and future file below it. |
   | Working with files selected by path patterns rather than directory hierarchy | Claude path rule in `.claude/rules/` | Quoted `paths:` globs scope the instruction to matching files. |
   | Starting a named product, design, operations, or decision task | Maintained task document | Cross-cutting context has an inbound route and a workflow that keeps it current. |
   | Running a repeatable repository-local procedure | Named workflow document | The procedure remains multi-step and repository-specific. |
   | Running a repeatable cross-repository or external-platform procedure | Skill | The procedure has a reliable trigger; a repository-internal fact alone is not a skill. |
   | Tracking queued or in-progress work | Active-state document | A workflow reads, updates, and retires it. |
   | Preserving a scoped question, evidence, provisional findings, or open decisions | Dated investigation outside ordinary auto-load | Closure promotes current conclusions, routes unfinished work to active state, and retains only unique evidence. |
3. **Choose the delivery boundary before considering file reuse:**
   - **Create.** Create an artifact when its trigger and scope form a distinct delivery boundary.
   - **Reuse.** Reuse an artifact only when its trigger, scope, audience, upkeep, and retirement path already match.
   - **Split.** Split an artifact when it mixes material with different triggers or scopes.
   - **Judge bloat.** Look for duplicated ownership, mixed scopes, broken routes, and unnecessary eager loading; file count alone is not bloat.
4. **Confirm the full placement contract:**
   - **Owner and scope.** Name one canonical owner and the exact paths, subtree, task, or procedure it governs.
   - **Delivery.** Keep one write path; use a relative symlink, native import, or generated view for another loader. Fall back to a copy only when derivation cannot work, and guard equality automatically.
   - **Upkeep.** Name what keeps the material current: editing it beside its source, a workflow, or an executable guard.
   - **Retirement.** Name the event that removes or re-homes the material.
5. **Prove the delivery before committing the placement:**
   - **Prefer executable guards.** Keep prose only for a decision, rationale, or required companion action that detection alone cannot convey.
   - **Verify every agent.** Confirm every supported agent discovers the material at its trigger and, when applicable, after compaction.
   - **Cover future files.** A Claude path rule may not fire on a new-file write; put a convention governing future files in the nearest `AGENTS.md`.
   - **Store Claude path rules once.** Keep each file-matching rule in `.claude/rules/`, with quoted `paths:` globs.
   - **Point only when needed.** Point from `AGENTS.md` only to a must-read target that will not already auto-load.
   - **Point to Claude path rules only for gaps.** Use one only for a cross-layer obligation or new-file gap; otherwise let the rule fire or widen its paths.
   - **Skip redundant routing.** Never point one `AGENTS.md` to another that already auto-loads, and never maintain a folder-to-owner map.
