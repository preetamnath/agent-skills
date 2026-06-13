---
name: place-fact
description: "Route a kept fact to its durable home by delivery trigger and most-local-wins — across in-file comment, nested CLAUDE.md, path-scoped rule, root CLAUDE.md, ARCHITECTURE.md, or a skill. TRIGGER when: user asks 'where should this go', 'which file/rule/home does this belong in', 'is this in the right place', 'should this be a pointer'; placing or re-homing a fact already judged worth keeping."
---

# Place Fact

Primitive: **PLACE** — which durable home does this fact belong in?

## Steps

1. **Name the delivery trigger — the moment a future agent must already hold the fact.** The trigger, not the topic, picks the home.
2. **Map trigger → home:**

   | Trigger — when the agent must already hold the fact | Home |
   |---|---|
   | Every session; must survive `/compact` | Root `CLAUDE.md`; unscoped `.claude/rules/*.md` |
   | Agent reads or edits a matching file | In-file comment; path-scoped `.claude/rules/*.md`; nested `CLAUDE.md` |
   | Task spans modules: design or cross-module debug | Root `ARCHITECTURE.md` |
   | External SDK / platform work | Skill, bundled with procedure |

   A **skill** is a home *only* for external-platform knowledge fused with procedure (fetch-the-docs → validate steps). Repo-internal facts have no description to match and no procedure to bundle — never a skill.

   **Not homes:** module `architecture.md` and `*-quirks.md` — no auto-load trigger, no write-path, so they drift. Decompose instead: per-file fact → in-file comment; module invariant → path-scoped rule or nested `CLAUDE.md`; quirk catalog → a path-scoped rule on the affected globs (or the platform skill if SDK-specific).
3. **Within "reads or edits a matching file," take the most-local home the feature's shape allows:**
   - **In-file comment** — a constraint, assumption, or coupling visible from that one file. Prefer it; ships with the code, needs no glob.
   - **Nested `CLAUDE.md`** — a clean single-folder module where the folder *is* the feature boundary; covers new-file `Write` inside it.
   - **Path-scoped rule** — a feature interleaved across shared folders it doesn't own; a multi-glob rule is the only file-triggered surface that reaches across folders. Does not fire on new-file `Write`.
4. **Confirm a write-path backs the home** — route only to homes a workflow maintains, not orphan files.
5. **Check loading mechanics against the trigger:**
   - Root `CLAUDE.md` and unscoped rules load eagerly and re-inject after `/compact`.
   - Nested `CLAUDE.md` and path-scoped rules are lost on `/compact`, re-arm on the next matching read.
   - Nothing fires on new-file `Write` — a convention a not-yet-written file must satisfy needs the directory's `CLAUDE.md`.
   - `ARCHITECTURE.md` isn't auto-discovered; an `@path` import is eager (full-cost every session), not a lazy pointer.
   - Rules need YAML frontmatter with a `paths:` list of **quoted** globs (`"**/*.md"`); unquoted patterns starting with `*` or `{` break YAML.
6. **Pointer rule — emit a pointer only to a target that won't auto-load on the trigger the reader is already on, and only when it carries a must-know-before-you-touch obligation:**
   - **Justified:** root `CLAUDE.md` → an `ARCHITECTURE.md` section or a skill — neither auto-loads.
   - **Narrow:** `CLAUDE.md` → a rule, only when the rule's glob is deliberately *narrower* than the files the obligation touches (a cross-layer audit contract, or the new-file-`Write` gap):
     - Glob already covers the reader's files → it auto-loads → no pointer.
     - Rule should simply fire on those files → widen the glob, no pointer.
     - Widening would re-arm a heavy rule on edits it shouldn't gate → keep the pointer.
   - **Never:** `CLAUDE.md` → `CLAUDE.md`, or a folder→owner map — those auto-load on touch; the map only rots on rename.
7. **One fact, one home; no home restates another.** If two homes tempt you, the fact is two facts or you named the wrong trigger.
