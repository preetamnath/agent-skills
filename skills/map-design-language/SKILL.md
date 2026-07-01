---
name: map-design-language
description: "Research a project's design language and write or refresh a lean meta/DESIGN.md of facts — surfaces, toolkits, tokens, styling models, docs pointers — that grounds mockups and new UI. TRIGGER when: user asks to map, document, or bootstrap the design language, or to create/refresh meta/DESIGN.md; a skill needs grounding facts and meta/DESIGN.md is missing or stale. SKIP when: meta/DESIGN.md exists and is current (just read it); inventing a new aesthetic from a blank canvas (frontend-design)."
---

# Map Design Language

Research what a project's UI is actually built from — toolkits, tokens, components, styling models — and record it as a lean `meta/DESIGN.md` of **facts**. Other skills (`generate-mockups`, `product-interview`) and humans read it to ground UI work. This skill writes the facts; how to *use* them (fidelity, how to mock) belongs to the consuming skill.

## When to use

YES: no `meta/DESIGN.md` exists and a skill or human needs grounding facts; the file exists but a surface's toolkit/tokens changed or it has gaps; the user asks to map/document/bootstrap/refresh the design language.

NOT this if:
- `meta/DESIGN.md` exists and is current → just read it.
- you're inventing a new aesthetic from a blank canvas → `frontend-design`.

## Protocol

### Step 1 — Detect state and mode

Check for `meta/DESIGN.md`:
- **Missing** → **bootstrap** mode: research everything, write the file.
- **Exists** → read it. A surface's toolkit/tokens changed, or blocks are missing/incomplete → **refresh** mode: update the affected blocks only. Current and complete → stop; tell the user it's already good.

### Step 2 — Probe the surfaces (don't assume)

Determine whether the project has **one implicit surface** or **several distinct UI contexts** — different toolkits, audiences, or render targets (e.g. an admin app vs a buyer extension, web vs email). Do a light scan (root `package.json`/workspaces, `extensions/` or app dirs, framework imports) — if the layout isn't obvious at a glance, delegate the scan to a single read-only `general-purpose` subagent that returns the candidate surface list (name + path + toolkit guess). If ambiguous, confirm the surface list via `AskUserQuestion`.

- **One surface** → the file is a single flat facts block, **no Surfaces table**.
- **Multiple surfaces** → a Surfaces table + one block per surface.

### Step 3 — Fan out research (read-only)

Dispatch parallel read-only `general-purpose` agents, scaled to the surface count:
- **One surface** → one agent covers styling system + tokens + components.
- **Multiple surfaces** → one agent per surface (plus a surface-map agent if the layout is unclear).

Each agent returns, concretely and with file paths: toolkit + version · the tokens actually used (names and/or values) · key components / signature patterns · the **styling model** (free-form CSS vs prop-constrained component library) · where appearance comes from (own CSS vs inherited branding) · the library's docs link. Extract real values; don't dump files.

**Refresh:** fan out only over the surfaces whose blocks are stale or incomplete — leave current blocks unread.

### Step 4 — Assemble and checkpoint

Synthesize into the [DESIGN.md template](#designmd-template) — **facts only**. Do NOT write fidelity ratings or how-to-mock guidance (that is the consuming skill's job). Keep it lean: the project-used subset + a docs link per external library, not a mirror of the library. Summarize the surfaces + key facts in chat and confirm via `AskUserQuestion` ("Write it" / "Adjust") before writing. **Refresh:** synthesize only the affected blocks; leave the rest untouched.

### Step 5 — Write or refresh

- **Bootstrap** → write `meta/DESIGN.md` from the template; stamp the Maintenance date.
- **Refresh** → edit only the changed blocks in place; keep structure and any human edits; update the Maintenance date. Say which blocks changed.

Report the path.

## Rules

- **Facts only.** DESIGN.md states what the UI is made of. Fidelity expectations and how-to-mock live in the consuming skill (`generate-mockups`), never here.
- **Probe surfaces, don't assume.** One implicit surface → a single flat block, no Surfaces table. Add the table only for genuinely distinct toolkits.
- **Point to library docs; don't mirror.** For an external library, capture only the project-used subset + a docs link — the library owns its exhaustive API.
- **Lean v1.** Enough to ground UI work, not a full design-system spec.
- **Read-only research.** The fan-out agents only read; the parent assembles and writes.
- **Refresh in place.** Update changed blocks; never rewrite a maintained file wholesale.

---

## DESIGN.md template

Inline the filled version into `meta/DESIGN.md`. Omit the Surfaces table and the surface numbering for a single-surface project.

```markdown
# Design reference — <project>

The design language <per surface, if multiple>, for grounding mockups and new UI. <If multi-surface: ground against the specific surface being worked on — token vocabularies are not interchangeable across surfaces.>

## Surfaces at a glance   <!-- OMIT for a single-surface project -->

| # | Surface | Audience | Toolkit | Styling model |
|---|---|---|---|---|
| 1 | <name + path> | <who> | <framework + lib + version> | <free CSS · or prop-only + branding source> |

## <Surface name>   <!-- one block per surface; a single surface gets one block, unnumbered -->

- **Toolkit:** <framework + component library + version>
- **Docs:** <link to the library's UI docs>   <!-- external libraries only -->
- **Components:** <the components / signature patterns actually used>
- **Tokens:** color <values> · spacing <scale> · radius <scale> · type <families/weights>
- **Styling model:** <free-form CSS · or prop-constrained>; appearance from <own CSS · or inherited branding>

## Maintenance

- Generated <date> from agent research.
```
