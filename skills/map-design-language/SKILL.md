---
name: map-design-language
description: "Research a project's established design language and write or refresh a lean meta/DESIGN.md that grounds mockups, critiques, and new UI. TRIGGER when: user asks to map, document, bootstrap, or refresh the design language; a skill needs design grounding and meta/DESIGN.md is missing, incomplete, or stale. SKIP when: meta/DESIGN.md is current (read it); the project has no established UI and needs a new aesthetic (offer frontend-design)."
---

# Map Design Language

Research the stable visual rules already established in a project and record them in one `meta/DESIGN.md`. The file explains how the UI should look and behave; runtime styling sources keep ownership of exact values.

## Protocol

### Step 1 — Detect mode

Check for `meta/DESIGN.md`:

- **Missing** → **bootstrap**: research the established UI and create the file.
- **Exists** → read the whole file, then use the Step 2 source scan to decide whether it needs a refresh.

When no established UI exists, stop and offer to invoke `frontend-design`; this skill records a design language and does not invent one.

### Step 2 — Map surfaces and canonical sources

Identify whether the repository has one design language or several distinct UI surfaces with different toolkits, token vocabularies, audiences, or render targets. Inspect the root package manifests, workspaces, UI directories, framework imports, and existing product or brand guidance.

- **One design language** → use one flat document without a surfaces table.
- **Several surfaces** → keep one `meta/DESIGN.md`; add a surfaces table and surface-specific blocks. Never mix tokens or toolkit rules across surfaces.

Find the runtime sources that own exact styling values. Sources can include CSS files, design-token files, Tailwind or framework theme configuration, component-library theme objects, and platform-owned token documentation.

- **Canonical source exists** → record token names, roles, and source paths; do not copy the complete palette or scale into `DESIGN.md`.
- **Values are distributed** → record only verified values that repeat or materially constrain new UI, cite their source paths, and state that `DESIGN.md` is a maintained reference rather than runtime authority.
- **Library or platform owns appearance** → record the allowed project-used tokens or props and link the authoritative documentation; do not mirror the full library.

If the repository layout is not clear after a light scan, dispatch one read-only subagent to return candidate surfaces and canonical styling sources with paths. Confirm a genuinely ambiguous surface boundary with the user.

For an existing `meta/DESIGN.md`, stop and report that no update is needed when the scan finds no conflict, material gap, or caller-named change. Otherwise, enter **refresh** mode for the affected sections.

### Step 3 — Research the established language

Dispatch read-only subagents in proportion to the surface count:

- **One design language** → one subagent covers the complete document.
- **Several surfaces** → one subagent per surface.
- **Refresh** → inspect only affected surfaces and sources, while preserving current sections and human edits elsewhere.

Each subagent returns concise facts with supporting paths:

- audience and the UI's established visual character, density, hierarchy, and dominant interaction approach;
- framework, component library, styling model, project-used components, official documentation, and inherent toolkit constraints;
- semantic color roles and themes; typography roles and hierarchy; layout, responsive behavior, and navigation model; shape and depth;
- motion rules when an established motion system exists; iconography and imagery when relevant;
- repeated component combinations and cross-component patterns, not individual page layouts;
- interface-copy rules for labels, errors, empty states, statuses, capitalization, and tone;
- project-specific do's and don'ts that prevent likely mistakes;
- canonical sources, ownership boundaries, related guidance, and refresh triggers.

Derive every fact from the current UI, code, or maintained product and brand documents. If the evidence does not establish a rule, report it as absent instead of inventing one.

### Step 4 — Assemble and checkpoint

Assemble the [DESIGN.md template](#designmd-template) with stable rules and source links:

- Keep each section to the project-used subset; exclude feature behavior, page-specific layouts, exhaustive library catalogs, and universal design advice.
- Write `Overview` from observable evidence. Do not substitute vague adjectives such as “modern,” “clean,” or “intuitive” for concrete rules.
- Keep universal quality rules such as contrast, keyboard access, focus visibility, and touch-target size in consuming skills. Record a project-specific accessibility mode, constraint, or exception in the section it affects.
- List canonical sources once in `Maintenance`. Add an inline path only for a non-obvious pattern or important constraint.
- Omit `Motion` when no deliberate motion system exists. Omit `Iconography and imagery` only when neither applies.

Before writing, present this checkpoint and confirm via `AskUserQuestion` (`Write it` / `Adjust`):

```text
**Design language summary:**
- Surfaces: <single design language | surface — audience — toolkit, one per line>
- Canonical sources: <paths>
- Overview: <established character, density, hierarchy, and interaction approach>
- Stable rules: <most important toolkit, pattern, content, and guardrail facts>
```

### Step 5 — Write or refresh

- **Bootstrap** → create `meta/DESIGN.md` from the template.
- **Refresh** → edit only affected sections; preserve current facts and human edits elsewhere.

Read the complete result cold, fix any conflict or missing source, and report the path plus the sections changed.

---

## DESIGN.md template

Use plain Markdown without YAML frontmatter. The single-surface form is canonical:

```markdown
# Design reference — <project>

<One sentence naming the UI surface and purpose of this reference.>

## Overview

<The audience, established visual character, density, hierarchy, and dominant interaction approach. Use concrete, observable rules.>

## Toolkit

- **Framework:** <framework and version>
- **Component library:** <library and version>
- **Styling model:** <CSS, utilities, theme props, platform-owned, or mixed>
- **Documentation:** <authoritative links>
- **Constraints:** <inherent toolkit limits only>

## Colors

- <Semantic roles, theme relationships, and colors reserved for specific meanings. Name tokens instead of copying code-owned values.>

## Typography

- <Font roles for UI, prose, headings, code, or data; hierarchy and density; special rules such as tabular numbers or reading measure.>

## Layout

- <Page width or grid model, main regions, responsive behavior, density, spacing approach, and navigation changes across viewports.>

## Shape and depth

- <Corner, border, divider, shadow, card, and surface-hierarchy rules. Keep this section even when the system is simple.>

## Motion

- <What moves, why, and the established timing or easing rules; patterns to avoid. Omit this section when no deliberate motion system exists.>

## Iconography and imagery

- <Approved icon set, icon treatment, photography or illustration style, asset sources, and restrictions. Omit when neither applies.>

## Components

- <Project-used components and stable usage rules.>

## Patterns

- <Repeated component combinations and cross-component behavior; no page-specific layouts.>

## Content

- <Interface-copy rules for labels, validation, empty and error states, statuses, capitalization, and tone. Exclude marketing strategy and page content.>

## Do's and Don'ts

- <Project-specific guardrails that prevent likely mistakes. Write `None established beyond the rules above.` when no additional guardrail is supported.>

## Maintenance

- **Canonical sources:** <paths that own exact values and implementation facts>
- **This file owns:** <design rationale and stable rules>
- **Refresh when:** <surface, toolkit, token-role, pattern, or content-rule changes that affect this reference>
- **Related guidance:** <brand, product, or other canonical documents; omit when none>
```

For several surfaces:

1. Keep one global `Overview`.
2. Add `## Surfaces at a glance` with `Surface`, `Audience`, `Path`, `Toolkit`, and `Styling model` columns.
3. Add one `## <Surface>` block per surface and use `Toolkit` through `Do's and Don'ts` as ordered `###` subsections.
4. Keep a rule global when it applies to every surface; otherwise put it only in the governing surface block.
5. End with one global `Maintenance` section.
